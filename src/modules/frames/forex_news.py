<<<<<<< Updated upstream
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
=======
import requests
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QTimer, QRunnable, QThreadPool, Signal, QObject
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
>>>>>>> Stashed changes

from src.modules.frames.ui_helper import create_label_df
from src.modules.frames.ui_utility import logger


<<<<<<< Updated upstream
=======
# Signal emitter for thread-safe callbacks
class NewsSignals(QObject):
    """Signals for news fetcher."""
    news_fetched = Signal(list)  # Emit list of article dicts
    error_occurred = Signal(str)  # Emit error message


# ----------------------------------------------------------------------
# 🧵 Background Worker for Fetching News
# ----------------------------------------------------------------------
class NewsFetcher(QRunnable):
    """Runs the news API call in a background thread."""

    def __init__(self):
        super().__init__()
        self.signals = NewsSignals()
        self.api_key = "demo"  # replace with your NewsData.io API key
        self.endpoint = f"https://newsdata.io/api/1/news?apikey={self.api_key}&q=forex%20market&language=en"

    def run(self):
        """Fetch forex news in background."""
        try:
            response = requests.get(self.endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = [
                    {
                        "title": a.get("title", "No Title"),
                        "source": a.get("source_id", "Unknown"),
                        "time": a.get("pubDate", "—"),
                    }
                    for a in data.get("results", [])[:10]
                ]
                # Emit signal with articles
                self.signals.news_fetched.emit(articles)
            else:
                logger.error(f"❌ News API error: {response.status_code}")
                # Emit empty list on error
                self.signals.news_fetched.emit([])
        except Exception as e:
            logger.error(f"Exception fetching forex news: {e}")
            # Emit error signal
            self.signals.error_occurred.emit(str(e))
            self.signals.news_fetched.emit([])


# ----------------------------------------------------------------------
# 📰 Forex News Dashboard
# ----------------------------------------------------------------------
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
      
=======
        # Initial fetch
        self.update_news()

    # ------------------------------------------------------------------
    # 🔄 News Fetching
    # ------------------------------------------------------------------
    def update_news(self):
        """Trigger background news fetch."""
        self.status_label.setText("🔄 Updating news...")
        fetcher = NewsFetcher()
        # Connect signals to slots
        fetcher.signals.news_fetched.connect(self._on_news_fetched)
        fetcher.signals.error_occurred.connect(self._on_news_error)
        self.thread_pool.start(fetcher)

    def _on_news_fetched(self, articles):
        """Callback after background fetch (runs in main thread)."""
        try:
            if not articles:
                # fallback to controller.bot.news_data if API failed
                self.logger.warning("⚠️ No news from API, using cached bot data.")
                self.news_data = getattr(self.bot, "news_data", [])
                if not self.news_data:
                    self.status_label.setText("⚠️ No news available.")
                    return
            else:
                self.news_data = articles
                self.logger.info(f"✅ Loaded {len(articles)} forex news articles.")
                self.status_label.setText("✅ News updated successfully!")

            self._refresh_ui()
        except Exception as e:
            self.logger.error(f"Error processing fetched news: {e}")
            self.status_label.setText("⚠️ Error updating news")
    
    def _on_news_error(self, error_msg: str):
        """Handle news fetch errors."""
        self.logger.error(f"News fetch error: {error_msg}")
        self.status_label.setText("⚠️ Failed to fetch news")

    # ------------------------------------------------------------------
    # 🧱 UI Refresh
    # ------------------------------------------------------------------
    def _refresh_ui(self):
        """Rebuild visible news list."""
        # Clear old labels
        for lbl in self.news_labels:
            self.main_layout.removeWidget(lbl)
            lbl.deleteLater()
        self.news_labels.clear()

        # Display updated news
        for news in self.news_data[:10]:
            title = news.get("title", "Untitled")
            source = news.get("source", "Unknown")
            time_str = news.get("time", "—")

            lbl = QLabel(f"• {title}\n🕒 {time_str} | {source}")
            lbl.setWordWrap(True)
            lbl.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
            lbl.setStyleSheet("color:#b2ff59; margin-bottom:8px;")
            self.main_layout.addWidget(lbl)
            self.news_labels.append(lbl)
>>>>>>> Stashed changes
