<<<<<<< Updated upstream
=======
"""
Beautiful Modern Login Frame for StellarBot
Clean, simple design with improved framing and user experience
"""

from __future__ import annotations

>>>>>>> Stashed changes
import csv
import os
import re
import requests
<<<<<<< Updated upstream
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QProgressBar, QGridLayout
=======
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import (
    QGridLayout, QVBoxLayout, QHBoxLayout, QDialog, QLabel, QFrame,
    QPushButton, QFileDialog, QMessageBox, QCheckBox, QLineEdit, QWidget, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QCursor
>>>>>>> Stashed changes
from stellar_sdk import Keypair

from src.modules.engine.settings_manager import SettingsManager
from src.modules.engine.smart_bot import SmartBot

try:
    from src.modules.frames.modern_ui import (
        ModernButton, ModernInput, ModernCard, ModernHeader
    )
    MODERN_UI_AVAILABLE = True
except ImportError:
    MODERN_UI_AVAILABLE = False


<<<<<<< Updated upstream
class SQLAlchemyError(Exception):
    """A custom exception for SQLAlchemy errors."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    pass


=======
>>>>>>> Stashed changes
def is_valid_stellar_secret(secret_key: str) -> bool:
    """Validate the format of a Stellar secret key."""
    return bool(re.match(r'^S[ABCDEFGHIJKLMNOPQRSTUVWXYZ234567]{55}$', secret_key))


def is_valid_stellar_account_id(account_id: str) -> bool:
    """Validate the format of a Stellar account ID."""
    return bool(re.match(r'^G[A-Z2-7]{55}$', account_id))


<<<<<<< Updated upstream
class Login(QtWidgets.QFrame):
    """A professional Stellar Network User Login Interface using PyQt5."""

    def __init__(self, parent=None, controller=None):
        """Initialize the Login widget and set up the UI."""
=======
class SQLAlchemyError(Exception):
    """A custom exception for SQLAlchemy errors."""
    pass


class Login(QFrame):
    """Beautiful Modern Stellar Network Login Frame - Simple & Clean Design"""

    def __init__(self, parent: Optional[QWidget] = None, controller=None):
>>>>>>> Stashed changes
        super().__init__(parent)

        self.bot = controller.bot
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

<<<<<<< Updated upstream
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
        self.grid_layout.addWidget(self.background_image, 60, 400)
        # Secret Key Entry
        layout.addWidget(self.create_label("Secret Key"), 2, 0)
        self.secret_key_entry.setPlaceholderText("Enter your Secret Key")
        self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.secret_key_entry, 2, 1)

        # Toggle Password Visibility layout.addWidget(self.create_label("Account ID"), 1, 0)
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
=======
        # Initialize widgets
        self.account_id_entry = None
        self.secret_key_entry = None
        self.password_toggle_btn = None
        self.remember_me = None
        self.login_button = None
        self.create_account_button = None
        self.network_status_label = None
        self.info_label = None

        self._init_ui()
        self._restore_settings()

        # Async network check
        QtCore.QTimer.singleShot(100, self._check_network_connectivity)

    # ==================================================================
    # BEAUTIFUL UI SETUP
    # ==================================================================
    def _init_ui(self) -> None:
        """Build beautiful modern UI with clean design."""
        self.setStyleSheet("""
            QFrame {
                background-color: #0F1419;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ============================================================
        # Header Section - Clean and Minimal
        # ============================================================
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 40, 0, 30)
        header_layout.setSpacing(8)

        # Logo/Title
        title = QLabel("🌟 StellarBot")
        title_font = QFont("Segoe UI", 32, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #00D4FF; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Stellar Network Trading Dashboard")
        subtitle_font = QFont("Segoe UI", 12)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #B0BEC5;")
        subtitle.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle)

        header_widget.setLayout(header_layout)
        main_layout.addWidget(header_widget)

        # ============================================================
        # Scrollable Content Area
        # ============================================================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #0F1419;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #16213E;
                border-radius: 6px;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background-color: #00D4FF;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #00E7FF;
            }
        """)

        # Container for centering
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 40)
        container_layout.setSpacing(20)
        container_layout.addStretch()

        # ============================================================
        # Beautiful Login Card
        # ============================================================
        card_widget = QWidget()
        card_widget.setMaximumWidth(420)
        card_widget.setMinimumWidth(360)
        
        # Clean card styling - subtle border, rounded corners
        card_widget.setStyleSheet("""
            QWidget {
                background-color: #16213E;
                border: 1px solid rgba(0, 212, 255, 0.15);
                border-radius: 16px;
            }
        """)

        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(18)

        # Account ID Input
        account_label = QLabel("Account ID")
        account_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        account_label.setStyleSheet("color: #FFFFFF; margin-bottom: 6px;")
        card_layout.addWidget(account_label)

        self.account_id_entry = QLineEdit()
        self.account_id_entry.setPlaceholderText("Enter your Stellar Account ID...")
        self.account_id_entry.setStyleSheet(self._get_input_stylesheet())
        self.account_id_entry.setMinimumHeight(44)
        self.account_id_entry.setFont(QFont("Segoe UI", 11))
        card_layout.addWidget(self.account_id_entry)

        # Secret Key Input
        secret_label = QLabel("Secret Key")
        secret_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        secret_label.setStyleSheet("color: #FFFFFF; margin-bottom: 6px; margin-top: 12px;")
        card_layout.addWidget(secret_label)

        secret_container = QHBoxLayout()
        secret_container.setContentsMargins(0, 0, 0, 0)
        secret_container.setSpacing(8)

        self.secret_key_entry = QLineEdit()
        self.secret_key_entry.setPlaceholderText("Enter your Secret Key...")
        self.secret_key_entry.setEchoMode(QLineEdit.Password)
        self.secret_key_entry.setStyleSheet(self._get_input_stylesheet())
        self.secret_key_entry.setMinimumHeight(44)
        self.secret_key_entry.setFont(QFont("Segoe UI", 11))
        secret_container.addWidget(self.secret_key_entry)

        self.password_toggle_btn = QPushButton("👁")
        self.password_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 212, 255, 0.1);
                color: #00D4FF;
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 212, 255, 0.2);
            }
            QPushButton:pressed {
                background-color: rgba(0, 212, 255, 0.15);
            }
        """)
        self.password_toggle_btn.setMaximumWidth(50)
        self.password_toggle_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.password_toggle_btn.clicked.connect(self._toggle_password_visibility)
        secret_container.addWidget(self.password_toggle_btn)

        card_layout.addLayout(secret_container)

        # Remember Me Checkbox
        self.remember_me = QCheckBox("Remember me on this device")
        self.remember_me.setStyleSheet("""
            QCheckBox {
                color: #B0BEC5;
                font-size: 11px;
                spacing: 6px;
                margin-top: 12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background-color: rgba(0, 212, 255, 0.1);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #00D4FF;
                border: 1px solid #00D4FF;
                border-radius: 4px;
            }
            QCheckBox:hover {
                color: #FFFFFF;
            }
        """)
        self.remember_me.setChecked(self.settings.get("remember_me", False))
        card_layout.addWidget(self.remember_me)

        # Status/Info Labels
        self.network_status_label = QLabel("🔄 Checking network...")
        self.network_status_label.setStyleSheet("color: #FFA726; font-size: 11px; font-weight: 500;")
        self.network_status_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.network_status_label)

        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #EF5350; font-size: 11px; margin-top: 4px;")
        self.info_label.setWordWrap(True)
        self.info_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.info_label)

        card_layout.addSpacing(12)

        # Beautiful Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.create_account_button = QPushButton("➕ Create Account")
        self.create_account_button.setStyleSheet(self._get_secondary_button_stylesheet())
        self.create_account_button.setMinimumHeight(44)
        self.create_account_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.create_account_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.create_account_button.clicked.connect(self._create_new_account)
        button_layout.addWidget(self.create_account_button)

        self.login_button = QPushButton("🚀 Login")
        self.login_button.setStyleSheet(self._get_primary_button_stylesheet())
        self.login_button.setMinimumHeight(44)
        self.login_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.login_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_button.clicked.connect(self._login)
        button_layout.addWidget(self.login_button)

        card_layout.addLayout(button_layout)
        card_layout.addStretch()
>>>>>>> Stashed changes

        container_layout.addWidget(card_widget)
        container_layout.addStretch()

<<<<<<< Updated upstream
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
            self.controller.account_id = self.account_id_entry.text()
        if 'secret_key' in self.settings:
            self.secret_key_entry.setText(self.settings['secret_key'])
            self.controller.account_id = self.account_id_entry.text()
            self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
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
            self.controller.account_id = self.settings['account_id']
            self.controller.secret_key = self.settings['secret_key']
            self.controller.logger.info(f"User {self.account_id_entry.text()} logged in.")
            self.bot = SmartBot(controller=self.controller)

            if self.bot is not None:

             self.controller.bot = self.bot




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
        self.settings = {
            'remember_me': self.remember_me.isChecked(),
            'account_id': self.account_id_entry.text() if self.remember_me.isChecked() else '',
            'secret_key': self.secret_key_entry.text() if self.remember_me.isChecked() else '',
            "telegram_token": self.controller.telegram_token,
            "chat_id": self.controller.chat_id
        }
        SettingsManager.save_settings(self.settings)

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

            self.account_id = self.controller.bot.account_id
=======
        scroll.setWidget(container)
        main_layout.addWidget(scroll, 1)
        self.setLayout(main_layout)

    # ==================================================================
    # STYLING METHODS
    # ==================================================================
    @staticmethod
    def _get_input_stylesheet() -> str:
        """Get stylesheet for input fields."""
        return """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 8px;
                padding: 10px 14px;
                color: #FFFFFF;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #00D4FF;
                background-color: rgba(0, 212, 255, 0.08);
            }
            QLineEdit::placeholder {
                color: rgba(176, 190, 197, 0.6);
            }
        """

    @staticmethod
    def _get_primary_button_stylesheet() -> str:
        """Get stylesheet for primary button (Login)."""
        return """
            QPushButton {
                background-color: #00D4FF;
                color: #0F1419;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00E7FF;
            }
            QPushButton:pressed {
                background-color: #00B8D4;
            }
            QPushButton:disabled {
                background-color: rgba(0, 212, 255, 0.3);
                color: rgba(15, 20, 25, 0.5);
            }
        """

    @staticmethod
    def _get_secondary_button_stylesheet() -> str:
        """Get stylesheet for secondary button (Create Account)."""
        return """
            QPushButton {
                background-color: rgba(0, 212, 255, 0.15);
                color: #00D4FF;
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 212, 255, 0.25);
                border: 1px solid rgba(0, 212, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(0, 212, 255, 0.2);
            }
            QPushButton:disabled {
                background-color: rgba(0, 212, 255, 0.08);
                color: rgba(0, 212, 255, 0.4);
            }
        """

    # ==================================================================
    # INTERACTIONS
    # ==================================================================
    def _toggle_password_visibility(self) -> None:
        """Toggle password field visibility."""
        if self.secret_key_entry.echoMode() == QLineEdit.Password:
            self.secret_key_entry.setEchoMode(QLineEdit.Normal)
            self.password_toggle_btn.setText("👁‍🗨")
        else:
            self.secret_key_entry.setEchoMode(QLineEdit.Password)
            self.password_toggle_btn.setText("👁")

    def _check_network_connectivity(self) -> None:
        """Check Stellar network connectivity."""
        try:
            response = requests.get("https://horizon.stellar.org", timeout=3)
            if response.status_code == 200:
                self.network_status_label.setText("✅ Network Connected")
                self.network_status_label.setStyleSheet("color: #00E676; font-size: 11px; font-weight: 500;")
                return
        except Exception:
            pass

        self.network_status_label.setText("⚠️ Network Issues - Check connection")
        self.network_status_label.setStyleSheet("color: #FFA726; font-size: 11px; font-weight: 500;")

    def _login(self) -> None:
        """Handle login button click."""
        account_id = self.account_id_entry.text().strip()
        secret_key = self.secret_key_entry.text().strip()

        if not account_id:
            self.info_label.setText("⚠️ Please enter your Account ID")
            return

        if not secret_key:
            self.info_label.setText("⚠️ Please enter your Secret Key")
            return

        if not is_valid_stellar_account_id(account_id):
            self.info_label.setText("❌ Invalid Account ID format")
            return

        if not is_valid_stellar_secret(secret_key):
            self.info_label.setText("❌ Invalid Secret Key format")
            return

        # Proceed with login (no settings saved)
        self.info_label.setText("✅ Login successful!")
        self.info_label.setStyleSheet("color: #00E676; font-size: 11px;")
>>>>>>> Stashed changes

        # Call controller's login
        if self.controller and hasattr(self.controller, "show_frame"):
            QtCore.QTimer.singleShot(500, lambda: self.controller.show_frame("Home"))

<<<<<<< Updated upstream
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
=======
    def _create_new_account(self) -> None:
        """Handle create account button click."""
        # Generate new keypair
        keypair = Keypair.random()
        account_id = keypair.public_key
        secret_key = keypair.secret

        # Show info dialog
        msg = QMessageBox()
        msg.setWindowTitle("New Stellar Account Created")
        msg.setTextFormat(Qt.RichText)
        msg.setText(f"""
        <b>✅ Account Successfully Created!</b><br><br>
        <b>Account ID:</b><br>
        <code>{account_id}</code><br><br>
        <b>Secret Key (Keep Safe!):</b><br>
        <code>{secret_key}</code><br><br>
        <i>⚠️ Never share your secret key with anyone!</i>
        """)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

        # Auto-fill the login fields
        self.account_id_entry.setText(account_id)
        self.secret_key_entry.setText(secret_key)

    def _restore_settings(self) -> None:
        """Settings restoration disabled."""
        pass
>>>>>>> Stashed changes
