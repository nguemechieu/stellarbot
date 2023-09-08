
import tkinter
from stellar_model import AccountResponse

from stellar_sdk import Server
import Login
from history import History
from home import Home
from marketwatch import MarketWatch
from orders import Orders
from tradingbot import TradingBot
from wallet import Wallet
from db import Db




class StellarBot(tkinter.Frame):


    def __init__(self, *args, **kwargs):

        tkinter.Frame.__init__(self, *args, **kwargs)
    
        self.tradingbot=TradingBot(controller=self)


        print(str(  self.tradingbot.get_assets()))
        print( str(self.tradingbot.account_df))
        

        self.grid(row=0,column=0,sticky="nsew")
     
        
