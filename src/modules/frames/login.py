from __future__ import annotations

import csv
import os
import re
from typing import Optional

import requests
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (
    QGridLayout, QVBoxLayout, QDialog, QLabel,
    QPushButton, QFileDialog, QMessageBox, QCheckBox, QLineEdit
)
from stellar_sdk import Keypair

from src.modules.engine.settings_manager import SettingsManager
from src.modules.engine.smart_bot import SmartBot


# ---------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------
def is_valid_stellar_secret(secret_key: str) -> bool:
    """Validate the format of a Stellar secret key."""
    return bool(re.match(r"^S[ABCDEFGHIJKLMNOPQRSTUVWXYZ234567]{55}$", secret_key))


def is_valid_stellar_account_id(account_id: str) -> bool:
    """Validate the format of a Stellar account ID."""
    return bool(re.match(r"^G[A-Z2-7]{55}$", account_id))


# ---------------------------------------------------------------------
# Custom Exception
# ---------------------------------------------------------------------
class SQLAlchemyError(Exception):
    """A custom exception for SQLAlchemy errors."""
    pass


# ---------------------------------------------------------------------
# Login Frame
# ---------------------------------------------------------------------
class Login(QtWidgets.QFrame):
    """Modern Stellar Network Login Frame with async validation."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, controller=None):
        super().__init__(parent)

        self.controller = controller
        self.bot: Optional[SmartBot] = getattr(controller, "bot", None)
        self.settings = SettingsManager.load_settings()

        # --- Widgets
        self.account_id_entry = QLineEdit(self)
        self.secret_key_entry = QLineEdit(self)
        self.password_toggle_btn = QPushButton("Show", self)
        self.remember_me = QCheckBox("Remember Me", self)
        self.login_button = QPushButton("Login", self)
        self.create_account_button = QPushButton("Create New Account", self)
        self.network_status_label = QLabel("Checking network...", self)
        self.info_label = QLabel("", self)



        self._init_ui()
        self._restore_settings()

        # Async network check
        QtCore.QTimer.singleShot(100, self._check_network_connectivity)

    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------
    def _init_ui(self) -> None:
        """Build and style the UI."""
        layout = QGridLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)
        layout.setAlignment(QtCore.Qt.AlignTop)

        title = QLabel("🔐 Stellar Network Login")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2;")
        layout.addWidget(title, 0, 0, 1, 3)

        layout.addWidget(QLabel("Account ID:"), 1, 0)
        self.account_id_entry.setPlaceholderText("Enter your Stellar Account ID")
        layout.addWidget(self.account_id_entry, 1, 1, 1, 2)

        layout.addWidget(QLabel("Secret Key:"), 2, 0)
        self.secret_key_entry.setPlaceholderText("Enter your Secret Key")
        self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.secret_key_entry, 2, 1)
        self.password_toggle_btn.clicked.connect(self._toggle_password_visibility)
        layout.addWidget(self.password_toggle_btn, 2, 2)

        layout.addWidget(self.remember_me, 3, 0)
        self.remember_me.setChecked(self.settings.get("remember_me", False))

        layout.addWidget(self.login_button, 4, 1)
        layout.addWidget(self.create_account_button, 4, 0)

        self.login_button.clicked.connect(self._login)
        self.create_account_button.clicked.connect(self._create_new_account)

        self.network_status_label.setStyleSheet("color: orange; font-size: 13px;")
        layout.addWidget(self.network_status_label, 5, 0, 1, 3)

        self.info_label.setStyleSheet("color: red; font-size: 13px;")
        layout.addWidget(self.info_label, 6, 0, 1, 3)



        self.setLayout(layout)
        self.setStyleSheet("""
            QFrame { background-color: #fafafa; border-radius: 8px; }
            QPushButton { background-color: #1976D2; color: white; padding: 6px 14px; border-radius: 6px; }
            QPushButton:hover { background-color: #2196F3; }
            QLineEdit { padding: 6px; border: 1px solid #ccc; border-radius: 4px; }
        """)

    # ------------------------------------------------------------------
    # Restore Saved Settings
    # ------------------------------------------------------------------
    def _restore_settings(self) -> None:
        if acc := self.settings.get("account_id"):
            self.account_id_entry.setText(acc)
            self.controller.account_id = acc
        if key := self.settings.get("secret_key"):
            self.secret_key_entry.setText(key)
            self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)

    # ------------------------------------------------------------------
    # Network Check
    # ------------------------------------------------------------------
    def _check_network_connectivity(self) -> None:
        """Check Horizon connectivity asynchronously."""
        def _run_check():
            try:
                r = requests.get("https://horizon.stellar.org/assets", timeout=5)
                return r.status_code == 200
            except Exception:
                return False

        def _update_ui(success: bool):
            if success:
                self.network_status_label.setText("✅ Connected to Stellar Network")
                self.network_status_label.setStyleSheet("color: green;")
            else:
                self.network_status_label.setText("❌ Network Unreachable")
                self.network_status_label.setStyleSheet("color: red;")

        QtCore.QThreadPool.globalInstance().start(QtRunnableTask(_run_check, _update_ui))

    # ------------------------------------------------------------------
    # Login Logic
    # ------------------------------------------------------------------
    def _login(self) -> None:
        """Validate and log in the user."""
        account_id = self.account_id_entry.text().strip()
        secret_key = self.secret_key_entry.text().strip()

        if not is_valid_stellar_secret(secret_key):
            return self._update_info("Invalid Stellar Secret Key!", "red")
        if not is_valid_stellar_account_id(account_id):
            return self._update_info("Invalid Stellar Account ID!", "red")


        self._update_info("Validating credentials...", "blue")

        try:
            self._save_user_settings()
            self.controller.account_id = account_id
            self.controller.secret_key = secret_key

            self.bot = SmartBot(controller=self.controller)
            self.controller.bot = self.bot


            self._update_info("✅ Login successful!", "green")
            QtCore.QTimer.singleShot(800, lambda: self.controller.show_frame("Home"))
        except Exception as e:
            self._update_info(f"❌ Login failed: {e}", "red")

    # ------------------------------------------------------------------
    # Account Creation
    # ------------------------------------------------------------------
    def _create_new_account(self) -> None:
        """Generate a new Stellar account and display a dialog."""
        kp = Keypair.random()
        dialog = QDialog(self)
        dialog.setWindowTitle("New Stellar Account")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("🎉 New Stellar Account Created"))
        layout.addWidget(QLabel(f"Account ID: {kp.public_key}"))
        layout.addWidget(QLabel(f"Secret Key: {kp.secret}"))

        save_btn = QPushButton("💾 Save to CSV")
        save_btn.clicked.connect(lambda: self._save_account_to_csv(kp.public_key, kp.secret))
        layout.addWidget(save_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def _save_account_to_csv(self, account_id: str, secret_key: str) -> None:
        """Save generated Stellar keys to a CSV file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Account", "", "CSV Files (*.csv)")
        if not file_path:
            return

        try:
            is_new = not os.path.exists(file_path)
            with open(file_path, "a", newline="") as f:
                writer = csv.writer(f)
                if is_new:
                    writer.writerow(["Account ID", "Secret Key"])
                writer.writerow([account_id, secret_key])
            QMessageBox.information(self, "Saved", f"✅ Account saved to:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving file:\n{e}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _save_user_settings(self) -> None:
        """Persist settings if Remember Me is checked."""
        remember = self.remember_me.isChecked()
        data = {
            "remember_me": remember,
            "account_id": self.account_id_entry.text() if remember else "",
            "secret_key": self.secret_key_entry.text() if remember else "",
        }
        SettingsManager.save_settings(data)

    def _toggle_password_visibility(self) -> None:
        """Show/Hide the secret key."""
        if self.secret_key_entry.echoMode() == QtWidgets.QLineEdit.Password:
            self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.password_toggle_btn.setText("Hide")
        else:
            self.secret_key_entry.setEchoMode(QtWidgets.QLineEdit.Password)
            self.password_toggle_btn.setText("Show")

    def _update_info(self, text: str, color: str = "black") -> None:
        """Display status message."""
        self.info_label.setText(text)
        self.info_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px;")


# ---------------------------------------------------------------------
# Simple thread utility for non-blocking network checks
# ---------------------------------------------------------------------
class QtRunnableTask(QtCore.QRunnable):
    """Run a background task and update UI callback."""

    def __init__(self, func, callback):
        super().__init__()
        self.func = func
        self.callback = callback

    def run(self):
        result = self.func()
        QtCore.QMetaObject.invokeMethod(
            self.callback.__self__, self.callback.__name__,
            QtCore.Qt.QueuedConnection, QtCore.Q_ARG(bool, result)
        )
