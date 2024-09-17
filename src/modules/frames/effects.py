import tkinter as tk
from tkinter import ttk
import pandas as pd
import requests

class Effects(tk.Frame):
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

        # Create widgets to display the effects information
        self.create_widgets()

        # Fetch and display the effects data
        self.update_effects_data()

    def create_widgets(self):


        self.effects_label = tk.Label(self, text="Market Effects", font=("Helvetica",20),fg='white')
        self.effects_label.place(x=600, y=20)

        # Section: Effects Treeview
        effects_frame = tk.Frame(self, bg="lightgrey", border=15,background='blue',borderwidth=4, relief=tk.RAISED, bd=2)
        effects_frame.place(x=20, y=20, width=1200, height=500)

        tk.Label(effects_frame, text="Effects", font=("Helvetica", 16, "bold"), bg="lightgrey").pack(pady=10)
        self.effects_tree = ttk.Treeview(effects_frame, columns=['id', 'type', 'account', 'created_at', 'amount', 'asset_code', 'asset_issuer'], show='headings')
        self.effects_tree.heading('id', text='ID')
        self.effects_tree.heading('type', text='Type')
        self.effects_tree.heading('account', text='Account')
        self.effects_tree.heading('created_at', text='Created At')
        self.effects_tree.heading('amount', text='Amount')
        self.effects_tree.heading('asset_code', text='Asset Code')
        self.effects_tree.heading('asset_issuer', text='Asset Issuer')

        for col in ['id', 'type', 'account', 'created_at', 'amount', 'asset_code', 'asset_issuer']:
            self.effects_tree.column(col, width=150, anchor=tk.CENTER)
        self.effects_tree.pack(fill=tk.BOTH, expand=True)

    def update_effects_data(self):
        
        effects_data = self.controller.bot.get_effects_data()

        

        # Convert effects data to DataFrame
        effects_df = pd.json_normalize(effects_data)

        # Update Effects Treeview
        for item in self.effects_tree.get_children():
            self.effects_tree.delete(item)
        for _, row in effects_df.iterrows():
            self.effects_tree.insert('', 'end', values=(
            row.get('id'),
            row.get('type'),
            row.get('account_id'),
            row.get('created_at'),
            row.get('amount'),
            row.get('asset_code')               
               
              
            ))
            # Update the GUI after fetching the data
        self.controller.update()
        self.after(1000, self.update_effects_data)
            
