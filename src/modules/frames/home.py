<<<<<<< Updated upstream
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFrame, QMenuBar, QAction, QMessageBox, QStatusBar
=======
from __future__ import annotations

from functools import partial
from typing import Type

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame, QMenuBar,
    QMessageBox, QStatusBar, QApplication, QLabel, QScrollArea
>>>>>>> Stashed changes
)

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
<<<<<<< Updated upstream
from src.modules.frames.trading_charts import TradingCharts
from src.modules.frames.trading_strategies import TradingStrategies
from src.modules.frames.transactions import Transactions
from src.modules.frames.trusted_assets import TrustedAsset


class Home(QFrame):
    def __init__(self, parent, controller):
=======
from src.modules.frames.trading_strategies import TradingStrategies
from src.modules.frames.transactions import Transactions
from src.modules.frames.modern_ui import ModernTabs, ModernButton, ModernButton, ModernHeader


class Home(QFrame):
    """🏠 Professional Trading Dashboard with tabbed interface."""

    def __init__(self, parent: QWidget | None, controller):
>>>>>>> Stashed changes
        super().__init__(parent)
        try:
            self.setFrameShape(QFrame.StyledPanel)
            self.setFrameShadow(QFrame.Raised)
            self.setContentsMargins(0, 0, 0, 0)

<<<<<<< Updated upstream
            self.controller = controller
            self.logger = controller.logger
            self.bot = controller.bot

            self.layout = QVBoxLayout(self)
            self.menu_bar = None
            self.tab_widget = None
            self.status_bar = None
=======
        self.menu_bar: QMenuBar | None = None
        self.tab_widget: ModernTabs | None = None
        self.status_bar: QStatusBar | None = None
        self.active_tab_name = "Dashboard"

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Apply professional dark theme
        self.setStyleSheet("""
            QFrame {
                background-color: #0C0E13;
                color: #D1D5DB;
            }
            QMenuBar {
                background-color: #1F2937;
                color: #D1D5DB;
                border-bottom: 1px solid #374151;
            }
            QMenuBar::item:selected {
                background-color: #2563EB;
            }
            QMenu {
                background-color: #1F2937;
                color: #D1D5DB;
            }
            QMenu::item:selected {
                background-color: #2563EB;
            }
            QStatusBar {
                background-color: #131722;
                color: #9CA3AF;
                border-top: 1px solid #374151;
            }
        """)
>>>>>>> Stashed changes

            self.init_menu_bar()
            self.init_tabs()
            self.init_status_bar()

            self.setLayout(self.layout)
        except Exception as e:
            self.log_error("Error initializing Home widget", e)

    def init_menu_bar(self):
        try:
            self.menu_bar = QMenuBar(self)
<<<<<<< Updated upstream
            self.layout.addWidget(self.menu_bar)

            # File Menu
            file_menu = self.menu_bar.addMenu("File")
            open_action = QAction("Open...", self)
            open_action.triggered.connect(self.open_file)
            file_menu.addAction(open_action)

            save_action = QAction("Save...", self)
            save_action.triggered.connect(self.save_file)
            file_menu.addAction(save_action)
            file_menu.addSeparator()

            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.close_application)
            file_menu.addAction(exit_action)

            # Other Menus (Edit, Tools, etc.)
            edit_menu = self.menu_bar.addMenu("Edit")
            tools_menu = self.menu_bar.addMenu("Tools")
            view_menu = self.menu_bar.addMenu("View")
            settings_menu = self.menu_bar.addMenu("Settings")
            help_menu = self.menu_bar.addMenu("Help")
=======
            self.menu_bar.setNativeMenuBar(False)
            self.menu_bar.setStyleSheet("""
                QMenuBar {
                    background-color: #1F2937;
                    color: #D1D5DB;
                    border-bottom: 1px solid #374151;
                    padding: 4px;
                }
                QMenuBar::item:selected {
                    background-color: #2563EB;
                    border-radius: 4px;
                }
            """)

            # File Menu
            file_menu = self.menu_bar.addMenu("📁 File")
            self._add_action(file_menu, "🔄 Refresh All", self.refresh_all_data, None)
            file_menu.addSeparator()
            self._add_action(file_menu, "❌ Exit", self.close_application, None)

            # Edit Menu
            edit_menu = self.menu_bar.addMenu("⚙️ Edit")
            self._add_action(edit_menu, "⚙️ Settings", self.show_settings, None)
            self._add_action(edit_menu, "🎨 Preferences", self.show_preferences, None)
            
            # View Menu
            view_menu = self.menu_bar.addMenu("👁️ View")
            self._add_action(view_menu, "🔄 Refresh Current", self.refresh_data, None)
            view_menu.addSeparator()
            self._add_action(view_menu, "🌙 Dark Theme", lambda: self.set_theme("dark"), None)
            self._add_action(view_menu, "☀️ Light Theme", lambda: self.set_theme("light"), None)

            # Help Menu
            help_menu = self.menu_bar.addMenu("❓ Help")
            self._add_action(help_menu, "ℹ️ About", self.show_about, None)
            self._add_action(help_menu, "📖 Documentation", self.show_help, None)
>>>>>>> Stashed changes

            # Example Help Action
            about_action = QAction("About StellarBot", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)

            self.menu_bar.setNativeMenuBar(True)
        except Exception as e:
            self.log_error("Error initializing menu bar", e)

    def init_tabs(self):
        try:
<<<<<<< Updated upstream
            self.tab_widget = QTabWidget()
            self.tab_widget.setTabPosition(QTabWidget.North)

            tab_frames = {
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
                "LiquidityPool": LiquidityPool,
                "Payments": Payments,
                "Send Money": SendMoney,
                "Fees Analysis": FeesAnalysis,
                "Ledger": Ledger
            }

            for tab_name, tab_class in tab_frames.items():
                tab = self.create_tab(tab_class)
                if tab:
                    self.tab_widget.addTab(tab, tab_name)

            self.layout.addWidget(self.tab_widget)
=======
            self.tab_widget = ModernTabs(self)
            self.tab_widget.setTabPosition(QTabWidget.North)
            self.tab_widget.setMovable(True)
            self.tab_widget.setDocumentMode(True)
            self.tab_widget.setUsesScrollButtons(True)
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #374151;
                    background-color: #0C0E13;
                }
                QTabBar::tab {
                    background-color: #1F2937;
                    color: #9CA3AF;
                    padding: 8px 16px;
                    border: 1px solid #374151;
                    border-bottom: none;
                    margin-right: 2px;
                    font-weight: 600;
                }
                QTabBar::tab:selected {
                    background-color: #2563EB;
                    color: #FFFFFF;
                    border-bottom: 2px solid #3B82F6;
                }
                QTabBar::tab:hover {
                    background-color: #2D3748;
                }
            """)

            self.tab_frames: dict[str, Type[QWidget]] = {
                "📊 Dashboard": Dashboard,
                "💎 Assets": AssetsFrame,
                "🌍 Market": MarketAssetsFrame,
                "📈 OrderBook": OrderBookFrame,
                "📉 Charts": Charts,
                "🛡️ Risk": RiskManagement,
                "🏷️ Offers": Offers,
                "⚡ Effects": EffectsFrame,
                "📝 Transactions": Transactions,
                "📋 History": OrdersHistory,
                "🎯 Analysis": TradingAnalysis,
                "📰 News": ForexNews,
                "🤖 Strategies": TradingStrategies,
                "🏊 Liquidity": LiquidityPool,
                "💳 Payments": Payments,
                "📚 Ledger": Ledger,
            }

            # Create lazy-load placeholders with better styling
            for tab_name in self.tab_frames:
                placeholder = QLabel(f"⏳ Loading {tab_name}…")
                placeholder.setAlignment(Qt.AlignCenter)
                placeholder_font = QFont()
                placeholder_font.setPointSize(12)
                placeholder.setFont(placeholder_font)
                placeholder.setStyleSheet("color: #9CA3AF;")
                self.tab_widget.addTab(placeholder, tab_name)

            self.tab_widget.currentChanged.connect(self._on_tab_changed)
            layout.addWidget(self.tab_widget, 1)
>>>>>>> Stashed changes
        except Exception as e:
            self.log_error("Error initializing tabs", e)

    def create_tab(self, tab_class):
        try:
<<<<<<< Updated upstream
            tab = QWidget()
            layout = QVBoxLayout(tab)

            # Dynamically instantiate the frame class
            if tab_class:
                frame = tab_class(tab, self.controller)
                layout.addWidget(frame)

            return tab
=======
            widget = self.tab_widget.widget(index)
            tab_name = self.tab_widget.tabText(index)
            self.active_tab_name = tab_name
            
            # Update status bar
            if self.status_bar:
                self.status_bar.showMessage(f"📍 Active: {tab_name}")

            if isinstance(widget, QLabel):  # not yet loaded
                frame_class = self.tab_frames.get(tab_name)
                if not frame_class:
                    if self.logger:
                        self.logger.error(f"Tab frame missing: {tab_name}")
                    return

                # Show loading indicator
                if self.status_bar:
                    self.status_bar.showMessage(f"⏳ Loading {tab_name}…")

                container = QWidget()
                container.setStyleSheet("background-color: #0C0E13;")
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)

                try:
                    frame = frame_class(container, self.controller)
                    if frame is None or not isinstance(frame, QWidget):
                        raise TypeError(f"{tab_name} did not return a QWidget instance")
                except Exception as fe:
                    if self.logger:
                        self.logger.error(f"Error loading frame {tab_name}: {fe}", exc_info=True)
                    err_label = QLabel(f"❌ Failed to load {tab_name}.\n\n{str(fe)[:100]}")
                    err_label.setAlignment(Qt.AlignCenter)
                    err_label.setStyleSheet("color: #EF4444; font-size: 12px;")
                    layout.addWidget(err_label)
                    frame = None

                if frame:
                    layout.addWidget(frame)

                self.tab_widget.removeTab(index)
                self.tab_widget.insertTab(index, container, tab_name)
                self.tab_widget.setCurrentIndex(index)
                
                if self.logger:
                    self.logger.info(f"✅ Loaded {tab_name} tab successfully.")
                if self.status_bar:
                    self.status_bar.showMessage(f"✅ {tab_name} loaded")
>>>>>>> Stashed changes
        except Exception as e:
            self.log_error(f"Error creating tab {tab_class.__name__}", e)
            return None

    def init_status_bar(self):
        try:
            self.status_bar = QStatusBar(self)
<<<<<<< Updated upstream
            self.layout.addWidget(self.status_bar)
            self.status_bar.showMessage("Welcome to StellarBot!")
        except Exception as e:
            self.log_error("Error initializing status bar", e)

    def open_file(self):
        self.status_bar.showMessage("Opening file...")
        QMessageBox.information(self, "Open File", "This feature is not yet implemented.")

    def save_file(self):
        self.status_bar.showMessage("Saving file...")
        QMessageBox.information(self, "Save File", "This feature is not yet implemented.")

    def close_application(self):
        self.status_bar.showMessage("Exiting application...")
        QMessageBox.information(self, "Exit", "Application will close.")
        self.controller.close()  # Assuming `controller` has a `close` method.

    def show_about(self):
        QMessageBox.about(self, "About StellarBot", "StellarBot v1.0\nA comprehensive trading platform.")

    def log_error(self, message, exception):
        self.logger.error(f"{message}: {exception}", exc_info=True)
=======
            self.status_bar.setStyleSheet("""
                QStatusBar {
                    background-color: #131722;
                    color: #9CA3AF;
                    border-top: 1px solid #374151;
                    padding: 4px 8px;
                    font-size: 11px;
                }
            """)
            self.status_bar.showMessage("🟢 Ready | Select a tab to begin")

            # Status update timer
            timer = QTimer(self)
            timer.timeout.connect(self._update_status)
            timer.start(60000)  # Update every 60 seconds

            layout.addWidget(self.status_bar)
        except Exception as e:
            self._log_error("Error initializing status bar", e)
    
    def _update_status(self):
        """Update status bar with current state."""
        if self.status_bar:
            app_name = QApplication.applicationName() or "Trading Dashboard"
            self.status_bar.showMessage(f"🟢 {app_name} | Active: {self.active_tab_name}")

    # ------------------------------------------------------------------ #
    #  ACTIONS
    # ------------------------------------------------------------------ #
    def close_application(self):
        """Close the application with confirmation."""
        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.status_bar.showMessage("👋 Closing application...")
            if hasattr(self.controller, "close"):
                self.controller.close()
            else:
                QApplication.quit()

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Trading Dashboard",
            "🚀 Professional Trading Platform\n"
            "Version 2.1\n\n"
            "AI-powered Stellar DEX trading and analytics.\n"
            "© 2025 All Rights Reserved",
        )

    def show_settings(self):
        """Navigate to settings."""
        self.status_bar.showMessage("⚙️ Opening settings...")
        if hasattr(self.controller, "show_frame"):
            try:
                self.controller.show_frame("Preferences")
                self.status_bar.showMessage("✅ Settings opened")
            except Exception as e:
                self.status_bar.showMessage(f"❌ Cannot open settings: {str(e)[:40]}")
                if self.logger:
                    self.logger.error(f"Error opening settings: {e}")
        else:
            self.status_bar.showMessage("⚠️ Settings not available")

    def show_preferences(self):
        """Show preferences dialog."""
        QMessageBox.information(
            self,
            "Preferences",
            "User preferences panel coming soon..."
        )

    def show_help(self):
        """Navigate to help."""
        self.status_bar.showMessage("📖 Opening help...")
        if hasattr(self.controller, "show_frame"):
            try:
                self.controller.show_frame("Help")
                self.status_bar.showMessage("✅ Help opened")
            except Exception as e:
                self.status_bar.showMessage(f"❌ Cannot open help: {str(e)[:40]}")
                if self.logger:
                    self.logger.error(f"Error opening help: {e}")
        else:
            self.status_bar.showMessage("⚠️ Help not available")

    def refresh_data(self):
        """Refresh data in the current tab."""
        self.status_bar.showMessage("🔄 Refreshing current tab...")
        try:
            current_index = self.tab_widget.currentIndex()
            if current_index >= 0:
                widget = self.tab_widget.widget(current_index)
                if hasattr(widget, "refresh") and callable(widget.refresh):
                    widget.refresh()
                    if self.logger:
                        self.logger.info(f"✅ {self.active_tab_name} refreshed.")
                    self.status_bar.showMessage(f"✅ {self.active_tab_name} refreshed")
                elif hasattr(widget, "populate_table") and callable(widget.populate_table):
                    widget.populate_table()
                    self.status_bar.showMessage(f"✅ {self.active_tab_name} refreshed")
                else:
                    self.status_bar.showMessage(f"⚠️ {self.active_tab_name} does not support refresh")
        except Exception as e:
            self._log_error("Error refreshing data", e)
            self.status_bar.showMessage(f"❌ Refresh failed: {str(e)[:40]}")

    def refresh_all_data(self):
        """Refresh data in all loaded tabs."""
        self.status_bar.showMessage("🔄 Refreshing all tabs...")
        count = 0
        try:
            for i in range(self.tab_widget.count()):
                widget = self.tab_widget.widget(i)
                if hasattr(widget, "refresh") and callable(widget.refresh):
                    try:
                        widget.refresh()
                        count += 1
                    except Exception:
                        pass
                elif hasattr(widget, "populate_table") and callable(widget.populate_table):
                    try:
                        widget.populate_table()
                        count += 1
                    except Exception:
                        pass
            self.status_bar.showMessage(f"✅ Refreshed {count} tabs")
            if self.logger:
                self.logger.info(f"✅ All {count} tabs refreshed.")
        except Exception as e:
            self._log_error("Error refreshing all data", e)
            self.status_bar.showMessage(f"❌ Refresh failed: {str(e)[:40]}")

    def set_theme(self, theme: str):
        """Set the application theme."""
        self.status_bar.showMessage(f"🎨 Switching to {theme} theme...")
        try:
            if hasattr(self.controller, "theme_manager"):
                self.controller.theme_manager.set_theme(theme)
                if self.logger:
                    self.logger.info(f"✅ Theme changed to {theme}.")
                self.status_bar.showMessage(f"✅ Theme: {theme}")
            else:
                self.status_bar.showMessage(f"⚠️ Theme switching not available")
        except Exception as e:
            self._log_error("Error setting theme", e)
            self.status_bar.showMessage(f"❌ Theme error: {str(e)[:40]}")

    # ------------------------------------------------------------------ #
    #  HELPERS
    # ------------------------------------------------------------------ #
    def _safe_execute(self, func):
        """Safely execute a function with error handling."""
        try:
            func()
        except Exception as e:
            self._log_error(f"Error executing {func.__name__}", e)

    def _log_error(self, message: str, exception: Exception):
        """Log error and show error dialog."""
        if self.logger:
            self.logger.error(f"{message}: {exception}", exc_info=True)
        error_text = str(exception)[:100] if exception else "Unknown error"
        QMessageBox.critical(self, "Error", f"{message}\n\n{error_text}")
        if self.status_bar:
            self.status_bar.showMessage(f"❌ Error: {message}")
>>>>>>> Stashed changes
