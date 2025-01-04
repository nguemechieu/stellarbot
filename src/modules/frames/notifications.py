from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QPushButton

class Notifications(QFrame):
    """A Notification widget to display messages."""

    def __init__(self, message, message_type="info", parent=None):
        super().__init__(parent)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)  # To make it popup
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # Transparent background
        self.setStyleSheet("background-color: #333; color: white; border-radius: 8px; padding: 10px;")

        self.layout = QVBoxLayout(self)

        # Define icons and styles based on message type
        if message_type == "success":
            self.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 8px; padding: 10px;")
            icon = QtGui.QIcon("success_icon.png")  # You can replace this with your own icon
        elif message_type == "warning":
            self.setStyleSheet("background-color: #FFC107; color: black; border-radius: 8px; padding: 10px;")
            icon = QtGui.QIcon("warning_icon.png")
        elif message_type == "error":
            self.setStyleSheet("background-color: #F44336; color: white; border-radius: 8px; padding: 10px;")
            icon = QtGui.QIcon("error_icon.png")
        else:
            self.setStyleSheet("background-color: #2196F3; color: white; border-radius: 8px; padding: 10px;")
            icon = QtGui.QIcon("info_icon.png")

        # Add an icon and message label
        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(icon.pixmap(32, 32))
        self.layout.addWidget(self.icon_label)

        self.message_label = QLabel(message, self)
        self.layout.addWidget(self.message_label)

        self.setLayout(self.layout)

        # Timer to close the notification after 3 seconds
        QtCore.QTimer.singleShot(3000, self.close_notification)

    def close_notification(self):
        """Close the notification after a short duration."""
        self.close()


def show_notification(message, message_type):
    """Display the notification on the screen."""
    notification = Notifications(message, message_type)
    notification.move(100, 100)  # Adjust the position of the notification on screen
    notification.show()


def show_warning_notification():
    """Show warning notification."""
    show_notification("Warning: Something might be wrong", message_type="warning")


def show_error_notification():
    """Show error notification."""
    show_notification("Error: Something went wrong", message_type="error")


def show_success_notification():
    """Show success notification."""
    show_notification({
        "title": "Transaction Successful",
        "message": "Your transaction was completed successfully."
    }, message_type="success")


class NotificationsWidget(QtWidgets.QWidget):
    """Widget to manage and display notifications."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Notifications")
        self.setGeometry(100, 100, 300, 400)
        self.layout = QVBoxLayout(self)

        # Create and show notification button
        self.show_success_button = QPushButton("Show Success Notification", self)
        self.show_warning_button = QPushButton("Show Warning Notification", self)
        self.show_error_button = QPushButton("Show Error Notification", self)

        self.show_success_button.clicked.connect(show_success_notification)
        self.show_warning_button.clicked.connect(show_warning_notification)
        self.show_error_button.clicked.connect(show_error_notification)

        self.layout.addWidget(self.show_success_button)
        self.layout.addWidget(self.show_warning_button)
        self.layout.addWidget(self.show_error_button)

        self.setLayout(self.layout)


# Main application
