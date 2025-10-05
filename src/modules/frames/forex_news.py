import requests
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QTimer, QRunnable, QThreadPool, Slot
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel

from src.modules.frames.ui_utility import logger


# ----------------------------------------------------------------------
# 🧵 Background Worker for Fetching News
# ----------------------------------------------------------------------
class NewsFetcher(QRunnable):
    """Runs the news API call in a background thread."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback  # function to call on completion
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
                QtCore.QMetaObject.invokeMethod(
                    self.callback,
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(object, articles)
                )
            else:
                logger.error(f"❌ News API error: {response.status_code}")
                QtCore.QMetaObject.invokeMethod(
                    self.callback,
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(object, [])
                )
        except Exception as e:
            logger.error(f"Exception fetching forex news: {e}")
            QtCore.QMetaObject.invokeMethod(
                self.callback,
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(object, [])
            )


# ----------------------------------------------------------------------
# 📰 Forex News Dashboard
# ----------------------------------------------------------------------
class ForexNews(QFrame):
    """Live Forex News display panel with background API refresh."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.logger = getattr(controller, "logger", logger)
        self.bot = getattr(controller, "bot", None)
        self.thread_pool = QThreadPool.globalInstance()
        self.news_data = []

        # Styling and layout
        self.setWindowTitle("Forex News")
        self.setStyleSheet("""
            QFrame { background-color: #0e0e0e; color: #00ff99; font-family: Consolas; }
            QLabel { font-size: 13px; }
        """)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(6)

        self.title_label = QLabel("🌍 Live Forex Market News")
        self.title_label.setStyleSheet("font-size:16px; font-weight:bold; color:#00e676;")
        self.main_layout.addWidget(self.title_label)

        self.status_label = QLabel("Fetching latest news...")
        self.main_layout.addWidget(self.status_label)

        self.news_labels = []

        # Timer setup (auto refresh every 2 minutes)
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(120_000)
        self.update_timer.timeout.connect(self.update_news)
        self.update_timer.start()

        # Initial fetch
        self.update_news()

    # ------------------------------------------------------------------
    # 🔄 News Fetching
    # ------------------------------------------------------------------
    def update_news(self):
        """Trigger background news fetch."""
        self.status_label.setText("🔄 Updating news...")
        fetcher = NewsFetcher(self._on_news_fetched)
        self.thread_pool.start(fetcher)

    @Slot(object)
    def _on_news_fetched(self, articles):
        """Callback after background fetch."""
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
