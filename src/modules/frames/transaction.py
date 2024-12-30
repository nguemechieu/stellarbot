import requests
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit, QVBoxLayout, QComboBox, QFrame


class Transaction(QFrame):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.source_entry = None
        self.title_label = None
        self.source_label = None
        self.controller = controller  # Application controller to access bot and other relevant data
        self.stellar_client = self.controller.bot  # Stellar client to interact with the Stellar network

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title Label
        self.title_label = QLabel("Transaction Details", self)
        self.title_label.setStyleSheet("font-size: 18pt;")
        layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Source Account
        self.source_label = QLabel("Source Account:", self)
        layout.addWidget(self.source_label)
        self.source_entry = QLineEdit(self)
        self.source_entry.setText(self.controller.account_id)
        self.source_entry.setReadOnly(True)
        layout.addWidget(self.source_entry)

        # Destination Account
        self.destination_label = QLabel("Destination Account:", self)
        layout.addWidget(self.destination_label)
        self.destination_entry = QLineEdit(self)
        layout.addWidget(self.destination_entry)

        # Asset Choice
        self.asset_choice = QComboBox(self)
        self.asset_choice.addItems(['XLM', 'USD', 'BTC', 'ETH'])
        self.asset_choice.currentIndexChanged.connect(self.update_deposit_withdrawal_options)
        layout.addWidget(self.asset_choice)

        # Amount to Send
        self.amount_label = QLabel("Amount:", self)
        layout.addWidget(self.amount_label)
        self.amount_entry = QLineEdit(self)
        layout.addWidget(self.amount_entry)

        # Deposit and Withdrawal Section
        self.deposit_withdrawal_label = QLabel("Deposit/Withdrawal", self)
        self.deposit_withdrawal_label.setStyleSheet("font-size: 14pt;")
        layout.addWidget(self.deposit_withdrawal_label)

        self.deposit_button = QPushButton("Deposit", self)
        self.deposit_button.clicked.connect(self.deposit_asset)
        layout.addWidget(self.deposit_button)

        self.withdrawal_button = QPushButton("Withdraw", self)
        self.withdrawal_button.clicked.connect(self.withdraw_asset)
        layout.addWidget(self.withdrawal_button)

        # Status Message
        self.status_label = QLabel("Status:", self)
        layout.addWidget(self.status_label)
        self.status_message = QLabel(self)
        self.status_message.setStyleSheet("font-size: 12pt; color: green;")
        layout.addWidget(self.status_message)

        # Submit Transaction Button
        self.submit_button = QPushButton("Submit Transaction", self)
        self.submit_button.clicked.connect(self.submit_transaction)
        layout.addWidget(self.submit_button)

        # Transaction History
        self.history_label = QLabel("Transaction History", self)
        self.history_label.setStyleSheet("font-size: 14pt;")
        layout.addWidget(self.history_label)

        self.history_listbox = QtWidgets.QListWidget(self)
        layout.addWidget(self.history_listbox)

        self.setLayout(layout)

    def update_deposit_withdrawal_options(self):
        selected_asset = self.asset_choice.currentText()
        self.deposit_button.setEnabled(selected_asset == "XLM")
        self.withdrawal_button.setEnabled(True)

    def deposit_asset(self):
        selected_asset = self.asset_choice.currentText()
        amount = self.amount_entry.text()

        if not amount:
            self.status_message.setText("Please enter an amount for deposit")
            self.status_message.setStyleSheet("color: red;")
            return

        self.status_message.setText(f"Depositing {amount} {selected_asset}...")
        self.status_message.setStyleSheet("color: green;")
        # Implement actual deposit logic here
        self.status_message.setText(f"{amount} {selected_asset} deposited successfully")

    def withdraw_asset(self):
        selected_asset = self.asset_choice.currentText()
        amount = self.amount_entry.text()

        if not amount:
            self.status_message.setText("Please enter an amount for withdrawal")
            self.status_message.setStyleSheet("color: red;")
            return

        self.status_message.setText(f"Withdrawing {amount} {selected_asset}...")
        self.status_message.setStyleSheet("color: green;")
        # Implement actual withdrawal logic here
        self.status_message.setText(f"{amount} {selected_asset} withdrawn successfully")

    def submit_transaction(self):
        source_account = self.controller.bot.account
        destination_account = self.destination_entry.text()

        if not destination_account:
            self.status_message.setText("Please enter a destination account")
            self.status_message.setStyleSheet("color: red;")
            return

        amount = self.amount_entry.text()

        if not amount:
            self.status_message.setText("Please enter an amount")
            self.status_message.setStyleSheet("color: red;")
            return

        try:
            self.controller.bot.submit_transaction(source_account, destination_account, amount)
            self.status_message.setText("Transaction submitted successfully!")
            self.status_message.setStyleSheet("color: green;")
            self.fetch_transaction_history()
        except Exception as e:
            self.status_message.setText(f"Error: {str(e)}")
            self.status_message.setStyleSheet("color: red;")

    def fetch_transaction_history(self):
        try:
            response = self.controller.bot.get_transactions()
            response.raise_for_status()

            history = response.json()['_embedded']['records']
            self.history_listbox.clear()
            for tx in history:
                tx_details = f"Hash: {tx['hash']} | Date: {tx['created_at']} | Successful: {tx['successful']}"
                self.history_listbox.addItem(tx_details)
        except requests.exceptions.RequestException as e:
            self.history_listbox.addItem(f"Error fetching history: {str(e)}")
