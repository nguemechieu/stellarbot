from datetime import datetime
from tkinter import LEFT, TOP, BOTH
import tkinter

from stellar_sdk import Asset


from tradingbot import TradingBot


class Home(tkinter.Frame):
    def __init__(self, parent, controller):
        
        
       
        tkinter. Frame.__init__(self, parent)
        self.controller = controller
        self.parent=parent
       
        self.trade_info = {}
       
 
        self.start = tkinter.Button(self, text='Start', command=lambda:self.start_bot)
        self.start.grid(row=6, column=0, sticky='nsew',pady=20,padx=200)


        self.menu_home = tkinter.Menu(self.parent, tearoff=0)
    
        self.menu_home.add_command(label='Start', command=lambda:self.start)
        self.menu_home.add_separator()
        self.menu_home.add_command(label='Stop', command=lambda:self.stop)
        self.menu_home.add_separator()
        self.menu_home.add_command(label='File', command=lambda:self.file)
        self.menu_home.add_separator()
        self.menu_home.add_command(label='Open', command=lambda:self.open)
        self.menu_home.add_separator()
        self.menu_home.add_command(label='Save', command=lambda:self.save)
        self.menu_home.add_separator()
        self.menu_home.add_command(label='Exit', command=lambda:exit(1))
        self.grid(row=0, column=0, sticky='nsew')

    def start_bot(self):
         self.bot = TradingBot(controller=self.controller)

         print(str( self.bot.get_assets(asset_code=Asset.native())))


       


  
          
