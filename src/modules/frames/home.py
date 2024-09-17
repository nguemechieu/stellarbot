import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Import messagebox for showing dialogs
from modules.frames.dashboard import Dashboard
from modules.frames.account_details import AccountDetails
from modules.frames. offers import Offers
from modules.frames.payments import Payments
from modules.frames.trades import Trades
from modules.frames.stellar_expert import StellarExpert
from modules.frames.transaction import Transaction
from modules.frames.order_book import OrderBook
from modules.frames.wallet import Wallet
from modules.frames.asset import Asset
from modules.frames.trading_charts import TradingCharts

class Home(tk.Frame):
    """Main frame of the application containing tabs, menu bar, and widgets."""

    def __init__(self, parent, controller):
        super().__init__(parent)  # Initialize parent class correctly
        self.controller = controller
        self.parent = parent

        # Set layout and background
        self.configure(bg='#1e2a38')
        self.grid(row=0, column=0, sticky="nsew")
        self.place(x=0, y=0, width=1530, height=780)

        # Create Menu
        self.create_menu()

        # Create and style the tabs
        self.create_tabs()

    def create_menu(self):
        """Create the menu bar with multiple useful tools and options."""
        menu_bar = tk.Menu(self.parent)
        self.parent.config(menu=menu_bar)

        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Account", command=lambda: self.controller.show_frame("AccountDetails"))
        file_menu.add_command(label="Transaction History", command=lambda: self.controller.show_frame("TransactionHistory"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # View Menu for different frames
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Charts")
        view_menu.add_command(label="Offers")
        view_menu.add_command(label="Order Book")
        menu_bar.add_cascade(label="View", menu=view_menu)

        # Tools Menu for specific tools like Trade History, Market Watch
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Market Watch")
        tools_menu.add_command(label="Trade History")
        tools_menu.add_command(label="Order Management")
        tools_menu.add_command(label="Wallet Management")
        menu_bar.add_cascade(label="Tools", menu=tools_menu)

        # Charts Menu for different chart options
        chart_menu = tk.Menu(menu_bar, tearoff=0)
        chart_menu.add_command(label="Line Chart", command=lambda: self.controller.show_frame("LineChart"))
        chart_menu.add_command(label="Bar Chart", command=lambda: self.controller.show_frame("BarChart"))
        chart_menu.add_command(label="Candlestick Chart", command=lambda: self.controller.show_frame("CandlestickChart"))
        chart_menu.add_command(label="Renko Chart")
        chart_menu.add_command(label="Heatmap Chart")


        menu_bar.add_cascade(label="Charts", menu=chart_menu)

        # Settings Menu for application settings
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Preferences", command=lambda: self.controller.show_frame("Preferences"))
        settings_menu.add_command(label="API Keys", command=lambda: self.controller.show_frame("APIKeys"))
        settings_menu.add_command(label="Stellar Expert", command=lambda: self.controller.show_frame("StellarExpert"))
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        # Help and License Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="License", command=self.show_license)
        help_menu.add_command(label="Help Topics", command=lambda: self.controller.show_frame("Help"))
        help_menu.add_separator()
        help_menu.add_command(label="About StellarBot", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

    def create_tabs(self):
        """Create the tabs and their respective frames."""
        tab_control = ttk.Notebook(self, width=1530, height=780)  # Use `self` as the parent
        tab_control.grid(row=0, column=0, sticky="nsew")

        # Define the different tabs
        dashboard_tab = tk.Frame(tab_control, width=1500, height=780)
        Dashboard(dashboard_tab, self.controller)

        account_details_tab = tk.Frame(tab_control, width=1500, height=780)
        AccountDetails(account_details_tab, self.controller)

        assets_tab = tk.Frame(tab_control, width=1500, height=780)
        Asset(assets_tab, self.controller)

        payment_details_tab = tk.Frame(tab_control, width=1500, height=780)
        Payments(payment_details_tab, self.controller)

        trading_charts_tab = tk.Frame( tab_control, width=1500, height = 780)
        TradingCharts(trading_charts_tab, self.controller)

        offers_tab = tk.Frame(tab_control, width=1500, height=780)
        Offers(offers_tab, self.controller)

        trades_tab = tk.Frame(tab_control, width=1500, height=780)
        Trades(trades_tab, self.controller)

        stellar_experts_tab = tk.Frame(tab_control, width=1500, height=780)
        StellarExpert(stellar_experts_tab, self.controller)

        order_tab = tk.Frame(tab_control, width=1500, height=780)
        OrderBook(order_tab, self.controller)

        transactions_tab = tk.Frame(tab_control, width=1500, height=780)
        Transaction(transactions_tab, self.controller)

        wallet_tab = tk.Frame(tab_control, width=1500, height=780)
        Wallet(wallet_tab, self.controller)
        trading_charts_tab = tk.Frame(tab_control, width=1500, height=780)
        TradingCharts(trading_charts_tab, self.controller)

        # Add the tabs and their respective frames
        tab_control.add(dashboard_tab, text='Dashboard')
        tab_control.add(account_details_tab, text='Account Details')
        tab_control.add(assets_tab, text='Assets')
        tab_control.add(trading_charts_tab, text='Trading Charts')
        tab_control.add(payment_details_tab, text='Payments')
        tab_control.add(offers_tab, text='Offers')
        tab_control.add(trades_tab, text='Trades')
        tab_control.add(order_tab, text='Order Book')
        tab_control.add(transactions_tab, text='Transactions')
        tab_control.add(stellar_experts_tab, text='Stellar Experts')
        tab_control.add(wallet_tab, text='Wallet')

        # Configure the frame's layout
        tk.Label(dashboard_tab, text="Welcome to the Dashboard", background='white', fg="green").pack(padx=10, pady=10)

    def show_license(self):
        """Display license information for the software."""
        messagebox.showinfo("License", "StellarBot is licensed under the MIT License.")

    def show_about(self):
        """Display information about the software."""
        messagebox.showinfo("About StellarBot", "StellarBot v1.0.0\n\nStellar trading and analytics platform.")

