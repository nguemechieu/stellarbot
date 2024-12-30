from PyQt5 import QtWidgets, QtCore
import pandas as pd
from PyQt5.QtWidgets import QFrame


class Effects(QFrame):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.effects_table = None
        self.effects_label = None
        self.controller = controller

        self.account_id = self.controller.offers

        
        # Create widgets to display the effect information
        self.create_widgets()

        # Fetch and display the effect data
        self.update_effects_data()

    def create_widgets(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.effects_label = QtWidgets.QLabel("Market Effects", self)

        self.effects_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.effects_label)

        # Section: Effects Table
        self.effects_table = QtWidgets.QTableWidget()
        self.effects_table.setColumnCount(6)
        self.effects_table.setHorizontalHeaderLabels(['ID', 'Type', 'Account', 'Created At', 'Amount', 'Asset Code'])
        self.effects_table.horizontalHeader().setStretchLastSection(True)
        self.effects_table.setAlternatingRowColors(True)
        layout.addWidget(self.effects_table)

    def update_effects_data(self):
        """Fetch and display effects data."""
        effects_data = self.controller.effects
        if not effects_data:
            return  # No effects data available

        # Convert effects data to DataFrame
        effects_df = pd.json_normalize(effects_data)

        # Update Effects Table
        self.effects_table.setRowCount(0)  # Clear the table
        for idx, row in effects_df.iterrows():
            self._extracted_from_update_effects_data_11(idx, row)
        # Update the table and schedule the next data fetch
        self.effects_table.resizeColumnsToContents()
        QtCore.QTimer.singleShot(1000, self.update_effects_data)

    # update_effects_data
    def _extracted_from_update_effects_data_11(self, idx, row):
        self.effects_table.insertRow(idx)
        self.effects_table.setItem(idx, 0, QtWidgets.QTableWidgetItem(str(row.get('id', 'N/A'))))
        self.effects_table.setItem(idx, 1, QtWidgets.QTableWidgetItem(str(row.get('type', 'N/A'))))
        self.effects_table.setItem(idx, 2, QtWidgets.QTableWidgetItem(str(row.get('account_id', 'N/A'))))
        self.effects_table.setItem(idx, 3, QtWidgets.QTableWidgetItem(str(row.get('created_at', 'N/A'))))
        self.effects_table.setItem(idx, 4, QtWidgets.QTableWidgetItem(str(row.get('amount', 'N/A'))))
        self.effects_table.setItem(idx, 5, QtWidgets.QTableWidgetItem(str(row.get('asset_code', 'N/A'))))
