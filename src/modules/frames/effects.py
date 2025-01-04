from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFrame
class Effects(QFrame):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.effects_table = None
        self.effects_label = None
        self.controller = controller

        # Create widgets to display the effect information
        self.create_widgets()

        # Fetch and display the effect data
       # self.update_effects_data()

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
        effects_data = self.controller.effects_df
        if not effects_data:
            self.effects_label.setText("No Market Effects Available")
            self.effects_table.setRowCount(0)
            self.effects_table.setSortingEnabled(False)
            return  # No effects data available

        # Convert effects data to DataFrame
        effects_df = effects_data

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
        # Add custom tooltips
        self.effects_table.item(idx, 0).setToolTip("Effect ID")
        self.effects_table.item(idx, 1).setToolTip("Effect Type")
        self.effects_table.item(idx, 2).setToolTip("Account ID")
        self.effects_table.item(idx, 3).setToolTip("Created At")
        self.effects_table.item(idx, 4).setToolTip("Amount")
        self.effects_table.item(idx, 5).setToolTip("Asset Code")
        # Add custom background colors
        if row.get('type') == 'trade':
            self.effects_table.item(idx, 1).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 2).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 3).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 4).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 5).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 0).setBackgroundColor(QtCore.Qt.green)
            self.effects_table.item(idx, 2).setBackgroundColor(QtCore.Qt.green)
            self.effects_table.item(idx, 3).setBackgroundColor(QtCore.Qt.green)
            self.effects_table.item(idx, 4).setBackgroundColor(QtCore.Qt.green)
            self.effects_table.item(idx, 5).setBackgroundColor(QtCore.Qt.green)
            self.effects_table.item(idx, 0).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.effects_table.item(idx, 1).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.effects_table.item(idx, 2).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.effects_table.item(idx, 3).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.effects_table.item(idx, 4).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.effects_table.item(idx, 5).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.effects_table.item(idx, 0).setTextAlignment(QtCore.Qt.AlignRight)
            self.effects_table.item(idx, 1).setTextAlignment(QtCore.Qt.AlignRight)
            self.effects_table.item(idx, 2).setTextAlignment(QtCore.Qt.AlignRight)
            self.effects_table.item(idx, 3).setTextAlignment(QtCore.Qt.AlignRight)
            self.effects_table.item(idx, 4).setTextAlignment(QtCore.Qt.AlignRight)
            self.effects_table.item(idx, 5).setTextAlignment(QtCore.Qt.AlignRight)
            self.effects_table.item(idx, 0).setCheckState(QtCore.Qt.Unchecked)
            self.effects_table.item(idx, 1).setCheckState(QtCore.Qt.Unchecked)
            self.effects_table.item(idx, 2).setCheckState(QtCore.Qt.Unchecked)


        if row.get('type') == 'trustline_created':
            self.effects_table.item(idx, 1).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 2).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 3).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 4).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 5).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 0).setBackgroundColor(QtCore.Qt.green)
            self.effects_table.item(idx, 2).setBackgroundColor(QtCore.Qt.green)
            self.effects_table.item(idx, 3).setBackgroundColor(QtCore.Qt.green)

        if row.get('type') == 'trustline_updated':
            self.effects_table.item(idx, 1).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 2).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 3).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 4).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 5).setBackgroundColor(QtCore.Qt.yellow)
            self.effects_table.item(idx, 0).setBackgroundColor(QtCore.Qt.green)
            self.effects_table.item(idx, 2).setBackgroundColor(QtCore.Qt.green)
            self.effects_table.item(idx, 3).setBackgroundColor(QtCore.Qt.green)