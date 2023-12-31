
from tkinter import  ttk
import tkinter
import pandas as pd
import os


class Home(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter. Frame.__init__(self, parent)
        self.controller = controller
      
        self.parent=parent
        self.grid( row=0,column=0, sticky='nsew',ipadx=1530,ipady=800)
        self.tab = ttk.Notebook(self)
        self.tab.grid(row=0, column=0, sticky='nsew',ipadx=1530,ipady=800)
        self.trade_tab = tkinter.Frame(self.tab, relief='groove',background='gray')
        self.history_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='gray')
        self.order_book_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='gray')
        self.settings_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='gray')
        self.about_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='gray')
        self.transactions_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='gray')
        self.transactions_label = tkinter.Label(self.transactions_tab, 
                                                text='Transactions', 
                                               borderwidth=1)
        self.transactions_label.grid(row=1, column=0, sticky='nsew')

        self.transactions_list = tkinter.Listbox(self.transactions_tab, selectmode=tkinter.SINGLE, height=20, width=600)
        self.transactions_list.place(x=10, y=20, width=600, height=400)
        self.transactions_list.config(yscrollcommand=self.transactions_list.yview)
        
        read_transactions = self.controller.bot.get_transactions()

        self.offers_list = tkinter.Listbox(self.transactions_tab, selectmode=tkinter.SINGLE, height=20, width=1100)
        self.offers_list.place(x=700, y=20, width=600, height=400)
        for index in read_transactions:

            index0=0
            while index0<len(read_transactions):
                self.offers_list.insert(tkinter.END, str(index.__str__()+' : '+read_transactions[index0].__str__()))
                index0+=1
     
        self.send_money_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='gray')
        self.send_money_tab.grid(row=2, column=0, sticky='nsew')

        self.send_money_label = tkinter.Label(self.send_money_tab, text='Send Money', relief='groove', borderwidth=1)
        self.send_money_label.grid(row=1, column=0, sticky='nsew')

        self.receive_money_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='gray')
        self.receive_money_tab.grid(row=2, column=0, sticky='nsew')

        self.receive_money_label = tkinter.Label(self.receive_money_tab, text='Receive Money', relief='groove', borderwidth=1)
        self.receive_money_label.grid(row=2, column=1, sticky=' nsew')

        self.licence_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='gray')
        self.licence_tab.grid(row=5, column= 0,  rowspan=2, sticky='nsew')

        self.licence_label = tkinter.Label(self.licence_tab, text='Licence', relief='groove', borderwidth=1)
        self.licence_label.grid(row=6, column=0, sticky='nsew')

        self.about_tab = tkinter.Frame(self.tab, relief='groove', border=1,background='gray')
        self.about_tab.grid(row=6, column=1, sticky='nsew')

        self.balance_label = tkinter.Label(self.transactions_tab, text='Balance', relief='ridge')
        self.balance_label.grid(row=7, column=0, sticky='nsew')
        

        if not os.path.exists('balances.csv'):
            with open('balances.csv', 'w') as f:
                f.write('asset_code,asset_type,asset_issuer,asset_code,limit,buying_liabilities,selling_liabilities,last_modified_ledger,is_authorized,is_authorized.1,is_authorized_to_maintain_liabilities,asset_code\n')
                f.close()

                 
        read=pd.read_csv('balances.csv')
        
        self.balance_tree = ttk.Treeview(self.transactions_tab, selectmode='extended')
        self.balance_tree.place(x=10, y=400)

        columns = ('asset_code','asset_type','asset_issuer','asset_code','limit','buying_liabilities','selling_liabilities','last_modified_ledger','is_authorized','is_authorized.1','is_authorized_to_maintain_liabilities','asset_code')
       
      
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
          






        self.account_tab =  tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='gray')
        self.account_tab.place(x=0, y=0, relwidth=1, relheight=1)
        self.account_canvas = tkinter.Canvas(self.account_tab, width=1300, height = 600,background= 'black')
        self.account_canvas.place(x=0, y=30, relwidth=1, relheight=1)

        account=pd.read_csv('account.csv')
        self.account_canvas.create_text(10, 10, text=[account].sort(), font= ('Arial',14) )

     
        self.trade_server_text = tkinter.StringVar()

        self.trade_server_label = tkinter.Label(self.trade_tab, background='black',font= ('Arial',14),
                                                foreground='lightgreen', relief = 'groove',borderwidth=6)
        self.trade_server_label.place(x=0, y=0, width=1000, height=150)

        self.toggled_button1 = tkinter.Button(self.trade_tab,bg='green',fg='white', text="START",width=20, command=lambda:self.start_bot())
        self.toggled_button1.place(x=1000, y=10)                                                                                                                       
        self.toggled_button = tkinter.Button(self.trade_tab,bg='red',fg='white',text='STOP',width=20, command=lambda:self.stop_bot())
        self.toggled_button.place(x=1100, y=10)

        


        self.trade_tree =  ttk.Treeview(self.trade_tab, selectmode='browse')
        self.trade_tree.place(x=0, y=500, width=1000, height=300)
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
        self.order_book_canvas.place(x=0, y=30, width=1200, height=600)
        order_book = pd.read_csv('order_book.csv')
        self.order_book_canvas.create_text(10, 10, text=[order_book].__str__(), font= ('Arial',14), anchor= 'nw' )
        self.history=[]                             

        self.history_label = tkinter.Label(self.history_tab, text='History')
        self.history_label.grid(row=0, column=0, sticky='nsew')
        self.history_canvas = tkinter.Canvas( self.history_tab, width=1200, height=300, relief='groove',background='black',bd= 3)
        self.history_canvas.place(x=0, y=30, width=1500, height= 600 ,anchor= 'nw')
        self.history_canvas.create_text(10, 10, text=self.history.sort().__str__(), font=('Arial',14), anchor= 'nw')
        



        self.transactions_label = tkinter.Label(self.transactions_tab, text='Transactions')
        self.transactions_label.grid(row=1, column=0, sticky='nsew')

        self.settings_label = tkinter.Label(self.settings_tab, text='Settings')
        self.settings_label.grid(row=4, column=0, sticky='nsew')
        self.settings_canvas = tkinter.Canvas( self.settings_tab, width=1000, height=600, relief='groove',background='black')
        self.settings_canvas.place(x=0, y=30, width=1000, height=   600,anchor= 'nw')
        self.about_label = tkinter.Label(self.about_tab, text='Trading Bot')
        self.about_label.grid(row=5, column=0, sticky='nsew')

        self.trade_canvas = tkinter.Canvas( self.trade_tab, relief='groove',background='black')
        self.trade_canvas.place(x=0, y=150, width= 1000, height= 350)
         
        self.tab.add(self.trade_tab, text='Trade')
        self.tab.add(self.order_book_tab, text='OrderBook')
        self.tab.add(self.account_tab, text='Account')
        self.tab.add(self.history_tab, text='History')
        self.tab.add(self.transactions_tab, text='Transactions')
        self.tab.add(self.send_money_tab, text='Send Money')
        self.tab.add(self.receive_money_tab, text='Receive Money')
        self.tab.add(self.settings_tab, text='Settings')
        self.tab.add(self.licence_tab, text='Licence')
        self.tab.add(self.about_tab, text='About')
        self.trade_tree.bind('<<TreeviewSelect>>', self.on_treeview)

        
        self.trade_tab.configure(scrollregion=self.trade_canvas.bbox('all'))
               
       

      
        #Update the GUI
        self.updateMe()
    def on_treeview(self,event):

        if event:
            index = self.trade_tree.focus()
            self.trade_tree.item(index)

    def stop_bot(self)->None:

        self.controller.bot.stop()
        self.toggled_button1.config( background='gray',fg='yellow',state='normal',text='START')
        self.toggled_button.config(background='green',fg='yellow',state='disabled',text='STOP')

    def start_bot(self  )->None:
       self.controller.bot.start()

       self.toggled_button1.config( background='green',fg='yellow',state='disabled',text='START')
       self.toggled_button.config(background='gray',fg='yellow',state='normal',text='STOP')
    
    
    def updateMe(self)->None:
        self.update()
    
        self.trades =self.controller.bot.get_trades()
        self.history_canvas.create_text(10, 10, text=self.controller.bot.get_history().__str__(), font= ('Arial',14),fill='white') 
        self.trade_canvas.create_text(10, 10, text=self.trades.__str__(), font= ('Arial',14), fill='white') 


         # Create candles update time 
        update_time = self.controller.bot.get_update_time()
        last_update_time = self.controller.bot.last_update_time
        if update_time < last_update_time:
          last_update_time = update_time
          candles = self.controller.bot.candles
          if candles['symbol'] is not None:
           self.trade_tree.insert('', 'end', text='symbol', values=(candles['symbol'], candles['timestamp'],
                                                                candles['open'], 
                                                                candles['high'],
                                                                candles['low'], 
                                                                candles['close'])) 
        
        self.trade_server_label.config(text=str("Server: "+self.controller.bot.server_msg['status'].__str__()+'\n\n'+
                                                     self.controller.bot.server_msg['message'].__str__()+
                                                     "\n\n"+self.controller.bot.learn.fibo_msg.__str__()+'\n'),
                                                     anchor= 'nw',activebackground='lightblue')
        self.after(1000, self.updateMe)

    
    def send_money(self)->None:
        print('starting send')
      
   

    def receive_money(self)->None:
        print('starting receive')
      
       


  
          
