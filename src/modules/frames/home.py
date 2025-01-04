from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QFrame, QMenuBar, QAction, QMessageBox, QStatusBar
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
from src.modules.frames.trading_charts import TradingCharts
from src.modules.frames.trading_strategies import TradingStrategies
from src.modules.frames.transactions import Transactions
from src.modules.frames.trusted_assets import TrustedAsset


class Home(QFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        try:
            self.setFrameShape(QFrame.StyledPanel)
            self.setFrameShadow(QFrame.Raised)
            self.setContentsMargins(0, 0, 0, 0)

            self.controller = controller
            self.logger = controller.logger
            self.bot = controller.bot

            self.layout = QVBoxLayout(self)
            self.menu_bar = None
            self.tab_widget = None
            self.status_bar = None

            self.init_menu_bar()
            self.init_tabs()
            self.init_status_bar()

            self.setLayout(self.layout)
        except Exception as e:
            self.log_error("Error initializing Home widget", e)

    def init_menu_bar(self):
        try:
            self.menu_bar = QMenuBar(self)
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

            # Example Help Action
            about_action = QAction("About StellarBot", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)

            self.menu_bar.setNativeMenuBar(True)
        except Exception as e:
            self.log_error("Error initializing menu bar", e)

    def init_tabs(self):
        try:
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
        except Exception as e:
            self.log_error("Error initializing tabs", e)

    def create_tab(self, tab_class):
        try:
            tab = QWidget()
            layout = QVBoxLayout(tab)

            # Dynamically instantiate the frame class
            if tab_class:
                frame = tab_class(tab, self.controller)
                layout.addWidget(frame)

            return tab
        except Exception as e:
            self.log_error(f"Error creating tab {tab_class.__name__}", e)
            return None

    def init_status_bar(self):
        try:
            self.status_bar = QStatusBar(self)
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
