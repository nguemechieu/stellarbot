import csv
import os
import re
import tkinter as tk
from tkinter import StringVar, ttk, messagebox, filedialog
import qrcode
import requests
from stellar_sdk import Keypair
from modules.classes.settings_manager import SettingsManager
from modules.classes.stellar_client import StellarClient


class Login(tk.Frame):
    """Stellar Network User Login Frame."""

    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller

        # Load saved settings like account and secret keys
        self.settings = SettingsManager.load_settings()

        # Set background color and frame size
        self.configure(bg='#1e2a38')
        self.place(x=0, y=0, width=1530, height=780)

        # Set styling for the frame
        self.style = ttk.Style()
        self.style.configure("Treeview", font=("Helvetica", 10), rowheight=25)
        self.style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))

        # Application name label
        self.app_name_label = tk.Label(self, text="Welcome to StellarBot", font=("Helvetica", 23, "bold"), bg='#1e2a38', fg='green')
        self.app_name_label.pack(pady=20)

        # Title label
        self.title_label = tk.Label(self, text="Stellar Network Login", font=("Helvetica", 16, "bold"), bg='#1e2a38', fg='white')
        self.title_label.pack(pady=20)

        # Account ID entry field
        self.account_id_label = tk.Label(self, text="Account ID", font=("Helvetica", 12), bg='#1e2a38', fg='white')
        self.account_id_label.pack(pady=10)
        self.account_id = StringVar()
        self.account_id_entry = tk.Entry(self, textvariable=self.account_id, font=("Helvetica", 12), width=40)
        self.account_id_entry.pack(pady=10)

        # Set the saved account ID if available
        if 'account_id' in self.settings:
            self.account_id.set(self.settings['account_id'])

        # Secret Key entry field
        self.secret_key_label = tk.Label(self, text="Secret Key", font=("Helvetica", 12), bg='#1e2a38', fg='white')
        self.secret_key_label.pack(pady=10)
        self.secret_id = StringVar()
        self.secret_key_entry = tk.Entry(self, textvariable=self.secret_id, font=("Helvetica", 12), width=40, show='*')
        self.secret_key_entry.pack(pady=10)

        # Set the saved secret key if available
        if 'secret_key' in self.settings:
            self.secret_id.set(self.settings['secret_key'])

        # Password visibility toggle button
        self.password_visibility_toggle = tk.Button(self, text="Show", font=("Helvetica", 12), bg='gray', fg='white', command=self.toggle_password_visibility)
        self.password_visibility_toggle.pack(pady=10)

        # Login button
        self.login_button = tk.Button(self, text="Login", font=("Helvetica", 12), bg='gray', fg='white', command=self.login)
        self.login_button.pack(pady=20)

        # Create new account button
        self.create_account_button = tk.Button(self, text="Create New Account", font=("Helvetica", 12), bg='blue', fg='white', command=self.create_new_account)
        self.create_account_button.pack(pady=20)

        # Remember Me checkbox
        self.remember_me = tk.BooleanVar(value=self.settings.get('remember_me', False))
        self.remember_me_checkbox = tk.Checkbutton(self, text="Remember Me", font=("Helvetica", 12), bg='#1e2a38', fg='white', variable=self.remember_me)
        self.remember_me_checkbox.pack(pady=10)

        # Network connectivity status label
        self.network_status_label = tk.Label(self, text="Checking network status...", font=("Helvetica", 12), bg='#1e2a38', fg='orange')
        self.network_status_label.pack(pady=10)
        self.connectivity = self.check_network_connectivity()

        # Info label to display messages
        self.info_label = tk.Label(self, text="", font=("Helvetica", 12), bg='#1e2a38', fg='white')
        self.info_label.pack(pady=5)

    def check_network_connectivity(self):
        """Check network connectivity to the Stellar Network and update the status."""
        try:
            response = requests.get('https://horizon.stellar.org')
            if response.status_code == 200:
                self.network_status_label.config(text="Connected to Stellar Network", fg='green')
                return True
            else:
                self.network_status_label.config(text="Network Unreachable", fg='red')
                return False
        except Exception:
            self.network_status_label.config(text="Network Unreachable", fg='red')
            return False

    def login(self):
        """Handle the login process using the provided Account ID and Secret Key."""
        if not self.is_valid_stellar_account_id(self.account_id.get()):
            self.info_label.config(text="Invalid Stellar Network Account ID!", fg='red')
            return
        
        if not self.is_valid_stellar_secret(self.secret_id.get()):
            self.info_label.config(text="Invalid Stellar Network Account Secret!", fg='red')
            return
        
        if not self.account_id.get() or not self.secret_id.get():
            self.info_label.config(text="Both Account ID and Secret Key are required!", fg='red')
            return
        
        try:
            self.info_label.config(text="Logging in...", fg='green')

            # Check network connectivity
            if not self.connectivity:
                self.info_label.config(text="Unable to connect to Stellar Network. Please check your internet connection.", fg='red')
                return

            # Initialize StellarClient
            self.controller.bot = StellarClient(controller=self.controller, account_id=self.account_id.get(), secret_key=self.secret_id.get())
            self.controller.show_pages("Home")

            # Save user settings if "Remember Me" is checked
            self.save_user_settings()

        except Exception as e:
            self.info_label.config(text=f"Error: {e}", fg='red')

    def save_user_settings(self):
        """Save user settings like account ID and secret key if 'Remember Me' is checked."""
        settings = {
            'remember_me': self.remember_me.get(),
            'account_id': self.account_id.get() if self.remember_me.get() else '',
            'secret_key': self.secret_id.get() if self.remember_me.get() else ''
        }
        SettingsManager.save_settings(settings)

    def create_new_account(self):
        """Generate a new Stellar account and display it in a new window."""
        new_keypair = Keypair.random()

        # Create new account window
        new_account_window = tk.Toplevel(self)
        new_account_window.geometry("600x700")  # Increase window size for better display
        new_account_window.title("New Stellar Lumen's Account")
        new_account_window.configure(bg='#1e2a38')

        tk.Label(new_account_window, text="Stellar Account Creation", font=("Helvetica", 16, "bold"), bg='#1e2a38', fg='green').pack(pady=20)

        # Display the account information
        tk.Label(new_account_window, text="New Account Created", font=("Helvetica", 14, "bold"), bg='#1e2a38', fg='white').pack(pady=10)
        tk.Label(new_account_window, text="Account ID (Public Key):", font=("Helvetica", 12), bg='#1e2a38', fg='white').pack(pady=5)
        account_id_label = tk.Entry(new_account_window, font=("Helvetica", 12), width=60)  # Increased width for long keys
        account_id_label.insert(0, new_keypair.public_key)
        account_id_label.config(state='readonly')  # Set to read-only
        account_id_label.pack(pady=5)

        # Generate and display a QR code for the account ID
        try:
            self.display_qr_code(new_keypair, new_account_window)
        except Exception as e:
            print(f"Error generating QR code: {e}")
            tk.Label(new_account_window, text=f"Error generating QR code: {e}", font=("Helvetica", 12), bg='#1e2a38', fg='red').pack(pady=5)
            return

        tk.Label(new_account_window, text="Secret Key (Private Key):", font=("Helvetica", 12), bg='#1e2a38', fg='white').pack(pady=5)
        secret_key_label = tk.Entry(new_account_window, font=("Helvetica", 12), width=60, show="*")  # Increased width for long keys
        secret_key_label.insert(0, new_keypair.secret)
        secret_key_label.config(state='readonly')  # Set to read-only
        secret_key_label.pack(pady=5)

        # Save button
        save_button = tk.Button(new_account_window, text="Save to CSV", font=("Helvetica", 12), bg='green', fg='white',
                                command=lambda: self.save_account_to_csv(new_keypair.public_key, new_keypair.secret))
        save_button.pack(pady=10)

        # Close button
        close_button = tk.Button(new_account_window, text="Close", font=("Helvetica", 12), bg='red', fg='white', command=new_account_window.destroy)
        close_button.pack(pady=10)

    def display_qr_code(self, new_keypair, new_account_window):
        """Generate and display a QR code for the new Stellar account."""
        # Generate QR code for account ID
        qr_code_image = qrcode.make(new_keypair.public_key)
        qr_code_path = "./src/images/account_id.png"
        qr_code_image.save(qr_code_path)

        # Display QR code
        qr_code_label = tk.Label(new_account_window, text="Scan this QR code and add 2 XLM or more to activate your account:", font=("Helvetica", 12), bg='#1e2a38', fg='white')
        qr_code_label.pack(pady=5)
        qr_code_image = tk.PhotoImage(file=qr_code_path)

        qr_code_display = tk.Label(new_account_window, image=qr_code_image, bg='#1e2a38')
        qr_code_display.image = qr_code_image  # Keep a reference to the image to prevent garbage collection
        qr_code_display.pack(pady=2)

    def save_account_to_csv(self, account_id: str, secret_key: str):
        """Save the newly created Stellar account to a CSV file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], title="Save New Account")

        if not file_path:
            return  # User canceled the save dialog

        file_exists = os.path.isfile(file_path)

        try:
            with open(file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Account ID", "Secret Key"])  # Write header if the file doesn't exist yet
                writer.writerow([account_id, secret_key])
                messagebox.showinfo("Saved", f"Account saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving account: {e}")

    def is_valid_stellar_secret(self, secret_key: str) -> bool:
        """Validate the format of a Stellar secret key."""
        pattern = r'^S[ABCDEFGHIJKLMNOPQRSTUVWXYZ234567]{55}$'
        return bool(re.match(pattern, secret_key))

    def is_valid_stellar_account_id(self, account_id: str) -> bool:
        """Validate the format of a Stellar account ID."""
        pattern = r'^G[A-Z2-7]{55}$'
        return bool(re.match(pattern, account_id))

    def toggle_password_visibility(self):
        """Toggle the visibility of the Secret Key entry field."""
        if self.secret_key_entry['show'] == '*':
            self.secret_key_entry.config(show='')
            self.password_visibility_toggle.config(text="Hide")
        else:
            self.secret_key_entry.config(show='*')
            self.password_visibility_toggle.config(text="Show")
