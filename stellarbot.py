import logging
import sys
import traceback

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QSystemTrayIcon, QMenu, QMessageBox
from stellar_sdk import Server, Asset

from src.modules.classes.db_manager import DatabaseManager
from src.modules.classes.settings_manager import SettingsManager
from src.modules.classes.stellar_client import StellarClient
from src.modules.frames.about import About
from src.modules.frames.help import Help
from src.modules.frames.home import Home
from src.modules.frames.login import Login
from src.modules.frames.preferences import Preferences
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

sys.excepthook = exception_hook


class StellarBot(QMainWindow):
    """Main window class for StellarBot, managing different frames and database connections."""

    def __init__(self):
        """Initialize StellarBot with database setup, UI setup, and frame management."""
        super().__init__()
# https://dashboard.stellar.org/api/v2/lumens/
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        # Database and controller setup
        self.controller = self
        self.db = DatabaseManager('StellarBot.db').db
        # Initialize the bot object


        self.price = 0.05
        self.login_frame = None
        self.trade_strategy=None
        self.preferences_frame = None
        self.help_frame = None
        self.about_frame = None
        self.current_frame = None
        self.account_id =None
        self.data_fetcher = None
        self.secret_key = None
        self.selected_strategy=None
        self.available_strategies=None
        self.account=None


        self.marketdata= None
        self.server_horizon_url = "https://horizon.stellar.org"
        self.server = Server(self.server_horizon_url)

        self.time_frame_selected = "H1"
        self.ledger_entries = None
        self.fees=None
        self.data_fetcher=None

        self.keep_running = True
        self.balances={}
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
            "error": "",
            "total_trades": 0,
            "average_price": 0.0,
            "total_balance": 0.0,
            "profit": 0.0,
            "win_rate": 0.0,
            "total_fees": 0.0,
            "trade_count": 0,
            "total_assets": 0,
            "total_balances": 0,
            "total_offers": 0,
            "total_effects": 0,
            "total_transactions": 0
        }
        self.base_asset = Asset.native()

        #centre.io public address GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN
        self.counter_asset = Asset("USDC", "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN")
        self.assets ={ "assets":{(self.base_asset, self.counter_asset): {
            "price": 0.0,
            "balance": 0.0,
            "offers": 0,
            "effects": 0,
            "transactions": 0,
            "orderbook": {
                "bids": [],
                "asks": []
            },
            "candles": [],
            "trades": [],
            "balances": {},
            "ledger": {
                "operations": []
            },
            "transaction_history": [],
            "transaction_details": {},
            "account_details": {
                "balances": [],
                "offers": [],
                "effects": [],
                "transactions": []
            }}
        }
        }

        self.telegram_chat_id = None

        self.telegram_token = None

        self.account_details={}
        self.secret_key=None
        self.selected_strategy=None
        self.trades=None
        self.offers=None
        self.assets=None
        self.transactions=None
        self.effects=None
        self.orderbook=None
        self.fees_stats={
            "total_fees": 0.0,
            "total_fee_percent": 0.0,
            "average_fee": 0.0,
            "fee_distribution": {}

        }
        self.ohlcv_data=None
        self.transaction_history={}
        self.transaction_details={}

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

    def show_frame(self, page_name):
        """Switch between different application frames (Login, Home, Settings, etc.)."""
        frame_classes = {
            'Login': Login,
            'Home': Home,
            'Preferences': Preferences,"Settings": SettingsManager,

            'About': About,
            'Help': Help
        }

        self.delete_frame()  # Clear the current central widget
        self.setWindowTitle(f"StellarBot - {page_name}")

        frame_class = frame_classes.get(page_name)
        if not frame_class:
            self.logger.error(f"Invalid page name: {page_name}")
            self.show_error_message(f"Invalid page name: {page_name}")
            return

        frame = frame_class(self, self.controller)
        ql = QVBoxLayout(self)
        self.main_layout.addWidget(frame)
        ql.addWidget(frame)
        frame.setLayout(ql)

        frame.setToolTip(f"StellarBot - {page_name}")
        self.current_frame = frame  # Store the current frame for future use
        self.setCentralWidget(frame)
        self.logger.info(f"open  to {page_name} page")
        frame.update()
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
        title = "Live Trading"  # Example title

        # Example implementation using the QMessageBox
        error_dialog = QtWidgets.QMessageBox(self)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.exec_()

        # Example implementation using the QNotification
        # Note: This requires the application to have permission to display notifications
        # notification = QNotification(title, message)
        # notification.setStandardIcon(QNotification.Information)
        # notification.show()
        # Example implementation using the QSystemTrayIcon
        tray_icon = QSystemTrayIcon(self)
        tray_icon.setContextMenu(QMenu())
        tray_icon.show()

        notification = QSystemTrayIcon.MessageIcon.Information
        tray_icon.showMessage(title, message, notification)




if __name__ == "__main__":
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
    stellar_bot.show()  # Show the application
    app.exec_()  # Execute the application
  except Exception as e:
    exception_hook(type(e), e, traceback.format_exc())
    sys.exit(app.exec_())
