from atexit import register
import smtplib
import sys
import tkinter
from datetime import datetime
from email.mime.text import MIMEText
from tkinter import filedialog, RAISED, BOTTOM

from Login import Login
from createAccount import CreateAccount
from db import Db
from home import Home
from marketwatch import MarketWatch
from orders import Orders
from tradingbot import TradingBot

def send_email(subject: str = "", body: str = "", sender: str = "",
               recipients=None, password: str = ""):
    if recipients is None:
        recipients = ["r@gmail.com", "recipient2@gmail.com"]
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
        print("Message sent!")

import os

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')
class StellarBot(tkinter.Tk):
    

    def __init__(self):
        tkinter.Tk.__init__(self)

        self.controller = self
        self.parent = self.master
        self.frames = {

        }
        self.pages = {}
        self.filename = None
        self.Messagebox = None
    
        # self.parent.iconbitmap('src/images/stellarbot.ico')
        #self.image = tkinter.PhotoImage(file=r"src/images/stellarbot.png")
      
       
        
        self.show_pages("Login")
        self.mainloop()
     

    def show_pages(self, param):
        self.title(
            "StellarBot    |     AI POWERED crypto Trader |    -->" + datetime.strftime(datetime.now(),
                                                                                                 "%Y")
            )

        self.geometry("1530x800")
        self.configure(bg="#004d99")
        self.configure(highlightbackground="#004d99")
        self.configure(highlightcolor="black")
        self.configure(padx=10)
        self.configure(pady=10)
        self.configure(relief=RAISED)
        
      
        self.resizable(width=True, height=True)
          
        self.configure(background="gray", relief=RAISED, border=9, bg="#004d99")


      
      
        self.delete_frame()

        if param in ['Login', 'Register', 'ForgotPassword', 'ResetPassword', 'Home', 'About', 'News', 'CreateAccount']:
             frames = [ Login, Home,MarketWatch,Orders, CreateAccount]

        for frame in frames:
                if param == frame.__name__:
                    frame = frame(self, self.controller)
                    frame.tkraise()

    def delete_frame(self):
        for _frame in self.winfo_children():
            _frame.destroy()


    def show_error(self, param):
        if param is not None:
            self.Messagebox = tkinter.Message(self.master, text=param, width=300)
            print(param)
            self.Messagebox.pack(side=BOTTOM)
            self.Messagebox.after(3000, self.Messagebox.destroy)

    def open_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            try:
                self.trades.load_from_file(filename)
                self.show_pages("Home")
            except Exception as e:
                self.show_error(str(e))

    def save_file(self):
        self.filename = filedialog.asksaveasfilename()
        if self.filename is not None:
            try:
                self.trades.save_to_file(self.filename)
                self.show_pages("Login")
            except Exception as e:
                self.show_error(str(e))

    def exit(self):
        sys.exit(0)


