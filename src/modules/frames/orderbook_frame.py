from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QTextEdit, QDialog, QFormLayout, QSizePolicy, QMessageBox
)
from stellar_sdk import Asset
import json


class OrderBookFrame(QFrame):
    """📊 Real-time order book viewer for selected Stellar markets."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.server = getattr(self.bot, "server", None)

        # Default pair: XLM/USDC
        self.selling_asset = Asset.native()
        self.buying_asset = Asset("USDC", "GDMTVHLWJTHSUDMZVVMXXH6VJHA2ZV3HNG5LYNAZ6RTWB7GISM6PGTUV")

        self.orderbook_data = {}
        self._init_ui()
        self._load_pairs()
        self._fetch_orderbook()
        self._start_auto_refresh()

    # ------------------------------------------------------------------
    # 🧱 UI SETUP
    # ------------------------------------------------------------------
    def _init_ui(self):
        self.setStyleSheet("""
            QFrame { background-color: #0D1117; color: #E0E0E0; }
            QHeaderView::section { background-color: #263238; color: white; font-weight: bold; }
            QTableWidget { gridline-color: #333; font-size: 13px; selection-background-color: #1976D2; }
            QLabel { color: #00E676; font-size: 16px; }
            QPushButton { background-color: #1E88E5; color: white; border-radius: 4px; padding: 5px; }
            QPushButton:hover { background-color: #42A5F5; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Title & pair selector
        title_layout = QHBoxLayout()
        self.title_label = QLabel("📊 Stellar Order Book Viewer")
        self.title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.title_label, alignment=Qt.AlignLeft)

        self.pair_selector = QComboBox()
        title_layout.addWidget(QLabel("Select Market:"))
        title_layout.addWidget(self.pair_selector)
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._fetch_orderbook)
        title_layout.addWidget(refresh_btn)
        layout.addLayout(title_layout)

        # Spread info
        self.spread_label = QLabel("Spread: --")
        layout.addWidget(self.spread_label)

        # Bids Table
        self.bids_table = QTableWidget(0, 3)
        self.bids_table.setHorizontalHeaderLabels(["Price", "Amount", "Total"])
        self.bids_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bids_table.setAlternatingRowColors(True)
        layout.addWidget(QLabel("🟢 Bids"))
        layout.addWidget(self.bids_table)

        # Asks Table
        self.asks_table = QTableWidget(0, 3)
        self.asks_table.setHorizontalHeaderLabels(["Price", "Amount", "Total"])
        self.asks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.asks_table.setAlternatingRowColors(True)
        layout.addWidget(QLabel("🔴 Asks"))
        layout.addWidget(self.asks_table)

        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    # ------------------------------------------------------------------
    # 📈 LOAD MARKET PAIRS
    # ------------------------------------------------------------------
    def _load_pairs(self):
        """Populate selector with assets from account + common pairs."""
        self.pair_selector.clear()
        self.pair_selector.addItem("XLM/USDC")
        self.pair_selector.addItem("XLM/EURT")
        self.pair_selector.addItem("XLM/BTC")
        self.pair_selector.addItem("USDC/USDT")
        self.pair_selector.currentIndexChanged.connect(self._on_pair_changed)

    def _on_pair_changed(self):
        """Update selected pair and fetch new orderbook."""
        text = self.pair_selector.currentText()
        try:
            base, quote = text.split("/")
            if base == "XLM":
                self.selling_asset = Asset.native()
            else:
                self.selling_asset = Asset(base, "GDMTVHLWJTHSUDMZVVMXXH6VJHA2ZV3HNG5LYNAZ6RTWB7GISM6PGTUV")

            self.buying_asset = (
                Asset.native() if quote == "XLM" else Asset(quote, "GDMTVHLWJTHSUDMZVVMXXH6VJHA2ZV3HNG5LYNAZ6RTWB7GISM6PGTUV")
            )
            self._fetch_orderbook()
        except Exception as e:
            self._set_status(f"Error selecting pair: {e}")

    # ------------------------------------------------------------------
    # 🧾 FETCH ORDERBOOK
    # ------------------------------------------------------------------
    def _fetch_orderbook(self):
        """Fetch orderbook from Horizon and update tables."""
        try:
            self._set_status("⏳ Fetching orderbook...")
            data = self.server.orderbook(selling=self.selling_asset, buying=self.buying_asset).limit(20).call()
            self.orderbook_data = data

            bids = data.get("bids", [])
            asks = data.get("asks", [])
            self._populate_table(self.bids_table, bids, is_bid=True)
            self._populate_table(self.asks_table, asks, is_bid=False)

            if bids and asks:
                best_bid = float(bids[0]["price"])
                best_ask = float(asks[0]["price"])
                spread = ((best_ask - best_bid) / best_bid) * 100
                self.spread_label.setText(f"Spread: {spread:.2f}% | Best Bid: {best_bid:.5f} | Best Ask: {best_ask:.5f}")
            else:
                self.spread_label.setText("Spread: --")

            self._set_status("✅ Orderbook updated.")
        except Exception as e:
            self._set_status(f"❌ Error fetching orderbook: {e}")

    # ------------------------------------------------------------------
    # 🪶 POPULATE TABLE
    # ------------------------------------------------------------------
    def _populate_table(self, table, entries, is_bid=False):
        table.setRowCount(len(entries))
        total_accum = 0
        for i, e in enumerate(entries):
            try:
                price = float(e["price"])
                amount = float(e["amount"])
                total_accum += amount
                table.setItem(i, 0, QTableWidgetItem(f"{price:.5f}"))
                table.setItem(i, 1, QTableWidgetItem(f"{amount:,.2f}"))
                table.setItem(i, 2, QTableWidgetItem(f"{total_accum:,.2f}"))

                # Color styling
                color = QColor("#4CAF50") if is_bid else QColor("#F44336")
                for c in range(3):
                    table.item(i, c).setForeground(QBrush(color))
            except Exception as err:
                print(f"[OrderBookFrame] Row error: {err}")

    # ------------------------------------------------------------------
    # 🔁 AUTO REFRESH
    # ------------------------------------------------------------------
    def _start_auto_refresh(self):
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._fetch_orderbook)
        self.refresh_timer.start(15000)  # refresh every 15 seconds

    # ------------------------------------------------------------------
    # 📜 DETAILS DIALOG
    # ------------------------------------------------------------------
    def _show_order_details(self, entry):
        """Display JSON details for a selected bid/ask."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Order Details")
        dialog.setMinimumSize(400, 300)

        layout = QFormLayout(dialog)
        layout.addRow("Price:", QLabel(str(entry.get("price", "N/A"))))
        layout.addRow("Amount:", QLabel(str(entry.get("amount", "N/A"))))

        json_box = QTextEdit(json.dumps(entry, indent=2))
        json_box.setReadOnly(True)
        layout.addRow(QLabel("<b>Raw JSON:</b>"))
        layout.addRow(json_box)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addRow(close_btn)
        dialog.exec()

    # ------------------------------------------------------------------
    # ℹ️ STATUS HELPER
    # ------------------------------------------------------------------
    def _set_status(self, text):
        self.status_label.setText(text)
