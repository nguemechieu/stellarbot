import logging
import sys

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow
from tensorflow.python.trackable.asset import Asset

from src.modules.classes.db_manager import DatabaseManager
from src.modules.classes.settings_manager import SettingsManager
from src.modules.frames.about import About
from src.modules.frames.help import Help
from src.modules.frames.home import Home
from src.modules.frames.login import Login
from src.modules.frames.preferences import Preferences


class StellarBot(QMainWindow):
    """Main window class for StellarBot, managing different frames and database connections."""

    def __init__(self):
        """Initialize StellarBot with database setup, UI setup, and frame management."""
        super().__init__()

        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        # Database and controller setup
        self.controller = self
        self.db = DatabaseManager('StellarBot.db').db
        # Initialize the bot object

        self.amount = 10
        self.price = 0.05
        self.login_frame = None
        self.preferences_frame = None
        self.help_frame = None
        self.about_frame = None
        self.current_frame = None
        self.current_account_id = None
        self.current_secret_key = None
        self.current_server = None
        self.current_keypair = None
        self.current_account = None
        self.current_base_asset = None
        self.current_counter_asset = None
        self.current_server_msg = None
        self.time_frame_selected = "H1"
        self.server_thread = None

        self.keep_running = False
        #Create the database tables assets if not already exists
        self.db.execute("""CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_code TEXT NOT NULL UNIQUE,
            asset_issuer TEXT NOT NULL UNIQUE,
                   image TEXT NOT NULL  DEFAULT 'default.png'
        )""")
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS ohlcv_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        self.bot = None
        self.amount = 10
        self.price = 0.05
        self.login_frame = None
        self.preferences_frame = None
        self.help_frame = None
        self.about_frame = None
        self.current_frame = None
        self.current_account_id = None
        self.current_secret_key = None
        self.current_server = None

        self.assets :{{}:Asset}= self.db.execute(
            "SELECT * FROM assets"
        ).fetchall()
        # Set the main window geometry and style
        self.secret_key = ""
        self.account_id = ""
        self.server=None
        self.keypair =None
        self.account=None
        self.base_asset = Asset("XLM")
        self.counter_asset = Asset("USDC")
        self.server_msg = {'message': 'N/A', 'status': 'OFF', 'info': 'N/A'}
        self.time_frame_selected = "H1"

        # Set the main window geometry and style
        self.setGeometry(0, 0, 1530, 780)
        self.setWindowIcon(QtGui.QIcon("stellarbot.ico"))
        self.setUpdatesEnabled(True)
        self.settings_manager = SettingsManager()

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
        except Exception as e:
            self.logger.error(f"Database error: {e}")
            self.show_error_message("An error occurred while setting up the database.")

    def init_ui(self):
        """Initialize the UI by showing the login page."""
        self.show_frame("Login")

    def show_frame(self, page_name):
        """Switch between different application frames (Login, Home, Settings, etc.)."""
        frame_classes = {
            'Login': Login,
            'Home': Home,
            'Preferences': Preferences,
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
        self.logger.info(f"Switched to {page_name} page")
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

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
