from __future__ import annotations
from functools import partial
from typing import Type

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFrame, QMenuBar,
    QMessageBox, QStatusBar, QApplication, QLabel
)
from PySide6.QtCore import Qt, QTimer

# --- Import frames dynamically ---
from src.modules.frames.account_overview import AccountOverview
from src.modules.frames.dashboard import Dashboard
from src.modules.frames.effects import Effects
from src.modules.frames.fees_analysis import FeesAnalysis
from src.modules.frames.forex_news import ForexNews

from src.modules.frames.ledger import Ledger
from src.modules.frames.liquidity_pool import LiquidityPool
from src.modules.frames.market_depth import MarketDepth
from src.modules.frames.offers import Offers
from src.modules.frames.order_history import OrdersHistory
from src.modules.frames.payments import Payments
from src.modules.frames.risk_management import RiskManagement
from src.modules.frames.send_money import SendMoney
from src.modules.frames.trading_analytics_analytics import TradingAnalysis
from src.modules.frames.trading_charts import TradingCharts
from src.modules.frames.trading_strategies import TradingStrategies
from src.modules.frames.transactions import Transactions
from src.modules.frames.trusted_assets import TrustedAsset


class Home(QFrame):
    """🏠 Main StellarBot workspace — Menu + Tabs + Status bar."""

    def __init__(self, parent: QWidget | None, controller):
        super().__init__(parent)
        self.controller = controller
        self.logger = controller.logger
        self.bot = getattr(controller, "bot", None)

        self.menu_bar: QMenuBar | None = None
        self.tab_widget: QTabWidget | None = None
        self.status_bar: QStatusBar | None = None

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setContentsMargins(0, 0, 0, 0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Initialize UI
        self._init_menu_bar(layout)
        self._init_tabs(layout)
        self._init_status_bar(layout)

        # Apply global theme
        self.setStyleSheet("""
            QFrame { background-color: #121212; color: #E0E0E0; }
            QTabBar::tab {
                padding: 8px 16px;
                background: #1E1E1E;
                border-radius: 5px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: #1976D2;
                color: white;
                font-weight: bold;
            }
            QStatusBar {
                background: #0D47A1;
                color: white;
                padding: 6px;
                font-weight: 500;
            }
        """)

    # ------------------------------------------------------------------ #
    #  MENU BAR
    # ------------------------------------------------------------------ #
    def _init_menu_bar(self, layout: QVBoxLayout) -> None:
        """Initialize application menu bar."""
        try:
            self.menu_bar = QMenuBar(self)
            self.menu_bar.setNativeMenuBar(False)

            # File Menu
            file_menu = self.menu_bar.addMenu("&File")
            self._add_action(file_menu, "Open…", self.open_file, "document-open")
            self._add_action(file_menu, "Save…", self.save_file, "document-save")
            file_menu.addSeparator()
            self._add_action(file_menu, "Exit", self.close_application, "application-exit")

            # Tools & Settings placeholders
            self.menu_bar.addMenu("&Edit")
            self.menu_bar.addMenu("&Tools")
            self.menu_bar.addMenu("&View")
            self.menu_bar.addMenu("&Settings")

            # Help Menu
            help_menu = self.menu_bar.addMenu("&Help")
            self._add_action(help_menu, "About StellarBot", self.show_about, "help-about")

            layout.addWidget(self.menu_bar)
        except Exception as e:
            self._log_error("Error initializing menu bar", e)

    def _add_action(self, menu, name: str, func, icon_name: str | None = None) -> QAction:
        """Utility to create and connect a menu action."""
        action = QAction(QIcon.fromTheme(icon_name or ""), name, self)
        action.triggered.connect(partial(self._safe_execute, func))
        menu.addAction(action)
        return action

    # ------------------------------------------------------------------ #
    #  TABS
    # ------------------------------------------------------------------ #
    def _init_tabs(self, layout: QVBoxLayout) -> None:
        """Initialize main tabs (lazy-loading to improve performance)."""
        try:
            self.tab_widget = QTabWidget()
            self.tab_widget.setTabPosition(QTabWidget.North)
            self.tab_widget.setMovable(True)
            self.tab_widget.setDocumentMode(True)
            self.tab_widget.setUsesScrollButtons(True)

            # Map of all available frames
            self.tab_frames: dict[str, Type[QWidget]] = {
                "Dashboard": Dashboard,
                "Account Overview": AccountOverview,
                "Trusted Assets": TrustedAsset,
                "Market Depth": MarketDepth,
                "Charting": TradingCharts,
                "Risk Management": RiskManagement,
                "Offers": Offers,
                "Effects": Effects,
                "Order History": OrdersHistory,
                "Trading Analysis": TradingAnalysis,
                "Forex News": ForexNews,
                "Trading Strategies": TradingStrategies,
                "Transactions": Transactions,
                "Liquidity Pool": LiquidityPool,
                "Payments": Payments,
                "Send Money": SendMoney,
                "Fees Analysis": FeesAnalysis,
                "Ledger": Ledger,
            }

            # Add placeholder tabs for lazy initialization
            for tab_name in self.tab_frames.keys():
                placeholder = QLabel(f"⏳ Loading {tab_name}…")
                placeholder.setAlignment(Qt.AlignCenter)
                self.tab_widget.addTab(placeholder, tab_name)

            self.tab_widget.currentChanged.connect(self._on_tab_changed)
            layout.addWidget(self.tab_widget)
        except Exception as e:
            self._log_error("Error initializing tabs", e)

    def _on_tab_changed(self, index: int):
        """Lazy-load the actual frame when tab is first selected."""
        try:
            widget = self.tab_widget.widget(index)
            tab_name = self.tab_widget.tabText(index)

            if isinstance(widget, QLabel):  # means not yet loaded
                frame_class = self.tab_frames.get(tab_name)
                if not frame_class:
                    return

                container = QWidget()
                layout = QVBoxLayout(container)
                layout.setContentsMargins(6, 6, 6, 6)
                layout.setSpacing(0)

                frame = frame_class(container, self.controller)
                layout.addWidget(frame)

                self.tab_widget.removeTab(index)
                self.tab_widget.insertTab(index, container, tab_name)
                self.tab_widget.setCurrentIndex(index)
                self.logger.info(f"✅ Loaded {tab_name} tab successfully.")
        except Exception as e:
            self._log_error("Error loading tab", e)

    # ------------------------------------------------------------------ #
    #  STATUS BAR
    # ------------------------------------------------------------------ #
    def _init_status_bar(self, layout: QVBoxLayout) -> None:
        """Initialize bottom status bar."""
        try:
            self.status_bar = QStatusBar(self)
            self.status_bar.showMessage("Welcome to StellarBot ✨")

            # Optional: Auto-refresh time every 30s
            timer = QTimer(self)
            timer.timeout.connect(lambda: self.status_bar.showMessage(f"⏰ {QApplication.applicationName()} running..."))
            timer.start(30000)

            layout.addWidget(self.status_bar)
        except Exception as e:
            self._log_error("Error initializing status bar", e)

    # ------------------------------------------------------------------ #
    #  ACTIONS
    # ------------------------------------------------------------------ #
    def open_file(self) -> None:
        self.status_bar.showMessage("📂 Opening file...")
        QMessageBox.information(self, "Open File", "File loading coming soon.")

    def save_file(self) -> None:
        self.status_bar.showMessage("💾 Saving file...")
        QMessageBox.information(self, "Save File", "Save feature coming soon.")

    def close_application(self) -> None:
        self.status_bar.showMessage("🚪 Exiting StellarBot...")
        QMessageBox.information(self, "Exit", "Application will close now.")
        if hasattr(self.controller, "close"):
            self.controller.close()

    def show_about(self) -> None:
        QMessageBox.about(
            self,
            "About StellarBot",
            "✨ StellarBot v2.1\nAI-driven trading and analytics platform.\n© 2025 Sopotek Technologies.",
        )

    # ------------------------------------------------------------------ #
    #  HELPERS
    # ------------------------------------------------------------------ #
    def _safe_execute(self, func) -> None:
        """Run menu action safely with logging."""
        try:
            func()
        except Exception as e:
            self._log_error(f"Error executing {func.__name__}", e)

    def _log_error(self, message: str, exception: Exception) -> None:
        """Log errors with traceback."""
        self.logger.error(f"{message}: {exception}", exc_info=True)
        QMessageBox.critical(self, "Error", f"{message}\n{exception}")
