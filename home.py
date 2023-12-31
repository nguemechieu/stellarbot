
from tkinter import LEFT, ttk
import tkinter
import pandas as pd
from account import Account
from order_book import OrderBook
from tradingbot import TradingBot




class Home(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter. Frame.__init__(self, parent)
        self.controller = controller
      
        self.parent=parent
        self.grid( row=0,column=0, sticky='nsew',ipadx=1530,ipady=800)
        self.tab = ttk.Notebook(self)
        self.tab.grid(row=0, column=0, sticky='nsew',ipadx=1530,ipady=800)
        self.trade_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1,cursor= 'hand2')
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
        self.transactions_list.config(yscrollcommand=self.transactions_list.yview)
    
        # for index, row in read_transactions.iterrows():
        #     self.transactions_list.insert(tkinter.END, str(row))
        self.send_money_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)
        self.send_money_tab.grid(row=2, column=0, sticky='nsew')

        self.send_money_label = tkinter.Label(self.send_money_tab, text='Send Money', relief='groove', borderwidth=1)
        self.send_money_label.grid(row=1, column=0, sticky='nsew')

        self.receive_money_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)
        self.receive_money_tab.grid(row=2, column=0, sticky='nsew')

        self.receive_money_label = tkinter.Label(self.receive_money_tab, text='Receive Money', relief='groove', borderwidth=1)
        self.receive_money_label.grid(row=2, column=1, sticky=' nsew')




        self.licence_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)
        self.licence_tab.grid(row=5, column= 0,  rowspan=2, sticky='nsew')

        self.licence_label = tkinter.Label(self.licence_tab, text='Licence', relief='groove', borderwidth=1)
        self.licence_label.grid(row=6, column=0, sticky='nsew')

        self.balance_label = tkinter.Label(self.transactions_tab, text='Balance', relief='ridge')
        self.balance_label.grid(row=7, column=0, sticky='nsew')
        


        read=pd.read_csv('balances.csv')
        
        self.balance_tree = ttk.Treeview(self.transactions_tab)
        self.balance_tree.grid(row=7, column=1, sticky='nsew')

        columns = ('asset_code','asset_type','asset_issuer','asset_code','limit','limit','buying_liabilities','selling_liabilities','last_modified_ledger','is_authorized','is_authorized.1','is_authorized_to_maintain_liabilities','asset_code')
       
      
     #values=(row['asset_code'], row('asset_type'), row['asset_issuer'], row['asset_code'], row['limit'], row['buying_liabilities'], row['selling_liabilities'], row['last_modified_ledger'], row['is_authorized'], row['is_authorized.1'],
       
        self.balance_tree['columns'] = columns
        self.balance_tree['show'] = 'headings'
        self.balance_tree.heading('asset_code', text='Asset Code')
        self.balance_tree.heading('asset_type', text='Asset Type')
        self.balance_tree.heading('asset_issuer', text='Asset Issuer')
        self.balance_tree.heading('limit', text='Limit')
        self.balance_tree.heading('buying_liabilities', text='Buying Liabilities')
        self.balance_tree.heading('selling_liabilities', text='Selling Liabilities')
        self.balance_tree.heading('last_modified_ledger', text='Last Modified Ledger')
        self.balance_tree.heading('is_authorized', text='Is Authorized')
        self.balance_tree.heading('is_authorized.1', text='Is Authorized.1')
        self.balance_tree.heading('is_authorized_to_maintain_liabilities', text='Is Authorized To Maintain Liabilities')
        self.balance_tree.heading('asset_code', text='Asset Code')
        
        for index, row in read.iterrows():

            print(index,row)
            
            self.balance_tree.insert('', 'end', text=row['asset_code'], values=(row['asset_code'], row['asset_type'], row['asset_issuer'], row['asset_code'], row['limit'], row['buying_liabilities'], row['selling_liabilities'], row['last_modified_ledger'], row['is_authorized'], row['is_authorized.1'], row['is_authorized_to_maintain_liabilities'], row['asset_code']))
          

        self.history_label = tkinter.Label(self.history_tab, text='History', relief='groove', borderwidth=1)
        self.history_label.grid(row=1, column=0, sticky='nsew')

        self.account_tab =  tkinter.Frame(self.tab, relief='groove', borderwidth=1)
        self.account_tab.place(x=0, y=0, relwidth=1, relheight=1)

        self.settings_label = tkinter.Label(self.account_tab, text='Settings', relief='groove', borderwidth=1)
        self.settings_label.grid(row=0, column=0, sticky='nsew')
        

        self.trade_server_text = tkinter.StringVar()

        self.trade_server_label = tkinter.Label(self.trade_tab, background='black',font= ('Arial',14),
                                                foreground='lightgreen', relief = 'groove',borderwidth=6)
        self.trade_server_label.place(x=10, y=20, width=1000, height=100)




      

# Create the toggle button

        #read= pd.read_csv('account.csv')
        self.account_id = tkinter.StringVar()
        self.account_secret = tkinter.StringVar()
        self.toggled_button1 = tkinter.Button(self.trade_tab,bg='green',fg='white', text="START",width=20, command=lambda:self.start_bot(account_id= self.account_id, account_secret= self.account_secret))
        self.toggled_button1.place(x=300, y=20)                                                                                                                       
        self.toggled_button = tkinter.Button(self.trade_tab,bg='red',fg='white',text='STOP',width=20, command=lambda:self.stop_bot())
        self.toggled_button.place(x=450, y=20)

        self.trade_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume','Time'])
        self.trade_df.set_index('Time', inplace=True)

        self.history_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume','Time'])

        self.history_df.set_index('Time', inplace=True)



        self.trade_tree =  ttk.Treeview(self.trade_tab, selectmode='browse')
        self.trade_tree.place(x=10, y=500, width=1000, height=400)

        self.trade_tree['columns'] = ('symbol','timestamp','open', 'high', 'low', 'close')
        self.trade_tree['show'] = 'headings'
        self.trade_tree.heading('symbol', text='symbol')
        self.trade_tree.heading('timestamp', text='timestamp')
        self.trade_tree.heading('open', text='open')
        self.trade_tree.heading('high', text='high')
        self.trade_tree.heading('low', text='low')
        self.trade_tree.heading('close', text='close')
       
        
        
        self.order_book_label = tkinter.Label(self.order_book_tab, text='Order Book')
        self.order_book_label.grid(row=1, column=0, sticky='nsew')
        self.order_book_canvas = tkinter.Canvas( self.order_book_tab,relief='groove',background='black')
        self.order_book_canvas.place(x=0, y=10, width=1500, height=700)

        self.history_label = tkinter.Label(self.history_tab, text='History')
        self.history_label.grid(row=0, column=0, sticky='nsew')
        self.history_canvas = tkinter.Canvas( self.history_tab, width=1200, height=300, relief='groove',background='black')
        self.history_canvas.place(x=0, y=50, width=1500, height= 800 ,anchor= 'nw')

        self.settings_label = tkinter.Label(self.settings_tab, text='Settings')
        self.settings_label.grid(row=4, column=0, sticky='nsew')
        self.settings_canvas = tkinter.Canvas( self.settings_tab, width=1000, height=300, relief='groove',background='black')
        self.settings_canvas.grid(row=4, column=0, sticky='nsew')
        self.about_label = tkinter.Label(self.about_tab, text='Trading Bot')
        self.about_label.grid(row=5, column=0, sticky='nsew')

        self.trade_canvas = tkinter.Canvas( self.trade_tab, relief='groove',background='black')
        self.trade_canvas.place(x=10, y=110, width= 1000, height= 400)
         
        self.tab.add(self.trade_tab, text='Trade')
        self.tab.add(self.order_book_tab, text='OrderBook')
        self.tab.add(self.account_tab, text='Account')
        self.tab.add(self.history_tab, text='History')
        self.tab.add(self.transactions_tab, text='Transactions')
        self.tab.add(self.send_money_tab, text='Send Money')
        self.tab.add(self.receive_money_tab, text='Receive Money')
        self.tab.add(self.settings_tab, text='Settings')
        self.tab.add(self.licence_tab, text='Licence')
        
       

      
        #Update the GUI
        self.updateMe()
    def stop_bot(self)->None:

        self.controller.bot.stop()
        self.toggled_button1.config( background='gray',fg='yellow',state='normal',text='START')
        self.toggled_button.config(background='green',fg='yellow',state='disabled',text='STOP')

    def start_bot(self, account_id='', account_secret=''  )->None:
       self.controller.bot.start()
       self.controller.bot.account_id=account_id
       self.controller.bot.account_secret=account_secret
       self.toggled_button1.config( background='green',fg='yellow',state='disabled',text='START')
       self.toggled_button.config(background='gray',fg='yellow',state='normal',text='STOP')
    
    
    def updateMe(self)->None:
        self.update()
        self.trade_tree.delete(*self.trade_tree.get_children())
        self.trade_tree.insert('', 'end', text='symbol', values=(self.controller.bot.candles['symbol'], self.controller.bot.candles['timestamp'], self.controller.bot.candles['open'], self.controller.bot.candles['high'], self.controller.bot.candles['low'], self.controller.bot.candles['close'])) 
     
        
        
        
        
        self.trade_server_label.config(text=str(self.controller.bot.server_msg['status']+'\n'+
                                                     self.controller.bot.server_msg['message']))
        self.after(1000, self.updateMe)

    
    def send_money(self)->None:
        print('starting send')
      
   

    def receive_money(self)->None:
        print('starting receive')
      
       


  
          
