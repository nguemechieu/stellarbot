import tkinter as tk
from tkinter import ttk
import pandas as pd
import requests

class StellarExpert(tk.Frame):
    """This class represents the frame for Stellar asset data like assets, ranking, rates, etc."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.data = self.get_assets()  # Load data from a CSV file
        self.place(x=0, y=0, width=1530, height=750)
        self.create_widgets()

    def create_widgets(self):
        # Create a tab layout using ttk.Notebook
        self.tab_control = ttk.Notebook(self)

        # Create tabs
        self.assets_tab = tk.Frame(self.tab_control,width=1500, height=700)
        self.rankings_tab = tk.Frame(self.tab_control,width=1500, height=700)
        self.rates_tab = tk.Frame(self.tab_control,width=1500, height=700)

        # Add tabs to the tab control
        self.tab_control.add(self.assets_tab, text="Assets")
        self.tab_control.add(self.rankings_tab, text="Rankings")
        self.tab_control.add(self.rates_tab, text="Rates")

        self.tab_control.pack(expand=1, fill="both")

        # Set up the content for each tab
        self.setup_assets_tab()
        self.setup_rankings_tab()
        self.setup_rates_tab()

        self.display_data_in_treeview(self.data)

    
    def display_data_in_treeview(self,data):
    # Create the main window
  

    # Create the TreeView widget
     self.tree = ttk.Treeview(self, columns=("value"), show="tree")
     self.tree.pack(fill="both", expand=True)

    # Define the columns
     self.tree.heading("#0", text="Attribute")
     self.tree.heading("value", text="Value")

    # Add data to the TreeView
    def insert_treeview(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                item = self.tree.insert('', "end", text=key, open=True)
                self.insert_treeview( value)
            elif isinstance(value, list):
                item = self.tree.insert('', "end", text=key, open=True)
                for i, sub_value in enumerate(value):
                    self.insert_treeview(data= {f"Item {i}": sub_value})
            else:
                self.tree.insert('', "end", text=key, values=(value,))

    # Insert the data
        for i, record in enumerate(data):
         record_id = self.tree.insert("", "end", text=f"Record {i + 1}", open=True)
         self.insert_treeview( record)

    def setup_assets_tab(self):
        # Frame for the Assets tab
        tk.Label(self.assets_tab, text="List of Assets", font=("Arial", 16)).pack(pady=10)
        
        # Create Treeview for displaying asset data
        self.assets_tree = ttk.Treeview(self.assets_tab, columns=("asset", "issuer", "supply"), show='headings')
        
        # Define columns
        self.assets_tree.heading("asset", text="Asset")
        self.assets_tree.heading("issuer", text="Issuer")
        self.assets_tree.heading("supply", text="Supply")

        self.assets_tree.pack(fill=tk.BOTH, expand=True)
        
        # Populate the Treeview with data from Stellar Expert API
        self.populate_assets()

    def setup_rankings_tab(self):
        tk.Label(self.rankings_tab, text="Asset Rankings", font=("Arial", 16)).pack(pady=10)
        self.rankings_listbox = tk.Listbox(self.rankings_tab)
        self.rankings_listbox.pack(fill=tk.BOTH, expand=True)

        # Populate the rankings listbox with data
        self.populate_rankings()

    def setup_rates_tab(self):
        tk.Label(self.rates_tab, text="Asset Rates", font=("Arial", 16)).pack(pady=10)
        self.rates_listbox = tk.Listbox(self.rates_tab)
        self.rates_listbox.pack(fill=tk.BOTH, expand=True)

        # Populate the rates listbox with data
        self.populate_rates()

    def populate_assets(self):
        # Fetch assets from Stellar Expert API and populate the Treeview
        assets = self.get_assets()
        if assets is not None:
            assets.to_csv("ledger_assets.csv", index=False)

            for index, asset in assets.iterrows():
                # Insert each asset record into the Treeview

                asset_value = asset.get('asset')

# Split the value by a delimiter, e.g., '-'
                parts = str(asset_value).split(' ')[0][1]
                self.assets_tree.insert('', tk.END, values=(
                    asset.get('asset'),
                    parts,
                   
                    asset.get('supply')
                ))

    def populate_rankings(self):
        # Placeholder for rankings data (can be extended)
        rankings = ["Asset A - Rank 1", "Asset B - Rank 2", "Asset C - Rank 3"]
        for rank in rankings:
            self.rankings_listbox.insert(tk.END, rank)

    def populate_rates(self):
        # Placeholder for rates data (can be extended)
        rates = ["Asset A - Rate 0.05", "Asset B - Rate 0.10", "Asset C - Rate 0.20"]
        for rate in rates:
            self.rates_listbox.insert(tk.END, rate)

    def get_assets(self):
        # API call to Stellar Expert to retrieve asset data
        try:
            response = requests.get('https://api.stellar.expert/explorer/public/asset')
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            self.data = response.json()
            records = self.data['_embedded']['records']
            df = pd.DataFrame(records)
            
            # Add missing columns if necessary
            missing_columns = [
                'issuer', 'amount', 'flags', 'account_count', 'balance',
                'offers_count', 'data', 'created', 'paging_token', 'total_issuances',
                'total_burns', 'total_transfers', 'total_offers', 'total_liabilities',
                'total_trustlines', 'total_signers', 'trustlines', 'payments', 'domain',
                'rating', 'volume7d', 'tomlInfo', 'price7d'
            ]
            for column in missing_columns:
                if column not in df.columns:
                    df[column] = pd.NA
            
            return df
        
        except requests.RequestException as e:
            print(f"Error fetching asset data: {e}")
            return None
