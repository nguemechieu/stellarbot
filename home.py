import os
import datetime 
from tkinter import  ttk
import tkinter
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


 
'''   This class is the main frame of the application. It contains the tabs and the widgets.'''
class Home(tkinter.Frame):
    '''This class is the main frame of the application. It contains the tabs and the widgets.'''
    def __init__(self, parent, controller):
        tkinter. Frame.__init__(self, parent)
        self.controller = controller
      
        self.parent=parent
        self.grid( row=0,column=0, sticky='nsew',ipadx=1530,ipady=800)
        self.tab = ttk.Notebook(self)
        self.tab.grid(row=0, column=0, sticky='nsew',ipadx=1530,ipady=800)
        self.trade_tab = tkinter.Frame(self.tab, relief='groove',background='green')
        self.history_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='green')
        self.order_book_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='purple')
        self.settings_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='green')
        self.about_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='orange')
        self.transactions_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='blue')
        self.transactions_label = tkinter.Label(self.transactions_tab, 
                                                text='Transactions', 
                                               borderwidth=1)
     

        self.transactions_list = tkinter.Listbox(self.transactions_tab, selectmode=tkinter.SINGLE, height=20, width=600)
        self.transactions_list.place(x=0, y=20, width=600, height=400)
        
        read_transactions = pd.read_csv('ledger_transactions.csv')

        self.offers_list = tkinter.Listbox(self.transactions_tab, selectmode=tkinter.SINGLE, height=20, width=1100)
        self.offers_list.place(x=700, y=20, width=600, height=400)
      
        offers = pd.read_csv('ledger_offers.csv')
        self.offers_list.insert(tkinter.END, str(offers.__str__())  + '\n')
              
        self.transactions_list.insert(tkinter.END, str(read_transactions.__str__()+'\n'))
  
        self.send_money_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='gray')
        self.send_money_tab.grid(row=2, column=0, sticky='nsew')

        self.send_money_label = tkinter.Label(self.send_money_tab, text='Send Money', relief='groove', borderwidth=1)
        self.send_money_label.place(x= 400, y=500, height=40)

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
        

                 
        #read=pd.read_csv('ledger_account.csv')
        
        self.balance_tree = ttk.Treeview(self.transactions_tab, selectmode='browse')
        self.balance_tree.place(x=10, y=20)

        columns = ('asset_code','asset_type','asset_code','limit','buying_liabilities','selling_liabilities','last_modified_ledger','is_authorized','is_authorized.1','is_authorized_to_maintain_liabilities','asset_code')
        self.balance_tree['columns'] = columns
        self.balance_tree['show'] = 'headings'
        self.balance_tree.heading('asset_code', text='Asset Code')
        self.balance_tree.heading('asset_type', text='Asset Type')
      
        self.balance_tree.heading('limit', text='Limit')
        self.balance_tree.heading('buying_liabilities', text='Buying Liabilities')
        self.balance_tree.heading('selling_liabilities', text='Selling Liabilities')
        self.balance_tree.heading('last_modified_ledger', text='Last Modified Ledger')
        self.balance_tree.heading('is_authorized', text='Is Authorized')
        self.balance_tree.heading('is_authorized.1', text='Is Authorized.1')
        self.balance_tree.heading('is_authorized_to_maintain_liabilities', text='Is Authorized To Maintain Liabilities')
        self.balance_tree.heading('asset_code', text='Asset Code')
   
        # row = pd.DataFrame(read)
        # self.balance_tree.insert('', 'end', text=(row['asset_code'], row['asset_type'], row['limit'], row['buying_liabilities'], row['selling_liabilities'], row['last_modified_ledger'], row['is_authorized'], row['is_authorized.1'], row['is_authorized_to_maintain_liabilities']))
        

        self.account_tab =  tkinter.Frame(self.tab, relief='groove', borderwidth=1,background='gray')
        self.account_tab.place(x=0, y=0)
      
        self.trade_server_text = tkinter.StringVar()

        self.account=None#pd.read_csv('ledger_account.csv')
     
        self.toggled_button1 = tkinter.Button(self.trade_tab,bg='green',fg='white', text="START",width=20, command=lambda:self.start_bot())
        self.toggled_button1.place(x=400, y=410)                                                                                                                       
        self.toggled_button = tkinter.Button(self.trade_tab,bg='red',fg='white',text='STOP',width=20, command=lambda:self.stop_bot())
        self.toggled_button.place(x=600, y=410)

        self.trade_tree =  ttk.Treeview(self.trade_tab, selectmode='browse',height=500)
        self.trade_tree.place(x=10, y=500)
        self.trade_tree['columns'] = ('timestamp','symbol','open', 'high', 'low', 'close', 'base_volume', 'counter_volume', 'avg','trade_count')
        self.trade_tree['show'] = 'headings'
        self.trade_tree.heading('timestamp', text='timestamp')
        self.trade_tree.heading('symbol', text='symbol')
        self.trade_tree.heading('open', text='open')
        self.trade_tree.heading('high', text='high')
        self.trade_tree.heading('low', text='low')
        self.trade_tree.heading('close', text='close')
        self.trade_tree.heading('base_volume', text='base_volume')
        self.trade_tree.heading('counter_volume', text='counter_volume')
        self.trade_tree.heading('avg', text='avg')
        self.trade_tree.heading('trade_count', text='trade_count')

        self.order_book_canvas = tkinter.Canvas( self.order_book_tab,relief='groove',background='black', borderwidth=1, bd= 3)
        self.order_book_canvas.place(x=10, y=10, width=800, height=360)
        
        self.order_book_tree =  ttk.Treeview(self.order_book_tab, selectmode='browse')
        self.order_book_tree.place(x=10, y=500, width=400, height=260)

        self.order_book_tree['columns'] = ('price', 'quantity')
        self.order_book_tree['show'] = 'headings'
        self.order_book_tree.heading('price', text='price', anchor='center')
        self.order_book_tree.heading('quantity', text='quantity')
        order_book = pd.read_csv('ledger_order_book.csv')
        for index, row in order_book.iterrows():
            print(index,row)
            self.order_book_tree.insert('', 'end', text=(index,row))

        self.offers_canvas = tkinter.Canvas( self.history_tab, width=600, height=400,bg='green', relief='groove',background='black', bd= 3)
        self.offers_canvas.place(x=30, y=400,anchor= 'nw')

        self.offers_canvas.create_text(300, 40, text=offers.__str__(), font=('Arial',14), anchor= 'nw')
        self.account_canvas = tkinter.Canvas(self.account_tab, width=1200, height = 500,background= 'black',border=9)
        self.account_canvas.place(x=10, y=10)

        self.history_canvas = tkinter.Canvas( self.history_tab, width=500,bg='green', relief='groove',background='black',bd= 3)
        self.history_canvas.place(x=1000, y=500 ,anchor= 'nw')
        self.history_canvas.create_text(300, 200, text='history', font=('Arial',14), anchor= 'nw')
        
        
        self.transactions_canvas = tkinter.Canvas( self.transactions_tab, width=500,bg='green', relief='groove',background='black',bd= 3)
        self.transactions_canvas.place(x=10, y=400,anchor= 'nw')

       
        self.transactions=pd.read_csv('ledger_transactions.csv')

        self.transactions_canvas.create_text(10, 0, text='Transactions', font=('Arial',14), anchor= 'nw')
        self.transactions_canvas.create_text(300, 200, text=[f+'\n' for f in self.transactions].__str__(), font=('Arial',14), anchor= 'nw')
       # self.account= pd.read_csv('ledger_account.csv')
        # Create a candlestick chart
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.xticks(rotation=45)
        self.trade_canvas = tkinter.Canvas( self.trade_tab, relief='groove',background='black',border=3,bd=5)
        self.trade_canvas.place(x=100, y=10, width=1300, height=400,anchor='nw')

        self.chart_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1 )
        self.chart_tab.place(x=0, y=10)

        self.chart_canvas = tkinter.Canvas(self.chart_tab, width=1300,height=400,background= 'black', bd= 3)
        self.chart_canvas.place(x=10, y=400, anchor='nw')

        
        self.trade_canvas.create_text(10, 310, text='', font=('Arial',14), anchor= 'nw')
        
        figure_canvas = FigureCanvasTkAgg(fig, master=self.chart_canvas)
        figure_canvas.draw()
        figure_canvas.get_tk_widget().place(x=200, y=60)
        ax.xaxis_date()
        ax.autoscale_view()
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Price')
        fig.autofmt_xdate()
        fig.autofmt_xdate(rotation=45)
        fig.tight_layout()
        fig.subplots_adjust(top=0.95)


        plt.xticks(rotation=45)
        self.candle_data0 = pd.DataFrame(columns=['symbol','timestamp', 'open', 'high', 'low', 'close', 'base_volume','counter_volume', 'avg','trade_count'])
        if not os.path.exists('ledger_candles.csv'):
         self.candle_data0.to_csv('ledger_candles.csv')
        self.candle_data = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        self.candle_data['open'] = self.candle_data0['open'].values
        self.candle_data['high'] = self.candle_data0['high'].values
        self. candle_data['low'] = self.candle_data0['low'].values
        self.candle_data['close'] = self.candle_data0['close'].values
        self. candle_data['volume'] = self.candle_data0['base_volume'].values
        self.candle_data['timestamp'] = pd.to_datetime(self.candle_data['timestamp'])
        self.candle_data.set_index('timestamp', inplace=True)
        fig, ax = plt.subplots(figsize=(10, 6))

        # ax.plot(candle_data['timestamp'], candle_data['open'], candle_data[ 'high'], candle_data['low'], candle_data['close'], candle_data['volume'], color='red', linewidth=2)
     
        # OHCL = mpf.plot(candle_data,  type='candle', style='charles',
        #     title='candlestick',
        #     ylabel='Price ($)',
        #     ylabel_lower='Shares \nTraded',
        #     volume=False, 
        #     mav=(3,6,9), 
        #     savefig='test-mplfiance.png')
        # print(OHCL)
        
      
        plt.tight_layout()


        self.send_money_image_label = tkinter.Label(self.send_money_tab,image= tkinter.PhotoImage(file='images/send_money.png'),width=200, height = 100)
        self.send_money_image_label.place(x=400, y=20, anchor= 'nw')
        self.send_money_label = tkinter.Label(self.send_money_tab, text='Send Money', font=('Arial',14))
        self.send_money_label.place(x=400, y=50, anchor= 'nw',width=20, height= 20)
        self.send_money_address = tkinter.Label(self.send_money_tab, text='Enter Address', font=('Arial',14),height=20, width=200) 
        self.send_money_address.place(x=40, y=30,  anchor= 'nw', height= 20)
        self.send_money_address_entry = tkinter.Entry(self.send_money_tab, width=20 , font=('Arial',14), bg='white', fg='black') 
        self.send_money_address_entry.place(x=50, y=30,  anchor= 'nw',width=20, height= 20)
        self.send_money_amount = tkinter.Label(self.send_money_tab, text='Enter Amount', font=('Arial',14), height=20, width=200                                            )
        self.send_money_amount.place(x=40, y=60,  anchor= 'nw', height= 20) 
        self.send_money_amount_entry = tkinter.Entry(self.send_money_tab, width=20, font=('Arial',14), bg='white', fg='black') 
        self.send_money_amount_entry.place(x=50, y=60, anchor= 'nw',width=20, height= 20)
        self.send_money_asset = tkinter.Label(self.send_money_tab, text='Enter Asset', font =('Arial',14), height=20, width=200) 
        self.send_money_asset.place(x=40, y=90, relwidth=1, relheight=1, anchor= 'nw', height= 20)
        self.send_money_asset_entry = tkinter.Entry(self.send_money_tab, width=20, font=('Arial',14), bg='white', fg='black')
        self.send_money_asset_entry.place(x=50, y=90, relwidth=1, relheight=1, anchor= 'nw',width=20, height= 20)
        self.send_money_button = tkinter.Button(self.send_money_tab, text='Send', font=('Arial',14), command=lambda:self.controller.bot.send_money(
            self.send_money_address_entry.get(),
            self.send_money_amount_entry.get(),
            self.send_money_asset_entry.get()))

        self.receive_money = tkinter.Label(self.send_money_tab, text='Receive Money', font=('Arial',14),image= tkinter.PhotoImage(file='images/receive_money.png'))
        self.receive_money.place(x=200, y=10,  anchor= 'nw')
        
        
        self.balances_tab = tkinter.Frame(self.tab, relief='groove', borderwidth=1 , background='gray')
        self.balances_canvas = tkinter.Canvas(self.balances_tab, width=1500, height = 660,background= 'black', bd= 3)
        self.balances_canvas.place(x=0, y=0, anchor='nw')
    
        self.tab.add(self.trade_tab, text='Server')
        self.tab.add(self.chart_tab, text='Charts')
        self.tab.add(self.order_book_tab, text='OrderBook')
        self.tab.add(self.account_tab, text='Account')
        self.tab.add(self.balances_tab, text='Balances')
        self.tab.add(self.history_tab, text='History')
        self.tab.add(self.transactions_tab, text='Transactions')
        self.tab.add(self.send_money_tab, text='Send Money')
        self.tab.add(self.receive_money_tab, text='Receive Money')
        self.tab.add(self.settings_tab, text='Settings')
        self.tab.add(self.licence_tab, text='Licence')
        self.tab.add(self.about_tab, text='About')
        self.trade_tree.bind('<<TreeviewSelect>>', self.on_treeview)
        #Update the GUI
        self.updateMe()
    def on_treeview(self, event)->None:
        
        if len(self.trade_tree.selection_get())>0:
         self.trade_tree.selection_set(self.trade_tree.get_children()[0])
         self.trade_tree.focus(self.trade_tree.get_children()[0])
         self.trade_tree.see(self.trade_tree.get_children()[0])
   
        
    def stop_bot(self)->None:


        self.toggled_button1.config( background='green',fg='yellow',state='normal',text='START')
        self.toggled_button.config(background='gray',fg='yellow',state='disabled',text='STOP')
        self.controller.bot.stop()

    def start_bot(self  )->None:
     

       self.toggled_button1.config( background='gray',fg='yellow',state='disabled',text='START')
       self.toggled_button.config(background='red',fg='yellow',state='normal',text='STOP')
       self.controller.bot.start()
    
    
    def updateMe(self)->None:
        
        trades =pd.read_csv('ledger_trades.csv')
        self.history_canvas.create_text(400, 200, text=[f+'\n' for f in trades].__str__(), font= ('Arial',14),fill='white' )
        self.trade_tree.delete(*self.trade_tree.get_children()) 
        v=self.candle_data0
        if len(v)>0:
         self.trade_tree.insert('', 'end', text='timestamp', values=([0],v['symbol'],v['open'],v['close'],v['high'],v['low'],v['base_volume'],v['counter_volume'],v['avg'], v['trade_count']),tag='trade')
        self.trade_canvas.delete('all') 

        self.trade_canvas.create_text(200, 40, text= 'TIMESTAMP', font= ('Arial',14), fill='lightgreen')
        self.trade_canvas.create_text(400, 40, text= datetime.datetime.now().__str__(), font= ('Arial',14), fill='lightgreen')   
        self.trade_canvas.create_text(200, 60, text= 'STATUS:', font= ('Arial',14), fill='lightgreen')
        self.trade_canvas.create_text(400, 60, text= self.controller.bot.server_msg['status'].__str__(), font= ('Arial',14), fill='lightgreen')
 
        self.trade_canvas.create_text(200, 190, text= 'MESSAGE:', font= ('Arial',14), fill='green')
        self.trade_canvas.create_text(400, 190, text= self.controller.bot.server_msg['message'].__str__(), font= ('Arial',14), fill='white')
        account =self.account 
        self.account_canvas.delete('all')
        self.account_canvas.create_text(300, 50, text= 'AccountID:', font= ('Arial',14), fill='white')
        self.account_canvas.create_text(600, 50, text= account.__str__(), font= ('Arial',14), fill='white')
 
        # self.account_canvas.create_text(300, 250, text= 'last_modified_ledger:', font= ('Arial',14), fill='white')
        self.after(1000, self.updateMe)


        
      
   


  
          
