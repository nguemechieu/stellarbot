import tkinter as tk
from tkinter import Canvas, ttk
import pandas as pd
from stellar_sdk import Asset

class AccountDetails(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.account_id = self.controller.bot.account_id
        self.place(x=0, y=0, width=1530, height=780)

        # Set up the styling for a professional look
        self.style = ttk.Style()
        self.style.configure("Treeview", font=("Helvetica", 10), rowheight=25)
        self.style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
        self.config(background='#1e2a38')

        # Create widgets to display the account information
        self.create_widgets()

        # Fetch and display the account data
        self.update_account_data()

    def create_account_dataframe(self, account_data):
        balances_df = pd.json_normalize(account_data['balances'])
       
        self.controller.bot.balances_df = balances_df
        signers_df = pd.json_normalize(account_data['signers'])
        return balances_df, signers_df

    def create_widgets(self):
        # Section 1: Account Basic Details
        self.details_frame = tk.Frame(self, bg="green", border=14, relief=tk.RAISED, bd=2)
        self.details_frame.place(x=20, y=20, width=900, height=500)

        tk.Label(self.details_frame, text="Account Details", font=("Helvetica", 16, "bold"), bg="lightgrey").pack(pady=10)

        self.details_canvas = Canvas(self.details_frame, width=800, height=400, background='black')
        self.details_canvas.place(x=20, y=50)

        # Section 2: Balances Treeview
        self.balance_frame = tk.Frame(self, bg="lightblue", border=14, relief=tk.RAISED, bd=2)
        self.balance_frame.place(x=900, y=20, width=600, height=500)

        tk.Label(self.balance_frame, text="Balances", font=("Helvetica", 16, "bold"), bg="lightblue").pack(pady=10)
        self.balance_tree = ttk.Treeview(self.balance_frame, columns=['balance', 'limit', 'asset_code', 'asset_issuer', 'asset_type'], show='headings')
        self.balance_tree.heading('balance', text='Balance')
        self.balance_tree.heading('limit', text='Limit')
        self.balance_tree.heading('asset_code', text='Asset Code')
        self.balance_tree.heading('asset_issuer', text='Asset Issuer')
        self.balance_tree.heading('asset_type', text='Asset Type')

        for col in ['balance', 'limit', 'asset_code', 'asset_issuer', 'asset_type']:
            self.balance_tree.column(col, width=120, anchor=tk.CENTER)
        self.balance_tree.pack(fill=tk.BOTH, expand=True)

        # Section 3: Signers Treeview
        self.signers_frame = tk.Frame(self, bg="lightgreen", border=14, relief=tk.RAISED, bd=2)
        self.signers_frame.place(x=20, y=600, width=1500, height=170)

        tk.Label(self.signers_frame, text="Signers", font=("Helvetica", 16, "bold"), bg="lightgreen").pack(pady=10)
        self.signers_tree = ttk.Treeview(self.signers_frame, columns=['key', 'weight', 'type'], show='headings')
        self.signers_tree.heading('key', text='Signer Key')
        self.signers_tree.heading('weight', text='Weight')
        self.signers_tree.heading('type', text='Type')

        for col in ['key', 'weight', 'type']:
            self.signers_tree.column(col, width=300, anchor=tk.CENTER)
        self.signers_tree.pack(fill=tk.BOTH, expand=True)

    def update_account_data(self):
        # Fetch account data from the controller
        self.account_data = self.controller.bot.trading_engine.get_accounts()

        # Create DataFrames from account data
        balances_df, signers_df = self.create_account_dataframe(self.account_data)

        # Update the details canvas
        self.details_canvas.delete('all')
        self.details_canvas.create_text(100, 30, text='Account ID :', fill="green", font=("Helvetica", 14))
        self.details_canvas.create_text(600, 30, text=self.account_data['account_id'], fill="green", font=("Helvetica", 14))
        self.details_canvas.create_text(100, 60, text='Sequence :', fill="green", font=("Helvetica", 14))
        self.details_canvas.create_text(600, 60, text=self.account_data['sequence'], fill="green", font=("Helvetica", 14))
        self.details_canvas.create_text(100, 100, text='Last Modified Time :', fill="green", font=("Helvetica", 14))
        self.details_canvas.create_text(600, 100, text=self.account_data['last_modified_time'], fill="green", font=("Helvetica", 14))
        self.details_canvas.create_text(100, 150, text='Thresholds :', fill="green", font=("Helvetica", 14))
        self.details_canvas.create_text(600, 150, text=self.account_data['thresholds'], fill="green", font=("Helvetica", 14))
        self.details_canvas.create_text(100, 200, text='Flags :', fill="green", font=("Helvetica", 14))
        self.details_canvas.create_text(600, 200, text=self.account_data['flags'], fill="green", font=("Helvetica", 14))
        self.details_canvas.create_text(100, 300, text='Subentry Count :', fill="green", font=("Helvetica", 14))
        self.details_canvas.create_text(600, 300, text=self.account_data['subentry_count'], fill="green", font=("Helvetica", 14))
        assets=pd.DataFrame( columns=
                     [
                         'balance',
                         'limit',
                         'asset_code',
                         'asset_issuer',
                         'asset_type'
    
                     ])
        # Update Balances Treeview
        for item in self.balance_tree.get_children():
            self.balance_tree.delete(item)
        for _, row in balances_df.iterrows():
            self.balance_tree.insert('', 'end', values=(
                row['balance'],
                row.get('limit', 'N/A'),
                row.get('asset_code', 'N/A'),
                row.get('asset_issuer', 'N/A'),
                row['asset_type']
            ))
            assets['balance']=row['balance']
            assets['limit']=row.get('limit', 'N/A')
            assets['asset_code']=row.get('asset_code', 'N/A')
            assets['asset_issuer']=row.get('asset_issuer', 'N/A')
            assets['asset_type']=row['asset_type']
        assets.to_csv('ledger_assets.csv', index=False)

        # Update Signers Treeview
        for item in self.signers_tree.get_children():
            self.signers_tree.delete(item)
        for _, row in signers_df.iterrows():
            self.signers_tree.insert('', 'end', values=(
                row['key'],
                row['weight'],
                row['type']
            ))
        self.after(5000, self.update_account_data)