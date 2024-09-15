
import tkinter as tk
from tkinter import ttk
from stellar_sdk import Server, Asset

class OrderBook(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.place(x=0, y=0, width=1530, height=780)

        # Stellar Network Settings
        self.server = self.controller.bot.server
        # Order book data
       # self.order_book = self.controller.bot.orders

        # Create and arrange widgets in the frame
        self.create_widgets()

     

    def create_widgets(self):
        self.title_label = tk.Label(self, text="Order Book", font=("Helvetica", 18), pady=10)
        self.title_label.grid(row=1, column=0, columnspan=2)

        # Labels for bids and asks
        self.bids_label = tk.Label(self, text="Bids", font=("Helvetica", 14))
        self.bids_label.grid(row=2, column=0, padx=10, pady=5)

        self.asks_label = tk.Label(self, text="Asks", font=("Helvetica", 14))
        self.asks_label.grid(row=3, column=1, padx=10, pady=5)

        # Listboxes for bids and asks
        self.bids_listbox = tk.Listbox(self, height=300, width=30)
        self.bids_listbox.place(x=100, y=100, width=300, height=300)

        self.asks_listbox = tk.Listbox(self, height=300, width=30)
        self.asks_listbox.place(x=400, y=100, width=300, height=300)

        # Button to refresh order book
        self.refresh_button = tk.Button(self, text="Refresh", font=("Helvetica", 12), command=self.fetch_order_book)
        self.refresh_button.grid(row=3, column=0, columnspan=2, pady=10)

    def fetch_order_book(self):
    #    try:
            # Fetch the order book from the Stellar network
           

            # Clear previous entries
            self.bids_listbox.delete(0, tk.END)
            self.asks_listbox.delete(0, tk.END)

            # Display bids
        #     for bid in self.order_book['bids']:
        #         price = bid['price']
        #         amount = bid['amount']
        #         self.bids_listbox.insert(tk.END, f"Price: {price}, Amount: {amount}")

        #     # Display asks
        #     for ask in self.order_book['asks']:
        #         price = ask['price']
        #         amount = ask['amount']
        #         self.asks_listbox.insert(tk.END, f"Price: {price}, Amount: {amount}")

        # except Exception as e:
        #     print(f"Error fetching order book: {e}")
        #     self.bids_listbox.insert(tk.END, "Error fetching bids")
        #     self.asks_listbox.insert(tk.END, "Error fetching asks")
