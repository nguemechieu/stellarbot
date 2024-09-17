import tkinter
import tkinter as tk
from datetime import datetime
import qrcode
from PIL import Image, ImageTk

class Dashboard(tk.Frame):
    """Dashboard frame displaying live data, control buttons, and QR code for account_id."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        
        self.controller = controller
        # Light background for the dashboard frame
        self.place(x=0, y=0, width=1530, height=780)

        self.config(background='#1e2a38')

        # Create and style the canvas for the dashboard
        self.canvas = tk.Canvas(parent, width=1430, height=600, border=23,borderwidth=3,background='black')
        self.canvas.place(x=0, y=0)

        # Add server control buttons
        self.toggled_button1 = tk.Button(self, bg='#4CAF50', fg='white', text="START", width=20, command=self.start_bot, font=("Helvetica", 12, "bold"))
        self.toggled_button1.place(x=400, y=610)
        self.toggled_button = tk.Button(self, bg='#F44336', fg='white', text='STOP', width=20, command=self.stop_bot, font=("Helvetica", 12, "bold"))
        self.toggled_button.place(x=600, y=610)

        self.image = tk.PhotoImage( "./account_id.png" )
        
        account_id_label= tkinter.Label(self,image=self.image, width=200, height= 200)
        account_id_label.place(x=500, y=90)
                   

        # Start automatic updates for dashboard
        self.updates()

    def stop_bot(self):
        """Stop the trading bot and update button states."""
        self.toggled_button1.config(bg='#4CAF50', fg='white', state='normal', text='START')
        self.toggled_button.config(bg='#F44336', fg='white', state='disabled', text='STOP')
        self.controller.bot.stop()

    def start_bot(self):
        """Start the trading bot and update button states."""
        self.toggled_button1.config(bg='gray', fg='yellow', state='disabled', text='START')
        self.toggled_button.config(bg='#F44336', fg='yellow', state='normal', text='STOP')
        self.controller.bot.start()

    def updates(self):
        """Update the dashboard regularly with live data."""
        self.canvas.delete("all")
        self.canvas.create_text(450, 60, text="=========== Welcome to StellarBot ============", font=('Arial', 16, "italic"), fill='white')
        self.canvas.create_text(250, 100, text="Time :", font=('Arial', 14), fill='green')
        self.canvas.create_text(450, 100, text=str(datetime.now()), font=('Arial', 14), fill='white')
        self.canvas.create_text(1200, 60, text="Version: 1.0", font=('Arial', 14), fill='white')

        # Display account details from controller's bot data
        self.canvas.create_text(250, 200, text="Status:", font=('Arial', 14), fill='green')
        self.canvas.create_text(450, 200, text=self.controller.bot.server_msg.get('status', 'N/A'), font=('Arial', 14), fill='white')
        self.canvas.create_text(250, 300, text="Info:", font=('Arial', 14), fill='green')
        self.canvas.create_text(650, 300, text=self.controller.bot.server_msg.get('info', 'N/A'), font=('Arial', 14), fill='white')
        self.canvas.create_text(250, 500, text="Message:", font=('Arial', 14), fill='green')
        self.canvas.create_text(650, 500, text=self.controller.bot.server_msg.get('message', 'N/A'), font=('Arial', 14), fill='white')

        

        # Schedule next update in 1 second

    
        self.after(1000, self.updates)
