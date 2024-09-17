
import tkinter as tk
from tkinter import PhotoImage, ttk

import pandas as pd



class Wallet(tk.Frame):
    """Stellar wallet frame displaying balance, transactions, and payment options."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config(background='#1e2a38')
        # Layout for the wallet
        self.place(x=0, y=0, width=1530, height=780)
        
        # Title
        self.wallet_title = tk.Label(self, text="Stellar Wallet", font=("Helvetica", 24), fg='white', bg='#1e2a38')    
        self.wallet_title.place(x=20, y=20)

        # Balance Display
        self.balance_label = tk.Label(self, text="Balance:", font=("Helvetica", 16), fg='white', bg='#1e2a38')
        self.balance_label.place(x=20, y=80)
        self.balance_amount_label = tk.Label(self, text="Loading...", font=("Helvetica", 16), fg='orange', bg='#1e2a38')
        self.balance_amount_label.place(x=120, y=80)

        # Transaction History
        self.transaction_history_label = tk.Label(self, text="Transaction Details", font=("Helvetica", 18), fg='white', bg='#1e2a38')
        self.transaction_history_label.place(x=20, y=140)
        
        # Transaction Table with extended details
        self.transaction_table = ttk.Treeview(self, columns=("ID", "Paging Token", "Hash", "Successful", "Created At", "Ledger"), show="headings", height=20)
        self.transaction_table.config(height=600)

        self.transaction_table.heading("ID", text="ID")
        

        self.transaction_table.heading("Paging Token", text="Paging Token")
        self.transaction_table.heading("Hash", text="Hash")
        self.transaction_table.heading("Successful", text="Successful")
        self.transaction_table.heading("Created At", text="Created At")
        self.transaction_table.heading("Ledger", text="Ledger")
        self.transaction_table.column("ID", width=100)
        self.transaction_table.column("Paging Token", width=100)
        self.transaction_table.column("Hash", width=100)
        self.transaction_table.column("Successful", width=100)
        self.transaction_table.column("Created At", width=100)
        self.transaction_table.column("Ledger", width=100)
        self.transaction_table.place(x=20, y=180)

        # Transaction Details Section
        self.transaction_details_label = tk.Label(self, text="Transaction Metadata", font=("Helvetica", 18), fg='white', bg='#1e2a38')
        self.transaction_details_label.place(x=600, y=140)

        # Transaction Metadata text area
        self.transaction_details_text = tk.Text(self, height=600, width=200,font= ("Helvetica",14), fg='white', bg='#1e2a38')
        self.transaction_details_text.place(x=600, y=180)

        # Send Payment Section
        self.send_payment_label = tk.Label(self, text="Send Payment", font=("Helvetica", 18), fg='white', bg='#1e2a38')
        self.send_payment_label.place(x=600, y=520)
        
        # Recipient Entry
        self.recipient_label = tk.Label(self, text="Recipient Account ID", font=("Helvetica", 14), fg='white', bg='#1e2a38')
        self.recipient_label.place(x=600, y=560)
        self.recipient_entry = tk.Entry(self, width=50)
        self.recipient_entry.place(x=800, y=560)

        # Amount Entry
        self.amount_label = tk.Label(self, text="Amount", font=("Helvetica", 14), fg='white', bg='#1e2a38')
        self.amount_label.place(x=600, y=600)
        self.amount_entry = tk.Entry(self, width=20)
        self.amount_entry.place(x=800, y=600)

        # Asset Entry (e.g., XLM, USDC)
        self.asset_label = tk.Label(self, text="Asset (e.g., XLM)", font=("Helvetica", 14), fg='white', bg='#1e2a38')
        self.asset_label.place(x=600, y=640)
        self.asset_entry = tk.Entry(self, width=20)
        self.asset_entry.place(x=800, y=640)

        # Send Payment Button
        self.send_button = tk.Button(self, text="Send Payment", command=lambda:self.send_payment, bg='#4CAF50', fg='white', font=("Helvetica", 14))
        self.send_button.place(x=800, y=680)

        # Start auto-refresh for wallet data
        self.refresh_wallet_data()
      

    def refresh_wallet_data(self):
        """Refresh the wallet data like balance and transaction history."""
        # Get balance and update UI
        balance = pd.read_csv('ledger_accounts.csv')
        self.balance_amount_label.config(
            text=f"${balance['balance']}"
        )

        # Get transaction history and update table
        transactions = self.controller.bot.trading_engine.get_transactions()  # Example method
        for row in self.transaction_table.get_children():
            self.transaction_table.delete(row)
        
        for  transaction in transactions:

            
            self.transaction_table.insert('', 'end', values=(
                transaction["id"], 

                transaction["paging_token"], 
                transaction["hash"],
                transaction["successful"],
                transaction["created_at"],
                transaction["ledger"]
                
            ))
       
        account_id_label = tk.Label(self,  width=200, height=200)
        account_id_label.place(x=800, y=50)
  
    def send_payment(self):
     """Send a payment to a recipient."""
     recipient_account_id = self.recipient_entry.get()
     amount = self.amount_entry.get()
     asset = self.asset_entry.get()

     
     if not recipient_account_id or not amount or not asset:
         tk.Message(self,text="Please fill in all required fields.")
         return
     
     if not self.controller.bot.trading_engine.send_payment(recipient_account_id, amount, asset):
         tk.Message(self,text="Failed to send payment.")
         return
     
  