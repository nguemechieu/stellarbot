import traceback
from typing import Optional, List, Dict
import requests
import pandas as pd
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QSizePolicy
)


# ⚙️ Background Worker
class Worker(QtCore.QRunnable):
    """Executes long-running tasks safely in background threads."""
    def __init__(self, fn, callback=None, error_callback=None):
        super().__init__()
        self.fn = fn
        self.callback = callback
        self.error_callback = error_callback

    def run(self):
        try:
            result = self.fn()
            if self.callback:
                QtCore.QMetaObject.invokeMethod(
                    self.callback.__self__,
                    self.callback.__name__,
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(object, result)
                )
        except Exception as e:
            msg = f"{e}\n{traceback.format_exc()}"
            if self.error_callback:
                QtCore.QMetaObject.invokeMethod(
                    self.error_callback.__self__,
                    self.error_callback.__name__,
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, msg)
                )


# 🧾 Account Overview
class AccountOverview(QFrame):
    """Displays Stellar account balance, assets, and recent transactions."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.logger = getattr(controller, "logger", None)

        self.session = requests.Session()
        self.thread_pool = QtCore.QThreadPool.globalInstance()

        self._init_ui()

        # Refresh every 30s
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self._load_account_data_async)
        self.refresh_timer.start(30000)
        self._load_account_data_async()

    # ------------------------------------------------------------------
    # UI SETUP
    # ------------------------------------------------------------------
    def _init_ui(self):
        self.setStyleSheet("background-color: #0A0A0A; color: #00FF7F;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.account_id_label = QLabel("Account ID: Loading...")
        self.account_id_label.setStyleSheet("font-weight:bold; font-size:16px; color:#00FF7F;")
        layout.addWidget(self.account_id_label)

        self.balance_label = QLabel("Total Balance: Loading...")
        self.balance_label.setStyleSheet("font-size:14px; margin-bottom:10px; color:#99FF99;")
        layout.addWidget(self.balance_label)

        # 🪙 Assets Table
        self.assets_table = QTableWidget(0, 4)
        self.assets_table.setHorizontalHeaderLabels(["Asset", "Balance", "Issuer", "Type"])
        self.assets_table.horizontalHeader().setStretchLastSection(True)
        self.assets_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.assets_table)

        # 💳 Transactions Table
        self.transactions_table = QTableWidget(0, 3)
        self.transactions_table.setHorizontalHeaderLabels(["Date", "Amount", "Status"])
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        self.transactions_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.transactions_table)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    # ASYNC DATA LOADING
    # ------------------------------------------------------------------
    def _load_account_data_async(self):
        if not self.bot:
            self._on_error("Bot not initialized yet.")
            return
        self._set_loading_state(True)
        worker = Worker(self._fetch_account_data, self._on_account_data_loaded, self._on_error)
        self.thread_pool.start(worker)

    def _fetch_account_data(self) -> dict:
        """Safely extract data from SmartBot's cached DataFrames."""
        try:
            df_acc = getattr(self.bot, "accounts_df", pd.DataFrame())
            df_tx = getattr(self.bot, "transactions_df", pd.DataFrame())

            # ✅ Account ID
            account_id = self.bot.account_id if hasattr(self.bot, "account_id") else "Unknown"

            # ✅ Balances extraction
            balances_data = []
            if not df_acc.empty:
                data = df_acc.iloc[0].to_dict()
                balances = data.get("balances", [])
                for b in balances:
                    balances_data.append({
                        "asset_code": b.get("asset_code", "XLM" if b.get("asset_type") == "native" else b.get("asset_code")),
                        "balance": float(b.get("balance", 0.0)),
                        "asset_issuer": b.get("asset_issuer", "Native"),
                        "asset_type": b.get("asset_type", "native"),
                    })

            total_xlm = sum(b["balance"] for b in balances_data if b["asset_type"] == "native")
            usd_value = self._convert_xlm_to_usd(total_xlm)

            # ✅ Transactions extraction
            transactions = []
            if not df_tx.empty:
                for _, tx in df_tx.head(10).iterrows():
                    transactions.append({
                        "date": str(tx.get("created_at", ""))[:19],
                        "amount": float(tx.get("fee_charged", 0.0)) / 1e7,  # convert stroops
                        "type": "✅ Success" if tx.get("successful") else "❌ Failed"
                    })

            return {
                "account_id": account_id,
                "balance": total_xlm,
                "usd_value": usd_value,
                "balances": balances_data,
                "transactions": transactions,
            }

        except Exception as e:
            raise RuntimeError(f"Error reading account data: {e}")

    # ------------------------------------------------------------------
    # UI UPDATE CALLBACKS
    # ------------------------------------------------------------------
    def _on_account_data_loaded(self, data: dict):
        self._set_loading_state(False)
        try:
            self.account_id_label.setText(f"Account ID: {data.get('account_id', 'Unknown')}")
            self.balance_label.setText(
                f"Total Balance: {data['balance']:.2f} XLM (~${data['usd_value']:.2f} USD)"
            )

            # --- Populate assets
            balances = data.get("balances", [])
            self.assets_table.setRowCount(len(balances))
            for i, a in enumerate(balances):
                self.assets_table.setItem(i, 0, QTableWidgetItem(a["asset_code"]))
                self.assets_table.setItem(i, 1, QTableWidgetItem(str(a["balance"])))
                self.assets_table.setItem(i, 2, QTableWidgetItem(a["asset_issuer"]))
                self.assets_table.setItem(i, 3, QTableWidgetItem(a["asset_type"]))

            # --- Populate transactions
            txs = data.get("transactions", [])
            self.transactions_table.setRowCount(len(txs))
            for i, tx in enumerate(txs):
                self.transactions_table.setItem(i, 0, QTableWidgetItem(tx["date"]))
                self.transactions_table.setItem(i, 1, QTableWidgetItem(f"{tx['amount']:.4f} XLM"))
                self.transactions_table.setItem(i, 2, QTableWidgetItem(tx["type"]))

                color = QColor("#4CAF50") if "✅" in tx["type"] else QColor("#F44336")
                self.transactions_table.item(i, 2).setForeground(color)

        except Exception as e:
            self._on_error(str(e))

    def _on_error(self, msg: str):
        self._set_loading_state(False)
        if self.logger:
            self.logger.error(msg)
        QMessageBox.critical(self, "Error", f"Failed to load account data:\n{msg}")

    def _set_loading_state(self, loading: bool):
        text = "Loading..." if loading else ""
        self.account_id_label.setText(f"Account ID: {text}")
        self.balance_label.setText(f"Total Balance: {text}")

    # ------------------------------------------------------------------
    # 💰 Conversion
    # ------------------------------------------------------------------
    def _convert_xlm_to_usd(self, xlm_balance: float) -> float:
        """Convert XLM balance to USD using Binance API."""
        try:
            r = self.session.get("https://api.binance.us/api/v3/ticker/price?symbol=XLMUSDT", timeout=5)
            r.raise_for_status()
            price = float(r.json().get("price", 0))
            return xlm_balance * price
        except Exception as e:
            if self.logger:
                self.logger.warning(f"USD conversion failed: {e}")
            return 0.0
