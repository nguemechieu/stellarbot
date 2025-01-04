from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

from src.modules.frames.market_depth import random_color


class SendMoney(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Send Money widget."""
        super().__init__(parent)
        self.controller = controller
        self.user_id_display = None

        self.recipient_input = None
        self.amount_input = None

        self.setGeometry(10, 10, 1530, 780)

        # Main layout for the widget
        self.layout = QVBoxLayout()


        # Create the send money section
        self.create_send_money_section()

        # Create the receiver money section
        self.create_receive_money_section()

    def create_send_money_section(self):
        """Create the UI components for sending money."""
        send_label = QLabel("Send Money")
        send_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(send_label)

        # Recipient ID
        recipient_label = QLabel("Recipient ID:")
        recipient_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(recipient_label)

        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText("Enter recipient ID")
        self.layout.addWidget(self.recipient_input)

        # Amount
        amount_label = QLabel("Amount:")
        amount_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(amount_label)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        self.layout.addWidget(self.amount_input)

        # Send Button
        send_button = QPushButton("Send")
        send_button.setStyleSheet("background-color: "+random_color()+"; color: white; font-size: 14px; padding: 5px;")
        send_button.clicked.connect(self.send_money)
        self.layout.addWidget(send_button)

    def create_receive_money_section(self):
        """Create the UI components for receiving money."""
        receive_label = QLabel("Receive Money")
        receive_label.setStyleSheet(""
                                    "font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(receive_label)

        # User ID
        user_id_label = QLabel("Your User ID:")
        user_id_label.setStyleSheet("font-size: 14px;")
        self.layout.addWidget(user_id_label)

        self.user_id_display = QLabel(self.controller.account_id if self.controller else "Unknown")
        self.user_id_display.setStyleSheet("font-size: 14px; color: #333; padding: 5px; border: 1px solid #CCC; background-color: #FFF;")
        self.layout.addWidget(self.user_id_display)

        # Refresh Button
        refresh_button = QPushButton("Refresh")
        refresh_button.setStyleSheet("background-color: #2196F3; color: white; font-size: 14px; padding: 5px;")
        refresh_button.clicked.connect(self.refresh_user_id)
        self.layout.addWidget(refresh_button)
        self.setLayout(self.layout)

    def send_money(self):
        """Handle the sent money functionality."""
        recipient = self.recipient_input.text().strip()
        amount = self.amount_input.text().strip()

        if not recipient or not amount:
            QMessageBox.warning(self, "Input Error", "Please enter both Recipient ID and Amount.")
            return

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive.")
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Invalid amount: {e}")
            return

        if self.controller:
            try:
                success = self.controller.bot.send_money(recipient, amount)
                if success:
                    QMessageBox.information(self, "Success", f"Successfully sent {amount} to {recipient}.")
                    self.recipient_input.clear()
                    self.amount_input.clear()
                else:
                    QMessageBox.warning(self, "Error", "Failed to send money. Please try again.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
        else:
            QMessageBox.warning(self, "Controller Error", "Controller is not available.")

    def refresh_user_id(self):
        """Refresh the displayed user ID."""
        if self.controller:
            self.user_id_display.setText(self.controller.account_id)
        else:
            self.user_id_display.setText("Unknown")
