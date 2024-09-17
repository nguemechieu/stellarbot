import tkinter as tk
from tkinter import ttk
import requests

class Asset(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.place(x=0, y=0, width=1530, height=780)

        # Title label
        self.title_label = tk.Label(self, text="Asset List", font=("Helvetica", 18), pady=10)
        self.title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Create the Treeview widget
        self.asset_tree = ttk.Treeview(self, columns=("Asset Code", "Asset Type", "Issuer"), show="headings")
        self.asset_tree.heading("Asset Code", text="Asset Code")
        self.asset_tree.heading("Asset Type", text="Asset Type")
        self.asset_tree.heading("Issuer", text="Issuer")
        
        self.asset_tree.column("Asset Code", width=150, anchor=tk.CENTER)
        self.asset_tree.column("Asset Type", width=150, anchor=tk.CENTER)
        self.asset_tree.column("Issuer", width=400, anchor=tk.CENTER)

        # Scrollbar for the Treeview
        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.asset_tree.yview)
        self.asset_tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=1, sticky='ns')
        self.asset_tree.grid(row=1, column=0, padx=20, pady=20)

        # Button to fetch asset data from Stellar
        self.fetch_button = tk.Button(self, text="Fetch Assets", font=("Helvetica", 12), command=self.fetch_assets_from_stellar)
        self.fetch_button.grid(row=2, column=0, columnspan=2, pady=10)
        self.config(background='#1e2a38')

    def populate_assets(self, asset_list):
        """Populates the Treeview with asset data"""
        # Clear the Treeview first
        for row in self.asset_tree.get_children():
            self.asset_tree.delete(row)
        
        # Insert asset data into Treeview
        for asset in asset_list:
            asset_code = asset.get("asset_code", "native")
            asset_type = asset.get("asset_type", "native")
            asset_issuer = asset.get("asset_issuer", "N/A" if asset_type == "native" else asset.get("asset_issuer", "Unknown"))
            self.asset_tree.insert("", "end", values=(asset_code, asset_type, asset_issuer))

    def fetch_assets_from_stellar(self):
        """Fetch asset data from Stellar Horizon API and populate the Treeview"""
        url = "https://horizon.stellar.org/assets"
        try:
            response = requests.get(url)
            response.raise_for_status()
            asset_data = response.json()['_embedded']['records']

            asset_list = [
                {
                    'asset_code': asset.get('asset_code', 'native'),
                    'asset_type': asset.get('asset_type', 'native'),
                    'asset_issuer': asset.get(
                        'asset_issuer', None
                    ),  # None for native asset (XLM)
                }
                for asset in asset_data
            ]
            # Populate the Treeview with fetched asset data
            self.populate_assets(asset_list)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching assets: {e}")


