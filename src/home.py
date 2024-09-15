import tkinter as tk
from tkinter import ttk



from dashboard import Dashboard
from account_details import AccountDetails
from offers import Offers
from payments import Payments
from trades import Trades
from stellar_expert import StellarExpert

from transaction import Transaction
from order_book import OrderBook


class Home(tk.Frame):
    """Main frame of the application containing tabs and widgets."""

    def __init__(self, parent, controller):
        super().__init__(parent)  # Initialize parent class correctly
        self.controller = controller
        self.parent = parent

        # Set a layout and background
        self.configure(bg="#1e2a38")
        self.grid(row=0, column=0, sticky="nsew")

        self.place(x=0, y=0, width=1530, height=780)

        # Create Menu
        self.create_menu()

        # Create and style the tabs
        self.create_tabs()

    def create_menu(self):
        """Create the menu bar."""
        menu_bar = tk.Menu(self.parent)
        self.parent.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Account", command=lambda: self.controller.show_frame("AccountDetails"))
        file_menu.add_command(label="Transaction History", command=lambda: self.controller.show_frame("TransactionHistory"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: self.controller.show_frame("About"))
        menu_bar.add_cascade(label="Help", menu=help_menu)

        chart_menu = tk.Menu(menu_bar, tearoff=0)
        chart_menu.add_command(label="Line Chart", command=lambda: self.controller.show_frame("LineChart"))
        chart_menu.add_command(label="Bar Chart", command=lambda: self.controller.show_frame("BarChart"))
        chart_menu.add_command(label="Pie Chart", command=lambda: self.controller.show_frame("PieChart"))
        menu_bar.add_cascade(label="Charts", menu=chart_menu)

        zoom_menu = tk.Menu(menu_bar, tearoff=0)
        zoom_menu.add_command(label="Zoom In", command=lambda: self.controller.show_frame("ZoomIn"))
        zoom_menu.add_command(label="Zoom Out", command=lambda: self.controller.show_frame("ZoomOut"))
        menu_bar.add_cascade(label="Zoom", menu=zoom_menu)


        about_menu = tk.Menu(menu_bar, tearoff=0)
        about_menu.add_command(label="About StellarBot", command=lambda: self.controller.show_frame("About"))

        help_menu = tk.Menu(menu_bar, tearoff= 0)
        help_menu.add_command(label="Help", command=lambda: self.controller.show_frame("Help"))

    def create_tabs(self):
        """Create the tabs and their respective frames."""
        tab_control = ttk.Notebook(self)  # Use `self` as the parent
        tab_control.grid(row=0, column=0, sticky="nsew")

        # Define the different tabs
        dashboard_tab = tk.Frame(tab_control,width=1500, height=700)
        Dashboard(dashboard_tab,self.controller)



        account_details_tab = tk.Frame(tab_control,width=1500, height=700)
        AccountDetails(account_details_tab,self.controller)



        payment_details_tab = tk.Frame(tab_control,width=1500, height=700)

        Payments(payment_details_tab,self.controller)
        offers_tab = tk.Frame(tab_control,width=1500, height=700)
        Offers(offers_tab,self.controller)

        trades_tab = tk.Frame(tab_control, width=1500, height=700)
        Trades(trades_tab,self.controller)

        
        performance_analytics_tab = tk.Frame(tab_control,width=1500, height=700)
        stellar_experts_tab = tk.Frame(tab_control,width=1500, height=700)
        
        trust_lines_tab = tk.Frame(tab_control,width=1500, height=700)
        StellarExpert(trust_lines_tab,self.controller)
        wallet_tab = tk.Frame(tab_control,width=1500, height=700)
        Transaction(wallet_tab,self.controller)
        order_tab = tk.Frame(tab_control,width=1500, height=700)
        OrderBook(order_tab,self.controller)
        transactions_tab = tk.Frame(tab_control,width=1500, height=700)
        Transaction(transactions_tab,self.controller)

        # Add the tabs and their respective frames
        tab_control.add(dashboard_tab, text='Dashboard')
        tab_control.add(account_details_tab, text='Account Details')
        tab_control.add(payment_details_tab, text='Payment Details')
        tab_control.add(offers_tab, text='Offers')
        tab_control.add(order_tab, text='Order Details')
        tab_control.add(transactions_tab, text='Transactions')
        tab_control.add(trades_tab, text='Trades')
        tab_control.add(trust_lines_tab, text='Trust Lines')
        tab_control.add(stellar_experts_tab, text=' Stellar-Experts')
        tab_control.add(performance_analytics_tab, text='Performance Analytics')
        tab_control.add(wallet_tab, text='Wallet')

        # Optionally add widgets to each tab here
        #  a label in the dashboard tab
        tk.Label(dashboard_tab, text="Welcome to the Dashboard", bg="green").pack(padx=10, pady=10)

        # Configure grid for the `Home` frame
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)
