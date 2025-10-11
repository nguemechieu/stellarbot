from __future__ import annotations

from functools import partial
from typing import Type

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFrame, QMenuBar,
    QMessageBox, QStatusBar, QApplication, QLabel
)

# --- Import frames safely ---
from src.modules.frames.assets_frame import AssetsFrame
from src.modules.frames.charts import Charts
from src.modules.frames.dashboard import Dashboard
from src.modules.frames.effects_frame import EffectsFrame
from src.modules.frames.forex_news import ForexNews
from src.modules.frames.ledger import Ledger
from src.modules.frames.liquidity_pool import LiquidityPool
from src.modules.frames.market_assets_frame import MarketAssetsFrame
from src.modules.frames.offers import Offers
from src.modules.frames.order_history import OrdersHistory
from src.modules.frames.orderbook_frame import OrderBookFrame
from src.modules.frames.payments import Payments
from src.modules.frames.risk_management import RiskManagement
from src.modules.frames.trading_analytics_analytics import TradingAnalysis

from src.modules.frames.trading_strategies import TradingStrategies
from src.modules.frames.transactions import Transactions


class Home(QFrame):
    """🏠 Main StellarBot workspace — Menu + Tabs + Status bar."""

    def __init__(self, parent: QWidget | None, controller):
        super().__init__(parent)
        self.controller = controller
        self.logger = getattr(controller, "logger", None)

        self.menu_bar: QMenuBar | None = None
        self.tab_widget: QTabWidget | None = None
        self.status_bar: QStatusBar | None = None

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._init_menu_bar(layout)
        self._init_tabs(layout)
        self._init_status_bar(layout)

    # ------------------------------------------------------------------ #
    #  MENU BAR
    # ------------------------------------------------------------------ #
    def _init_menu_bar(self, layout: QVBoxLayout) -> None:
        try:
            self.menu_bar = QMenuBar(self)
            self.menu_bar.setNativeMenuBar(False)

            file_menu = self.menu_bar.addMenu("&File")
            self._add_action(file_menu, "Open…", self.open_file, "document-open")
            self._add_action(file_menu, "Save…", self.save_file, "document-save")
            file_menu.addSeparator()
            self._add_action(file_menu, "Exit", self.close_application, "application-exit")

            self.menu_bar.addMenu("&Edit")
            self.menu_bar.addMenu("&Tools")
            self.menu_bar.addMenu("&View")
            self.menu_bar.addMenu("&Settings")

            help_menu = self.menu_bar.addMenu("&Help")
            self._add_action(help_menu, "About StellarBot", self.show_about, "help-about")

            layout.addWidget(self.menu_bar)
        except Exception as e:
            self._log_error("Error initializing menu bar", e)

    def _add_action(self, menu, name: str, func, icon_name: str | None = None) -> QAction:
        icon = QIcon.fromTheme(icon_name) if icon_name else QIcon()
        action = QAction(icon, name, self)
        action.triggered.connect(partial(self._safe_execute, func))
        menu.addAction(action)
        return action

    # ------------------------------------------------------------------ #
    #  TABS
    # ------------------------------------------------------------------ #
    def _init_tabs(self, layout: QVBoxLayout) -> None:
        try:
            self.tab_widget = QTabWidget(self)
            self.tab_widget.setTabPosition(QTabWidget.North)
            self.tab_widget.setMovable(True)
            self.tab_widget.setDocumentMode(True)
            self.tab_widget.setUsesScrollButtons(True)

            self.tab_frames: dict[str, Type[QWidget]] = {
                "Dashboard": Dashboard,
                "Account Assets":AssetsFrame,
                "Market Assets": MarketAssetsFrame,
                "OrderBook": OrderBookFrame,
                "DexCharting": Charts,
                "Risk Management": RiskManagement,
                "Offers": Offers,
                "Effects": EffectsFrame,
                "Transactions": Transactions,
                "History": OrdersHistory,
                "Analysis": TradingAnalysis,
                "Forex News": ForexNews,
                "Strategies": TradingStrategies,

                "Liquidity Pool": LiquidityPool,
                "Payments": Payments,
                "Ledger": Ledger,
            }

            # Create lazy-load placeholders
            for tab_name in self.tab_frames:
                placeholder = QLabel(f"⏳ Loading {tab_name}…")
                placeholder.setAlignment(Qt.AlignCenter)
                self.tab_widget.addTab(placeholder, tab_name)

            self.tab_widget.currentChanged.connect(self._on_tab_changed)
            layout.addWidget(self.tab_widget)
        except Exception as e:
            self._log_error("Error initializing tabs", e)

    def _on_tab_changed(self, index: int):
        """Lazy-load the actual frame when first selected."""
        try:
            widget = self.tab_widget.widget(index)
            tab_name = self.tab_widget.tabText(index)

            if isinstance(widget, QLabel):  # not yet loaded
                frame_class = self.tab_frames.get(tab_name)
                if not frame_class:
                    self._log_error("Tab frame missing", tab_name)
                    return

                container = QWidget()
                layout = QVBoxLayout(container)
                layout.setContentsMargins(6, 6, 6, 6)
                layout.setSpacing(1)

                try:
                    frame = frame_class(container, self.controller)
                    if frame is None or not isinstance(frame, QWidget):
                        raise TypeError(f"{tab_name} did not return a QWidget instance")
                except Exception as fe:
                    self._log_error(f"Error loading frame {tab_name}", fe)
                    err_label = QLabel(f"❌ Failed to load {tab_name}.\n{fe}")
                    err_label.setAlignment(Qt.AlignCenter)
                    layout.addWidget(err_label)
                    frame = None

                if frame:
                    layout.addWidget(frame)

                self.tab_widget.removeTab(index)
                self.tab_widget.insertTab(index, container, tab_name)
                self.tab_widget.setCurrentIndex(index)
                if self.logger:
                    self.logger.info(f"✅ Loaded {tab_name} tab successfully.")
        except Exception as e:
            self._log_error("Error loading tab", e)

    # ------------------------------------------------------------------ #
    #  STATUS BAR
    # ------------------------------------------------------------------ #
    def _init_status_bar(self, layout: QVBoxLayout) -> None:
        try:
            self.status_bar = QStatusBar(self)
            self.status_bar.showMessage("Welcome to StellarBot ✨")

            timer = QTimer(self)
            timer.timeout.connect(
                lambda: self.status_bar.showMessage(
                    f"⏰ {QApplication.applicationName()} running..."
                )
            )
            timer.start(30000)

            layout.addWidget(self.status_bar)
        except Exception as e:
            self._log_error("Error initializing status bar", e)

    # ------------------------------------------------------------------ #
    #  ACTIONS
    # ------------------------------------------------------------------ #
    def open_file(self):
        self.status_bar.showMessage("📂 Opening file...")
        QMessageBox.information(self, "Open File", "File loading coming soon.")

    def save_file(self):
        self.status_bar.showMessage("💾 Saving file...")
        QMessageBox.information(self, "Save File", "Save feature coming soon.")

    def close_application(self):
        self.status_bar.showMessage("🚪 Exiting StellarBot...")
        QMessageBox.information(self, "Exit", "Application will close now.")
        if hasattr(self.controller, "close"):
            self.controller.close()
        else:
            QApplication.quit()

    def show_about(self):
        QMessageBox.about(
            self,
            "About StellarBot",
            "✨ StellarBot v2.1\nAI-driven trading and analytics platform.\n© 2025 Sopotek Technologies.",
        )

    # ------------------------------------------------------------------ #
    #  HELPERS
    # ------------------------------------------------------------------ #
    def _safe_execute(self, func):
        try:
            func()
        except Exception as e:
            self._log_error(f"Error executing {func.__name__}", e)

    def _log_error(self, message: str, exception: Exception):
        if self.logger:
            self.logger.error(f"{message}: {exception}", exc_info=True)
        QMessageBox.critical(self, "Error", f"{message}\n{exception}")
