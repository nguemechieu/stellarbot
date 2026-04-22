import logging
import sys
import traceback

import pandas as pd
<<<<<<< Updated upstream
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QSystemTrayIcon, QMenu, QMessageBox
=======
from PySide6 import QtGui, QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QLayout, QMainWindow, QVBoxLayout, QHBoxLayout, QMessageBox,
    QSystemTrayIcon, QMenu, QWidget, QTextEdit, QPushButton, QLabel,
    QStackedWidget, QStatusBar
)
from PySide6.QtCore import Qt
>>>>>>> Stashed changes

from src.modules.engine.db_manager import DatabaseManager
from src.modules.engine.settings_manager import SettingsManager
<<<<<<< Updated upstream
from src.modules.frames.about import About
from src.modules.frames.help import Help
from src.modules.frames.home import Home
from src.modules.frames.login import Login
from src.modules.frames.preferences import Preferences
=======
from src.modules.engine.smart_bot import SmartBot
from src.modules.frames import about, help, home, login, preferences
from src.modules.frames.theme_manager import ThemeManager
from src.modules.frames.modern_ui import (
    apply_modern_stylesheet, ModernButton, ModernCard,
    ModernMetricCard, ModernHeader, ModernStatusBar
)
>>>>>>> Stashed changes


# Global exception hook
def exception_hook(exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions and display an error dialog."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow keyboard interrupt to exit the app
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    # Optionally, you can display a message box here
    QMessageBox.critical(None, "Error", f"An unexpected error occurred:\n{exc_value}")

sys.exception = exception_hook


class StellarBot(QMainWindow):
    """Main window class for StellarBot, managing different frames and database connections."""

    def __init__(self):
        """Initialize StellarBot with database setup, UI setup, and frame management."""
        super().__init__()
<<<<<<< Updated upstream
        # https://dashboard.stellar.org/api/v2/lumens/
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
=======
        self.setWindowTitle("StellarBot - Trading Dashboard")
        self.setWindowIcon(QIcon("stellarbot.ico"))
        self.setGeometry(100, 100, 1600, 900)
        self.logger = logging.getLogger("StellarBot")
        self.logger.info("🚀 Initializing StellarBot application"
                         )
        self.layout = QVBoxLayout(self)
        self.setCentralWidget(QWidget())
        
        # Apply modern styling to entire application
        apply_modern_stylesheet(QApplication.instance())
>>>>>>> Stashed changes

        # Database and controller setup
        self.controller = self
        self.db = DatabaseManager('StellarBot.db').db
        # Initialize the bot object
        self.price = 0.05
        self.login_frame = None

        self.preferences_frame = None
        self.help_frame = None
        self.about_frame = None
        self.current_frame = None
        self.offers_df=pd.DataFrame()
        self.orders_df=pd.DataFrame()
        self.assets_df = pd.DataFrame()
        self.asset_pairs_df = pd.DataFrame()
        self.assets_balances_df = pd.DataFrame()
        self.transactions_df = pd.DataFrame()
        self.order_book = {"bids": [], "asks": []}
        self.effects_df=pd.DataFrame()
        self.assets = {}

        self.data_fetcher = None

        self.payments=None


        self.time_frame_selected = "H1"

        self.keep_running = True

        #Create the database tables assets if not already exists
        self.db.execute("""CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT CURRENT_TIMESTAMP,
            asset_code TEXT NOT NULL UNIQUE,
            asset_issuer TEXT NOT NULL UNIQUE,
                   image TEXT NOT NULL  DEFAULT 'default.png'
        )""")
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS ohlcv_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT CURRENT_TIMESTAMP,
                account_id TEXT NOT NULL,
                open_time TEXT NOT NULL,
                close_time TEXT NOT NULL,
                low TEXT NOT NULL,
                high TEXT NOT NULL,
                close TEXT NOT NULL,
                volume TEXT NOT NULL
            ) """)
        self.db.commit()
        # Initialize the bot object

        self.amount = 10
        self.server_thread = None
        self.keep_running = False
        self.server_msg = {
            "status": "Idle",
            "message": "",
            "info": "",
            "error": ""}

<<<<<<< Updated upstream
        self.chat_id = None
        self.telegram_token = None
        self.selected_strategy="FOREX NEWS"
        # Set the main window geometry and style
        self.time_frame_selected = "H1"
        # Set the main window geometry and style
        self.setGeometry(0, 0, 1530, 780)
        self.setWindowIcon(QtGui.QIcon("stellarbot.ico"))
        self.setUpdatesEnabled(True)
        self.settings_manager = SettingsManager()
        self.bot=None
        if not self.db:
            self.logger.error("Failed to connect to the database.")
            self.show_error_message("An error occurred while connecting to the database.")
=======
        # --- UI setup ---
        self.log_signal.connect(self._log_to_console)
        self._init_tray_icon()
        self._init_async_db()
        self._setup_modern_ui()



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
>>>>>>> Stashed changes
            return

        # Set up the central widget layout and add the desired frames
        self.central_widget = self
        self.main_layout = QVBoxLayout(self.central_widget)
        self.central_widget.setLayout(self.main_layout)

        # Create database tables if necessary
        self.setup_database()
        self.init_ui()

    def setup_database(self):
        """Create necessary database tables if they don't exist."""
        try:
            self.db.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                account_id VARCHAR(255) NOT NULL UNIQUE,
                                account_secret VARCHAR(255) NOT NULL UNIQUE,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
            self.db.commit()
        except Exception as ex:
            self.logger.error(f"Database error: {ex}")
            self.show_error_message("An error occurred while setting up the database.")

    def init_ui(self):
        """Initialize the UI by showing the login page."""
        self.show_frame("Login")

<<<<<<< Updated upstream
    def show_frame(self, page_name):
        """Switch between different application frames (Login, Home, Settings, etc.)."""
        frame_classes = {
            'Login': Login,
            'Home': Home,
            'Preferences': Preferences,
            "Settings": SettingsManager,
            'Help': Help,
            'About': About
        }

        self.delete_frame()  # Clear the current central widget
        self.setWindowTitle(f"StellarBot - {page_name}")
        frame_class = frame_classes.get(page_name)
=======
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
    # Modern UI Setup
    # ============================================================
    def _setup_modern_ui(self):
        """Setup modern UI with stacked widget for frame navigation"""
        # Create central widget with modern layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = ModernHeader("StellarBot", "Stellar DEX Trading Dashboard")
        main_layout.addWidget(header)
        
        # Content area with stacked widget
        self.stacked_widget = QStackedWidget()
        
        # Console panel (initial screen)
        console_panel = self._create_console_panel()
        self.stacked_widget.addWidget(console_panel)
        
        main_layout.addWidget(self.stacked_widget, 1)
        
        # Modern status bar
        self.status_bar = ModernStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.set_status("Ready", "success")
        
        self.setCentralWidget(central_widget)
    
    def _create_console_panel(self) -> QWidget:
        """Create modern console and control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Console card
        console_card = ModernCard("🤖 Bot Console")
        self.console_log = QTextEdit(readOnly=True)
        self.console_log.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0a0e27;
                color: #00ff88;
                border: 1px solid #2c3e50;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 12px;
            }}
        """)
        console_card.add_content(self.console_log)
        layout.addWidget(console_card, 1)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        
        start_btn = ModernButton(
            "▶ Start Trading Bot",
            ModernButton.ButtonStyle.SUCCESS,
            callback=self.start_bot
        )
        controls_layout.addWidget(start_btn)
        
        stop_btn = ModernButton(
            "⏹ Stop Bot",
            ModernButton.ButtonStyle.DANGER,
            callback=self.stop_bot
        )
        controls_layout.addWidget(stop_btn)
        
        backtest_btn = ModernButton(
            "🧠 Run Backtest",
            ModernButton.ButtonStyle.PRIMARY,
            callback=self.run_backtest
        )
        controls_layout.addWidget(backtest_btn)
        
        layout.addLayout(controls_layout)
        
        return panel

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
            # Check if we have Stellar credentials
            if not (self.account_id and self.secret_key):
                self.show_error("❌ Stellar account credentials not configured.\n\nPlease:\n1. Set STELLAR_ACCOUNT_ID and STELLAR_SECRET_KEY in .env\n2. Or log in with your credentials first")
                self.log_signal.emit("❌ Cannot start bot: Missing Stellar credentials")
                return
            
            if self.bot and getattr(self.bot, "running", False):
                self.logger.warning("Bot already running.")
                return

            self.bot = SmartBot(controller=self, test_mode=True)
            
            # Check if bot was successfully initialized with Stellar connection
            if not self.bot.account_id:
                self.show_error("❌ Failed to connect to Stellar Network.\n\nPlease verify:\n1. Internet connection\n2. Stellar account credentials are correct\n3. .env file is properly configured")
                self.log_signal.emit("❌ Cannot start bot: Stellar connection failed")
                return
            
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
        """Safely switch between frames with modern UI"""
        frames = {
            "Login": login.Login,
            "Home": home.Home  
        }
        frame_class = frames.get(name, None)
>>>>>>> Stashed changes
        if not frame_class:
            self.logger.error(f"Invalid page name: {page_name}")
            self.show_error_message(f"Invalid page name: {page_name}")
            return
        frame = frame_class(self, self.controller)
        ql = QVBoxLayout()
        self.main_layout.addWidget(frame)
        ql.addWidget(frame)
        frame.setLayout(ql)

<<<<<<< Updated upstream
        frame.setToolTip(f"StellarBot - {page_name}")
        self.current_frame = frame  # Store the current frame for future use
        self.setCentralWidget(frame)
        self.logger.info(f"open  to {page_name} page")
        frame.update()
=======
        try:
            # Create new frame
            frame = frame_class(self, self)
            if frame is None or not isinstance(frame, QWidget):
                self.show_error(f"Invalid frame: {name}")
                return
            
            # Clear existing widgets in stacked widget
            while self.stacked_widget.count() > 0:
                widget = self.stacked_widget.widget(0)
                self.stacked_widget.removeWidget(widget)
                widget.deleteLater()
            
            # Add new frame
            self.stacked_widget.addWidget(frame)
            self.stacked_widget.setCurrentWidget(frame)
            self.layout.addWidget(self.stacked_widget)
            self.current_frame = frame
            
            self.logger.info(f"✅ Switched to frame: {name}")
            self.status_bar.set_status(f"Viewing: {name}", "info")
        except Exception as e:
            self.logger.error(f"Error loading frame {name}: {e}")
            self.show_error(f"Failed to load {name}: {e}")
>>>>>>> Stashed changes
        self.show()

    def delete_frame(self):
        """Clear the current central widget before displaying a new frame."""
        if self.centralWidget():
            self.centralWidget().deleteLater()

    def show_error_message(self, msg: str = "Invalid"):
        """Display an error message dialog."""
        error_dialog = QtWidgets.QMessageBox(self)
        error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        error_dialog.setText(msg)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()

    def exit(self):
        """Exit the application."""
        self.close()

    def send_notification(self,message: str):
        """Send a notification message using the system's notification system."""
        title = "Trading"
        # Example implementation using the QMessageBox
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.exec_()
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setContextMenu(QMenu())
        tray_icon.show()


        notification = QSystemTrayIcon.MessageIcon.Information
        tray_icon.showMessage(title, message, notification)


<<<<<<< Updated upstream
=======
    def show_settings(self, key: str, default=None):
        """Retrieve and display a setting from the settings manager."""
        try:
            current_settings = self.settings.load_settings()
            value = current_settings.get(key, default)
            
            if value is None:
                self.logger.warning(f"⚠️ Setting '{key}' not found")
                return None
            
            self.logger.info(f"✅ Setting '{key}': {value}")
            return value
        except Exception as e:
            self.logger.error(f"❌ Error retrieving setting '{key}': {e}")
            return default

    def closeEvent(self, event: QtGui.QCloseEvent):
        """Graceful shutdown with proper thread cleanup."""
        self.logger.info("Shutting down StellarBot...")
        try:
            # Stop the bot if running
            if self.bot and getattr(self.bot, "running", False):
                self.bot.stop()
            
            # Close database connection
            if self.db:
                self.db.close()
            
            # Wait for database thread to finish
            if self.db_thread and self.db_thread.isRunning():
                self.db_thread.quit()
                self.db_thread.wait(5000)  # Wait max 5 seconds
                if self.db_thread.isRunning():
                    self.logger.warning("Database thread did not finish gracefully, terminating...")
                    self.db_thread.terminate()
                    self.db_thread.wait()
            
            # Hide tray icon
            if self.tray_icon:
                self.tray_icon.hide()
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        finally:
            super().closeEvent(event)
>>>>>>> Stashed changes


if __name__ == "__main__":
<<<<<<< Updated upstream
  app = QtWidgets.QApplication(sys.argv)
  try:
    # Create and run the StellarBot application
    stellar_bot = StellarBot()  # Initialize the application
    # Apply the stylesheet
    with open("stellarbot.css", "r") as file:
        stellar_bot.setStyleSheet(file.read())
    stellar_bot.setWindowIcon(QIcon("stellarbot.ico"))
    stellar_bot.setWindowFilePath("StellarBot")
    stellar_bot.setWindowIconText("StellarBot")
    stellar_bot.setWindowTitle("StellarBot")
    stellar_bot.showMaximized()  # Maximize the application
    stellar_bot.show()  # Show the application
    app.exec_()  # Execute the application
    # Log the error and exit the application
    # sys.exit(app.exec_())
  except Exception as e:
    exception_hook(type(e), e, traceback.format_exc())
    sys.exit(app.exec_())
=======
    faulthandler.enable()
    sys.excepthook = exception_hook

    try:
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)
    except Exception as e:
        logging.error(f"❌ Failed to initialize Qt Application: {e}")
        print(f"❌ ERROR: Cannot initialize graphical display")
        print(f"   Details: {str(e)}")
        print()
        print("💡 This is a GUI application that requires a display.")
        print("   Options:")
        print("   1. Run on a machine with a display (Windows/Linux desktop)")
        print("   2. Use VNC/remote display forwarding")
        print("   3. Use the new production entry point for server mode:")
        print("      python stellarbot_app.py --debug")
        sys.exit(1)

    # Apply theme BEFORE UI
    try:
        theme = ThemeManager(app)
        theme.apply_theme("style")
        logging.info("✅ Applied style theme")
    except Exception as e:
        logging.error(f"Theme application failed: {e}")

    try:
        window = StellarBot()
        window.showMaximized()
        app.exec()
    except Exception as e:
        exception_hook(type(e), e, traceback.format_exc())
        sys.exit(1)
>>>>>>> Stashed changes
