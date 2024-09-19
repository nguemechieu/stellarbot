from PyQt5 import QtWidgets, QtGui


class AccountOverview(QtWidgets.QWidget):
    def __init__(self, parent=None, controller=None):
        """Initialize the Account Overview widget."""
        super().__init__(parent)

        self.controller = controller

        # Set the widget's geometry and style sheet
        self.setGeometry(0, 0, 1530, 780)
        

        # Main layout for the widget
        layout = QtWidgets.QVBoxLayout(self)

        # Create a dark-themed frame for the account overview section
        self.account_frame = QtWidgets.QFrame(self)
        
        
        layout.addWidget(self.account_frame)

        # Create a frame for the account overview section
        account_overview_frame = self.create_frame(self.account_frame, "#2E2E2E", 600, 350, "Account Overview")

        # Create widgets for the account overview section
        self.create_account_widgets(account_overview_frame)

        # Create a light-themed frame for financial summary section
        financial_summary_frame = self.create_frame(self.account_frame, "#E0E0E0", 600, 400, "Financial Summary")

        # Create widgets for the financial summary section
        self.create_financial_widgets(financial_summary_frame)

    def create_account_widgets(self, frame):
        """Create widgets for the Account Overview section."""
        account_details = [
            ("Name:", 40),
            ("Account Number/ID:", 70),
            ("Broker Platform:", 100),
            ("Account Type:", 130),
            ("Account Balance:", 190),
            ("Available Margin/Leverage:", 220),
            ("Portfolio Allocation:", 250),
            ("Last Login Date:", 280)
        ]

        # Create and position the fields dynamically
        for label_text, y_pos in account_details:
            label = QtWidgets.QLabel(label_text, frame)
            label.setStyleSheet("color: white; font-size: 12px;")
            label.move(10, y_pos)

            entry = QtWidgets.QLineEdit(frame)
            entry.setFixedWidth(300)
            entry.move(200, y_pos)

    def create_financial_widgets(self, frame):
        """Create widgets for the Financial Summary section."""
        financial_details = [
            ("Initial Deposit:", 40),
            ("Current Balance:", 70),
            ("Unrealized Profit/Loss:", 100),
            ("Realized Profit/Loss:", 130)
        ]

        # Create and position the fields dynamically
        for label_text, y_pos in financial_details:
            label = QtWidgets.QLabel(label_text, frame)
            label.setStyleSheet("color: #003366; font-size: 12px;")
            label.move(10, y_pos)

            entry = QtWidgets.QLineEdit(frame)
            entry.setFixedWidth(300)
            entry.move(200, y_pos)

        self.create_withdrawal_history(frame, "Withdrawal History", 170, 200)
        self.create_withdrawal_history(frame, "Deposit History", 300, 330)

    def create_withdrawal_history(self, frame, text, y, height):
        """Create a section for Withdrawal or Deposit history."""
        history_label = QtWidgets.QLabel(text, frame)
        history_label.setStyleSheet("color: #003366; font-size: 14px; font-weight: bold;")
        history_label.move(10, y)

        # Create a frame to hold the history date and amount entries
        history_frame = QtWidgets.QFrame(frame)
        history_frame.setStyleSheet("background-color: #E0E0E0;")
        history_frame.setGeometry(10, height, 580, 120)

        # Add headers for history
        date_label = QtWidgets.QLabel("Date", history_frame)
        date_label.setStyleSheet("color: #003366; font-size: 12px;")
        date_label.move(5, 5)

        amount_label = QtWidgets.QLabel("Amount", history_frame)
        amount_label.setStyleSheet("color: #003366; font-size: 12px;")
        amount_label.move(200, 5)

        # Add multiple entries for history (e.g., 3 entries)
        for i in range(3):
            date_entry = QtWidgets.QLineEdit(history_frame)
            date_entry.setFixedWidth(120)
            date_entry.move(5, 30 + i * 30)

            amount_entry = QtWidgets.QLineEdit(history_frame)
            amount_entry.setFixedWidth(120)
            amount_entry.move(200, 30 + i * 30)

    def create_frame(self, parent, bg_color, width, height, title):
        """Create a frame with a title."""
        frame = QtWidgets.QFrame(parent)
        frame.setStyleSheet(f"background-color: {bg_color};")
        frame.setFixedSize(width, height)

        title_label = QtWidgets.QLabel(title, frame)
        title_label.setStyleSheet(f"color: {'white' if bg_color == '#2E2E2E' else '#003366'}; font-size: 16px; font-weight: bold;")
        title_label.move(10, 10)

        return frame
