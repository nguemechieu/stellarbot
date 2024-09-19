import os
import re
import csv
import requests
from PyQt5 import QtGui, QtWidgets
from stellar_sdk import Keypair
from modules.classes.settings_manager import SettingsManager
from modules.classes.stellar_client import StellarClient

class Login(QtWidgets.QWidget):
    """A professional Stellar Network User Login Interface using PyQt5."""

    def __init__(self, parent=None, controller=None):
        """Initialize the Login widget and set up the UI."""
        super().__init__(parent)
        self.controller = controller
        self.settings = SettingsManager.load_settings()
        self.setup_ui()
        self.populate_saved_settings()

    def setup_ui(self):    # sourcery skip: class-extract-method
        """Set up the layout, styling, and widgets."""
        self.setWindowTitle("StellarBot Login")
        self.setGeometry(0, 0, 1530, 780)
        self.setStyleSheet("background-color: #f0f0f0;")
        layout = QtWidgets.QVBoxLayout(self)

        self._extracted_from_setup_ui_9("Welcome to StellarBot", 23, layout)
        self._extracted_from_setup_ui_9("Stellar Network Login", 16, layout)
        # Account ID Entry
        layout.addWidget(self.create_label("Account ID"))
        self.account_id_entry = QtWidgets.QLineEdit(self)
        self.account_id_entry.setPlaceholderText("Enter your Stellar Account ID")
        layout.addWidget(self.account_id_entry)

        # Secret Key Entry
        layout.addWidget(self.create_label("Secret Key"))
        self.secret_key_entry = QtWidgets.QLineEdit(self)
        self.secret_key_entry.setPlaceholderText("Enter your Secret Key")
        self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.secret_key_entry)

        # Toggle Password Visibility
        self.password_visibility_toggle = QtWidgets.QPushButton("Show", self)
        self.password_visibility_toggle.clicked.connect(self.toggle_password_visibility)
        layout.addWidget(self.password_visibility_toggle)

        # Login Button
        self.login_button = QtWidgets.QPushButton("Login", self)
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        # Create New Account Button
        self.create_account_button = QtWidgets.QPushButton("Create New Account", self)
        self.create_account_button.setStyleSheet("background-color: #2196F3; color: white; font-size: 14px;")
        self.create_account_button.clicked.connect(self.create_new_account)
        layout.addWidget(self.create_account_button)

        # Remember Me Checkbox
        self.remember_me = QtWidgets.QCheckBox("Remember Me", self)
        layout.addWidget(self.remember_me)

        # Network Connectivity Status
        self.network_status_label = QtWidgets.QLabel("Checking network status...", self)
        layout.addWidget(self.network_status_label)
        self.check_network_connectivity()

        # Info Label for displaying messages
        self.info_label = QtWidgets.QLabel("", self)
        layout.addWidget(self.info_label)

    # TODO Rename this here and in `setup_ui`
    def _extracted_from_setup_ui_9(self, arg0, arg1, layout):
        # Application Name
        app_name_label = QtWidgets.QLabel(arg0, self)
        app_name_label.setFont(QtGui.QFont("Helvetica", arg1, QtGui.QFont.Bold))

        layout.addWidget(app_name_label)
        layout.addSpacing(20)

    def create_label(self, text):
        """Create a standardized label for fields."""
        label = QtWidgets.QLabel(text, self)
        label.setStyleSheet("font-size: 14px; color: #1c1c1c;")
        return label

    def populate_saved_settings(self):
        """Populate fields with saved account ID and secret key if available."""
        if 'account_id' in self.settings:
            self.account_id_entry.setText(self.settings['account_id'])
        if 'secret_key' in self.settings:
            self.secret_key_entry.setText(self.settings['secret_key'])
        self.remember_me.setChecked(self.settings.get('remember_me', False))

    def check_network_connectivity(self):
        """Check network connectivity to the Stellar Network."""
        try:
            response = requests.get('https://horizon.stellar.org/assets')
            if response.status_code == 200:
                self.update_network_status("Connected to Stellar Network", "color: green;")
                return True
            else:
                self.update_network_status("Network Unreachable", "color: red;")
                return False
        except requests.RequestException:
            self.update_network_status("Network Unreachable", "color: red;")
            return False

    def update_network_status(self, message, style):
        """Update the network status label."""
        self.network_status_label.setText(message)
        self.network_status_label.setStyleSheet(style)

    def login(self):
        """Handle login logic and validate the Stellar account credentials."""
        account_id = self.account_id_entry.text()
        secret_key = self.secret_key_entry.text()

        if not self.is_valid_stellar_account_id(account_id):
            self.update_info_label("Invalid Stellar Network Account ID!", "red")
            return

        if not self.is_valid_stellar_secret(secret_key):
            self.update_info_label("Invalid Stellar Network Secret!", "red")
            return

        if not self.check_network_connectivity():
            self.update_info_label("Unable to connect to Stellar Network.", "red")
            return

        try:
            # Initialize the Stellar client and transition to Home frame
            self.controller.bot = StellarClient(controller=self.controller, account_id=account_id, secret_key=secret_key)
            self.save_user_settings()
            self.controller.show_frame("Home")
        except Exception as e:
            self.update_info_label(f"An error occurred: {str(e)}", "red")

    def save_user_settings(self):
        """Save user settings if 'Remember Me' is checked."""
        settings = {
            'remember_me': self.remember_me.isChecked(),
            'account_id': self.account_id_entry.text() if self.remember_me.isChecked() else '',
            'secret_key': self.secret_key_entry.text() if self.remember_me.isChecked() else ''
        }
        SettingsManager.save_settings(settings)

    def create_new_account(self):
        """Generate a new Stellar account and display the details."""
        new_keypair = Keypair.random()
        new_account_window = QtWidgets.QDialog(self)
        new_account_window.setWindowTitle("New Stellar Account")
        layout = QtWidgets.QVBoxLayout(new_account_window)

        title_label = QtWidgets.QLabel("New Stellar Account Created", new_account_window)
        title_label.setFont(QtGui.QFont("Helvetica", 16, QtGui.QFont.Bold))
        title_label.setStyleSheet("color: #1c1c1c;")
        layout.addWidget(title_label)

        layout.addWidget(QtWidgets.QLabel(f"Account ID (Public Key): {new_keypair.public_key}", new_account_window))
        layout.addWidget(QtWidgets.QLabel(f"Secret Key (Private Key): {new_keypair.secret}", new_account_window))

        save_button = QtWidgets.QPushButton("Save to CSV", new_account_window)
        save_button.clicked.connect(lambda: self.save_account_to_csv(new_keypair.public_key, new_keypair.secret))
        layout.addWidget(save_button)

        close_button = QtWidgets.QPushButton("Close", new_account_window)
        close_button.clicked.connect(new_account_window.close)
        layout.addWidget(close_button)

        new_account_window.setLayout(layout)
        new_account_window.exec_()

    def save_account_to_csv(self, account_id, secret_key):
        """Save the new Stellar account to a CSV file."""
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save New Account", "", "CSV Files (*.csv)")
        if file_path:
            try:
                with open(file_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    if os.path.getsize(file_path) == 0:  # Add header if file is empty
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

    def update_info_label(self, message, color):
        """Update the info label with a message and style."""
        self.info_label.setText(message)
        self.info_label.setStyleSheet(
            f"color: {color};"
            "font-size: 14px;"
            "margin-top: 10px;"
            "margin-bottom: 10px;")
