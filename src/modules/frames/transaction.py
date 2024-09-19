from PyQt5 import QtWidgets, QtGui, QtCore
import requests


class Transaction(QtWidgets.QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller  # Application controller object to access bot and other relevant data
        self.stellar_client = self.controller.bot  # Stellar client object to interact with the Stellar network
        self.setGeometry(0, 0, 1530, 780)
        self.setStyleSheet("background-color: #1e2a38; color: white;")

        # Create and arrange widgets in the frame
        self.create_widgets()

    def create_widgets(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Title Label
        self.title_label = QtWidgets.QLabel("Transaction Details", self)
        self.title_label.setStyleSheet("font-size: 18pt;")
        layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        # Source Account
        self.source_label = QtWidgets.QLabel("Source Account:", self)
        layout.addWidget(self.source_label)
        self.source_entry = QtWidgets.QLineEdit(self)
        self.source_entry.setText(self.controller.bot.account_id)
        self.source_entry.setReadOnly(True)
        layout.addWidget(self.source_entry)

        # Destination Account
        self.destination_label = QtWidgets.QLabel("Destination Account:", self)
        layout.addWidget(self.destination_label)
        self.destination_entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.destination_entry)

        # Asset Choice
        self.asset_choice = QtWidgets.QComboBox(self)
        self.asset_choice.addItems(['XLM', 'USD', 'BTC', 'ETH'])
        self.asset_choice.currentIndexChanged.connect(self.update_deposit_withdrawal_options)
        layout.addWidget(self.asset_choice)

        # Amount to Send
        self.amount_label = QtWidgets.QLabel("Amount:", self)
        layout.addWidget(self.amount_label)
        self.amount_entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.amount_entry)

        # Deposit and Withdrawal section
        self.deposit_withdrawal_label = QtWidgets.QLabel("Deposit/Withdrawal", self)
        self.deposit_withdrawal_label.setStyleSheet("font-size: 14pt;")
        layout.addWidget(self.deposit_withdrawal_label)

        # Deposit Button
        self.deposit_button = QtWidgets.QPushButton("Deposit", self)
        self.deposit_button.clicked.connect(self.deposit_asset)
        layout.addWidget(self.deposit_button)

        # Withdrawal Button
        self.withdrawal_button = QtWidgets.QPushButton("Withdraw", self)
        self.withdrawal_button.clicked.connect(self.withdraw_asset)
        layout.addWidget(self.withdrawal_button)

        # Status Message
        self.status_label = QtWidgets.QLabel("Status:", self)
        layout.addWidget(self.status_label)
        self.status_message = QtWidgets.QLabel(self)
        self.status_message.setStyleSheet("font-size: 12pt; color: green;")
        layout.addWidget(self.status_message)

        # Submit Transaction Button
        self.submit_button = QtWidgets.QPushButton("Submit Transaction", self)
        self.submit_button.clicked.connect(self.submit_transaction)
        layout.addWidget(self.submit_button)

        # Transaction History
        self.history_label = QtWidgets.QLabel("Transaction History", self)
        self.history_label.setStyleSheet("font-size: 14pt;")
        layout.addWidget(self.history_label)

        self.history_listbox = QtWidgets.QListWidget(self)
        layout.addWidget(self.history_listbox)

        self.setLayout(layout)

    def update_deposit_withdrawal_options(self):
        selected_asset = self.asset_choice.currentText()
        if selected_asset == "XLM":
            self.deposit_button.setEnabled(True)
        else:
            self.deposit_button.setEnabled(False)
        self.withdrawal_button.setEnabled(True)

    def deposit_asset(self):
        selected_asset = self.asset_choice.currentText()
        amount = self.amount_entry.text()

        if not amount:
            self.status_message.setText("Please enter an amount for deposit")
            self.status_message.setStyleSheet("color: red;")
            return

        # Example logic for handling deposits
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

        # Example logic for handling withdrawals
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
            # Create and submit the transaction via the Stellar client
            response = self.controller.bot.submit_transaction(source_account, destination_account, amount)
            self.status_message.setText("Transaction submitted successfully!")
            self.status_message.setStyleSheet("color: green;")
            self.fetch_transaction_history()  # Refresh transaction history after successful submission
        except Exception as e:
            self.status_message.setText(f"Error: {str(e)}")
            self.status_message.setStyleSheet("color: red;")

    def fetch_transaction_history(self):
        try:
            response = self.controller.bot.get_transactions()
            response.raise_for_status()

            # Get the transaction history from the response
            history = response.json()['_embedded']['records']
            self.history_listbox.clear()  # Clear the listbox before adding new data

            for tx in history:
                tx_details = f"Hash: {tx['hash']} | Date: {tx['created_at']} | Successful: {tx['successful']}"
                self.history_listbox.addItem(tx_details)
        except requests.exceptions.RequestException as e:
            self.history_listbox.addItem(f"Error fetching history: {str(e)}")
