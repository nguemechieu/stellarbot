import tkinter
from history import History
from home import Home
from order_book import OrderBook
from orders import Orders

from tradingbot import TradingBot
from stellar_sdk import Server
from stellar_model import AccountResponse

class Login(tkinter.Frame):

    def __init__(self, parent=None,controller=None):
        tkinter.Frame.__init__(self, parent)

        self.controller=controller
        self.grid( row =0,column=0,pady=20,padx=20, sticky ='nswe')


        tkinter.Label(self,text="Account ID",font=("Helvetica",15)).grid(row=1,column=0)
        tkinter.Label(self,text="Account Secret",font=("Helvetica",15)).grid(row=2,column=0)
        tkinter.Label(self,text="Server",font=("Helvetica",15)).grid(row=3,column=0)
        self.account_id=tkinter.StringVar()
        self.account_secret=tkinter.StringVar()
        self.server=tkinter.StringVar()
        self.network=tkinter.StringVar()
        self.network_passphrase=tkinter.StringVar()
        tkinter.Entry(self,textvariable=self.account_id).grid(row=1,column=1,padx=300
                                                              )
        tkinter.Entry(self,textvariable=self.account_secret).grid(row=2,column=1,padx=300)
        tkinter.Entry(self,textvariable=self.server).grid(row=3,column=1)
     
        tkinter.Button(self,text="Login",command=lambda:self.login(accountid= self.account_id.get(),accountsecret=self.account_secret.get())).grid(row=7,column=6)
        tkinter.Button(self,text="Cancel",command=lambda:self.cancel).grid(row=7,column=1)
        tkinter.Button(self,text="Reset",command=lambda:self.reset()).grid(row=7,column=2)


    def cancel(self):
         self.controller.show_pages('Login')
    def reset(self):
         self.account_id.set("")
         self.account_secret.set("")
         self.server.set("")
         self.network.set("")
         self.network_passphrase.set("")        

    def login(self,accountid:str=None, accountsecret:str=None):
            if accountid is not None and accountsecret is not None:
                self.account_id=accountid
                self.account_secret=accountsecret
               
                self.controller.show_pages('Home')
            
    


                
            

                  

        

    