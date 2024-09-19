from PyQt5 import QtWidgets
from modules.frames.dashboard import Dashboard
from modules.frames.account_overview import AccountOverview
from modules.frames.asset_portfolio import AssetPortfolio
from modules.frames.order_history import OrderHistory
from modules.frames.payments import Payments
from modules.frames.performance_analytics import PerformanceAnalytics
from modules.frames.risk_management import RiskManagement
from modules.frames.trades import Trades
from modules.frames.wallet import Wallet
from modules.frames.trading_charts import TradingCharts
from modules.frames.offers import Offers


class Home(QtWidgets.QWidget):
    """Main frame of the application containing tabs, menu bar, and widgets."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller

        # Set layout and background
        self.setGeometry(
            0, 0,1530,780
        )
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)

        # Create Menu and Tabs
        self.create_menu()
        self.create_tabs()

    def create_menu(self):
        """Create the menu bar with multiple useful tools and options."""
        menu_bar = QtWidgets.QMenuBar(self)

        # File Menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Open Account", lambda: self.controller.show_frame("AccountDetails"))
        file_menu.addAction("Close Account")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Cut")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")
        edit_menu.addAction("Select All")
        edit_menu.addSeparator()
        edit_menu.addAction("Find")
        edit_menu.addAction("Replace")

        # View Menu
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction("Charts")
        view_menu.addAction("Offers")
        view_menu.addAction("Order Book")

        # Tools Menu
        tools_menu = menu_bar.addMenu("Tools")
        tools_menu.addAction("Market Watch")
        tools_menu.addAction("Trade History")
        tools_menu.addAction("Order Management")
        tools_menu.addAction("Wallet Management")

    
        # Settings Menu
        settings_menu = menu_bar.addMenu("Settings")
        settings_menu.addAction("Preferences", lambda: self.controller.show_frame("SettingsPreferences"))

        # Help Menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("License", self.show_license)
        help_menu.addAction("Help Topics", lambda: self.controller.show_frame("Help"))
        help_menu.addSeparator()
        help_menu.addAction("About StellarBot", self.show_about)

        # Add menu bar to the layout
        layout = self.layout()
        layout.setMenuBar(menu_bar)

    def create_tabs(self):
        """Create the tabs and their respective frames."""
        tab_widget = QtWidgets.QTabWidget(self)
        tab_widget.setStyleSheet("background-color: #1e2a38;")

        # Helper to add each tab
        def add_tab(title, widget_class):
            tab = QtWidgets.QWidget()
            widget_class(tab, self.controller)
            tab_widget.addTab(tab, title)

        # Add all the tabs
        add_tab("Dashboard", Dashboard)
        add_tab("Account Overview", AccountOverview)
        add_tab("Asset Portfolio", AssetPortfolio)
        add_tab("Order History", OrderHistory)
        add_tab("Risk Management", RiskManagement)
        add_tab("Payments", Payments)
        add_tab("Trading Charts", TradingCharts)
        add_tab("Offers", Offers)
        add_tab("Trades", Trades)
        add_tab("Wallet", Wallet)
        add_tab("Performance Analytics", PerformanceAnalytics)

        # Add tabs to the layout
        self.layout().addWidget(tab_widget)

    def show_license(self):
        """Display license information for the software."""
        QtWidgets.QMessageBox.information(self, "License", "StellarBot is licensed under the MIT License.")

    def show_about(self):
        """Display information about the software."""
        QtWidgets.QMessageBox.information(self, "About StellarBot", "StellarBot v1.0.0\n\nStellar trading and analytics platform.")


