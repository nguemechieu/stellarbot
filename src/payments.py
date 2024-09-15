import tkinter as tk
from tkinter import ttk
import pandas as pd
import requests

class Payments(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.place(x=0, y=0, width=1530, height=780)
        # Set up the styling for a professional look
        self.style = ttk.Style()
        self.style.configure("Treeview", font=("Helvetica", 10), rowheight=25)
        self.style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))

        # Create widgets to display the payments information
        self.create_widgets()

        # Fetch and display the payments data
        self.update_payments_data()

    def create_widgets(self):
        # Section: Payments Treeview
        payments_frame = tk.Frame(self, bg="lightgrey", border=14, relief=tk.RAISED, bd=2)
        payments_frame.place(x=20, y=20, width=1200, height=500)

        tk.Label(payments_frame, text="Payments", font=("Helvetica", 16, "bold"), bg="lightgrey").pack(pady=10)

        # Treeview to display the payments data
        self.payments_tree = ttk.Treeview(payments_frame, columns=['id', 'type', 'created_at', 'transaction_hash', 'amount', 'asset_code', 'from', 'to'], show='headings')
        self.payments_tree.heading('id', text='ID')
        self.payments_tree.heading('type', text='Type')
        self.payments_tree.heading('created_at', text='Created At')
        self.payments_tree.heading('transaction_hash', text='Transaction Hash')
        self.payments_tree.heading('amount', text='Amount')
        self.payments_tree.heading('asset_code', text='Asset Code')
        self.payments_tree.heading('from', text='From Account')
        self.payments_tree.heading('to', text='To Account')

        # Configure columns
        for col in ['id', 'type', 'created_at', 'transaction_hash', 'amount', 'asset_code', 'from', 'to']:
            self.payments_tree.column(col, width=150, anchor=tk.CENTER)
        
        self.payments_tree.pack(fill=tk.BOTH, expand=True)

    def update_payments_data(self):
        # Fetch payments data from the Stellar Horizon API
        url = 'https://horizon.stellar.org/payments'
        response = requests.get(url)
        payments_data = response.json().get('_embedded', {}).get('records', [])

        # Convert payments data to DataFrame
        payments_df = pd.json_normalize(payments_data)

        # Clear the current data in the Treeview
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)

        # Insert new data into the Treeview
        for _, row in payments_df.iterrows():
            self.payments_tree.insert('', 'end', values=(
                row.get('id', 'N/A'),
                row.get('type', 'N/A'),
                row.get('created_at', 'N/A'),
                row.get('transaction_hash', 'N/A'),
                row.get('amount', 'N/A'),
                row.get('asset_code', 'N/A'),
                row.get('from', 'N/A'),
                row.get('to', 'N/A')
            ))

