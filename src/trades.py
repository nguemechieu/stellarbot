import tkinter as tk
from tkinter import ttk


class Trades(tk.Frame):
    """Frame to display trades from Stellar."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f8f9fa")  # Light background for a clean look
        self.place(x=0, y=0, width=1530, height=780)
        # Title label
        title_label = tk.Label(self, text="Trades", font=("Helvetica", 18, "bold"), fg="#343a40", bg="#f8f9fa")
        title_label.pack(pady=20)

        # Create the treeview (table) to display the trades
        columns = ("id", "buyer", "seller", "sold_asset", "bought_asset", "amount", "price")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)

        # Define column headers
        self.tree.heading("id", text="Trade ID")
        self.tree.heading("buyer", text="Buyer")
        self.tree.heading("seller", text="Seller")
        self.tree.heading("sold_asset", text="Sold Asset")
        self.tree.heading("bought_asset", text="Bought Asset")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("price", text="Price")

        # Set column widths
        self.tree.column("id", width=100)
        self.tree.column("buyer", width=200)
        self.tree.column("seller", width=200)
        self.tree.column("sold_asset", width=150)
        self.tree.column("bought_asset", width=150)
        self.tree.column("amount", width=100)
        self.tree.column("price", width=100)

        # Pack the treeview into the frame
        self.tree.pack(pady=20, fill="x")

        self.trades=self.controller.bot.trades_df

        # Display trades in the treeview
        for k,row in self.trades.iterrows():
            self.tree.insert("", "end", values=(
                row["id"],
                row.get('buyer', 'N/A'),
                  row.get("seller", 'N/A'),
                 row.get("sold_asset", 'N/A'),
                 row.get("bought_asset", 'N/A'),
                 row.get("amount", 0),
                 row.get("price", 0)  # Fetch asset details for each trade
              
            ))
            # Fetch asset details for each trade
           


