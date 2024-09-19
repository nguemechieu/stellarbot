import re
from PyQt5 import QtWidgets, QtGui, QtCore
import pandas as pd


class Wallet(QtWidgets.QWidget):
    """Stellar wallet widget displaying balance, transactions, and payment options."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(0, 0, 1530, 780)
        self.setStyleSheet("background-color: #1e2a38; color: white;")

        # Layout for the wallet
        self.create_widgets()

        # Start auto-refresh for wallet data
        self.refresh_wallet_data()

    def create_widgets(self):
        """Create and arrange the widgets."""
        layout = QtWidgets.QVBoxLayout(self)

        # Title
        self.wallet_title = QtWidgets.QLabel("Stellar Wallet", self)
        self.wallet_title.setStyleSheet("font-size: 24pt; color: white;")
        layout.addWidget(self.wallet_title, alignment=QtCore.Qt.AlignLeft)

        # Balance Display
        self.balance_label = QtWidgets.QLabel("Balance:", self)
        self.balance_label.setStyleSheet("font-size: 16pt; color: white;")
        layout.addWidget(self.balance_label)

        self.balance_amount_label = QtWidgets.QLabel("Loading...", self)
        self.balance_amount_label.setStyleSheet("font-size: 16pt; color: orange;")
        layout.addWidget(self.balance_amount_label)

        # Transaction History Table
        self.transaction_table = QtWidgets.QTableWidget(self)
        self.transaction_table.setColumnCount(6)
        self.transaction_table.setHorizontalHeaderLabels(["ID", "Paging Token", "Hash", "Successful", "Created At", "Ledger"])
        self.transaction_table.setColumnWidth(0, 100)
        self.transaction_table.setColumnWidth(1, 100)
        self.transaction_table.setColumnWidth(2, 100)
        self.transaction_table.setColumnWidth(3, 100)
        self.transaction_table.setColumnWidth(4, 100)
        self.transaction_table.setColumnWidth(5, 100)
        layout.addWidget(self.transaction_table)

        # Transaction Details Section
        self.transaction_details_label = QtWidgets.QLabel("Transaction Metadata", self)
        self.transaction_details_label.setStyleSheet("font-size: 18pt; color: white;")
        layout.addWidget(self.transaction_details_label)

        # Transaction Metadata text area
        self.transaction_details_text = QtWidgets.QTextEdit(self)
        self.transaction_details_text.setFixedHeight(100)
        layout.addWidget(self.transaction_details_text)

        # Send Payment Section
        self.send_payment_label = QtWidgets.QLabel("Send Payment", self)
        self.send_payment_label.setStyleSheet("font-size: 18pt; color: white;")
        layout.addWidget(self.send_payment_label)

        # Recipient Account ID
        self.recipient_label = QtWidgets.QLabel("Recipient Account ID", self)
        layout.addWidget(self.recipient_label)
        self.recipient_entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.recipient_entry)

        # Amount Entry
        self.amount_label = QtWidgets.QLabel("Amount", self)
        layout.addWidget(self.amount_label)
        self.amount_entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.amount_entry)

        # Asset Entry
        self.asset_label = QtWidgets.QLabel("Asset (e.g., XLM)", self)
        layout.addWidget(self.asset_label)
        self.asset_entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.asset_entry)

        # Send Payment Button
        self.send_button = QtWidgets.QPushButton("Send Payment", self)
        self.send_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14pt;")
        self.send_button.clicked.connect(self.send_payment)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def refresh_wallet_data(self):
        """Refresh the wallet data like balance and transaction history."""
        # Get balance and update UI
        balance = pd.read_csv('ledger_accounts.csv')
        self.balance_amount_label.setText(f"${balance['balance'][0]}")  # Assuming balance is in the first row

        # Get transaction history and update table
        transactions = pd.read_csv('ledger_transactions.csv')
        self.transaction_table.setRowCount(0)  # Clear previous data

        for idx, transaction in transactions.iterrows():
            self._extracted_from_refresh_wallet_data_12(idx, transaction)

    # TODO Rename this here and in `refresh_wallet_data`
    def _extracted_from_refresh_wallet_data_12(self, idx, transaction):
        self.transaction_table.insertRow(idx)
        self.transaction_table.setItem(idx, 0, QtWidgets.QTableWidgetItem(str(transaction.get('id', 'N/A'))))
        self.transaction_table.setItem(idx, 1, QtWidgets.QTableWidgetItem(str(transaction.get('paging_token', 'N/A'))))
        self.transaction_table.setItem(idx, 2, QtWidgets.QTableWidgetItem(str(transaction.get('hash', 'N/A'))))
        self.transaction_table.setItem(idx, 3, QtWidgets.QTableWidgetItem(str(transaction.get('successful', 'N/A'))))
        self.transaction_table.setItem(idx, 4, QtWidgets.QTableWidgetItem(str(transaction.get('created_at', 'N/A'))))
        self.transaction_table.setItem(idx, 5, QtWidgets.QTableWidgetItem(str(transaction.get('ledger', 'N/A'))))

    def send_payment(self):
        """Send a payment to a recipient."""
        recipient_account_id = self.recipient_entry.text()

        #Verify that the recipient address is correct for the transaction
        if not self.verify_address(self.recipient_entry.text()):
            QtWidgets.QMessageBox.warning(self, "Invalid Address", "Please enter a valid Stellar address.")
            return



        amount = self.amount_entry.text()
        asset = self.asset_entry.text()

        if not recipient_account_id or not amount or not asset:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        if not self.controller.bot.trading_engine.send_payment(recipient_account_id, amount, asset):
            QtWidgets.QMessageBox.critical(self, "Payment Error", "Failed to send payment.")
            return

        QtWidgets.QMessageBox.information(self, "Payment Sent", "Payment sent successfully.")
    
    def verify_address(self, address):
        """Check if the given address is a valid Stellar address."""
        #Check if the address matches the stell address regex pattern


        # For simplicity, let's assume this is a valid regex pattern
        return re.match(r'G[A-Fa-f0-9]{55}', address)