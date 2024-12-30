from PyQt5 import QtWidgets, QtCore
import pandas as pd
from PyQt5.QtWidgets import QWidget
class Trades(QWidget):
    """Widget to display trades from Stellar."""
    
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller

        self.setGeometry(
            0, 0,1530,780
        )

        layout = QtWidgets.QVBoxLayout(parent)

        # Title label
        title_label = QtWidgets.QLabel("Trades", self)
        title_label.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(title_label)

        # Create the table (QTableWidget) to display the trades
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Trade ID", "Buyer", "Seller", "Sold Asset", "Bought Asset", "Amount", "Price"])
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)  # Prevent editing
        layout.addWidget(self.table)

        # Load trade data from CSV
        self.trades = pd.read_csv('ledger_trades.csv')

        # Populate the table with data
        self.update_trades_data()

    def update_trades_data(self):
        """Fetch and display trades data in the table."""
        self.table.setRowCount(0)  # Clear existing data

        # Populate the table with data from the DataFrame
        for idx, row in self.trades:
            self.table.insertRow(idx)
            self.table.setItem(idx, 0, QtWidgets.QTableWidgetItem(str(row.get("id", "N/A"))))
            self.table.setItem(idx, 1, QtWidgets.QTableWidgetItem(row.get("buyer", "N/A")))
            self.table.setItem(idx, 2, QtWidgets.QTableWidgetItem(row.get("seller", "N/A")))
            self.table.setItem(idx, 3, QtWidgets.QTableWidgetItem(row.get("sold_asset", "N/A")))
            self.table.setItem(idx, 4, QtWidgets.QTableWidgetItem(row.get("bought_asset", "N/A")))
            self.table.setItem(idx, 5, QtWidgets.QTableWidgetItem(str(row.get("amount", 0))))
            self.table.setItem(idx, 6, QtWidgets.QTableWidgetItem(str(row.get("price", 0))))

        # Automatically resize columns
        self.table.resizeColumnsToContents()

        # Schedule the next update
        QtCore.QTimer.singleShot(1000, self.update_trades_data)
