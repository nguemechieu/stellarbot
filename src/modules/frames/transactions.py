import threading
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QVBoxLayout, QComboBox, QFrame, QMessageBox
)
from stellar_sdk import Asset, TransactionBuilder, Network, exceptions as stellar_exceptions


class Transactions(QFrame):
    """Handles sending, depositing, and viewing Stellar transactions."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = controller.bot
        self.server = self.bot.server
        self.keypair = self.bot.keypair

        self.init_ui()
        self.load_assets()
        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self.fetch_transaction_history)
        self.refresh_timer.start(60000)  # auto-refresh every 60s
        self.fetch_transaction_history()

    # ------------------------------------------------------------------
    # UI SETUP
    # ------------------------------------------------------------------
    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("💱 Stellar Transactions", self)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff99;")
        layout.addWidget(title, alignment=QtCore.Qt.AlignCenter)

        # Source account
        layout.addWidget(QLabel("Source Account:"))
        self.source_entry = QLineEdit(self.controller.account_id)
        self.source_entry.setReadOnly(True)
        layout.addWidget(self.source_entry)

        # Destination
        layout.addWidget(QLabel("Destination Account:"))
        self.destination_entry = QLineEdit()
        self.destination_entry.setPlaceholderText("Enter recipient Stellar address (G...)")
        layout.addWidget(self.destination_entry)

        # Asset
        layout.addWidget(QLabel("Select Asset:"))
        self.asset_choice = QComboBox()
        layout.addWidget(self.asset_choice)

        # Amount
        layout.addWidget(QLabel("Amount:"))
        self.amount_entry = QLineEdit()
        self.amount_entry.setPlaceholderText("e.g. 50.25")
        layout.addWidget(self.amount_entry)

        # Actions
        self.deposit_button = QPushButton("Deposit (Simulated)")
        self.deposit_button.clicked.connect(self.deposit_asset)
        self.withdraw_button = QPushButton("Withdraw (Simulated)")
        self.withdraw_button.clicked.connect(self.withdraw_asset)
        layout.addWidget(self.deposit_button)
        layout.addWidget(self.withdraw_button)

        self.submit_button = QPushButton("Submit Transaction")
        self.submit_button.clicked.connect(self.submit_transaction)
        layout.addWidget(self.submit_button)

        # Status + history
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #cccccc;")
        layout.addWidget(self.status_label)

        layout.addWidget(QLabel("Recent Transactions:"))
        self.history_listbox = QtWidgets.QListWidget()
        layout.addWidget(self.history_listbox)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    # LOAD ASSETS
    # ------------------------------------------------------------------
    def load_assets(self):
        """Load account assets into dropdown."""
        try:
            balances = self.bot._on_account_balances()
            self.asset_choice.clear()
            for _, row in balances.iterrows():
                code = "XLM" if row["asset_type"] == "native" else row["asset_code"]
                self.asset_choice.addItem(code)
            self._show_success("Assets loaded successfully.")
        except Exception as e:
            self._show_error(f"Error loading assets: {e}")

    # ------------------------------------------------------------------
    # SIMULATED ACTIONS
    # ------------------------------------------------------------------
    def deposit_asset(self):
        asset = self.asset_choice.currentText()
        amount = self.amount_entry.text().strip()
        if not amount:
            return self._show_error("Please enter an amount.")
        self._show_info(f"💰 Depositing {amount} {asset} (simulation).")

    def withdraw_asset(self):
        asset = self.asset_choice.currentText()
        amount = self.amount_entry.text().strip()
        if not amount:
            return self._show_error("Please enter an amount.")
        self._show_info(f"🏦 Withdrawing {amount} {asset} (simulation).")

    # ------------------------------------------------------------------
    # TRANSACTION EXECUTION
    # ------------------------------------------------------------------
    def submit_transaction(self):
        """Start threaded payment submission."""
        dest = self.destination_entry.text().strip()
        amount = self.amount_entry.text().strip()
        asset_code = self.asset_choice.currentText().strip()

        if not dest.startswith("G"):
            return self._show_error("Invalid destination: must start with G...")
        if not amount or float(amount) <= 0:
            return self._show_error("Amount must be greater than zero.")

        self._show_info(f"🚀 Sending {amount} {asset_code} to {dest}...")
        threading.Thread(
            target=self._send_payment_thread, args=(dest, amount, asset_code), daemon=True
        ).start()

    def _send_payment_thread(self, dest: str, amount: str, asset_code: str):
        """Execute Stellar payment operation."""
        try:
            account = self.server.load_account(self.keypair.public_key)
            asset = Asset.native() if asset_code == "XLM" else Asset(asset_code, self.controller.account_id)

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
            resp = self.server.submit_transaction(tx)
            tx_hash = resp.get("hash", "unknown")

            QtCore.QMetaObject.invokeMethod(
                self, "_show_success",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"✅ Transaction successful! Hash: {tx_hash}")
            )

            self.fetch_transaction_history()

        except stellar_exceptions.BaseHorizonError as e:
            QtCore.QMetaObject.invokeMethod(
                self, "_show_error",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"❌ Horizon error: {e}")
            )
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(
                self, "_show_error",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"❌ Failed to send transaction: {e}")
            )

    # ------------------------------------------------------------------
    # TRANSACTION HISTORY
    # ------------------------------------------------------------------
    def fetch_transaction_history(self):
        """Refresh the transaction history from SmartBot’s cache."""
        try:
            df = self.bot.transaction_df
            self.history_listbox.clear()
            if df.empty:
                self.history_listbox.addItem("No recent transactions found.")
                return

            for _, tx in df.iterrows():
                txt = f"{tx.get('created_at', '')[:19]} | {'SUCCESS' if tx.get('successful') else 'FAILED'} | Hash: {tx.get('hash', '')[:10]}..."
                self.history_listbox.addItem(txt)

            self._show_info("📜 Transaction history updated.")
        except Exception as e:
            self._show_error(f"Error loading history: {e}")

    # ------------------------------------------------------------------
    # STATUS UTILITIES
    # ------------------------------------------------------------------
    @QtCore.Slot(str)
    def _show_info(self, text: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: #00ccff;")

    @QtCore.Slot(str)
    def _show_success(self, text: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: #00ff66;")

    @QtCore.Slot(str)
    def _show_error(self, text: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: red;")
        QtWidgets.QMessageBox.critical(self, "Error", text)
