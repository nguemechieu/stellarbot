import time
import traceback
from typing import Optional, List, Dict

import requests
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QSizePolicy
)


# ⚙️ Background Worker for non-blocking tasks
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
                    self.callback.__self__, self.callback.__name__,
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(object, result)
                )
        except Exception as e:
            if self.error_callback:
                QtCore.QMetaObject.invokeMethod(
                    self.error_callback.__self__, self.error_callback.__name__,
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, f"{e}\n{traceback.format_exc()}")
                )


# 🧾 Account Overview UI
class AccountOverview(QFrame):
    """Displays Stellar account balance, assets, and recent transactions."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.logger = getattr(controller, "logger", None)
        self.server_msg = getattr(controller, "server_msg", {})
        self.bot = getattr(controller, "bot", None)

        self.session = requests.Session()
        self.thread_pool = QtCore.QThreadPool.globalInstance()



        self._init_ui()

        self._load_account_data_async()

        # Periodically refresh balances
        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self._load_account_data_async)
        self.refresh_timer.start(30_000)  # every 30s

    # ------------------------------------------------------------------
    # 🧱 UI Initialization
    # ------------------------------------------------------------------
    def _init_ui(self):
        """Builds UI layout."""
        self.setGeometry(0, 0, 1530, 780)
        self.setWindowTitle("Stellar Account Overview")
        self.setStyleSheet("background-color: #0A0A0A; color: #00FF7F;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        self.account_id_label = QLabel("Account ID: Loading...")
        self.account_id_label.setStyleSheet("font-weight:bold; font-size:16px; color:#00FF7F;")
        layout.addWidget(self.account_id_label)

        self.balance_label = QLabel("Total Balance: Loading...")
        self.balance_label.setStyleSheet("font-size:14px; margin-bottom:10px; color:#99FF99;")
        layout.addWidget(self.balance_label)

        # Assets Table
        self.assets_table = QTableWidget(0, 3)
        self.assets_table.setHorizontalHeaderLabels(["Asset", "Balance", "Issuer"])
        self.assets_table.horizontalHeader().setStretchLastSection(True)
        self.assets_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.assets_table)

        # Transactions Table
        self.transactions_table = QTableWidget(0, 3)
        self.transactions_table.setHorizontalHeaderLabels(["Date", "Amount", "Type"])
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        self.transactions_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.transactions_table)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    # ⚡ Async Data Loading
    # ------------------------------------------------------------------
    def _load_account_data_async(self):
        """Run account data loading asynchronously."""
        self._set_loading_state(True)
        worker = Worker(self._fetch_account_data, self._on_account_data_loaded, self._on_error)
        self.thread_pool.start(worker)

    def _fetch_account_data(self) -> dict:
        """Simulate fetching data (replace with real Stellar API/bot logic)."""
        if not self.bot or not hasattr(self.bot, "account_info"):
            raise ValueError("Bot not initialized or missing account_info.")

        # Get local data (should be fast)
        account_data = self.bot.account_balances_df
        balances = account_data.get("balances", [])
        usd_value = self._convert_xlm_to_usd(balances)
        account_data["usd_value"] = usd_value
        return account_data

    def _on_account_data_loaded(self, account_data: dict):
        """Safely update UI from thread result."""
        self._set_loading_state(False)

        try:
            account_id = account_data.get("account_id", "Unknown")
            balance = account_data.get("balance", 0.0)
            usd_value = account_data.get("usd_value", 0.0)

            self.account_id_label.setText(f"Account ID: {account_id}")
            self.balance_label.setText(f"Total Balance: {balance:.2f} XLM (~${usd_value:.2f} USD)")

            # Assets
            assets = account_data.get("balances", [])
            self.assets_table.setRowCount(len(assets))
            for row, a in enumerate(assets):
                self.assets_table.setItem(row, 0, QTableWidgetItem(a.get("asset_code", "XLM")))
                self.assets_table.setItem(row, 1, QTableWidgetItem(str(a.get("balance", "0"))))
                self.assets_table.setItem(row, 2, QTableWidgetItem(a.get("asset_issuer", "Native")))

            # Transactions
            transactions = account_data.get("transactions", [])
            self.transactions_table.setRowCount(len(transactions))
            for row, tx in enumerate(transactions):
                self.transactions_table.setItem(row, 0, QTableWidgetItem(tx.get("date", "—")))
                self.transactions_table.setItem(row, 1, QTableWidgetItem(f"{tx.get('amount', 0)} XLM"))
                self.transactions_table.setItem(row, 2, QTableWidgetItem(tx.get("type", "—")))

                amount = tx.get("amount", 0)
                color = QColor("#4CAF50") if amount >= 0 else QColor("#F44336")
                self.transactions_table.item(row, 1).setForeground(color)

        except Exception as e:
            self._on_error(str(e))

    def _on_error(self, message: str):
        """Handle errors gracefully."""
        self._set_loading_state(False)
        self.server_msg["error"] = message
        if self.logger:
            self.logger.error(message)
        QMessageBox.critical(self, "Error", f"Failed to load account data:\n{message}")

    def _set_loading_state(self, loading: bool):
        """Visual feedback while loading."""
        text = "Loading..." if loading else ""
        self.balance_label.setText(f"Total Balance: {text}")
        self.account_id_label.setText(f"Account ID: {text}")

    # ------------------------------------------------------------------
    # 💰 Price Conversion
    # ------------------------------------------------------------------
    def _convert_xlm_to_usd(self, balances: List[Dict]) -> float:
        """Fetch real-time XLM/USD rate (Binance)."""
        try:
            response = self.session.get("https://api.binance.us/api/v3/ticker/price?symbol=XLMUSDT", timeout=5)
            response.raise_for_status()
            data = response.json()
            usd_price = float(data.get("price", 0.0))
            xlm_balance = next((float(b.get("balance", 0)) for b in balances if b.get("asset") == "XLM"), 0.0)
            usd_value = usd_price * xlm_balance
            if self.logger:
                self.logger.info(f"1 XLM = {usd_price:.4f} USD → Total = ${usd_value:.2f}")
            return usd_value
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Price conversion failed: {e}")
            return 0.0
