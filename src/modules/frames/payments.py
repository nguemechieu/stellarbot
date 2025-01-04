from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFrame


class Payments(QFrame):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.payments_table = None

        # Set up frame appearance
        self.setGeometry(100, 50, 1530, 780)
        self.setStyleSheet(
            "font-size:24px;"
            "border: 1px solid #ccc;"
            "padding: 20px;"
        )

        # Create widgets and populate table
        self.create_widgets()
        self.update_payments_data()

    def create_widgets(self):
        """Set up the layout and payments table."""
        layout = QtWidgets.QVBoxLayout(self)

        # Add a label
        ledger_label = QtWidgets.QLabel("Payments")
        layout.addWidget(ledger_label)

        # Create the payments table
        self.payments_table = QtWidgets.QTableWidget()
        self.payments_table.setColumnCount(11)
        self.payments_table.setHorizontalHeaderLabels([
            "ID", "Account", "From", "To", "Amount", "Asset Type",
            "Asset Code", "Asset Issuer", "Created At", "Memo Type", "Memo"
        ])

        # Set column widths
  
        self.payments_table.setSortingEnabled(True)  # Enable sorting for all columns
        self.payments_table.setColumnHidden(0, True)  # Hide the ID column
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.payments_table)

        # Assign layout to the frame
        self.setLayout(layout)

    def update_payments_data(self):
        """Fetch and update payment data in the table."""
        try:
            # Fetch payment data
            payments_df = self.get_payments_data()

            # Clear existing rows
            self.payments_table.setRowCount(0)

            # Populate the table with new data
            for idx, row in payments_df.iterrows():
                self.payments_table.insertRow(idx)

                # Fill each column with data
                self.payments_table.setItem(idx, 0, QtWidgets.QTableWidgetItem(str(row.get('id', 'N/A'))))
                self.payments_table.setItem(idx, 1, QtWidgets.QTableWidgetItem(str(row.get('account', 'N/A'))))
                self.payments_table.setItem(idx, 2, QtWidgets.QTableWidgetItem(str(row.get('from', 'N/A'))))
                self.payments_table.setItem(idx, 3, QtWidgets.QTableWidgetItem(str(row.get('to', 'N/A'))))
                self.payments_table.setItem(idx, 4, QtWidgets.QTableWidgetItem(str(row.get('amount', 'N/A'))))
                self.payments_table.setItem(idx, 5, QtWidgets.QTableWidgetItem(str(row.get('asset_type', 'N/A'))))
                self.payments_table.setItem(idx, 6, QtWidgets.QTableWidgetItem(str(row.get('asset_code', 'N/A'))))
                self.payments_table.setItem(idx, 7, QtWidgets.QTableWidgetItem(str(row.get('asset_issuer', 'N/A'))))
                self.payments_table.setItem(idx, 8, QtWidgets.QTableWidgetItem(str(row.get('created_at', 'N/A'))))
                self.payments_table.setItem(idx, 9, QtWidgets.QTableWidgetItem(str(row.get('memo_type', 'N/A'))))
                self.payments_table.setItem(idx, 10, QtWidgets.QTableWidgetItem(str(row.get('memo', 'N/A'))))

                # Optional: Add custom tooltips
                tooltips = [
                    "Payment ID", "Account ID", "From Account ID", "To Account ID",
                    "Payment Amount", "Payment Asset Type", "Payment Asset Code",
                    "Payment Asset Issuer", "Created At", "Memo Type", "Memo"
                ]
                for col in range(len(tooltips)):
                    if self.payments_table.item(idx, col):
                        self.payments_table.item(idx, col).setToolTip(tooltips[col])

                # Optional: Add custom background colors
                if row.get('asset_type') != 'native':
                    self.payments_table.item(idx, 5).setBackground(QColor(240, 240, 240))  # Light gray background for non-native assets

        except AttributeError as e:
            print(f"Error fetching payments data: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def get_payments_data(self):
        """Retrieve payment data from the bot controller."""
        return self.controller.bot.payments_df
