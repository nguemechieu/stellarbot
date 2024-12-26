from datetime import datetime

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QPushButton
from qrcode.compat.pil import Image
from qrcode.main import QRCode


class Dashboard(QtWidgets.QWidget):
    """Dashboard widget displaying live data, control buttons, and QR code for account_id."""

    def __init__(self, parent=None, controller=None):
        super(Dashboard, self).__init__(parent)

        self.start_button = QPushButton("START", self)
        self.start_button.setStyleSheet("background-color: #333; color: green;")
        self.stop_button = QPushButton("STOP", self)
        self.stop_button.setStyleSheet("background-color: #333; color: red;")

        self.controller = controller

        # Set layout and background
        layout = QtWidgets.QVBoxLayout(self)

        # Create and style the canvas (QWidget in PyQt5)
        self.lbl = QtWidgets.QLabel(self)
        layout.addWidget(self.lbl)

        # Welcome Message
        welcome_label = QtWidgets.QLabel("Welcome to StellarBot Dashboard", self)
        welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(welcome_label)

        self.lbl_text = QtWidgets.QLabel()
        self.lbl_text.setStyleSheet("color: white; font-size: 16px;")
        self.lbl_text.setText(
            f"Account ID: {self.controller.bot.account_id}\n"
            f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            f"\nStatus: {self.controller.bot.server_msg['status']}\n"
            f"Info: {self.controller.bot.server_msg['info']}\n"
            f"Message: {self.controller.bot.server_msg['message']}"
        )

        layout.addWidget(self.lbl_text)
        # Create account ID QR code
        self.create_qr_code("account_id")
        # Add server control buttons
        buttons_layout = QtWidgets.QHBoxLayout(self)


        self.start_button.clicked.connect(self.start_bot)
        self.stop_button.clicked.connect(self.stop_bot)
        if self.controller.bot.server_msg['status'] == "RUNNING":
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        else:
            self.start_button.setEnabled(True)

            self.stop_button.setEnabled(False)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        layout.addLayout(buttons_layout)

        # Performance stats
        self.create_performance_stats(layout)

        # Display time and live data
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updates)
        self.timer.start(1000)

    def create_qr_code(self, account_id):
        """Create a QR code for the account ID and display it on the dashboard."""

        qr = QRCode(version=1, box_size=10, border=2)
        qr.add_data(account_id)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")

        # Save and display QR code
        qr_img.save("temp_qr.png")
        img = Image.open("temp_qr.png")
        img.resize((150, 150))
        qt_img = QtGui.QPixmap("temp_qr.png")

        qr_label = QtWidgets.QLabel(self)
        qr_label.setPixmap(qt_img)
        self._extracted_from_create_qr_code_16(qr_label, "background-color: #1e2a38;")
        label = QtWidgets.QLabel("Account ID", self)
        self._extracted_from_create_qr_code_16(
            label, "color: white; font-size: 14px; font-weight: bold;"
        )


    # TODO Rename this here and in `create_qr_code`
    def _extracted_from_create_qr_code_16(self, arg0, arg1):
        arg0.setAlignment(QtCore.Qt.AlignCenter)
        arg0.setStyleSheet(arg1)
        self.layout().addWidget(arg0)

    def create_performance_stats(self, layout):
        """Create a section to show performance stats such as total trades and profit."""
        performance_group = QtWidgets.QGroupBox("Performance Stats")
        performance_group.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background-color: #2d3e50;")
        performance_layout = QtWidgets.QVBoxLayout(performance_group)

        stats = {
            "Total Trades": "345",
            "Profit": "$15,000",
            "Win Rate": "75%"
        }

        for stat, value in stats.items():
            stat_label = QtWidgets.QLabel(f"{stat}: {value}")
            stat_label.setStyleSheet("color: #4CAF50; font-size: 12px; font-weight: bold;")
            performance_layout.addWidget(stat_label)

        layout.addWidget(performance_group)

    def start_bot(self):

        self.controller.bot.start()

    def stop_bot(self):

        self.controller.bot.stop()

    # TODO Rename this here and in `start_bot` and `stop_bot`
    def _extracted_from_stop_bot_3(self, arg0, arg1, arg2):
        self.start_button.setEnabled(arg0)
        self.start_button.setStyleSheet(arg1)
        self.stop_button.setEnabled(arg2)
    def updates(self):
        """Update the dashboard regularly with live data."""
        # Create time and update labels
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Fetch the latest data from the bot's server messages
        status = self.controller.bot.server_msg['status']
        info = self.controller.bot.server_msg['info']
        message = self.controller.bot.server_msg['message']

        # Update the text label to reflect new data
        self.lbl_text.setText(
            f"Account ID: {self.controller.bot.account_id}\n"
            f"Last Update: {current_time}\n"
            f"Status: {status}\n"
            f"Info: {info}\n"
            f"Message: {message}"
        )
        self.lbl_text.adjustSize()  # Adjust the label size based on the new content