from datetime import datetime
from tkinter import LEFT, TOP, BOTH, StringVar
import tkinter

from stellar_sdk import Asset


from tradingbot import TradingBot


class Home(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter. Frame.__init__(self, parent)
        self.controller = controller
        self.parent=parent
       
        self.grid(row=0, column=0, sticky='nsew')
        self.startvar=StringVar()
        self.startvar.set('START SERVER')
        self.start = tkinter.Button(self, text=self.startvar.get(), command=lambda:self.start_bot())
        self.start.grid(row=6, column=0, sticky='nsew',pady=20,padx=200)
    
        



    def start_bot(self)->None:
         self.bot = TradingBot(controller=self.controller)
         self.startvar.set('STOP SERVER')
         self.update()

         print(str( self.bot.get_assets(asset_code=Asset.native())))


       


  
          
