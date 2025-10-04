from datetime import datetime
from PIL import Image
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import (
    QFrame, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout
)
from qrcode.main import QRCode

# Ensure you install the qrcode library


class Dashboard(QFrame):
    """Dashboard widget displaying live data, control buttons, and QR code for account_id."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.stop_button = None
        self.start_button = None
        self.controller = controller
        self.timer = None
        self.bot = self.controller.bot
        self.init_ui()
        self.update_dashboard()

    def init_ui(self):
        """Initialize the user interface components."""
        layout = QGridLayout()

        layout.addWidget(QLabel("Last Update: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")), 0, 2, 0, 1)
        layout.addWidget(QLabel("Account ID: " + self.controller.account_id), 1, 0, 0, 2)
        layout.addWidget(QLabel("Scan to Send Money here"), 2, 0, 0, 2)
        layout.addWidget(QLabel("Status: " + self.controller.server_msg.get('status', 'Unknown')), 3, 0, 0, 2)
        layout.addWidget(QLabel("Info: " + self.controller.server_msg.get('info', 'No info available')), 4, 0, 0, 2)
        layout.addWidget(QLabel("Message: " + self.controller.server_msg.get('message', 'No message')), 5, 0, 0, 2)
        layout.update()

        # QR Code Section (Positioned at the top)
        self.create_qr_code_section(layout)
        # Black Canvas Section (Positioned at the top)
        self.create_black_canvas(layout)

        # Control Buttons Section
        self.start_button = QPushButton("START")
        self.stop_button = QPushButton("STOP")
        self.start_button.clicked.connect(self.start_bot, QtCore.Qt.UniqueConnection)
        self.stop_button.clicked.connect(self.stop_bot, QtCore.Qt.UniqueConnection)
        self.update_button_state(True, False)
        self.start_button.setStyleSheet("background-color: green; color: #1e2a38;")
        self.stop_button.setStyleSheet("background-color: red; color: #1e2a38;")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        layout.addLayout(buttons_layout, 2, 1)
        # Performance Stats Section (Positioned lower in the layout)
        self.create_performance_stats(layout)

        self.setLayout(layout)

    def create_qr_code_section(self, layout):
        """Create the QR code section."""
        qr_group = QGroupBox("Account Information")
        qr_group.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #f0f0f0;")
        qr_layout = QVBoxLayout(qr_group)

        # QR Code Generation
        qr = QRCode(version=1, box_size=10, border=2)
        qr.add_data(self.controller.account_id)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")
        qr_img.save("temp_qr.png")

        qr_label = QLabel()
        qr_pixmap = QtGui.QPixmap("temp_qr.png").scaled(150, 150, QtCore.Qt.KeepAspectRatio)
        qr_label.setPixmap(qr_pixmap)
        qr_label.setAlignment(QtCore.Qt.AlignCenter)

        account_label = QLabel(f"Account ID: {self.controller.account_id}")
        account_label.setAlignment(QtCore.Qt.AlignCenter)
        account_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        qr_layout.addWidget(account_label)
        qr_layout.addWidget(qr_label)
        layout.addWidget(qr_group, 0,1)

    def create_black_canvas(self, layout):
        """Create the black canvas section for server messages."""
        canvas_group = QGroupBox("Server Messages")

        canvas_group.setStyleSheet("background-color: black; color: white; font-size: 14px;")
        canvas_layout = QVBoxLayout(canvas_group)
        canvas_layout.setAlignment(QtCore.Qt.AlignTop)

        for key in ['status', 'info', 'message', 'error']:
            label = QLabel(self.controller.server_msg.get(key, ""))
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("font-size: 12px;")
            canvas_layout.addWidget(label)
        layout.addWidget(canvas_group , 1, 1)

    def create_performance_stats(self, layout_):
        """Create a section to show performance stats such as total trades, profit, and win rate."""
        stats_group = QGroupBox("Performance Stats")
        stats_group.setStyleSheet("font-size: 16px; font-weight: bold; background-color: green; color: white;")
        stats_layout = QVBoxLayout(stats_group)

        for stat in ["Total Trades", "Profit", "Win Rate"]:
            label_ = QLabel(f"{stat}: 0")
            label_.setObjectName(stat)
            stats_layout.addWidget(label_)


        layout_.addWidget(stats_group,  1, 2)


    def update_dashboard(self):
        """Update the dashboard with live data."""
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_live_data)
        self.timer.start(1000)  # Update every second

    def update_live_data(self):
        """Fetch and display live data on the dashboard."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = self.controller.server_msg.get('status', 'Unknown')
        info = self.controller.server_msg.get('info', 'No info available')
        message = self.controller.server_msg.get('message', 'No message')

        # Update Performance Stats
        self.update_performance_stats()

    def update_performance_stats(self):
        """Update the performance stats section with live data."""
        stats = self.controller.server_msg.get('performance_stats', {})
        for stat, value in stats.items():
            label = self.findChild(QLabel, stat)
            if label:
                label.setText(f"{stat}: {value}")

    def start_bot(self):
        """Start the bot."""
        self.bot.start()

    def stop_bot(self):
        """Stop the bot."""
        self.bot.stop()


    def update_button_state(self, start_enabled, stop_enabled):
        """Enable or disable control buttons."""
        self.start_button.setEnabled(start_enabled)
        self.stop_button.setEnabled(stop_enabled)
        if start_enabled:
            self.controller.server_msg['status'] = 'STOP'
