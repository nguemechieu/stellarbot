from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QFormLayout, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FeeAnalysis(QWidget):
    def __init__(self, parent=None):
        """Initialize the Fee Analysis widget."""
        super().__init__(parent)
        self.setGeometry(
            0, 0,1530,780
        )
        # Set up the main layout for the widget
        main_layout = QVBoxLayout()

        # Create the title label for the fee analysis section
        title_label = QLabel("Fee Analysis")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("color: #2874A6; font-weight: bold;")  # QSS for title styling
        main_layout.addWidget(title_label)

        # Create a form layout for the fee details
        form_layout = QFormLayout()

        # Create and add Total Fees Paid field
        self.total_fees = self.create_readonly_entry("$500")
        form_layout.addRow("Total Fees Paid (Spread, Commission):", self.total_fees)

        # Create and add Average Fee Per Trade field
        self.avg_fee = self.create_readonly_entry("$5")
        form_layout.addRow("Average Fee Per Trade:", self.avg_fee)

        # Create and add Fee Impact on Performance field
        self.fee_impact = self.create_readonly_entry("-1.5%")
        form_layout.addRow("Fee Impact on Performance:", self.fee_impact)

        # Add the form layout to the main layout
        main_layout.addLayout(form_layout)

        # Set the layout for the widget
        self.setLayout(main_layout)

        # Apply global QSS styling to the widget
        self.setStyleSheet("""
            QWidget {
                background-color: #F2F4F4;
            }
            QLineEdit {
                background-color: #D5DBDB;
                color: #2874A6;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                border: 1px solid #2874A6;
            }
            QLabel {
                color: #2874A6;
                font-size: 14px;
            }
        """)

    def create_readonly_entry(self, value):
        """Helper function to create a read-only QLineEdit with pre-filled value."""
        entry = QLineEdit()
        entry.setText(value)
        entry.setReadOnly(True)
        entry.setAlignment(Qt.AlignCenter)
        return entry

