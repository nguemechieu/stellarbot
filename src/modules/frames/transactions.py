import threading
import pandas as pd
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QVBoxLayout, QComboBox,
    QFrame, QMessageBox, QListWidget
)
from stellar_sdk import Asset, TransactionBuilder, Network, exceptions as stellar_exceptions


class Transactions(QFrame):
    """💱 Handles sending, depositing, and viewing Stellar transactions."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.keypair = getattr(self.bot, "keypair", None)

        self.init_ui()
        self.load_assets()

        # Auto-refresh every 60s
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self.fetch_transaction_history)
        self.refresh_timer.start(60000)
        self.fetch_transaction_history()

    # ------------------------------------------------------------------
    # 🧱 UI Setup
    # ------------------------------------------------------------------
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("💱 Stellar Transactions")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00FF99;")
        layout.addWidget(title, alignment=QtCore.Qt.AlignCenter)

        # Source Account
        layout.addWidget(QLabel("Source Account:"))
        self.source_entry = QLineEdit(getattr(self.controller, "account_id", ""))
        self.source_entry.setReadOnly(True)
        layout.addWidget(self.source_entry)

        # Destination
        layout.addWidget(QLabel("Destination Account:"))
        self.destination_entry = QLineEdit()
        self.destination_entry.setPlaceholderText("Enter recipient Stellar address (G...)")
        layout.addWidget(self.destination_entry)

        # Asset Selector
        layout.addWidget(QLabel("Select Asset:"))
        self.asset_choice = QComboBox()
        layout.addWidget(self.asset_choice)

        # Amount
        layout.addWidget(QLabel("Amount:"))
        self.amount_entry = QLineEdit()
        self.amount_entry.setPlaceholderText("e.g. 50.25")
        layout.addWidget(self.amount_entry)

        # Action Buttons
        self.deposit_button = QPushButton("💰 Deposit (Simulated)")
        self.deposit_button.clicked.connect(self.deposit_asset)

        self.withdraw_button = QPushButton("🏦 Withdraw (Simulated)")
        self.withdraw_button.clicked.connect(self.withdraw_asset)

        self.submit_button = QPushButton("🚀 Submit Transaction")
        self.submit_button.clicked.connect(self.submit_transaction)

        layout.addWidget(self.deposit_button)
        layout.addWidget(self.withdraw_button)
        layout.addWidget(self.submit_button)

        # Status and History
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #CCCCCC;")
        layout.addWidget(self.status_label)

        layout.addWidget(QLabel("Recent Transactions:"))
        self.history_listbox = QListWidget()
        layout.addWidget(self.history_listbox)

        self.setLayout(layout)
        self.setStyleSheet("""
            QFrame { background-color: #0D1117; color: #E0E0E0; }
            QPushButton { background-color: #1E88E5; color: white; border-radius: 6px; padding: 6px; }
            QPushButton:hover { background-color: #42A5F5; }
            QLabel { font-size: 14px; color: #E0E0E0; }
        """)

    # ------------------------------------------------------------------
    # 🪙 Asset Loading
    # ------------------------------------------------------------------
    def load_assets(self):
        """Load account assets into dropdown from bot cache."""
        try:
            if not self.bot or not hasattr(self.bot, "accounts_df"):
                return self._show_error("Bot or account data not initialized.")

            df = getattr(self.bot, "accounts_df", None)
            balances = []
            if df is not None and "balances" in df.columns:
                balances = df.iloc[0].get("balances", [])

            self.asset_choice.clear()
            for asset in balances:
                code = asset.get("asset_code", "XLM" if asset.get("asset_type") == "native" else asset.get("asset_code"))
                self.asset_choice.addItem(code)

            self._show_success("✅ Assets loaded successfully.")
        except Exception as e:
            self._show_error(f"Error loading assets: {e}")

    # ------------------------------------------------------------------
    # 💰 Simulated Actions
    # ------------------------------------------------------------------
    def deposit_asset(self):
        amount = self.amount_entry.text().strip()
        asset = self.asset_choice.currentText()
        if not amount:
            return self._show_error("Please enter an amount.")
        self._show_info(f"💰 Simulated deposit of {amount} {asset} complete.")

    def withdraw_asset(self):
        amount = self.amount_entry.text().strip()
        asset = self.asset_choice.currentText()
        if not amount:
            return self._show_error("Please enter an amount.")
        self._show_info(f"🏦 Simulated withdrawal of {amount} {asset} complete.")

    # ------------------------------------------------------------------
    # 🔗 Submit Transaction
    # ------------------------------------------------------------------
    def submit_transaction(self):
        """Start threaded payment submission."""
        dest = self.destination_entry.text().strip()
        amount = self.amount_entry.text().strip()
        asset_code = self.asset_choice.currentText().strip()

        if not dest.startswith("G"):
            return self._show_error("Invalid destination address (must start with G...).")
        if not amount or float(amount) <= 0:
            return self._show_error("Amount must be greater than zero.")

        self._show_info(f"🚀 Sending {amount} {asset_code} to {dest}...")

        thread = threading.Thread(target=self._send_payment_thread, args=(dest, amount, asset_code), daemon=True)
        thread.start()

    def _send_payment_thread(self, dest, amount, asset_code):
        """Execute Stellar payment operation in background."""
        try:
            if not self.bot or not self.keypair:
                raise ValueError("Bot or keypair not initialized.")

            account = self.bot.server.load_account(self.keypair.public_key)
            asset = Asset.native() if asset_code == "XLM" else Asset(asset_code, self.keypair.public_key)

            tx = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=100
                )
                .append_payment_op(destination=dest, asset=asset, amount=str(amount))
                .set_timeout(30)
                .build()
            )
            tx.sign(self.keypair)
            resp = self.bot.server.submit_transaction(tx)
            tx_hash = resp.get("hash", "unknown")

            QtCore.QMetaObject.invokeMethod(
                self, "_show_success", QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"✅ Transaction successful! Hash: {tx_hash}")
            )
            self.fetch_transaction_history()

        except stellar_exceptions.BaseHorizonError as e:
            QtCore.QMetaObject.invokeMethod(
                self, "_show_error", QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"❌ Horizon Error: {e}")
            )
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(
                self, "_show_error", QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"❌ Transaction failed: {e}")
            )

    # ------------------------------------------------------------------
    # 🧾 Transaction History
    # ------------------------------------------------------------------
    def fetch_transaction_history(self):
        """Fetch and display transactions from SmartBot cache."""
        try:
            df = getattr(self.bot, "transactions_df", None)
            if df is None or df.empty:
                self.history_listbox.clear()
                self.history_listbox.addItem("No recent transactions found.")
                return

            records = df.iloc[0].get("_embedded", {}).get("records", []) if "_embedded" in df.columns else []
            if not records:
                self.history_listbox.clear()
                self.history_listbox.addItem("No recent transactions found.")
                return

            self.history_listbox.clear()
            for tx in records[:20]:
                created_at = tx.get("created_at", "")[:19]
                success = "✅ SUCCESS" if tx.get("successful") else "❌ FAILED"
                tx_hash = tx.get("hash", "")[:10]
                self.history_listbox.addItem(f"{created_at} | {success} | {tx_hash}...")

            self._show_info("📜 Transaction history updated.")
        except Exception as e:
            self._show_error(f"Error loading history: {e}")

    # ------------------------------------------------------------------
    # 🔔 Status Utilities
    # ------------------------------------------------------------------
    @QtCore.Slot(str)
    def _show_info(self, text):
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: #00B0FF;")

    @QtCore.Slot(str)
    def _show_success(self, text):
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: #00E676;")

    @QtCore.Slot(str)
    def _show_error(self, text):
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: red;")
        QMessageBox.critical(self, "Error", text)
