from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel

from src.modules.frames.ui_utility import logger


class ForexNews(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Forex News widget."""
        super().__init__(parent)

        self.update_news = None
        try:

            # Assuming logger is a Logger instance from src.modules.frames.ui_utility
            # Set controller and retrieve news data
            self.controller = controller
            self.news_data = self.controller.bot.news_data  # Assuming this returns the news data
            self.logger = controller.logger
            # Set the window title, style, and geometry
            self.setWindowTitle("Forex News")
            # Main layout for the widget
            layout = QVBoxLayout()
            layout.setSpacing(0)  # Remove spacing between widgets
            # Set the news update timer
            self.update_news_timer = QTimer()
            self.update_news_timer.setInterval(10000)  # Update news every 10 seconds
            self.update_news_timer.timeout.connect(self.update_news)
            self.update_news_timer.start()  # Start the timer
            self.setLayout(layout)  # Set the layout for the widget
            # Create the initial widgets for the news data
            self.create_widgets()

        except Exception as e:
            logger.error(f"Error initializing ForexNews: {e}")

    def create_widgets(self):
        """Create the widgets for the news data."""
        try:
            # Clear the previous widgets in the layout
            while self.layout.count():
                item = self.layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Create labels for each news article
            for i, news in enumerate(self.news_data):
                label = QLabel(f"{i+1}. {news['title']}")
                label.setWordWrap(True)  # Wrap the text to fit the width of the label
                label.setAlignment( QLabel.AlignTop | QLabel.AlignLeft)  # Align the text to the top-left corner
                self.layout.addWidget(label)  # Add the label to the layout

        except Exception as e:
            logger.error(f"Error creating widgets: {e}")

      