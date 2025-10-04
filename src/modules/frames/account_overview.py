import time

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from requests import Session


class AccountOverview(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Stellar Account Overview widget."""
        super().__init__(parent)
        self.server_msg =  controller.server_msg
        self.logger = controller.logger
 
        self.session = Session()
        self.controller = controller


        self.setGeometry(0, 0, 1530, 780)
        self.setWindowTitle("Stellar Account Overview")
        self.setStyleSheet("background-color: black; color: green;")

        # Main layout for the widget
        layout = QVBoxLayout(parent)
        self.setLayout(layout)

        # Account Header
        self.account_id_label = QLabel("Account ID: Loading...")
        self.account_id_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(self.account_id_label)

        # Account Balance Section
        self.balance_label = QLabel("Total Balance: Loading...")
        self.balance_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(self.balance_label)

        # Asset Holdings Table
        self.assets_table = QTableWidget()
        self.assets_table.setColumnCount(3)
        self.assets_table.setHorizontalHeaderLabels(["Asset", "Balance", "Issuer"])
        self.assets_table.setStyleSheet("""
            QTableWidget { background-color: #F8F8F8; border: 1px solid #CCCCCC; }
            QHeaderView::section { background-color: #D9D9D9; font-weight: bold; }
        """)
        self.assets_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.assets_table)

        # Recent Transactions Section
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(3)
        self.transactions_table.setHorizontalHeaderLabels(["Date", "Amount", "Type"])
        self.transactions_table.setStyleSheet("""
            QTableWidget { background-color: #F8F8F8; border: 1px solid #CCCCCC; }
            QHeaderView::section { background-color: #D9D9D9; font-weight: bold; }
        """)
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.transactions_table)

        # Load account details
        self.load_account_details()

    def load_account_details(self):
        """Load and display account details."""
        try:
            # Mock account data (replace with actual data from the controller)
            account_data =self.controller.bot.account_info  # Fetch account details from the bot

            # Update account details
            self.account_id_label.setText(f"Account ID: {account_data['account_id']}")
            self.balance_label.setText(f"Total Balance: {account_data['balance']} XLM  Value: "+
            f"{0.0} USD")

            # Update assets table
            self.assets_table.setRowCount(len(self.controller.bot.assets))
            for row_idx, asset in enumerate(account_data):
                self.assets_table.setItem(row_idx, 0, QTableWidgetItem(asset["asset_code"]))
                self.assets_table.setItem(row_idx, 1, QTableWidgetItem(f"{asset['balance']}"))
                self.assets_table.setItem(row_idx, 2, QTableWidgetItem(asset["asset_issuer"]))

            # Update transactions table
            self.transactions_table.setRowCount(len(account_data["transactions"]))
            for row_idx, tx in enumerate(account_data["transactions"]):
                self.transactions_table.setItem(row_idx, 0, QTableWidgetItem(tx["date"]))
                self.transactions_table.setItem(row_idx, 1, QTableWidgetItem(f"{tx['amount']} XLM"))
                self.transactions_table.setItem(row_idx, 2, QTableWidgetItem(tx["type"]))

                # Highlight amounts (green for positive, red for negative)
                color = QColor("#4CAF50") if tx["amount"] > 0 else QColor("#F44336")
                self.transactions_table.item(row_idx, 1).setForeground(color)

        except Exception as e:

            self.controller.logger.error(f"Error loading account details: {e}")

            self.controller.server_msg['error'] = "Error loading account details:" +str(e)


    def convert_xlm_to_usd(self, balances: []) -> float:
     """Convert XLM to USD using the Stellar Price Feed."""
    # Get live Stellar price feed from Binance US API
     endpoint = "https://api.binance.us/api/v3/ticker/price?symbol=XLMUSDT"

     try:
        response = self.session.get(endpoint)

        if response.status_code != 200:
            self.logger.error(f"Error fetching Stellar price feed: {response.status_code}")
            self.server_msg['status'] = 'ERROR'
            self.server_msg['message'] = "Error fetching Stellar price feed"
            self.server_msg['timestamp'] = int(time.time())
            return 0.0

        data = response.json()
        if isinstance(data, dict) and 'price' in data:
            usd_price = float(data['price'])
            xlm_balance = next((float(b['balance']) for b in balances if b['asset'] == 'XLM'), 0.0)
            self.logger.info(f"Converted {xlm_balance} XLM to USD at {usd_price} USD/XLM")
            return usd_price * xlm_balance
        else:
            self.logger.error("Invalid response structure from price feed.")
            self.server_msg['status'] = 'ERROR'
            self.server_msg['message'] = "Invalid response structure from price feed"
            return 0.0
     except Exception as e:
        self.logger.exception(f"An error occurred: {e}")
        self.server_msg['status'] = 'ERROR'
        self.server_msg['message'] = str(e)
        self.server_msg['timestamp'] = int(time.time())
        return 0.0

