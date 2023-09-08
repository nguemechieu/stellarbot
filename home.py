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
        Frame.__init__(self, parent)
       
        self.createWidgets()

       
    
    def createWidgets(self):
        self.label_home = tkinter.Label( self.parent, text='Home')
        self.label_home.grid(row=0, column=0)


        self.menu_home = tkinter.Menu(self.parent)
        self.menu_home.grid(
            row =1,column=0
         )
        self.parent.config(menu=self.menu_home)
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
        self.menu_home.add_command(label='Exit', command=exit(1))
 


  
          
