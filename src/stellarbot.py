
from PyQt5 import QtWidgets, QtGui
from modules.frames.home import Home
from modules.frames.login import Login
from modules.frames.about import About
from modules.classes.db_manager import DatabaseManager
from modules.frames.settings_preferences import SettingsPreferences
from modules.frames.help import Help
import atexit
from PyQt5 import QtCore

class StellarBot(QtWidgets.QMainWindow):
    """Main window class for StellarBot, managing different frames and database connections."""

    def __init__(self):
        """Initialize StellarBot with database setup, UI setup, and frame management."""
        super().__init__()

        # Database and controller setup
        self.controller = self
        self.db = DatabaseManager('stellarBot.db').db
        self.bot = None  # Placeholder for bot logic to be attached later
        self.settings_manager = None

        # Set the main window geometry and basic settings
        self.setGeometry(0, 0, 1530, 780)
        self.setWindowFlags(self.windowFlags())
        self.setStyleSheet("background-color: #1e2a38;")
        self.setWindowIcon(QtGui.QIcon("src/assets/stellarbot.ico"))

        # Create necessary database tables if they don't exist
        self.db.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            account_id VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE,
                            account_secret VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.db.commit()

        # Initialize the UI with login page as the first screen
        self.init_ui()

    def init_ui(self):
        """Initialize the UI by showing the login page."""
        self.show_frame("Login")

    def show_frame(self, page_name):
        """Switch between different application frames (Login, Home, Settings, etc.)."""
        self.delete_frame()  # Clear the current frame
        
        if page_name == 'Login':
            frame = Login(self, self.controller)
        elif page_name == 'Home':
            self.setWindowTitle(f"StellarBot - Home (ID: {self.controller.bot.account_id})")
            frame = Home(self, self.controller)
        elif page_name == 'SettingsPreferences':
            frame = SettingsPreferences(self, self.controller)
        elif page_name == 'About':
            frame = About(self, self.controller)
        elif page_name == 'Help':
            frame = Help(self, self.controller)
        
        self.setCentralWidget(frame)

    def delete_frame(self):
        """Clear the current central widget before displaying a new frame."""
        if self.centralWidget():
            self.centralWidget().deleteLater()

    def show_error_message(self, msg):
        """Display an error message dialog."""
        error_dialog = QtWidgets.QMessageBox(self)
        error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        error_dialog.setText(msg)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()

    def exit(self):
        """Exit the application."""
        self.close()

# def check_os():
#     """Return the current operating system name."""
#     system = platform.system()
#     if system == "Windows":
#         return "Windows"
#     elif system == "Linux":
#         return "Linux"
#     elif system == "Darwin":
#         return "macOS"
#     return "Unknown"

# def start_xvfb():
#     """Start a virtual display using Xvfb on Linux."""
#     display_number = 99
#     xvfb_command = f"Xvfb :{display_number} -screen 0 1280x1024x24 &"
#     subprocess.Popen(xvfb_command, shell=True)
#     os.environ["DISPLAY"] = f":{display_number}"

# def cleanup_xvfb():
    """Ensure Xvfb process is killed when the application exits."""
  #  subprocess.Popen("kill -9 $(pgrep Xvfb)", shell=True)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    # For Linux systems, start Xvfb to create a virtual display
    # if check_os() == "Linux":
    #     start_xvfb()
    #     atexit.register(cleanup_xvfb)

    # Create the StellarBot window and run the application
    window = StellarBot()
    window.show()
    app.exec_()
