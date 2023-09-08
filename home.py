from datetime import datetime
from tkinter import LEFT, TOP, Frame, BOTH, Label
import tkinter


from tradingbot import TradingBot


class Home(Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        self.parent = parent
        self.bot = TradingBot(controller=self.controller)
        self.trade_info = {}



        self.label_home = tkinter.Label( self.parent, text='Home')
        self.label_home.pack(side=LEFT)
        Frame.__init__(self, parent)
        self.grid(row =0, column =0)


  
          
