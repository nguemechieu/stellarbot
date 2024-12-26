import csv
import os
import re

import pandas as pd
import requests
from PyQt5 import QtGui, QtWidgets
from stellar_sdk import Keypair

from src.modules.classes.settings_manager import SettingsManager
from src.modules.classes.stellar_client import StellarClient


class SQLAlchemyError (Exception) :
    """A custom exception for SQLAlchemy errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    pass


class Login(QtWidgets.QFrame):
    """A professional Stellar Network User Login Interface using PyQt5."""

    def __init__(self, parent=None, controller=None):
        """Initialize the Login widget and set up the UI."""
        super().__init__(parent)
        self.parent = parent
        self.controller = controller


        self.account_id_entry = QtWidgets.QLineEdit(self)
        self.secret_key_entry = QtWidgets.QLineEdit(self)
        self.password_visibility_toggle = QtWidgets.QPushButton("Show", self)
        self.remember_me = QtWidgets.QCheckBox("Remember Me", self)
        self.login_button = QtWidgets.QPushButton("Login", self)
        self.create_account_button = QtWidgets.QPushButton("Create New Account", self)
        self.network_status_label = QtWidgets.QLabel("Checking network status...", self)

        self.info_label = QtWidgets.QLabel("", self)

        self.settings = SettingsManager.load_settings()
        self.setup_ui()
        self.populate_saved_settings()

    def setup_ui(self):
        """Set up the layout, styling, and widgets."""
        layout = QtWidgets.QVBoxLayout(self)

        # Application and Login labels
        self.add_title_label("Welcome to StellarBot", 23, layout)
        self.add_title_label("Stellar Network Login", 16, layout)

        # Account ID Entry
        layout.addWidget(self.create_label("Account ID"))
        self.account_id_entry.setPlaceholderText("Enter your Stellar Account ID")
        layout.addWidget(self.account_id_entry)

        # Secret Key Entry
        layout.addWidget(self.create_label("Secret Key"))
        self.secret_key_entry.setPlaceholderText("Enter your Secret Key")
        self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.secret_key_entry)

        # Toggle Password Visibility
        self.password_visibility_toggle.clicked.connect(self.toggle_password_visibility)
        layout.addWidget(self.password_visibility_toggle)

        # Login Button
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        # Create New Account Button
        self.create_account_button.setStyleSheet("background-color: #2196F3; color: white; font-size: 14px;")
        self.create_account_button.clicked.connect(self.create_new_account)
        layout.addWidget(self.create_account_button)

        # Remember Me Checkbox
        layout.addWidget(self.remember_me)

        # Network Connectivity Status
        layout.addWidget(self.network_status_label)
        self.check_network_connectivity()

        # Info Label for displaying messages
        layout.addWidget(self.info_label)

    def add_title_label(self, text, font_size, layout):
        """Add a title label to the layout."""
        label = QtWidgets.QLabel(text, self)
        label.setFont(QtGui.QFont("Helvetica", font_size, QtGui.QFont.Bold))
        layout.addWidget(label)
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
        self.controller.account_id = account_id
        self.controller.secret_key = secret_key

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
            self.controller.bot = StellarClient(controller=self.controller)
            self.controller.assets_info = self.controller.bot.get_assets()
            pd_f=pd.DataFrame(self.controller.assets_info)
            pd_f.to_csv('stellar_assets.csv', index=False)
            # save to a database
            self.save_assets_to_database()


            self.save_user_settings()
            self.controller.show_frame("Home")
        except Exception as e:
            self.update_info_label(f"An error occurred: {str(e)}", "red")

    def save_assets_to_database(self):
      try:
        # Initialize Stellar client and fetch assets
        self.controller.bot = StellarClient(controller=self.controller)
        self.controller.assets_info = self.controller.bot.get_assets()

        # Convert asset info to a DataFrame
        assets_df = pd.DataFrame(self.controller.assets_info)

        # Log and save the assets information to CSV
        assets_df.to_csv('stellar_assets.csv', index=False)
        self.controller.logger.info(f"Assets saved to CSV")

        # Prepare an asset list for insertion into the database
        list_assets = [{'asset_code': asset['asset_code'], 'asset_issuer': asset['asset_issuer']} for asset in self.controller.assets_info]
        assets_for_db_df = pd.DataFrame(list_assets)

        # Save to the database in two steps (accounts and assets)
        with self.controller.db as con:
            self._save_to_db(con, assets_for_db_df, schema="accounts", table_name="stellar_assets")
            self._save_to_db(con, assets_for_db_df, schema="assets", table_name="stellar_assets")

        # Update info label and transition to Home
        self.update_info_label("Login successful!", "green")
        self.save_user_settings()
        self.controller.show_frame("Home")

      except SQLAlchemyError as db_error:
        # Handle database-specific errors
        self.update_info_label(f"Database error: {str(db_error)}", "red")
        self.controller.logger.error(f"Database error: {str(db_error)}")
      except Exception as e:
        # Catch-all for other exceptions
        self.update_info_label(f"An error occurred: {str(e)}", "red")
        self.controller.logger.error(f"Error: {str(e)}")

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
            'secret_key': self.secret_key_entry.text() if self.remember_me.isChecked() else ''
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
                    if os.path.getsize(file_path) == 0:
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
        self.info_label.setStyleSheet(f"color: {color}; font-size: 14px; margin-top: 10px; margin-bottom: 10px;")
