import csv
import os
import re

import requests
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QProgressBar, QGridLayout
from stellar_sdk import Keypair

from src.modules.classes.settings_manager import SettingsManager
from src.modules.classes.stellar_client import StellarClient


class SQLAlchemyError(Exception):
    """A custom exception for SQLAlchemy errors."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    pass


def is_valid_stellar_secret(secret_key: str) -> bool:
    """Validate the format of a Stellar secret key."""
    return bool(re.match(r'^S[ABCDEFGHIJKLMNOPQRSTUVWXYZ234567]{55}$', secret_key))


def is_valid_stellar_account_id(account_id: str) -> bool:
    """Validate the format of a Stellar account ID."""
    return bool(re.match(r'^G[A-Z2-7]{55}$', account_id))


class Login(QtWidgets.QFrame):
    """A professional Stellar Network User Login Interface using PyQt5."""

    def __init__(self, parent=None, controller=None):
        """Initialize the Login widget and set up the UI."""
        super().__init__(parent)

        self.account_id = None
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(20, 400, 200, 20)
        self.progress_bar.setValue(1)
        self.setWindowTitle("Stellar Network Login")

        self.background_image = QtWidgets.QLabel(self)
        self.background_image.setGeometry(0, 0, 600, 400)
        self.background_image.setAlignment(QtCore.Qt.AlignTop)
        self.background_image.setPixmap(QtGui.QPixmap("StellarBot.ico"))


        self.parent = parent
        self.controller = controller
        self.telegram_token = "2032573404:AAGnxJpNMJBKqLzvE5q4kGt1cCGF632bP7A"

        self.grid_layout = QGridLayout(self)

        self.account_id_entry = QtWidgets.QLineEdit(self)
        self.secret_key_entry = QtWidgets.QLineEdit(self)
        self.password_visibility_toggle = QtWidgets.QPushButton("Show", self)
        self.remember_me = QtWidgets.QCheckBox("Remember Me", self)
        self.login_button = QtWidgets.QPushButton("Login", self)
        self.create_account_button = QtWidgets.QPushButton("Create New Account", self)
        self.network_status_label = QtWidgets.QLabel("Checking network status...", self)

        self.info_label = QtWidgets.QLabel("", self)

        self.grid_layout.setRowStretch(1, 1)
        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setGeometry(200, 200, 600, 400)
        self.setLayout(self.grid_layout)

        self.settings = SettingsManager.load_settings()
        self.setup_ui()
        self.populate_saved_settings()

    def setup_ui(self):
        """Set up the layout, styling, and widgets."""
        layout = self.grid_layout

        # Introduction section
        # Account ID Entry
        layout.addWidget(self.create_label("Stellar Network Login"),
                         0,0, 1, 4)

        # Network Status Label]
        layout.addWidget(self.network_status_label, 0, 4)

        # Account ID Entry

        self.grid_layout.addWidget(self.background_image,
                                  60, 400
                            )
        # Secret Key Entry
        layout.addWidget(self.create_label("Secret Key"), 2, 0)
        self.secret_key_entry.setPlaceholderText("Enter your Secret Key")
        self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.secret_key_entry, 2, 1)

        # Toggle Password Visibilitylayout.addWidget(self.create_label("Account ID"), 1, 0)
        self.account_id_entry.setPlaceholderText("Enter your Stellar Account ID")
        layout.addWidget(self.account_id_entry, 1, 1)

        # Secret Key Entry
        layout.addWidget(self.create_label("Secret Key"), 2, 0)
        self.secret_key_entry.setPlaceholderText("Enter your Secret Key")
        self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.secret_key_entry, 2, 1)

        # Toggle Password Visibility
        self.password_visibility_toggle.clicked.connect(self.toggle_password_visibility)
        layout.addWidget(self.password_visibility_toggle, 2, 3)

        # Remember Me Checkbox
        self.remember_me.setCheckState(
            QtCore.Qt.Checked if self.settings.get('remember_me', False) else QtCore.Qt.Unchecked)
        layout.addWidget(self.remember_me, 3, 0)

        # Login Button
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button, 4, 2)

        # Create New Account Button

        self.create_account_button.clicked.connect(self.create_new_account)
        layout.addWidget(self.create_account_button, 4, 0)

        # Info Label for displaying messages
        self.info_label.setStyleSheet("color: red;")
        layout.addWidget(self.info_label, 5, 2)

        # Network Connectivity Status
        self.network_status_label.setStyleSheet("color: green;")
        layout.addWidget(self.network_status_label, 0,8)
        self.check_network_connectivity()

        # Progress Bar
        layout.addWidget(self.progress_bar, 7, 1, 1, 3)
        self.progress_bar.move(20, 380)


    def add_title_label(self, text, layout):
        """Add a title label to the layout."""
        label = QtWidgets.QLabel(text, self)
        layout.addWidget(label)
        layout.addSpacing(20)

    def create_label(self, text):
        """Create a standardized label for fields."""
        label = QtWidgets.QLabel(text, self)

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
        if not is_valid_stellar_secret(self.secret_key_entry.text()):
            self.update_progress(0, "Invalid Stellar Network Secret!")
            self.hide_progress()
            return
        if not is_valid_stellar_account_id(self.account_id_entry.text()):
            self.update_progress(0, "Invalid Stellar Network Account!")
            self.hide_progress()
            return
        if not self.check_network_connectivity():
            self.update_progress(0, "Unable to connect to Stellar Network.")
            self.hide_progress()
            return

        try:
            self.update_progress(50, "Validating credentials...")
            self.save_user_settings()
            self.update_progress(100, "Login successful!")
            self.controller.show_frame("Home")
        except Exception as e:
            self.update_progress(0, f"An error occurred: {str(e)}")
        finally:
            self.hide_progress()

    def _save_to_db(self, con, data_frame, schema, table_name):
        """Helper function to save DataFrame to the database."""
        try:
            # Save DataFrame to the specified schema and table
            data_frame.to_sql(name=table_name, con=con, schema=schema, index=False, if_exists='replace')
            self.controller.logger.info(f"Assets saved to {schema}.{table_name} table.")
        except SQLAlchemyError as db_error:
            # Log database-specific errors and re-raise them
            self.controller.logger.error(f"Error saving assets to {schema}.{table_name}: {str(db_error)}")
            raise db_error

    def save_user_settings(self):
        """Save user settings if 'Remember Me' is checked."""
        settings = {
            'remember_me': self.remember_me.isChecked(),
            'account_id': self.account_id_entry.text() if self.remember_me.isChecked() else '',
            'secret_key': self.secret_key_entry.text() if self.remember_me.isChecked() else '',
            "telegram_token": self.controller.telegram_token,
            "telegram_chat_id": self.controller.telegram_chat_id
        }
        SettingsManager.save_settings(settings)

    def create_new_account(self):
        """Generate a new Stellar account and display the details."""
        new_keypair = Keypair.random()
        new_account_window = QtWidgets.QDialog(self)
        new_account_window.setWindowTitle("New Stellar Account")
        layout = QtWidgets.QVBoxLayout(new_account_window)

        layout.addWidget(QtWidgets.QLabel("New Stellar Account Created", self))
        layout.addWidget(QtWidgets.QLabel(f"Account ID (Public Key): {new_keypair.public_key}", self))
        layout.addWidget(QtWidgets.QLabel(f"Secret Key (Private Key): {new_keypair.secret}", self))

        save_button = QtWidgets.QPushButton("Save to CSV", new_account_window)
        save_button.clicked.connect(self.save_account_to_csv(new_keypair.public_key, new_keypair.secret))
        layout.addWidget(save_button)

        close_button = QtWidgets.QPushButton("Close",   new_account_window)
        close_button.clicked.connect(new_account_window.close())
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
                    if os.path.getsize(file_path) == 0:
                        writer.writerow(["Account ID", "Secret Key"])
                    writer.writerow([account_id, secret_key])
                    QtWidgets.QMessageBox.information(self, "Saved", f"Account saved to {file_path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Error saving account: {e}")

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
        self.info_label.setStyleSheet(f"color: {color}; font-size: 14px; margin-top: 10px; margin-bottom: 10px;")

    def save_assets_to_database(self):
        """Fetch and save Stellar assets to the database."""
        try:
            # Initialize Stellar client
            self.controller.bot = StellarClient(controller=self.controller)
            self.account_id = self.controller.bot.account_id
            assets = self.controller.bot.asset_pairs  # Assuming fetch_assets is defined

            # Save to a database
            self._save_to_db(con=self.controller.database_connection, data_frame=assets, schema="public",
                             table_name="assets")

            # Update info label and transition
            self.update_info_label("Assets saved successfully!", "green")
        except SQLAlchemyError as db_error:
            self.handle_error(f"Database error: {str(db_error)}")
        except Exception as e:
            self.handle_error(f"An error occurred: {str(e)}")

    def handle_error(self, message):
        """Handle and log errors."""
        self.update_info_label(message, "red")
        self.controller.logger.error(message)

    def show_progress(self, message: str):
        """Show the progress bar and set the initial message."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.info_label.setText(message)

    def update_progress(self, value: int, message: str = ""):
        """Update the progress bar value and optional message."""
        self.progress_bar.setValue(value)
        if message:
            self.info_label.setText(message)

    def hide_progress(self):
        """Hide the progress bar."""
        self.progress_bar.setVisible(False)
