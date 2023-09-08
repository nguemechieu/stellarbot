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


        server = Server("https://horizon.stellar.org")
        account_id = "GALAXYVOIDAOPZTDLHILAJQKCVVFMD4IKLXLSZV5YHO7VY74IWZILUTO"
        raw_resp = server.accounts().account_id(account_id).call()
        parsed_resp = AccountResponse.model_validate(raw_resp)
        print(f"Account Sequence: {parsed_resp.sequence}")
        
        self.label_home = tkinter.Label(parent, text='Home')
        self.label_home.pack(side=tkinter.LEFT)
        self.controller=controller
        self.parent=parent
        self.width=400
        self.height=400
        self.canvas=tkinter.Canvas(parent, width=self.width, height=self.height, background='black')
        self.canvas.place(x=300,y=200)

        accountid= tkinter.StringVar()
        accountid.set('Enter account ID')
        

        self.account_id_label=tkinter.Label(self.parent, text='Account ID',textvariable=accountid)

        self.account_id_label.pack()

        accountsecret= tkinter.StringVar()
        accountsecret.set('Enter account secret')

        self.account_secret_label=tkinter.Label(self.parent, text='Account Secret',textvariable=accountsecret)
        self.account_secret_label.pack()


        self.login_btn = tkinter.Button(self.parent, text='Login',command=lambda: self.login(accountid.get(),accountsecret.get()))
        self.grid(row=0,column=0)
        

        def login(self,accountid:str=None, accountsecret:str=None):
            if accountid is not None and accountsecret is not None:
                bot =TradingBot(controller=self.controller)

                bot.login(self,accountid,accountsecret)
                self.controller.show_frame('Home')

    


                
            

                  

        

    