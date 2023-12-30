
import datetime
from tkinter import LEFT, StringVar, ttk
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
        self.grid( row=0,column=0, sticky='nsew',ipadx=1500,ipady=700)
        self.config(background='lightgreen',relief='ridge')

        
        self.tab = ttk.Notebook(self)
        self.tab.grid(row=1,column=0)
        self.config(background='lightgreen',relief='ridge')

       
        
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
        self.transactions_list.config(yscrollcommand=self.transactions_list.yview)
    
        # for index, row in read_transactions.iterrows():
        #     self.transactions_list.insert(tkinter.END, str(row))









        

        self.send_or_receive_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)

        self.send_or_receive_receive_Label = tkinter.Label(self.send_or_receive_tab, text='amount', relief='groove', borderwidth=1)
        self.send_or_receive_receive_Label.grid(row=1, column=0, sticky='nsew')
        self.send_or_receive_receive_amount = tkinter.Entry(self.send_or_receive_tab)
        self.send_or_receive_receive_amount.grid(row=1, column=1, sticky='nsew')

        self.send_or_receive_send_asset = tkinter.Label(self.send_or_receive_tab, text='asset', relief='groove', borderwidth=1)
        self.send_or_receive_send_asset.grid(row=2, column=0, sticky='nsew')

        self.send_or_receive_send_Label = tkinter.Label(self.send_or_receive_tab, text='to', relief='groove', borderwidth=1)
        self.send_or_receive_send_Label.grid(row=2, column=1, sticky='nsew')
        self.send_or_receive_send_to = tkinter.Entry(self.send_or_receive_tab)
        self.send_or_receive_send_to.grid(row=2, column=1, sticky='nsew')

        self.send_or_receive_send_btn = tkinter.Button(self.send_or_receive_tab, text='Send', command=lambda:self.send_order)
        self.send_or_receive_send_btn.grid(row=3, column=0, sticky='nsew',padx=100,pady=200)
        self.send_or_receive_receive_btn = tkinter.Button(self.send_or_receive_tab, text='Receive', command=lambda:self.receive_order)
        self.send_or_receive_receive_btn.grid(row=3, column=1, sticky='nsew',padx=20,pady=200)

        self.licence_tab = ttk.Frame(self.tab, relief='groove', borderwidth=1)
        self.licence_tab.grid(row=5, column= 0,  rowspan=2, sticky='nsew')

        self.licence_label = tkinter.Label(self.licence_tab, text='Licence', relief='groove', borderwidth=1)
        self.licence_label.grid(row=6, column=0, sticky='nsew')

        self.balance_label = tkinter.Label(self.transactions_tab, text='Balance', relief='ridge')
        self.balance_label.grid(row=7, column=0, sticky='nsew')
        


        read=pd.read_csv('balances.csv')
        
        self.balance_tree = ttk.Treeview(self.transactions_tab)
        self.balance_tree.grid(row=7, column=1, sticky='nsew')
#       balance                                                                                0.0
# limit                                                                  922337203685.477783
# buying_liabilities                                                                     0.0
# selling_liabilities                                                                    0.0
# last_modified_ledger                                                            48054224.0
# is_authorized                                                                         True
# is_authorized.1                                                                       True
# is_authorized_to_maintain_liabilities                                                 True
# asset_type                                                                credit_alphanum4
# asset_code                                                                            AQUA
# asset_issuer                             GBNZILSTVQZ4R7IKQDGHYGY2QXL5QOFJYQMXPKWRRM5PAV...

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
            
            self.balance_tree.insert('', 'end', text=row['asset_code'], values=(row['asset_code'], row['asset_type'], row['asset_issuer'], row['asset_code'], row['limit'], row['buying_liabilities'], row['selling_liabilities'], row['last_modified_ledger'], row['is_authorized'], row['is_authorized.1'], row['is_authorized_to_maintain_liabilities'], row['asset_code']))
          
                                     
                                     
                                     
                                     
                                     
                                     
                                     
        
              


        self.history_label = tkinter.Label(self.history_tab, text='History', relief='groove', borderwidth=1)
        self.history_label.grid(row=1, column=0, sticky='nsew')

        



    

        self.tab.add(self.trade_tab, text='Trade')
        self.tab.add(self.history_tab, text='History')
        self.tab.add(self.order_book_tab, text='OrderBook')
        self.tab.add(self.transactions_tab, text='Transactions')
        self.tab.add(self.send_or_receive_tab, text='Send or Receive')
        self.tab.add(self.licence_tab, text='Licence')



        self.tab.add(self.settings_tab, text='Settings')
        self.tab.add(self.about_tab, text='About')
        self.tab.pack(side=LEFT,expand=1, fill='both')
  
   
# Create the toggle button

        #read= pd.read_csv('account.csv')
        self.account_id = tkinter.StringVar()
        self.account_secret = tkinter.StringVar()
        self.toggled_button1 = tkinter.Button(self.trade_tab,bg='green',fg='white', text="START",width=20, command=lambda:self.start_bot(account_id= self.account_id, account_secret= self.account_secret))
        self.toggled_button1.place(x=300, y=20)                                                                                                                       
        self.toggled_button = tkinter.Button(self.trade_tab,bg='red',fg='white',text='STOP',width=20, command=lambda:self.stop_bot)
        self.toggled_button.place(x=450, y=20)

        self.trade_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume','Time'])
        self.trade_df.set_index('Time', inplace=True)

        self.history_df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume','Time'])

        self.history_df.set_index('Time', inplace=True)


        self.order_book_label = tkinter.Label(self.trade_tab, text='Order Book')


        self.trade_tree =  ttk.Treeview(self.trade_tab, selectmode='browse')
        self.trade_tree.place(x=700, y=600, width=1000, height=400)

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
        self.config(width=1560, height=800, relief='groove',background='black',borderwidth=1)
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
        self.screen_canvas = tkinter.Canvas( self.trade_tab,border=9, relief='raised', background='black')
        self.screen_canvas.place(x=0, y=50, width=1400, height=500  ,anchor= 'nw')

      
    
        self.update()
    def stop_bot(self)->None:

        self.controller.bot.stop()
        self.toggled_button1.config( background='yellow',fg='white',state='disabled',text='START')

    def start_bot(self, account_id='', account_secret=''  )->None:
       self.controller.bot.start_bot=True
       self.controller.bot.account_id=account_id
       self.controller.bot.account_secret=account_secret
       
       self.toggled_button1.config(background='red',fg='white',state='disabled',text='STOP')
    
    def updateMe(self)->None:
        self.update()
        self.trade_tree.delete(*self.trade_tree.get_children())
        self.trade_tree.insert(*self.trade_df.values.tolist())

        

        self.after(1000, self.updateMe)



       


  
          
