

import tkinter
from home import Home
from tradingbot import TradingBot
from wallet import Wallet
from db import Db



class StellarBot(tkinter.Tk):

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        self.frame_list = [Home, Wallet, TradingBot]
        self.title("StellarBot")
        self.geometry("1560x800")
        self.resizable(True, True)
        self.config(bg="black", borderwidth=2, relief="ridge",width=1560,height=800)
        self.iconbitmap('images/stellarbot.ico')
        #self.db = Db()
        self.iconphoto(True, tkinter.PhotoImage(file="images/stellarbot.png"))
        tkinter.Label(self, text="Welcome to StellarBot", bg="white", fg="green", font=("Arial", 30)).grid(row=1,
                                                                                                           column=0
                                                                                       )
     
        tkinter.Label(self, text="Account ID", font=("Arial", 10)).grid(row=2, column=0)
        acc = tkinter.StringVar()
        acc.set("Enter Account ID")
        tkinter.Entry(self, textvariable=acc).grid(row=2, column=1)
        tkinter.Label(self, text="Secret Key", font=("Arial", 10)).grid(row=3, column=0)
        sec = tkinter.StringVar()
        sec.set("Enter Secret Key")
        tkinter.Entry(self, textvariable=sec).grid(row=3, column=1)
        tkinter.Button(self, text="Login", command=lambda:self.login(user_id=acc,secret_key=sec)).grid(row=4, column=2)
        self.bot = TradingBot(controller=self)
        self.mainloop()
        #self.protocol("WM_DELETE_WINDOW", exit(1))

    def login(self, user_id, secret_key):
        self.show_frame("Home")
        # self.db.create_table()
        # try:
        #     self.bot.login(user_id, secret_key)
        # except Exception as e:
        #     tkinter.Message(text=str(e))
        # pass
        

    def show_frame(self, frame=None):

         for fram in self.winfo_children():
            fram.destroy()
        
        
         self.config(bg='black',border=10,relief='ridge', width=1560, height=800)
         frame.tkraise()
        
