import faulthandler
import logging
import sys
import traceback
from typing import Optional, Callable

import pandas as pd
from PySide6 import QtGui, QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QMessageBox,
    QSystemTrayIcon, QMenu, QWidget, QTextEdit, QPushButton, QLabel
)

# --- Local imports ---
from src.modules.engine.db_manager import DatabaseManager
from src.modules.engine.settings_manager import SettingsManager
from src.modules.engine.smart_bot import SmartBot
from src.modules.frames import about, help, home, login, preferences
from src.modules.frames.theme_manager import ThemeManager


# ============================================================
# Global Exception Hook
# ============================================================
def exception_hook(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions globally."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    QtCore.QTimer.singleShot(0, lambda: QMessageBox.critical(
        None, "Critical Error", f"An unexpected error occurred:\n{exc_value}"
    ))


# ============================================================
# Background Worker
# ============================================================
class Worker(QtCore.QObject):
    """Generic background worker for threaded tasks."""
    finished = QtCore.Signal(object)
    error = QtCore.Signal(Exception)

    def __init__(self, fn: Callable):
        super().__init__()
        self.fn = fn

    @QtCore.Slot()
    def run(self):
        try:
            result = self.fn()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)


# ============================================================
# Utility: Database Setup
# ============================================================
def setup_database():
    """Initialize the local database and tables."""
    try:
        dbm = DatabaseManager("StellarBot.db")
        db = dbm.db
        db.executescript("""
                         CREATE TABLE IF NOT EXISTS assets (
                                                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                               asset_code TEXT NOT NULL,
                                                               asset_issuer TEXT NOT NULL,
                                                               image TEXT DEFAULT 'default.png'
                         );

                         CREATE TABLE IF NOT EXISTS ohlcv_data (
                                                                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                   account_id TEXT NOT NULL,
                                                                   open_time TEXT NOT NULL,
                                                                   close_time TEXT NOT NULL,
                                                                   low TEXT NOT NULL,
                                                                   high TEXT NOT NULL,
                                                                   close TEXT NOT NULL,
                                                                   volume TEXT NOT NULL
                         );
                         """)
        db.commit()
        return db
    except Exception as e:
        logging.error("Database setup failed", exc_info=True)
        return None


# ============================================================
# Main Application
# ============================================================
class StellarBot(QMainWindow):
    """Main GUI controller and trading orchestrator."""

    log_signal = QtCore.Signal(str)  # Thread-safe log signal

    def __init__(self):
        super().__init__()
        self.setWindowTitle("StellarBot")
        self.setWindowIcon(QIcon("stellarbot.ico"))
        self.setGeometry(100, 100, 1550, 850)

        # --- Logger ---
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("StellarBot")

        # --- Config & Data ---
        self.settings = SettingsManager()
        self.settings.load_settings()
        self.effects_df=pd.DataFrame()
        # --- DataFrames ---
        self.transaction_df = pd.DataFrame()
        self.trade_history = pd.DataFrame(columns=["symbol", "side", "amount", "price", "result", "timestamp"])
        self.accounts_balances_df = pd.DataFrame()
        self.orders_df = pd.DataFrame()
        self.effects_df = pd.DataFrame()
        self.ledger_df = pd.DataFrame()
        self.liquidity_df = pd.DataFrame()
        self.payments_df = pd.DataFrame()
        self.backtest_results = pd.DataFrame()
        self.server=None
        self.server_msg={'message':'', 'error':''}


        self.db = None
        self.bot: Optional[SmartBot] =None
        self.current_frame: Optional[QWidget] = None
        self.tray_icon: Optional[QSystemTrayIcon] = None

        self.db_thread = None
        self.db_worker = None

        self.account_id = ""
        self.secret_key = ""
        self.liquidity_df = pd.DataFrame()

        self.server_msg = {"status": "OFF", "message": "", "info": "", "error": ""}

        # --- UI setup ---
        self.log_signal.connect(self._log_to_console)
        self._init_tray_icon()
        self._init_async_db()
        self._init_console_panel()



# ============================================================
    # Database Init
    # ============================================================
    def _init_async_db(self):
        """Initialize database in background thread safely."""
        self.db_thread = QtCore.QThread(self)
        self.db_worker = Worker(setup_database)
        self.db_worker.moveToThread(self.db_thread)

        self.db_worker.finished.connect(self._on_db_ready)
        self.db_worker.error.connect(lambda e: self.show_error(f"DB Error: {e}"))
        self.db_thread.started.connect(self.db_worker.run)

        self.db_thread.start()

    def _on_db_ready(self, db):
        if not db:
            self.show_error("Failed to initialize database.")
            return
        self.db = db
        self.logger.info("✅ Database initialized successfully.")
        self.show_frame("Login")

    # ============================================================
    # Tray Icon
    # ============================================================
    def _init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon("stellarbot.ico"), self)
        menu = QMenu()
        menu.addAction("Show", self.show)
        menu.addAction("Start Bot", self.start_bot)
        menu.addAction("Stop Bot", self.stop_bot)
        menu.addSeparator()
        menu.addAction("Exit", self.close)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def notify(self, message: str, title="StellarBot"):
        """Show tray notification safely."""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information)

    # ============================================================
    # Console Panel
    # ============================================================
    def _init_console_panel(self):
        console_widget = QWidget()
        layout = QVBoxLayout(console_widget)

        self.console_log = QTextEdit(readOnly=True)
        self.console_log.setStyleSheet("background-color:#1E1E1E; color:#00FF90;")
        layout.addWidget(QLabel("📊 Bot Console Log:"))
        layout.addWidget(self.console_log)

        for text, callback in [
            ("▶ Start Trading Bot", self.start_bot),
            ("⏹ Stop Bot", self.stop_bot),
            ("🧠 Run Backtest", self.run_backtest)
        ]:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        self.setCentralWidget(console_widget)

    @QtCore.Slot(str)
    def _log_to_console(self, message: str):
        timestamp = QtCore.QDateTime.currentDateTime().toString("hh:mm:ss")
        self.console_log.append(f"{timestamp} - {message}")

    # ============================================================
    # Bot Control
    # ============================================================
    def start_bot(self):
        """Start the trading bot."""
        try:
            if not (self.account_id and self.secret_key):
                self.show_error("Please log in or set Stellar account credentials.")
                return
            if self.bot and getattr(self.bot, "running", False):
                self.logger.warning("Bot already running.")
                return

            self.bot = SmartBot(controller=self, test_mode=True)
            self.bot.start()
            self.log_signal.emit("🚀 SmartBot started successfully.")
            self.notify("SmartBot started successfully.")
        except Exception as e:
            self.show_error(f"Error starting bot: {e}")
            self.log_signal.emit(f"❌ Error starting bot: {e}")

    def stop_bot(self):
        """Stop bot safely."""
        try:
            if self.bot and getattr(self.bot, "running", False):
                self.bot.stop()
                self.notify("SmartBot stopped.")
                self.log_signal.emit("🛑 SmartBot stopped.")
            else:
                self.log_signal.emit("⚠️ Bot not running.")
        except Exception as e:
            self.show_error(f"Error stopping bot: {e}")

    def run_backtest(self):
        """Run a test simulation."""
        try:
            self.bot = self.bot or SmartBot(self, test_mode=True)
            results = self.bot.backtest(self.bot.selling, self.bot.buying, days=5)
            self.log_signal.emit(f"🧠 Backtest Results: {results}")
            self.notify(f"Backtest completed. ROI: {results['roi']:.2f}%")
        except Exception as e:
            self.show_error(f"Backtest failed: {e}")

    # ============================================================
    # Frame Management
    # ============================================================
    def show_frame(self, name: str):
        """Safely switch between frames."""
        frames = {
            "Login": login.Login,
            "Home": home.Home,
            "Preferences": preferences.Preferences,
            "Help": help.Help,
            "About": about.About,
        }
        frame_class = frames.get(name)
        if not frame_class:
            self.show_error(f"Unknown frame: {name}")
            return

        if self.current_frame:
            self.current_frame.setParent(None)
            self.current_frame.deleteLater()

        frame = frame_class(self, self)
        self.setCentralWidget(frame)
        self.current_frame = frame

        self.logger.info(f"Switched to frame: {name}")
        QtCore.QTimer.singleShot(0, frame.update)
        self.show()

    # ============================================================
    # Error & Exit
    # ============================================================
    def show_error(self, msg: str):
        self.logger.error(msg)
        QtCore.QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Error", msg))

    def closeEvent(self, event: QtGui.QCloseEvent):
        """Graceful shutdown."""
        self.logger.info("Shutting down StellarBot...")
        try:
            if self.bot and getattr(self.bot, "running", False):
                self.bot.stop()
            if self.db:
                self.db.close()
            if self.tray_icon:
                self.tray_icon.hide()
        except Exception:
            pass
        super().closeEvent(event)


# ============================================================
# Entry Point
# ============================================================
if __name__ == "__main__":
    faulthandler.enable()
    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    # Apply theme BEFORE UI
    theme = ThemeManager(app)
    theme.apply_theme("style")
    print("✅ Applied style theme")

    try:
        window = StellarBot()
        window.showMaximized()
        app.exec()
    except Exception as e:
        exception_hook(type(e), e, traceback.format_exc())
        sys.exit(1)
