from PyQt5 import QtWidgets
import pandas as pd
import requests
from PyQt5.QtWidgets import QFrame


class Payments(QFrame):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.payments_table = None
        self.controller = controller
        self.setGeometry(0, 0, 1530, 780)

        # Create widgets to display the payments information
        self.create_widgets()

        # Fetch and display the payments data
        self.update_payments_data()

    def create_widgets(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Section: Payments Table
        self.payments_table = QtWidgets.QTableWidget(self)
        self.payments_table.setColumnCount(8)
        self.payments_table.setHorizontalHeaderLabels(
            ['ID', 'Type', 'Created At', 'Transaction Hash', 'Amount', 'Asset Code', 'From Account', 'To Account']
        )
        self.payments_table.horizontalHeader().setStretchLastSection(True)
        self.payments_table.setAlternatingRowColors(True)

        layout.addWidget(self.payments_table)

    def update_payments_data(self):
        # Fetch payments data from the Stellar Horizon API
        url = 'https://horizon.stellar.org/payments'
        response = requests.get(url)
        payments_data = response.json().get('_embedded', {}).get('records', [])

        # Convert payments data to DataFrame
        payments_df = pd.json_normalize(payments_data)

        # Clear the current data in the Table
        self.payments_table.setRowCount(0)

        # Insert new data into the Table
        for idx, row in payments_df.iterrows():
            self.payments_table.insertRow(idx)

            amount = row.get('amount', 'N/A')
            asset_code = row.get('asset_code', 'native' if row.get('asset_type') == 'native' else 'N/A')
            from_account = row.get('from', row.get('source_account', 'N/A'))
            to_account = row.get('to', row.get('to_account', 'N/A'))

            self.payments_table.setItem(idx, 0, QtWidgets.QTableWidgetItem(str(row.get('id', 'N/A'))))
            self.payments_table.setItem(idx, 1, QtWidgets.QTableWidgetItem(str(row.get('type', 'N/A'))))
            self.payments_table.setItem(idx, 2, QtWidgets.QTableWidgetItem(str(row.get('created_at', 'N/A'))))
            self.payments_table.setItem(idx, 3, QtWidgets.QTableWidgetItem(str(row.get('transaction_hash', 'N/A'))))
            self.payments_table.setItem(idx, 4, QtWidgets.QTableWidgetItem(str(amount)))
            self.payments_table.setItem(idx, 5, QtWidgets.QTableWidgetItem(str(asset_code)))
            self.payments_table.setItem(idx, 6, QtWidgets.QTableWidgetItem(str(from_account)))
            self.payments_table.setItem(idx, 7, QtWidgets.QTableWidgetItem(str(to_account)))

        self.payments_table.resizeColumnsToContents()

