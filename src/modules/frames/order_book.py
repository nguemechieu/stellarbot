import tkinter as tk
from tkinter import ttk
import pandas as pd
import requests
from stellar_sdk import Asset


# Define the schema structure
class MarketSchema:
    def __init__(self):
        self.bids = []
        self.asks = []
        self.base = {
            'asset_code': 'USD',
            'asset_issuer': 'GAAQ56B55K6276J2T67C5Z7Z356422J57443Z7A2',
            'asset_type': 'credit_alphanum4'
        }
        self.counter = {
            'asset_code': 'USDC',
            'asset_issuer': 'GAAQ56B55K6276J2T67C5Z7Z356422J57443Z7A2',
            'asset_type': 'credit_alphanum4'
        }

    def populate_bids(self, bids_data):
        """Populate bids list with data"""
        for bid in bids_data:
            self.bids.append({
                'price': bid['price'],
                'amount': bid['amount']
            })

    def populate_asks(self, asks_data):
        """Populate asks list with data"""
        for ask in asks_data:
            self.asks.append({
                'price': ask['price'],
                'amount': ask['amount']
            })

    def get_schema(self):
        """Return the complete schema"""
        return {
            'bids': self.bids,
            'asks': self.asks,
            'base': self.base,
            'counter': self.counter
        }


def fetch_market_data(base_asset, counter_asset):
    market_schema = MarketSchema()

    url = "https://horizon.stellar.org/order_book"
    params = {
        'base_asset_type': base_asset['asset_type'],
        'base_asset_code': base_asset['asset_code'],
        'base_asset_issuer': base_asset['asset_issuer'],
        'counter_asset_type': counter_asset['asset_type'],
        'counter_asset_code': counter_asset['asset_code'],
        'counter_asset_issuer': counter_asset['asset_issuer']
    }

    # Filter out None values from params
    params = {k: v for k, v in params.items() if v is not None}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Get bids and asks from the API response
        data = response.json()
        bids_data = data.get('bids', [])
        asks_data = data.get('asks', [])

        # Populate the schema
        market_schema.populate_bids(bids_data)
        market_schema.populate_asks(asks_data)
        return market_schema.get_schema()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching market data: {e}")
        return None


class OrderBook(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.place(x=0, y=0, width=1530, height=780)

        # Load the asset list
        self.assets_list = pd.read_csv('ledger_assets.csv')

        # Stellar Network Settings
        self.server = self.controller.bot.server
        self.config(background='#1e2a38')

        # Create and arrange widgets in the frame
        self.create_widgets()

    def create_widgets(self):
        self.title_label = tk.Label(self, text="Order Book", font=("Helvetica", 18), pady=10, fg="white", bg="#1e2a38")
        self.title_label.grid(row=0, column=0, columnspan=3)

        # Labels for bids and asks
        self.bids_label = tk.Label(self, text="Bids", font=("Helvetica", 14), fg="white", bg="#1e2a38")
        self.bids_label.grid(row=1, column=0, padx=10, pady=5)

        self.asks_label = tk.Label(self, text="Asks", font=("Helvetica", 14), fg="white", bg="#1e2a38")
        self.asks_label.grid(row=1, column=1, padx=10, pady=5)

        # Listboxes for bids and asks
        self.bids_listbox = tk.Listbox(self, height=15, width=40)
        self.bids_listbox.grid(row=2, column=0, padx=10, pady=10)

        self.asks_listbox = tk.Listbox(self, height=15, width=40)
        self.asks_listbox.grid(row=2, column=1, padx=10, pady=10)

        # Dropdown for base and counter assets
        self.base_asset_var = tk.StringVar(value="XLM")  # Default to XLM as base asset
        self.counter_asset_var = tk.StringVar(value="USD")  # Default to USD as counter asset

        tk.Label(self, text="Base Asset", font=("Helvetica", 12), fg="white", bg="#1e2a38").grid(row=3, column=0)

        self.base_asset_dropdown = ttk.Combobox(self, state="readonly")
        self.base_asset_dropdown['values'] = self.assets_list.get('code')
        self.base_asset_dropdown.grid(row=4, column=0, padx=10, pady=10)

        tk.Label(self, text="Counter Asset", font=("Helvetica", 12), fg="white", bg="#1e2a38").grid(row=3, column=1)
        self.counter_asset_dropdown = ttk.Combobox(self, state="readonly")
        self.counter_asset_dropdown['values'] = self.assets_list.get('code')
        self.counter_asset_dropdown.grid(row=4, column=1, padx=10, pady=10)

        # Button to refresh order book
        self.refresh_button = tk.Button(self, text="Refresh", font=("Helvetica", 12), command=self.fetch_order_book)
        self.refresh_button.grid(row=5, column=0, columnspan=2, pady=10)

    def fetch_order_book(self):
        # Get the selected assets from the dropdowns
        base_asset_code = self.base_asset_var.get()
        counter_asset_code = self.counter_asset_var.get()

        # Filter the selected base asset details
        base_asset = self.assets_list[self.assets_list['code'] == base_asset_code].iloc[0]
        counter_asset = self.assets_list[self.assets_list['code'] == counter_asset_code].iloc[0]

        # Construct asset details for base and counter assets
        base_asset = {
            'asset_code': base_asset['code'],
            'asset_issuer': base_asset['issuer'],
            'asset_type': base_asset['anchorAssetType']
        }

        counter_asset = {
            'asset_code': counter_asset['code'],
            'asset_issuer': counter_asset['issuer'],
            'asset_type': counter_asset['anchorAssetType']
        }

        

        # Fetch the order book data
        order_book_data = fetch_market_data(base_asset, counter_asset)

        if order_book_data:
            # Clear previous entries
            self.bids_listbox.delete(0, tk.END)
            self.asks_listbox.delete(0, tk.END)

            # Display bids
            for bid in order_book_data['bids']:
                price = bid['price']
                amount = bid['amount']
                self.bids_listbox.insert(tk.END, f"Price: {price}, Amount: {amount}")

            # Display asks
            for ask in order_book_data['asks']:
                price = ask['price']
                amount = ask['amount']
                self.asks_listbox.insert(tk.END, f"Price: {price}, Amount: {amount}")
        else:
            self.bids_listbox.insert(tk.END, "Error fetching bids")
            self.asks_listbox.insert(tk.END, "Error fetching asks")
