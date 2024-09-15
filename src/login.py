import re
import sqlite3
import tkinter

import tkinter as tk
from tkinter import Button, Checkbutton, Entry, Label, StringVar

from stellar_client import StellarClient

class Login(tk.Frame):
    '''This class is used to log in to the Stellar network.'''

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller

        self.db = sqlite3.connect('StellarBot.sql')

        self.db.execute('''CREATE TABLE IF NOT EXISTS users ( 
                            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                            account_id VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE, 
                            account_secret VARCHAR NOT NULL UNIQUE ON CONFLICT REPLACE,  
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                            last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.db.commit()

        self.image = tkinter.PhotoImage(file="./src/images/stellarbot.png")

        # Welcome label
        self.welcome_label = tkinter.Label(self, text="Welcome to StellarBot", 
                                           font=("Helvetica", 40), fg='white')
        self.welcome_label.grid(row=0, column=0, columnspan=2)

        self.account_id_var = StringVar()
        self.account_secret_var = StringVar()

        self.account_id_label = tkinter.Label(self, text="Account ID", width=20, font=('Helvetica', 15),  bg='green', fg='white')
        self.account_id_label.place(x=230, y=300)
        self.account_id_entry = Entry(self, textvariable=self.account_id_var, font=('Helvetica', 15), width=60)
        self.account_id_entry.place(x=450, y=300)
        self.account_id_entry.focus()

        self.infos_label = tkinter.Label(self, text=" infos", font=('Helvetica', 15), bg = 'green', fg = 'white')

        # Account secret entry
        self.account_secret_label = Label(self, text="Account Secret", width=20, 
                                          font=("Helvetica", 15), bg='green', fg='white')
        self.account_secret_label.place(x=230, y=400)

        self.account_secret_entry = Entry(self, textvariable=self.account_secret_var, 
                                          width=60, font=("Helvetica", 15), show="*")
        self.account_secret_entry.place(x=450, y=400)

        # Remember me checkbox
        self.remember_me_var = StringVar()
        self.remember_me_checkbox = Checkbutton(self, text="Remember Me", 
                                                variable=self.remember_me_var, onvalue="1", offvalue="0",
                                                command=self.register_remember_me,  
                                                font=("Helvetica", 15), bg='green', fg='white')
        self.remember_me_checkbox.place(x=450, y=450)

        # Create account button
        self.create_account_button = Button(self, text="Create Account", 
                                            command=lambda: self.controller.show_pages("CreateAccount"), 
                                            font=("Helvetica", 15), bg='gray', fg='white')
        self.create_account_button.place(x=500, y=500)

        # Login button
        self.login_button = Button(self, text="Login", 
                                   command=self.login,  
                                   font=("Helvetica", 15), bg='gray', fg='white')
        self.login_button.place(x=750, y=500)

        self.config(background='#1e2a38', border=12, relief=tkinter.RAISED,
                    width=1530, height=780)
        self.welcome_label.config(image=self.image,height=600, width= 600
                                  
                                  
                                  )

        self.grid(row=0, column=0, sticky='nsew')

        # Pack the frame
        self.pack(fill=tkinter.BOTH, expand=1, side=tkinter.TOP)

        self.update_ui()

    def login(self) -> None:
     
        if not self.account_id_var.get() or not self.account_secret_var.get():
            self.infos_label.config(text="Account ID and account secret are required!", fg='red')
            self.infos_label.place(x=550, y=200)
            print("Missing account ID or account secret")
            return

        if not self.is_valid_stellar_account_id(account_id=self.account_id_var.get()):


            
            self.infos_label.config(text="Invalid Stellar Lumen account ID!", fg='red')
            self.infos_label.place(x=450, y=200)

            print("Invalid Stellar Lumen account ID")

            return
        
         
        # Check if the account secret matches stellar lumen password
        if not self.is_valid_stellar_secret(secret_key=self.account_secret_var.get()):
            self.infos_label.config(text="Invalid Stellar Lumen account secret!", fg='red')
            self.infos_label.place(x=450, y=200)
            print("Invalid Stellar Lumen account secret")
            return
        
        self.infos_label.config(text="")

        self.controller.bot = StellarClient(db=self.db,controller=self.controller,
                                            
                                            account_id= self.account_id_var.get(),
                                             secret_key=self.account_secret_var.get()
                                            )
        self.controller.show_pages("Home")

    def register_remember_me(self) -> None:
        print("Remember me checkbox clicked")
        account_secret = self.account_secret_var.get()
        if self.remember_me_var.get() == "1":
            select = self.db.execute("SELECT * FROM users WHERE account_secret =?", (account_secret,))
            if select.fetchone() is None:
                print("Account does not exist, creating new one")
                self.db.execute("INSERT INTO users (account_secret) VALUES (?)", (account_secret,))
                self.db.commit()
            else:
                print("Account already exists")
                self.db.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE account_secret =?", (account_secret,))
                self.db.commit()

    def is_valid_stellar_secret(self, secret_key: str) -> bool:
        # Define the regex for a valid Stellar Lumens secret key
        pattern = r'^S[ABCDEFGHIJKLMNOPQRSTUVWXYZ234567]{55}$'
        # Check if the secret_key matches the pattern
        return bool(re.match(pattern, secret_key))

    def update_ui(self) -> None:
        self.infos_label.config(text="")
        
        # Check if the remember me checkbox is checked
        if self.remember_me_var.get() == "1":
            select = self.db.execute("SELECT * FROM users WHERE last_login > datetime('now', '-1 hour')")
            if select.fetchone() is not None:
                self.account_id_var.set(select.fetchone()[1])
                self.account_secret_var.set(select.fetchone()[2])
        self.after(1000, self.update_ui)

    def is_valid_stellar_account_id(self, account_id: str) -> bool:
    # Define the regex for a valid Stellar Lumens account ID
     pattern = r'^G[A-Z2-7]{55}$'
    # Check if the account_id matches the pattern
     return bool(re.match(pattern, account_id))
