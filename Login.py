import tkinter
from tkinter import ttk
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
        self.grid( row =0,column=0,pady=250,padx=650, sticky ='nswe')


        tkinter.Label(self,text="Account ID",font=("Helvetica",15)).grid(row=1,column=5)
        tkinter.Label(self,text="Account Secret",font=("Helvetica",15)).grid(row=2,column=5)
     
        self.account_id=tkinter.StringVar()
        self.account_secret=tkinter.StringVar()
        
        tkinter.Entry(self,textvariable=self.account_id).grid(row=1,column=6 )
        tkinter.Entry(self,textvariable=self.account_secret).grid(row=2,column=6)
        
        cff= tkinter.StringVar()
        cff.set(value='name')
        # self.choicebox= ttk.Combobox(self, width = 27, textvariable = cff)
        # self.choicebox.grid(row =4,column=3)
        
     
        tkinter.Button(self,text="Login",command=lambda:self.login(accountid= self.account_id.get(),accountsecret=self.account_secret.get())).grid(row=11,column=6)
        tkinter.Button(self,text="CreateAccount",command=lambda:self.controller.show_pages('CreateAccount')).grid(row=11,column=5,padx=1)


    def cancel(self):
         self.controller.show_pages('Login')
    def reset(self):
         self.account_id.set("")
         self.account_secret.set("")
       
    def login(self,accountid:str=None, accountsecret:str=None):
            if accountid is not None and accountsecret is not None:
                self.account_id=accountid
                self.account_secret=accountsecret
               
                self.controller.show_pages('Home')
            
    


                
            

                  

        

    