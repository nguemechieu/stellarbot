import os
import platform
import subprocess
from PyQt5 import QtWidgets, QtGui
from modules.frames.home import Home
from modules.frames.login import Login
from modules.frames.about import About
from modules.classes.db_manager import DatabaseManager
from modules.frames.settings_preferences import SettingsPreferences
from modules.frames.help import Help
import atexit

class StellarBot(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.controller = self
        self.db = DatabaseManager('stellarBot.db').db
        self.bot = None
        self.settings_manager = None
      
        # Create the database table
        self.db.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            account_id VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE,
                            account_secret VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.db.commit()
      
        self.init_ui()
        

    def init_ui(self):
        """Initialize the UI with the login page."""
        self.setWindowTitle('StellarBot@Login')
        self.setGeometry(0, 0, 1530, 780)
        self.setWindowIcon(QtGui.QIcon("src/assets/stellarbot.ico"))
        
        # Show login page initially
        self.show_frame("Login")

    def show_frame(self, page_name):
        """Switch to different frames (Login, Home, etc.)."""
       
        
        if page_name == 'Login':
            self.delete_frame()
            frame = Login(self, self.controller)
        elif page_name == 'Home':
            self.delete_frame()
            self.setWindowTitle(f"StellarBot@{page_name}====== ID :{self.controller.bot.account_id}")
            frame = Home(self, self.controller)
        elif page_name == 'SettingsPreferences':
            frame = SettingsPreferences(self, self.controller)
        elif page_name == 'About':
            frame = About(self, self.controller)
        elif page_name == 'Help':
            frame = Help(self, self.controller)
        
        self.setCentralWidget(frame)

    def delete_frame(self):
        """Clear existing widgets."""
        if self.centralWidget():
           
            self.centralWidget().deleteLater()

    def show_error_message(self, msg):
        """Display error messages."""
        error_dialog = QtWidgets.QMessageBox(self)
        error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        error_dialog.setText(msg)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()

    def exit(self):
        """Exit the application."""
        self.close()



def check_os():
    """Check the current operating system."""
    system = platform.system()

    if system == "Windows":
        return "Windows"
    elif system == "Linux":
        return "Linux"
    elif system == "Darwin":
        return "macOS"

    return "Unknown"


def start_xvfb():
    """Start Xvfb for Linux systems."""
    display_number = 99
    xvfb_command = f"Xvfb :{display_number} -screen 0 1280x1024x24 &"
    subprocess.Popen(xvfb_command, shell=True)
    os.environ["DISPLAY"] = f":{display_number}"


def cleanup_xvfb():
    """Kill Xvfb process on exit."""
    subprocess.Popen("kill -9 $(pgrep Xvfb)", shell=True)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    if check_os() == "Linux":
        start_xvfb()
        atexit.register(cleanup_xvfb)  # Ensure Xvfb is killed when the app exits

    # Create and run the StellarBot application
    window = StellarBot()
    window.show()
    app.exec_()
