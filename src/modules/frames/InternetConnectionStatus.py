from PyQt5 import QtWidgets, QtCore, QtGui
import requests

class InternetConnectionStatus(QtWidgets.QWidget):
    """Widget to show the status of the user's internet connection."""
    
    def __init__(self, parent=None):
        super(InternetConnectionStatus, self).__init__(parent)

        self.resize(300, 300)
        self.setWindowTitle("Internet Connection Status")

        self.setFixedSize(300, 300)
        self.setStyleSheet("background-color: #1e2a38;")

        # Create a label to display connection text
        self.status_label = QtWidgets.QLabel("Checking Internet Connection...", self)
        self.status_label.setStyleSheet("color: white; font-size: 16px;")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setGeometry(0, 250, 300, 40)

        # Variable to store the current internet connection quality
        self.connection_quality = "checking"

        # Timer to periodically check internet connection status
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_internet_connection)
        self.timer.start(3000)  # Check every 3 seconds

    def paintEvent(self, event):
        """Handle the painting of the widget to display the network strength."""
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Draw signal bars based on connection quality
        signal_colors = {
            'good': QtGui.QColor(76, 175, 80),  # Green for good connection
            'poor': QtGui.QColor(255, 165, 0),  # Orange for poor connection
            'disconnected': QtGui.QColor(244, 67, 54),  # Red for no connection
            'checking': QtGui.QColor(255, 255, 255)  # White while checking
        }
        color = signal_colors.get(self.connection_quality, QtGui.QColor(255, 255, 255))

        bar_width = 30
        bar_height = 30
        gap = 10

        # Draw 3 bars to represent the connection strength
        for i in range(3):
            rect_height = (i + 1) * bar_height
            rect = QtCore.QRect(80 + i * (bar_width + gap), 200 - rect_height, bar_width, rect_height)
            painter.fillRect(rect, color)

        painter.end()

    def check_internet_connection(self):
        """Check the quality of the internet connection by pinging a server."""
        try:
            response = requests.get("https://www.google.com", timeout=2)
            if response.status_code == 200:
                self.connection_quality = 'good'
                self.status_label.setText("Internet Connection: Good")
            else:
                self.connection_quality = 'poor'
                self.status_label.setText("Internet Connection: Poor")
        except requests.RequestException:
            self.connection_quality = 'disconnected'
            self.status_label.setText("Internet Connection: Disconnected")
        
        # Update the widget to repaint the signal bars
        self.update()


