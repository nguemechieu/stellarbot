import tkinter as tk
from tkinter import StringVar, ttk
import requests
from stellar_sdk import Server, Asset


class Transaction(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Application controller object to access bot and other relevant data
        self.stellar_client = self.controller.bot  # Stellar client object to interact with the Stellar network
        self.place(x=0, y=0, width=1530, height=780)
        # Create and arrange widgets in the frame
        self.create_widgets()

    def create_widgets(self):
        self.title_label = tk.Label(self, text="Transaction Details", font=("Helvetica", 18), pady=10)
        self.title_label.grid(row=0, column=0, columnspan=2)

        # Source account details
        self.source_label = tk.Label(self, text="Source Account:", font=("Helvetica", 12))
        self.source_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        dat = StringVar()
        dat.set(self.controller.bot.account_id)

        self.source_entry = tk.Entry(self, width=50, textvariable=dat, font=("Helvetica", 12), background='green')
        self.source_entry.grid(row=1, column=1, padx=10, pady=5)

        # Destination account details
        self.destination_label = tk.Label(self, text="Destination Account:", font=("Helvetica", 12))
        self.destination_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.destination_entry = tk.Entry(self, width=50)
        self.destination_entry.grid(row=2, column=1, padx=10, pady=5)

        # Asset choice
        self.asset_choice = ttk.Combobox(self, width=50, font=("Helvetica", 12))
        self.asset_choice.place(x=600, y=20)

        # Amount to send
        self.amount_label = tk.Label(self, text="Amount:", font=("Helvetica", 12))
        self.amount_label.grid(row=3, column=0, padx=10, pady=7, sticky="w")
        self.amount_entry = tk.Entry(self, width=50, font=("Helvetica", 12), background='lightblue')
        self.amount_entry.grid(row=3, column=1, padx=10, pady=7)

        # Transaction status label
        self.status_label = tk.Label(self, text="Status:", font=("Helvetica", 12))
        self.status_label.grid(row=4, column=0, padx=10, pady=8, sticky="w")
        self.status_message = tk.Label(self, font=("Helvetica", 12), fg="green")
        self.status_message.place(x=20, y=300)

        # Submit Transaction button
        self.submit_button = tk.Button(self, text="Submit Transaction", font=("Helvetica", 12),
                                       command=self.submit_transaction)
        self.submit_button.grid(row=5, column=0, columnspan=2, pady=10)

        # Transaction history
        self.history_label = tk.Label(self, text="Transaction History", font=("Helvetica", 14), pady=10)
        self.history_label.grid(row=6, column=0, columnspan=2)

        self.history_listbox = tk.Listbox(self, height=10, width=80)
        self.history_listbox.place(x=10, y=400, width=1000, height=300)

        # Fetch and display transaction history when frame is created
        self.update_screen()

    def submit_transaction(self):
        source_account = self.controller.bot.account
        destination_account = self.destination_entry.get()

        if not destination_account:
            self.status_message.config(text="Please enter a destination account", fg="red")
            return

        amount = self.amount_entry.get()

        if not amount:
            self.status_message.config(text="Please enter an amount", fg="red")
            return

        try:
            # Create and submit the transaction via the Stellar client
            response = self.stellar_client.submit_transaction(source_account, destination_account, amount)
            self.status_message.config(text="Transaction submitted successfully!\n" + response, fg="green")
            # Refresh transaction history after successful submission
            self.fetch_transaction_history()
        except Exception as e:
            self.status_message.config(text=f"Error: {str(e)}", fg="red")

    def fetch_transaction_history(self):
        account_id = self.controller.bot.account_id
        url = f"https://horizon.stellar.org/accounts/{account_id}/transactions"
        
        try:
            response = requests.get(url)
            response.raise_for_status()

            # Get the transaction history from the response
            history = response.json()['_embedded']['records']
            self.history_listbox.delete(0, tk.END)  # Clear the listbox before adding new data

            for tx in history:
                tx_details = f"Hash: {tx['hash']} | Date: {tx['created_at']} | Successful: {tx['successful']}"
                self.history_listbox.insert(tk.END, tx_details)
        except requests.exceptions.RequestException as e:
            self.history_listbox.insert(tk.END, f"Error fetching history: {str(e)}")

    def update_screen(self):
        # Update the transaction history every second
        self.fetch_transaction_history()  # Fetch transaction history
        self.status_message.after(5000, self.update_screen)  # Refresh status message every 5 seconds
