import tkinter as tk
from tkinter import ttk
import requests
import json

class Offers(tk.Frame):
    """Frame to display offers from Stellar."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f8f9fa")  # Light background for a clean look
        self.place(x=0, y=0, width=1530, height=780)
        # Title label
        title_label = tk.Label(self, text="Offers", font=("Helvetica", 18, "bold"), fg="#343a40", bg="#f8f9fa")
        title_label.pack(pady=20)

        # Create the treeview (table) to display the offers
        columns = ("id", "seller", "selling_asset", "buying_asset", "amount", "price")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)

        # Define column headers
        self.tree.heading("id", text="Offer ID")
        self.tree.heading("seller", text="Seller")
        self.tree.heading("selling_asset", text="Selling Asset")
        self.tree.heading("buying_asset", text="Buying Asset")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("price", text="Price")

        # Set column widths
        self.tree.column("id", width=100)
        self.tree.column("seller", width=200)
        self.tree.column("selling_asset", width=150)
        self.tree.column("buying_asset", width=150)
        self.tree.column("amount", width=100)
        self.tree.column("price", width=100)

        # Pack the treeview into the frame
        self.tree.pack(pady=20, fill="x")

        # Fetch and display offers
        self.fetch_offers()

    def fetch_offers(self):
        """Fetch offer data from Stellar API and populate the treeview."""
        url = "https://horizon.stellar.org/accounts/GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN/offers"
        
        try:
            response = requests.get(url)
            offers_data = response.json()["_embedded"]["records"]
            
            # Insert offers into the treeview
            for offer in offers_data:
                offer_id = offer.get("id")
                seller = offer.get("seller")
                selling_asset = self.format_asset(offer["selling"])
                buying_asset = self.format_asset(offer["buying"])
                amount = offer.get("amount")
                price = offer.get("price")
                
                # Insert into the Treeview
                self.tree.insert("", "end", values=(offer_id, seller, selling_asset, buying_asset, amount, price))
        
        except Exception as e:
            print(f"Error fetching offers: {e}")

    def format_asset(self, asset):
        """Helper function to format the asset data."""
        if asset["asset_type"] == "native":
            return "XLM"
        return f'{asset["asset_code"]} ({asset["asset_issuer"][:5]}...)'


