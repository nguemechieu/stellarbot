from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFrame


class AccountOverview(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Account Overview widget."""
        super().__init__(parent)
        self.controller = controller
        # Set the main layout for the widget
        main_layout = QtWidgets.QVBoxLayout(self)
        self.setGeometry(0, 0, 1530, 780)
        # Create the account overview section
        account_overview_frame = self.create_frame("Account Overview", "#2E2E2E")
        main_layout.addWidget(account_overview_frame)
        self.populate_account_overview(account_overview_frame)
        # Create the financial summary section
        financial_summary_frame = self.create_frame("Financial Summary", "green"  )
        main_layout.addWidget(financial_summary_frame)
        self.populate_financial_summary(financial_summary_frame)


    def create_frame(self, title, bg_color):
        """Create a styled frame with a title."""
        frame = QtWidgets.QFrame(self)
        frame.setStyleSheet(f"background-color: {bg_color}; padding: 10px;")

        layout = QtWidgets.QVBoxLayout(frame)
        title_label = QtWidgets.QLabel(title, frame)
        title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {'white' if bg_color == '#2E2E2E' else '#003366'};")
        layout.addWidget(title_label)

        return frame

    def populate_account_overview(self, frame):
        """Populate the Account Overview section with widgets."""
        layout = QtWidgets.QGridLayout()
        account_details = [
            ("Name:", ""),
            ("Account Number/ID:", ""),
            ("Broker Platform:", ""),
            ("Account Type:", ""),
            ("Account Balance:", ""),
            ("Available Margin/Leverage:", ""),
            ("Portfolio Allocation:", ""),
            ("Last Login Date:", "")
        ]

        # Create labels and input fields
        for row, (label_text, default_value) in enumerate(account_details):
            label = QtWidgets.QLabel(label_text, frame)
            label.setStyleSheet("color: white;")
            entry = QtWidgets.QLineEdit(frame)
            entry.setText(default_value)
            layout.addWidget(label, row, 0)
            layout.addWidget(entry, row, 1)

        frame.setLayout(layout)

    def populate_financial_summary(self, frame):
        """Populate the Financial Summary section with widgets."""
        layout = QtWidgets.QVBoxLayout()

        # Financial Details
        financial_details = [
            ("Initial Deposit:", ""),
            ("Current Balance:", ""),
            ("Unrealized Profit/Loss:", ""),
            ("Realized Profit/Loss:", "")
        ]
        for label_text, default_value in financial_details:
            row_layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(label_text, frame)
            label.setStyleSheet("color: #003366;")
            entry = QtWidgets.QLineEdit(frame)
            entry.setText(default_value)
            row_layout.addWidget(label)
            row_layout.addWidget(entry)
            layout.addLayout(row_layout)

        # Withdrawal History
        self.add_history_section(frame, layout, "Withdrawal History")
        # Deposit History
        self.add_history_section(frame, layout, "Deposit History")

        frame.setLayout(layout)

    def add_history_section(self, frame, layout, title):
        """Add a section for transaction history."""
        section_title = QtWidgets.QLabel(title, frame)
        section_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #003366;")
        layout.addWidget(section_title)

        history_layout = QtWidgets.QGridLayout()
        headers = ["Date", "Amount"]
        for col, header in enumerate(headers):
            header_label = QtWidgets.QLabel(header, frame)
            header_label.setStyleSheet("color: #003366; font-size: 12px; font-weight: bold;")
            history_layout.addWidget(header_label, 0, col)

        # Add rows for history data (example with 3 rows)
        for row in range(1, 4):
            date_entry = QtWidgets.QLineEdit(frame)
            amount_entry = QtWidgets.QLineEdit(frame)
            history_layout.addWidget(date_entry, row, 0)
            history_layout.addWidget(amount_entry, row, 1)

        layout.addLayout(history_layout)
