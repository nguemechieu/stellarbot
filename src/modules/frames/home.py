from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QFrame, QMenuBar

from src.modules.frames.account_overview import AccountOverview
from src.modules.frames.asset_portfolio import Portfolio
from src.modules.frames.dashboard import Dashboard
from src.modules.frames.effects import Effects
from src.modules.frames.offers import Offers
from src.modules.frames.trades import Trades
from src.modules.frames.transaction import Transaction
from src.modules.frames.wallet import Wallet


class Home(QFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.menu_bar = None
        self.tab_widget = None
        self.controller = controller
        self.bot = controller.bot
        self.layout = QVBoxLayout(self)


        self.init_menu_bar()
        self.init_tabs()
        self.layout.addStretch(2)

    def init_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        self.layout.addWidget(self.menu_bar)
        # File Menu
        file_menu = self.menu_bar.addMenu("File")
        file_menu.addAction("Open...")
        file_menu.addAction("Save As...")
        file_menu.addAction("Print...")
        file_menu.addSeparator()
        file_menu.addAction("Close")
        file_menu.addSeparator()
        file_menu.addSeparator()
        file_menu.addAction("Exit")

        # Edit Menu
        edit_menu = self.menu_bar.addMenu("Edit")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Cut")
        edit_menu.addAction("Copy")

        # View Menu
        view_menu = self.menu_bar.addMenu("View")
        view_menu.addAction("Zoom In")
        view_menu.addAction("Zoom Out")
        view_menu.addSeparator()
        view_menu.addAction("Screen Capture")
        view_menu.addSeparator()
        view_menu.addAction("Show Trading Pairs")
        view_menu.addAction("Show Market Data")
        view_menu.addAction("Show Performance")
        view_menu.addAction("Show Orders")
        view_menu.addAction("Show Wallet")
        view_menu.addAction("Show Transactions")
        view_menu.addAction("Show Ledgers")
        view_menu.addAction("Show Accounts")
        view_menu.addAction("Show Trades")
        view_menu.addAction("Show Order Book")
        view_menu.addSeparator()
        view_menu.addAction("Show Charts")

        # Chart Menu
        chart_menu = self.menu_bar.addMenu("Chart")
        chart_menu.addAction("Add Chart")
        chart_menu.addAction("Remove Chart")

        # Settings and Help Menus
        settings_menu = self.menu_bar.addMenu("Settings")
        settings_menu.addAction("Preferences")

        help_menu = self.menu_bar.addMenu("Help")
        help_menu.addAction("About")

    def init_tabs(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.layout.addWidget(self.tab_widget)

        tab_frames = {
            "Dashboard": Dashboard,
            "Account Overview": AccountOverview,
            # "Market Data": MarketData,
            # "Performance": Performance,
            # "Orders": Orders,
            #

            "Trades": Trades,
            "Offers": Offers,
             "Effects": Effects,
            "Portfolio": Portfolio,
            "Transactions": Transaction,
            "Wallet": Wallet,
            # "Account History": AccountHistory,
            # # "Address Book": AddressBook,

        }

        for tab_name, tab_class in tab_frames.items():
            tab = self.create_tab(tab_class)
            self.tab_widget.addTab(tab, tab_name)

    def create_tab(self, tab_class):
        tab = QWidget()


        tab.setAcceptDrops(
            # Enable drag and drop for widgets in this tab
            True
        )
        # Create and arrange widgets in the tab frame
        tab.setUpdatesEnabled(True)
        tab.setAccessibleName(tab_class.__name__)

        layout = QVBoxLayout(tab)

        # Dynamically instantiate frame class
        if tab_class:
            frame = tab_class(tab, self.controller)
            layout.addWidget(frame)

        return tab
