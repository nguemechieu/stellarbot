from datetime import datetime

from PIL import Image
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QPushButton, QFrame

from qrcode.main import QRCode


def create_performance_stats(layout):
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


class Dashboard(QFrame):
    """Dashboard widget displaying live data, control buttons, and QR code for account_id."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)

        self.start_button = QPushButton("START", self)

        self.stop_button = QPushButton("STOP", self)
        self.controller = controller
        self.bot=controller.bot

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
            f"Account ID: {self.controller.account_id}\n"
            f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            f"\nStatus: {self.controller.server_msg['status']}\n"
            f"Info: {self.controller.server_msg['info']}\n"
            f"Message: {self.controller.server_msg['message']}"
        )

        layout.addWidget(self.lbl_text)
        # Create account ID QR code
        self.create_qr_code("account_id")
        # Add server control buttons
        buttons_layout = QtWidgets.QHBoxLayout(self)
        self.start_button.clicked.connect(self.start_bot)
        self.stop_button.clicked.connect(self.stop_bot)


        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        layout.addLayout(buttons_layout)

        # Performance stats
        create_performance_stats(layout)
        self.setLayout(layout)
        self.update_dashboard()


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


    def _extracted_from_create_qr_code_16(self, arg0, arg1):
        arg0.setAlignment(QtCore.Qt.AlignCenter)
        arg0.setStyleSheet(arg1)
        self.layout().addWidget(arg0)

    def start_bot(self):

        self.controller.server_msg['status'] = 'START'
        self._extracted_from_start_bot_3(False, "background-color: gray; color: red;", True)



    def stop_bot(self):
        self.controller.server_msg['status'] = 'STOP'
        self._extracted_from_stop_bot_3(True, "background-color: green; color: red;", False)

    def _extracted_from_stop_bot_3(self, arg0, arg1, arg2):
        self.start_button.setEnabled(arg0)
        self.start_button.setStyleSheet(arg1)
        self.stop_button.setEnabled(arg2)
    def updates(self):
        """Update the dashboard regularly with live data."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Fetch the latest data from the bot's server messages
        status = self.controller.server_msg.get('status', 'Unknown')
        info = self.controller.server_msg.get('info', 'No info available')
        message = self.controller.server_msg.get('message', 'No message')

        # Update the text label with new data
        self.lbl_text.setText(
            f"Account ID: {self.controller.account_id}\n"
            f"Last Update: {current_time}\n"
            f"Status: {status}\n"
            f"Info: {info}\n"
            f"Message: {message}\n"
            f"Performance Stats:\n"

        )

    def update_dashboard(self):
        """Update the dashboard with live data."""
        self.updates()
        self.update()
        QtCore.QTimer.singleShot(1000, self.update_dashboard)




    def update_performance_stats(self):
        """Update the performance stats section with live data."""
        # Fetch the latest performance stats from the bot's server messages
        total_trades = self.controller.bot.server_msg['total_trades']
        profit = self.controller.bot.server_msg['profit']
        win_rate = self.controller.bot.server_msg['win_rate']

        # Update the performance stats section with new data
        for stat, value in zip(['Total Trades', 'Profit', 'Win Rate'], [total_trades, profit, win_rate]):
            stat_label = self.findChild(QtWidgets.QLabel, stat)
            stat_label.setText(f"{stat}: {value}")

    def _extracted_from_start_bot_3(self, param, param1, param2):
        self.start_button.setEnabled(param)
        self.start_button.setStyleSheet(param1)
        self.stop_button.setEnabled(param2)
        pass

