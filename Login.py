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


        # server = Server("https://horizon.stellar.org")
        # account_id = "GALAXYVOIDAOPZTDLHILAJQKCVVFMD4IKLXLSZV5YHO7VY74IWZILUTO"
        # raw_resp = server.accounts().account_id(account_id).call()
        # parsed_resp = AccountResponse.model_validate(raw_resp)
        # print(f"Account Sequence: {parsed_resp.sequence}")

        self.controller=controller
        self.parent=parent


        accountid= tkinter.StringVar()
        accountid.set('Enter account ID')
        
        tkinter.Label(self.parent, text='Account ID').grid(row=1,column=0, pady=20)
        tkinter.Entry(self.parent,textvariable= accountid).grid( row=1,column=1,pady=20)


        accountsecret= tkinter.StringVar()
        accountsecret.set('Enter account secret')

        tkinter.Label(self.parent, text='Account Secret').grid( row=2,column=0, pady=20)
        tkinter.Entry(self.parent,textvariable= accountsecret).grid( row=2,column=1,pady=20)
        


        tkinter.Button(self.parent, text='Login',command=lambda: self.login(accountid.get(),
                                                                            accountsecret.get())).grid(row=3,column=2,padx=20,pady=20)
        tkinter.Button(self.parent, text='CreateAccount',command=lambda:   self.controller.show_pages('CreateAccount')).grid(row=3,column=0,pady=20)

      
        

    def login(self,accountid:str=None, accountsecret:str=None):
            if accountid is not None and accountsecret is not None:
                self.account_id=accountid
                self.account_secret=accountsecret
               
                self.controller.show_pages('Home')
            
    


                
            

                  

        

    