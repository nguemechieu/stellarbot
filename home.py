
import datetime
import time
from tkinter import LEFT, StringVar, Text, Tk, ttk
import tkinter
import pandas as pd

from stellar_sdk import Asset

from tradingbot import TradingBot


class Home(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter. Frame.__init__(self, parent)
        self.controller = controller
        self.parent=parent
        self.grid( row=0,column=0, sticky='nsew',ipadx=1400,ipady=600)
        self.config(background='lightgreen',relief='ridge')

        self.bot=None
        self.tab = ttk.Notebook(self)
        self.tab.grid(row=0,column=0)
        
        
        self.trade_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)
        self.history_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)
        self.order_book_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)
        self.settings_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)
        self.about_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)
        self.transactions_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)
        self.transactions_label = tkinter.Label(self.transactions_tab, 
                                                text='Transactions', 
                                               borderwidth=1)
        self.transactions_label.grid(row=1, column=0, sticky='nsew')

        self.transactions_list = tkinter.Listbox(self.transactions_tab, selectmode=tkinter.SINGLE, height=10, width=100)
        self.transactions_list.grid(row=1, column=1, sticky='nsew')









        self.send_or_receive_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)

        self.send_or_receive_send_btn = tkinter.Button(self.send_or_receive_tab, text='Send', command=lambda:self.send_order)
        self.send_or_receive_send_btn.grid(row=3, column=0, sticky='nsew')
        self.send_or_receive_receive_btn = tkinter.Button(self.send_or_receive_tab, text='Receive', command=lambda:self.receive_order)
        self.send_or_receive_receive_btn.grid(row=4, column=1, sticky='nsew')

        self.licence_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)
        self.licence_tab.grid(row=5, column= 0,  rowspan=2, sticky='nsew')

        self.licence_label = tkinter.Label(self.licence_tab, text='Licence', relief='groove', borderwidth=1)
        self.licence_label.grid(row=6, column=0, sticky='nsew')



    

        self.tab.add(self.trade_tab, text='Trade')
        self.tab.add(self.history_tab, text='History')
        self.tab.add(self.order_book_tab, text='OrderBook')
        self.tab.add(self.transactions_tab, text='Transactions')
        self.tab.add(self.send_or_receive_tab, text='Send or Receive')
        self.tab.add(self.licence_tab, text='Licence')



        self.tab.add(self.settings_tab, text='Settings')
        self.tab.add(self.about_tab, text='About')
        self.tab.pack(side=LEFT,expand=1, fill='both')
        infosvar = tkinter.StringVar()
        infosvar.set('Live Crypto Markets  '+datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S'))

        self.trade_infos_label = tkinter.Label(self.trade_tab, text='Trade Infos', borderwidth=1,textvariable=infosvar)
        
        self.trade_infos_label.grid(row=1, column=0, sticky='nsew')



        # Variable to store the toggle state (0 for OFF, 1 for ON)
        toggle_var = StringVar()
        toggle_var.set('start bot')

# Create the toggle button

        #read= pd.read_csv('account.csv')

        toggled_button1 = tkinter.Button(self.trade_tab, text="start bot", command=lambda:self.start_bot(start_bot=True,
                                                                                                                                 account_id="GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY",
                                                                                                                                 
                                                                                                                                 account_secret = "SDYAPMSEK2N4LYRFROWHE4SK4LFXF2T2OMCU3BVDAJTEAYKHT4ESKO"))
        toggled_button1.place(x=3,y=500)
        toggled_button = tkinter.Button(self.trade_tab, text="stop bot", command=lambda:self.start_bot(start_bot=False,
                                                                                                                                 account_id="GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY",
                                                                                                                                 
                                                                                                                                 account_secret = "SDYAPMSEK2N4LYRFROWHE4SK4LFXF2T2OMCU3BVDAJTEAYKHT4ESKOJ6"))
        toggled_button.place(x=100,y=500)



        if toggle_var.get() !='start bot':
            toggled_button.set('stop bot')
            self.update()





        
        self.trade_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume','Time'])
        self.trade_df.set_index('Time', inplace=True)

        self.history_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume','Time'])

        self.history_df.set_index('Time', inplace=True)


        self.order_book_label = tkinter.Label(self.trade_tab, text='Order Book')


        self.trade_tree =  ttk.Treeview(self.trade_tab, selectmode='browse')
        self.trade_tree.grid(row=2, column=6, sticky='nsew')

        self.trade_tree['columns'] = ('Open', 'High', 'Low', 'Close', 'Volume','Time')
        self.trade_tree['show'] = 'headings'
        self.trade_tree.column('Open', width=100)
        self.trade_tree.column('High', width=100)
        self.trade_tree.column('Low', width=100)
        self.trade_tree.column('Close', width=100)
        self.trade_tree.column('Volume', width=100)
        self.trade_tree.column('Time', width=100)
        self.trade_tree.heading('Open', text='Open')
        self.trade_tree.heading('High', text='High')
        self.trade_tree.heading('Low', text='Low')
        self.trade_tree.heading('Close', text='Close')
        self.trade_tree.heading('Volume', text='Volume')
        self.trade_tree.heading('Time', text='Time')

        self.config(width=1560, height=800, relief='groove',background='black')

        self.order_book_label = tkinter.Label(self.order_book_tab, text='Order Book')
        self.order_book_label.grid(row=1, column=0, sticky='nsew')
        self.order_book_canvas = tkinter.Canvas( self.order_book_tab, width=1100, height=500, relief='groove',background='black')
        self.order_book_canvas.grid(row=4, column=2, sticky='nsew')

        self.history_label = tkinter.Label(self.history_tab, text='History')
        self.history_label.grid(row=0, column=0, sticky='nsew')
        self.history_canvas = tkinter.Canvas( self.history_tab, width=1200, height=300, relief='groove',background='black')
        self.history_canvas.grid(row=4, column=0, sticky='nsew')

        self.settings_label = tkinter.Label(self.settings_tab, text='Settings')
        self.settings_label.grid(row=4, column=0, sticky='nsew')
        self.settings_canvas = tkinter.Canvas( self.settings_tab, width=1000, height=300, relief='groove',background='black')
        self.settings_canvas.grid(row=4, column=0, sticky='nsew')




        self.about_label = tkinter.Label(self.about_tab, text='Trading Bot')
        self.about_label.grid(row=5, column=0, sticky='nsew')
        self.update()



      



    def start_bot(self, start_bot=False, account_id='', account_secret=''  )->None:
         self.bot = TradingBot(start_bot=start_bot,account_id=account_id,account_secret=account_secret)


    
        



       


  
          
