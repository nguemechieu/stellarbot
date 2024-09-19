import os
import re
import csv
import requests
import qrcode
from PyQt5 import QtGui, QtWidgets
from stellar_sdk import Keypair
from modules.classes.settings_manager import SettingsManager
from modules.classes.stellar_client import StellarClient


class Login(QtWidgets.QWidget):
    """Stellar Network User Login Frame using PyQt5."""


    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller

        self.setGeometry(
            0,
            0,
            1530,
            780
        )

        # Load saved settings like account and secret keys
        self.settings = SettingsManager.load_settings()

        # Set up styling and layout
        self.set_ui()
        self.populate_saved_settings()

    def set_ui(self):
        """Set up the UI layout and components."""
        self.setStyleSheet("background-color: #1e2a38; color: white;")
        self.setFixedSize(1530, 780)

        layout = QtWidgets.QVBoxLayout()

        # Application name label
        app_name_label = QtWidgets.QLabel("Welcome to StellarBot", self)
        app_name_label.setFont(QtGui.QFont("Helvetica", 23, QtGui.QFont.Bold))
        app_name_label.setStyleSheet("color: green;")
        layout.addWidget(app_name_label)
        layout.addSpacing(10)

        # Title label
        title_label = QtWidgets.QLabel("Stellar Network Login", self)
        title_label.setFont(QtGui.QFont("Helvetica", 16, QtGui.QFont.Bold))
        layout.addWidget(title_label)
        layout.addSpacing(10)

        # Account ID entry field
        layout.addWidget(self.create_label("Account ID"))
        self.account_id_entry = QtWidgets.QLineEdit(self)
        layout.addWidget(self.account_id_entry)

        # Secret Key entry field
        layout.addWidget(self.create_label("Secret Key"))
        self.secret_key_entry = QtWidgets.QLineEdit(self)
        self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.secret_key_entry)

        # Password visibility toggle button
        self.password_visibility_toggle = QtWidgets.QPushButton("Show", self)
        self.password_visibility_toggle.clicked.connect(self.toggle_password_visibility)
        layout.addWidget(self.password_visibility_toggle)

        # Login button
        self.login_button = QtWidgets.QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        # Create new account button
        self.create_account_button = QtWidgets.QPushButton("Create New Account", self)
        self.create_account_button.clicked.connect(self.create_new_account)
        layout.addWidget(self.create_account_button)

        # Remember Me checkbox
        self.remember_me = QtWidgets.QCheckBox("Remember Me", self)
        layout.addWidget(self.remember_me)

        # Network connectivity status label
        self.network_status_label = QtWidgets.QLabel("Checking network status...", self)
        layout.addWidget(self.network_status_label)
        self.check_network_connectivity()

        # Info label for messages
        self.info_label = QtWidgets.QLabel("", self)
        layout.addWidget(self.info_label)

        self.setLayout(layout)
     

    def create_label(self, text):
        """Helper method to create styled labels."""
        label = QtWidgets.QLabel(self)
        label.setText(text)
        label.setStyleSheet("font-size: 14px;")
        return label

    def populate_saved_settings(self):
        """Populate fields with saved settings if available."""
        if 'account_id' in self.settings:
            self.account_id_entry.setText(self.settings['account_id'])

        if 'secret_key' in self.settings:
            self.secret_key_entry.setText(self.settings['secret_key'])

        self.remember_me.setChecked(self.settings.get('remember_me', False))

    def check_network_connectivity(self):
        """Check network connectivity to the Stellar Network and update the status."""
        try:
            response = requests.get('https://horizon.stellar.org/assets')
            if response.status_code == 200:
               self.update_network_status("Connected to Stellar Network", "color: green;", True)
              
               return True
            
            else:
                self.update_network_status("Network Unreachable", "color: red;", False)
                return False
        except Exception:
            self.update_network_status("Network Unreachable", "color: red;", False)
            return False
    def update_network_status(self, message, style, connected):
        """Update the network status label."""
        self.network_status_label.setText(message)
        self.network_status_label.setStyleSheet(style)
        return connected

    def login(self):
        """Handle the login process using the provided Account ID and Secret Key."""
        account_id = self.account_id_entry.text()
        secret_key = self.secret_key_entry.text()

        if not self.is_valid_stellar_account_id(account_id):
            self.update_info_label("Invalid Stellar Network Account ID!", "red")
            return

        if not self.is_valid_stellar_secret(secret_key):
            self.update_info_label("Invalid Stellar Network Account Secret!", "red")
            return

        if not account_id or not secret_key:
            self.update_info_label("Both Account ID and Secret Key are required!", "red")
            return

        self.update_info_label("Logging in...", "green")

        # Check network connectivity before proceeding
        if not self.check_network_connectivity():
            self.update_info_label("Unable to connect to Stellar Network.", "red")
            return

        try:
            # Initialize StellarClient and navigate to Home
            self.controller.bot = StellarClient(controller=self.controller, account_id=account_id, secret_key=secret_key)
            self.save_user_settings()
            self.controller.show_frame("Home")
        except Exception as e:
            self.update_info_label(f"An error occurred: {str(e)}", "red")

    def update_info_label(self, message, color):
        """Update the info label with a message and style."""
        self.info_label.setText(message)
        self.info_label.setStyleSheet(f"color: {color};")

    def save_user_settings(self):
        """Save user settings if 'Remember Me' is checked."""
        settings = {
            'remember_me': self.remember_me.isChecked(),
            'account_id': self.account_id_entry.text() if self.remember_me.isChecked() else '',
            'secret_key': self.secret_key_entry.text() if self.remember_me.isChecked() else ''
        }
        SettingsManager.save_settings(settings)

    def create_new_account(self):
        """Generate a new Stellar account and display it in a new window."""
        new_keypair = Keypair.random()

        new_account_window = QtWidgets.QDialog(self)
        new_account_window.setWindowTitle("New Stellar Lumen's Account")
        new_account_window.setGeometry(600, 300, 600, 500)

        layout = QtWidgets.QVBoxLayout()

        title_label = QtWidgets.QLabel("Stellar Account Creation")
        title_label.setFont(QtGui.QFont("Helvetica", 16, QtGui.QFont.Bold))
        title_label.setStyleSheet("color: green;")
        layout.addWidget(title_label)

        layout.addWidget(QtWidgets.QLabel("New Account Created"))
        layout.addWidget(QtWidgets.QLabel(f"Account ID (Public Key): {new_keypair.public_key}"))

        # Generate and display a QR code
        self.display_qr_code(new_keypair.public_key, layout)

        layout.addWidget(QtWidgets.QLabel(f"Secret Key (Private Key): {new_keypair.secret}"))

        # Save to CSV button
        save_button = QtWidgets.QPushButton("Save to CSV")
        save_button.clicked.connect(lambda: self.save_account_to_csv(new_keypair.public_key, new_keypair.secret))
        layout.addWidget(save_button)

        # Close button
        close_button = QtWidgets.QPushButton("Close")
        close_button.clicked.connect(
            new_account_window.close()
        )
        layout.addWidget(close_button)

        new_account_window.setLayout(layout)
        new_account_window.exec_()

    def display_qr_code(self, public_key, layout):
        """Generate and display the QR code for the account's public key."""
        try:
            qr_code_image = qrcode.make(public_key)
            qr_code_image.save("./src/images/account_id.png")
            qr_code_pixmap = QtGui.QPixmap("./src/images/account_id.png")
            qr_label = QtWidgets.QLabel()
            qr_label.setPixmap(qr_code_pixmap)
            layout.addWidget(qr_label)
        except Exception as e:
            layout.addWidget(QtWidgets.QLabel(f"Error generating QR code: {str(e)}"))

    def save_account_to_csv(self, account_id: str, secret_key: str):
        """Save the newly created Stellar account to a CSV file."""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save New Account", "", "CSV files (*.csv)")
        if not file_path:
            return

        try:
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                if os.path.getsize(file_path) == 0:  # If file is empty, write headers
                    writer.writerow(["Account ID", "Secret Key"])
                writer.writerow([account_id, secret_key])
                QtWidgets.QMessageBox.information(self, "Saved", f"Account saved to {file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error saving account: {e}")

    def is_valid_stellar_secret(self, secret_key: str) -> bool:
        """Validate the format of a Stellar secret key."""
        return bool(re.match(r'^S[ABCDEFGHIJKLMNOPQRSTUVWXYZ234567]{55}$', secret_key))

    def is_valid_stellar_account_id(self, account_id: str) -> bool:
        """Validate the format of a Stellar account ID."""
        return bool(re.match(r'^G[A-Z2-7]{55}$', account_id))

    def toggle_password_visibility(self):
        """Toggle the visibility of the Secret Key entry field."""
        if self.secret_key_entry.echoMode() == QtWidgets.QLineEdit.Password:
            self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.password_visibility_toggle.setText("Hide")
        else:
            self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
            self.password_visibility_toggle.setText("Show")
