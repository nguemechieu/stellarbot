import sys
import logging
import traceback
from typing import Optional

import pandas as pd
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QMessageBox,
    QSystemTrayIcon, QMenu, QWidget, QTextEdit, QPushButton, QLabel
)
from PySide6.QtGui import QIcon

# Local imports
from src.modules.engine.db_manager import DatabaseManager
from src.modules.engine.settings_manager import SettingsManager
from src.modules.frames.about import About
from src.modules.frames.help import Help
from src.modules.frames.home import Home
from src.modules.frames.login import Login
from src.modules.frames.preferences import Preferences
from src.modules.frames.theme_manager import ThemeManager
from src.modules.engine.smart_bot import SmartBot  # ← integrate trading engine


# ============================================================
# Global Exception Hook
# ============================================================
def exception_hook(exc_type, exc_value, exc_traceback):
    """Global error handler for uncaught exceptions."""
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
    """Background worker using signals."""
    finished = QtCore.Signal(object)
    error = QtCore.Signal(Exception)

    def __init__(self, fn):
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
# Main Application
# ============================================================
class StellarBot(QMainWindow):
    """Main application controller and window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("StellarBot")
        self.setWindowIcon(QIcon("stellarbot.ico"))
        self.setGeometry(100, 100, 1550, 850)

        # --------------------------------------------------------
        # Logger setup
        # --------------------------------------------------------
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("StellarBot")
        self.settingManager=SettingsManager()
        self.settingManager.load_settings()
        self.liquidity_df=pd.DataFrame()



        # --------------------------------------------------------
        # Core attributes
        # --------------------------------------------------------
        self.db = None
        self.bot: Optional[SmartBot] = None
        self.server_msg = {"status": "OFF", "message": "", "info": "", "error": ""}
        self.controller = self
        self.current_frame: Optional[QWidget] = None
        self.tray_icon = None

        # Account placeholders
        self.account_id = ""
        self.secret_key = ""

        # --------------------------------------------------------
        # UI initialization
        # --------------------------------------------------------
        self._init_tray_icon()
        self._init_async_db()
        self._init_console_panel()

    # ============================================================
    # Database Setup
    # ============================================================
    def _init_async_db(self):
        thread = QtCore.QThread()
        worker = Worker(self._setup_database)
        worker.moveToThread(thread)
        worker.finished.connect(self._on_db_ready)
        thread.started.connect(worker.run)
        thread.start()

    def _setup_database(self):
        try:
            dbm = DatabaseManager("StellarBot.db")
            db = dbm.db
            db.execute("""
                       CREATE TABLE IF NOT EXISTS assets (
                                                             id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                             asset_code TEXT NOT NULL,
                                                             asset_issuer TEXT NOT NULL,
                                                             image TEXT DEFAULT 'default.png'
                       )""")
            db.execute("""
                       CREATE TABLE IF NOT EXISTS ohlcv_data (
                                                                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                 account_id TEXT NOT NULL,
                                                                 open_time TEXT NOT NULL,
                                                                 close_time TEXT NOT NULL,
                                                                 low TEXT NOT NULL,
                                                                 high TEXT NOT NULL,
                                                                 close TEXT NOT NULL,
                                                                 volume TEXT NOT NULL
                       )""")
            db.commit()
            return db
        except Exception as e:
            logging.error(f"Database setup failed: {e}", exc_info=True)
            return None

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
        tray_menu = QMenu()
        tray_menu.addAction("Show", self.show)
        tray_menu.addAction("Start Bot", self.start_bot)
        tray_menu.addAction("Stop Bot", self.stop_bot)
        tray_menu.addSeparator()
        tray_menu.addAction("Exit", self.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # ============================================================
    # Console Log Panel (bottom of window)
    # ============================================================
    def _init_console_panel(self):
        console_widget = QWidget()
        layout = QVBoxLayout()

        self.console_log = QTextEdit()
        self.console_log.setReadOnly(True)
        self.console_log.setStyleSheet("background-color:#1E1E1E; color:#00FF90;")
        layout.addWidget(QLabel("📊 Bot Console Log:"))
        layout.addWidget(self.console_log)

        self.start_button = QPushButton("▶ Start Trading Bot")
        self.start_button.clicked.connect(self.start_bot)
        self.stop_button = QPushButton("⏹ Stop Bot")
        self.stop_button.clicked.connect(self.stop_bot)
        self.backtest_button = QPushButton("🧠 Run Backtest")
        self.backtest_button.clicked.connect(self.run_backtest)

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.backtest_button)

        console_widget.setLayout(layout)
        self.setCentralWidget(console_widget)

    # ============================================================
    # Bot Control
    # ============================================================
    def start_bot(self):
        """Start the SmartBot trading loop."""
        try:
            if not self.account_id or not self.secret_key:
                self.show_error("Please log in or set Stellar account credentials.")
                return

            if self.bot and self.bot.running:
                self.logger.warning("Bot already running.")
                return

            self.bot = SmartBot(controller=self, test_mode=True)
            self.bot.start()
            self.notify("SmartBot started successfully.")
            self._log_to_console("🚀 SmartBot started successfully.")

        except Exception as e:
            self.show_error(f"Error starting bot: {e}")
            self._log_to_console(f"❌ Error starting bot: {e}")

    def stop_bot(self):
        """Stop bot execution."""
        try:
            if self.bot and self.bot.running:
                self.bot.stop()
                self.notify("SmartBot stopped.")
                self._log_to_console("🛑 SmartBot stopped.")
            else:
                self._log_to_console("Bot not running.")
        except Exception as e:
            self.show_error(f"Error stopping bot: {e}")

    def run_backtest(self):
        """Run a sample backtest from UI."""
        try:
            if not self.bot:
                self.bot = SmartBot(self, test_mode=True)
            base = self.bot.selling
            quote = self.bot.buying
            results = self.bot.backtest(base, quote, days=5)
            self._log_to_console(f"🧠 Backtest Results: {results}")
            self.notify(f"Backtest completed. ROI: {results['roi']:.2f}%")
        except Exception as e:
            self.show_error(f"Backtest failed: {e}")

    # ============================================================
    # Frame Management
    # ============================================================
    def show_frame(self, name: str):
        frames = {
            "Login": Login,
            "Home": Home,
            "Preferences": Preferences,
            "Help": Help,
            "About": About
        }
        frame_class = frames.get(name)
        if not frame_class:
            self.show_error(f"Unknown frame: {name}")
            return

        if self.current_frame:
            self.current_frame.deleteLater()

        frame = frame_class(self, self.controller)
        self.setCentralWidget(frame)
        self.current_frame = frame
        self.logger.info(f"Switched to frame: {name}")
        frame.update()
        self.show()

    # ============================================================
    # Error Handling
    # ============================================================
    def show_error(self, msg: str):
        self.logger.error(msg)
        QtCore.QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Error", msg))

    def _log_to_console(self, message: str):
        """Append log message to UI console."""
        self.console_log.append(f"{QtCore.QDateTime.currentDateTime().toString('hh:mm:ss')} - {message}")

    def notify(self, message: str, title="StellarBot"):
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information)

    # ============================================================
    # Clean Exit
    # ============================================================
    def closeEvent(self, event: QtGui.QCloseEvent):
        self.logger.info("Shutting down StellarBot...")
        if self.bot and self.bot.running:
            self.bot.stop()
        if self.db:
            try:
                self.db.close()
            except Exception:
                pass
        if self.tray_icon:
            self.tray_icon.hide()
        super().closeEvent(event)


# ============================================================
# Entry Point
# ============================================================
if __name__ == "__main__":
    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    theme_manager = ThemeManager(app)
    theme_manager.apply_theme("style")

    try:
        window = StellarBot()
        window.showMaximized()
        app.exec()
    except Exception as e:
        exception_hook(type(e), e, traceback.format_exc())
        sys.exit(1)
