

import tkinter

from db import Db

from home import Home
from tradingbot import TradingBot
from wallet import Wallet


class StellarBot(tkinter.Tk):

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        self.frame_list = [Home, Wallet, TradingBot]
        self.title("StellarBot")
        self.geometry("1560x800")
        self.resizable(True, True)
        self.configure(bg="black", borderwidth=0, relief="ridge")
        self.iconbitmap(bitmap='./images/stellarbot.ico')
        self.db = Db()
        self.iconphoto(True, tkinter.PhotoImage(file="images/stellarbot.png"))
        tkinter.Label(self, text="Welcome to StellarBot", bg="white", fg="green", font=("Arial", 40)).grid(row=0,
                                                                                                           column=0
                                                                                       )
        tkinter.Label(self, text="Account ID", font=("Arial", 10)).grid(row=1, column=0)
        acc = tkinter.StringVar()
        acc.set("Enter Account ID")
        tkinter.Entry(self, textvariable=acc).grid(row=1, column=1)
        tkinter.Label(self, text="Secret Key", font=("Arial", 10)).grid(row=2, column=0)
        sec = tkinter.StringVar()
        sec.set("Enter Secret Key")
        tkinter.Entry(self, textvariable=sec).grid(row=2, column=1)
        tkinter.Button(self, text="Login", command=lambda: self.login(acc, sec)).grid(row=3, column=4)
        self.bot = TradingBot(controller=self)
        self.mainloop()
        self.protocol("WM_DELETE_WINDOW", exit(1))

    def login(self, user_id, secret_key):
        self.db.create_table()
        try:
            self.bot.login(user_id, secret_key)
        except Exception as e:
            tkinter.Message(text=str(e))
        pass

    def show_frame(self, frame=None):

        for frame in self.winfo_children():
            frame.destroy()
        frame.grid(row=0, column=0, sticky="nsew")
