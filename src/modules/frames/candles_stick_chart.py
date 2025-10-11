import mplfinance as mpf
import pandas as pd
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QLabel, QLineEdit, QMessageBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from stellar_sdk import Server, Asset, TransactionBuilder, Network


class DexTradingChart(QFrame):
    """📈 Stellar DEX chart with EMA/SMA, order-book heatmap & Buy/Sell buttons."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.server = getattr(self.bot, "server", Server("https://horizon.stellar.org"))

        # Assets
        self.base_asset = Asset.native()  # XLM
        self.counter_asset = Asset("USDC", "GDMTVHLWJTHSUDMZVVMXXH6VJHA2ZV3HNG5LYNAZ6RTWB7GISM6PGTUV")


        # Chart setup
        self.df = pd.DataFrame()
        self.fig = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.fig.subplots_adjust(bottom=0.2)

        # UI
        self._init_ui()
        self._refresh_data()
        self._setup_timer()

        # Interactivity
        self.canvas.mpl_connect("scroll_event", self._on_scroll)

    # ------------------------------------------------------------------
    # 🧱 UI SETUP
    # ------------------------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()

        self._add_button(toolbar, "🔄 Refresh", self._refresh_data)
        self._add_button(toolbar, "➕ Zoom In", lambda: self._zoom_chart(0.8))
        self._add_button(toolbar, "➖ Zoom Out", lambda: self._zoom_chart(1.2))
        self._add_button(toolbar, "💾 Save", self._save_chart)

        # --- Trade Controls ---
        self.amount_entry = QLineEdit()
        self.amount_entry.setPlaceholderText("Amount (XLM)")
        self.price_entry = QLineEdit()
        self.price_entry.setPlaceholderText("Price (USDC)")

        self.buy_btn = QPushButton("🟢 Buy")
        self.sell_btn = QPushButton("🔴 Sell")
        self.buy_btn.clicked.connect(lambda: self._execute_trade("buy"))
        self.sell_btn.clicked.connect(lambda: self._execute_trade("sell"))

        toolbar.addWidget(self.amount_entry)
        toolbar.addWidget(self.price_entry)
        toolbar.addWidget(self.buy_btn)
        toolbar.addWidget(self.sell_btn)

        self.status_label = QLabel("Status: Ready")
        toolbar.addWidget(self.status_label)

        layout.addLayout(toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def _add_button(self, layout, text, callback):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        layout.addWidget(btn)

    # ------------------------------------------------------------------
    # ⏱ Auto Refresh
    # ------------------------------------------------------------------
    def _setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_data)
        self.timer.start(30000)  # 30s

    # ------------------------------------------------------------------
    # 📊 Fetch Trades + Orderbook
    # ------------------------------------------------------------------
    def _refresh_data(self):
        try:
            self.status_label.setText("Fetching market data...")
            trades_call = (
                self.server.trades()
                .for_asset_pair(self.base_asset, self.counter_asset)
                .order(desc=True)
                .limit(200)
                .call()
            )
            records = trades_call.get("_embedded", {}).get("records", [])
            if not records:
                self.status_label.setText("⚠️ No trades available.")
                return
            data = []
            for r in records:
                ts = pd.to_datetime(r["ledger_close_time"])
                price = float(r["price"]["n"]) / float(r["price"]["d"])
                amount = float(r["base_amount"])
                data.append([ts, price, amount])

            df = pd.DataFrame(data, columns=["Date", "Price", "Volume"])
            df = df.set_index("Date").sort_index()
            ohlc = df["Price"].resample("5T").ohlc()
            ohlc["Volume"] = df["Volume"].resample("5T").sum()
            ohlc.dropna(inplace=True)

            # Indicators
            ohlc["EMA20"] = ohlc["close"].ewm(span=20).mean()
            ohlc["SMA50"] = ohlc["close"].rolling(window=50).mean()

            self.df = ohlc
            self._plot_chart()
            self.status_label.setText("✅ Market updated.")
        except Exception as e:
            self.status_label.setText(f"❌ Fetch error: {e}")
            self.status_label.setStyleSheet("background-color: red")
            print(e)

    # ------------------------------------------------------------------
    # 🧮 Plot Chart + Heatmap
    # ------------------------------------------------------------------
    def _plot_chart(self):
        self.ax.clear()

        mpf.plot(
            self.df,
            type="candle",
            ax=self.ax,
            style="yahoo",
            show_nontrading=False,
        )

        # EMA/SMA overlays
        self.ax.plot(self.df.index, self.df["EMA20"], color="orange", label="EMA 20")
        self.ax.plot(self.df.index, self.df["SMA50"], color="cyan", label="SMA 50")

        # Add order-book heatmap
        try:
            book = self.server.orderbook(self.base_asset, self.counter_asset).call()
            bids = pd.DataFrame(book.get("bids", []))
            asks = pd.DataFrame(book.get("asks", []))
            if not bids.empty:
                bids["price"] = bids["price"].astype(float)
                bids["amount"] = bids["amount"].astype(float)
                self.ax.fill_between(
                    bids["price"], 0, bids["amount"], color="green", alpha=0.15, label="Bids"
                )
            if not asks.empty:
                asks["price"] = asks["price"].astype(float)
                asks["amount"] = asks["amount"].astype(float)
                self.ax.fill_between(
                    asks["price"], 0, asks["amount"], color="red", alpha=0.15, label="Asks"
                )
        except Exception as e:
            print(f"[OrderBook] Error: {e}")

        self.ax.legend(loc="upper left")
        self.ax.set_title("Stellar DEX: XLM/USDC with Orderbook Heatmap")
        self.ax.set_ylabel("Price (USD)")
        self.ax.grid(True, alpha=0.3)
        self.fig.autofmt_xdate()
        self.canvas.draw_idle()

    # ------------------------------------------------------------------
    # 🛒 Execute Buy/Sell
    # ------------------------------------------------------------------
    def _execute_trade(self, side):
        try:
            amount = self.amount_entry.text().strip()
            price = self.price_entry.text().strip()
            if not amount or not price:
                QMessageBox.warning(self, "Input Error", "Enter amount and price.")
                return

            amount = str(amount)
            price = str(price)

            account = self.server.load_account(self.bot.keypair.public_key)
            tx_builder = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=100
                )
            )

            if side == "buy":
                tx_builder.append_manage_buy_offer_op(
                    selling=self.counter_asset,  # buy XLM using USDC
                    buying=self.base_asset,
                    amount=amount,
                    price=price,
                )
            else:
                tx_builder.append_manage_sell_offer_op(
                    selling=self.base_asset,  # sell XLM for USDC
                    buying=self.counter_asset,
                    amount=amount,
                    price=price,
                )

            tx = tx_builder.set_timeout(30).build()
            tx.sign(self.bot.keypair)
            resp = self.server.submit_transaction(tx)

            QMessageBox.information(self, "Success", f"✅ Trade submitted.\nHash: {resp.get('hash')}")
            self._refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Trade Error", str(e))

    # ------------------------------------------------------------------
    # 🔍 Zoom + Save
    # ------------------------------------------------------------------
    def _zoom_chart(self, factor):
        n = int(len(self.df) * factor)
        n = max(20, min(len(self.df), n))
        self.df = self.df.tail(n)
        self._plot_chart()

    def _save_chart(self):
        self.fig.savefig("stellar_dex_trading_chart.png", dpi=300)
        self.status_label.setText("💾 Chart saved.")

# ------------------------------------------------------------------
# 🖱 Scroll Zoom
# ------------------------------------------------------------------
    def _on_scroll(self, event):
     factor = 0.8 if event.button == "up" else 1.25
     self._zoom_chart(factor)
