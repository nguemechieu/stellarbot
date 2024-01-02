
''' Trading Bot Class '''
import tkinter
import os
import logging
import random
import threading
import time
import stellar_sdk
import cv2
import datetime
import requests
import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
import numpy as np
import pickle

class TradingBot:
    ''' Constructor for the Trading Bot '''  
    #'SB2LHKBL24ITV2Y346BU46XPEL45BDAFOOJLZ6SESCJZ6V5JMP7D6G5X'  
    def __init__(self, account_id=None, account_secret=None,controller=None):   
        self.name = 'StellarBot'
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.addHandler(logging.FileHandler(self.name + '.log'))
        self.connected = False
        self.running = False
        self.secret_key=account_secret
        self.account_id = account_id
        self.thread = threading.Thread(target=self.run, args=())
        try:
         if not os.path.exists(self.name + '.sql'):
            self.db = sqlite3.connect(self.name + '.sql')

            
            self.db.execute( '''CREATE TABLE IF NOT EXISTS accounts(account_id TEXT, secret TEXT)''')
            self.db.execute('''CREATE TABLE IF NOT EXISTS assets(code TEXT,issuer TEXT,type TEXT)''')
            self.db.execute('''CREATE TABLE IF NOT EXISTS transactions(transaction_id TEXT, from_account TEXT, to_account TEXT, amount TEXT, type TEXT)''')
            self.db.execute('''CREATE TABLE IF NOT EXISTS settings(setting TEXT, value TEXT)''')
            self.db.execute('''CREATE TABLE IF NOT EXISTS candles(symbol TEXT,timestamp TEXT,open TEXT,high TEXT,low TEXT,close TEXT,base_volume TEXT,counter_volume TEXT , 'trade_count' TEXT, 'avg' TEXT)''')
            self.db.commit()
        except Exception as e:
            self.logger.error(e)
        self.logger.info('Database not initialized')
        
        self.db= sqlite3.connect(self.name + '.sql')
    
         #Saving the account id and secret in the database
        self.db.execute("INSERT INTO settings(setting, value) VALUES ('account_id', '{}')".format(self.account_id))
        self.db.execute("INSERT INTO settings(setting, value) VALUES ('account_secret',' {}')".format(self.secret_key))      
        self.db.commit()

        self.current_time = int(time.time())
        self.valid_duration =  60*60*24*365*1000 # 3 years
        self.min_time = 1631277600# Current time in Unix format
        self.max_time = self.current_time + self.valid_duration # Current time in Unix format
        self.timeframe_list=['1m','5m','15m','30m','1h','2h','4h','6h','8h','12h','1d','3d',' 1w','1M']
        #Converting the timeframe to milliseconds
        self.timeframe_selected = '1m'
        self.timeframe = int( self.timeframe_list.index(self.timeframe_selected) * 60000)
        print('timeframe ',self.timeframe)
        self.resolution = 60000 # 1 minute resolution or timeframe in milliseconds
        self.start_time = 0# Initial time in Unix format
        self.end_time = self.current_time + self.timeframe # Current time in Unix

        self.offset = 0 # Used to keep track of the offset of the timeframe in milliseconds
        self.logger.info('Database initialized')
        self.controller=controller # Used to communicate with the  tkinter GUI
        self.server_msg ={ 'session:':datetime.datetime.now(), 'status': 'OFFLINE', 'type': 'INFO','message': None,'sequence': None, 'balance': None, 'fibo': None }
                       
    # Used to learn the model
       
        self.stellar_horizon_url = "https://horizon.stellar.org" # Horizon server url
     
        self.stellar_network=stellar_sdk.Network.PUBLIC_NETWORK_PASSPHRASE# Stellar network to connect to 
        
        self.server = stellar_sdk.Server(horizon_url=self.stellar_horizon_url) # Initialize the server
        
        self.keypair = stellar_sdk.Keypair.from_secret(secret=self.secret_key) # Initialize the keypair

        # Get User account
        self.account=  self.server.load_account(account_id= self.account_id)
        if self.account :
            self.connected = True
            self.logger.info('CONNECTED TO STELLAR ACCOUNT')
            self.server_msg['status'] = 'CONNECTED TO STELLAR NETWORK'
        self.create_account_image= cv2.imread('stellar_account.png')
        # Create an order builder object
        self.order_tickets = pd.DataFrame(columns=['order_id', 'symbol','price', 'quantity','create_time', 'type'])
        
      
        self.asset_issuers_list = [] # Used to keep track of the asset issuers

        self.assets_list ={'asset_code':'','asset_issuer':'','asset_type':''} # Used to keep track of the asset list
        self.transaction_list = [] # Used to keep track of the transactions
      
    
        self.balance: float = 0.00
        
        self.balances = []
        self.base_asset_code= stellar_sdk.Asset.native().code
        self.base_asset_issuer = stellar_sdk.Asset.native().issuer

      
        self.counter_asset_code='USDC'
        self.counter_asset_issuer ="GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"
        self.base_asset= stellar_sdk.Asset.native()
        self.counter_asset= stellar_sdk.Asset(self.counter_asset_code,self.counter_asset_issuer)
        
        self.symbol = self.counter_asset_code+'/'+self.base_asset_code 
       
        print(self.account, self.account_id)
        self.server_data=self.server.data(account_id= self.account_id,data_name= 'balances')
        print(self.server_data)
        self.server_msg['data'] =  self.server_data 
        self.asset_list=self.get_asset_list()
          # Create a transaction builder object
        self.transaction = stellar_sdk.transaction_builder.TransactionBuilder(v1=True,                                           
                 source_account=self.account,
                 network_passphrase=self.stellar_network,
                 base_fee=100).add_time_bounds(min_time=self.min_time, max_time=self.max_time)
        self.logger.info('Bot started  ')
        self.server_msg['status'] = 'Welcome  to StellarBot'
       
     
        self.account_info = { '_links': {...}, } # The complete account info goes here
    
        #check if internet connection is established
        self.connection = self.check_connection()
        if not self.connection:
            self.logger.info('NO INTERNET CONNECTION!\nPlease check your internet connection')
            self.server_msg['status'] = 'OFFLINE'
            self.server_msg['message'] = 'NO INTERNET CONNECTION!\nPlease check your internet connection'
            return None

        self.server_msg['status'] = 'CONNECTED TO STELLAR NETWORK'

        if self.thread.is_alive():
            self.thread.join()
            self.thread_timer.cancel()
            
            self.server_msg['message'] = 'Bot stopped at @' + str(datetime.datetime.now())

           


        # Get current order book data
        self.order_book = self.server.orderbook(
            selling= stellar_sdk.Asset(self.counter_asset_code, self.counter_asset_issuer),
            buying= stellar_sdk.Asset(self.base_asset_code, self.base_asset_issuer)
            
        ).limit(100).call().popitem()[-1]
        print('order_book', str(self.order_book))
        self.order_book_df = pd.DataFrame(self.order_book,columns=['bid_prices', 'bid_quantity', 'ask_prices', 'ask_quantity'])
        self.order_book_df.to_csv('order_book.csv', index=0)
        self.order_book_df = pd.read_csv('order_book.csv')
        self.order_book_df = self.order_book_df.fillna(0)

        self.order_book_df['bid_prices'] = self.order_book_df['bid_prices'].astype(float)
        self.order_book_df['ask_prices'] = self.order_book_df['ask_prices'].astype(float)
        self.order_book_df['bid_quantity'] = self.order_book_df['bid_quantity'].astype(float)
        self.order_book_df['ask_quantity'] = self.order_book_df['ask_quantity'].astype(float)
        self.order_book_df['bid_prices'] = self.order_book_df['bid_prices'].astype(float)

        print(self.order_book_df)

                                 
                        
      
    

    def get_asset_list(self):

        # Create a DataFrame from the assets_list dictionary
        self.asset_0= self.server.assets().call().popitem()[-1]['records']
        self.asset_list = pd.DataFrame(self.asset_0,columns=['asset_code', 'asset_issuer', 'asset_type'])
        # Save the DataFrame to a CSV file
        self.asset_list.to_csv('asset_list.csv', index=False) 
        return self.asset_list

    
    # Check if connection is established
     
    
    def Check_account(self, account_id_: str=None) -> dict:
        endpoint = f"{self.stellar_horizon_url}/accounts/{account_id_}"
        response = requests.get(endpoint,timeout=5000)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.status_code)
            print(response.text)
            self.server_msg['account'] =  response.json()
            return None

    
    

    
    def check_connection(self):
        while True:
            try:
                response = requests.get(self.stellar_horizon_url, params={"addr":self.account_id},timeout=5000)
                if response.status_code == 200:
                  
                    self.logger.info('Connection established')
                    self.server_msg['message'] = 'Connection established'
                    self.server_msg['status'] = 'Connected!'
                    self.account_info = self.Check_account(self.account_id)
                    return response.status_code == 200
            except Exception as e:
                print("Connection not established",response.status_code)
                self.logger.info('No internet connection')
                self.server_msg['message'] = 'No internet connection '+ str(e)
            
                return False
            finally:
                time.sleep(0.5)



    def run(self):
          #client = bigquery.Client(project='tradeadviser',credentials=)
    
         balances = self.account_info['_links']
         df2=pd.DataFrame(balances,columns=['balance','limit','buying_liabilities','selling_liabilities','last_modified_ledger','is_authorized','is_authorized','is_authorized_to_maintain_liabilities','asset_type','asset_code','asset_issuer'])
         df2.to_csv('balances.csv',index=False)
        
         while True:         
             self.server_msg['status'] = 'LIVE TRADING'
          
            # self.send_money()
             self.get_stellar_candles()
             

             fee_statistic =self.server.fee_stats().limit(100).order(desc=True).call().popitem()[-1]
             self.fee_statistics_df=pd.DataFrame(fee_statistic,columns=['fee_asset','fee_asset_issuer','fee_amount','fee_asset_type'])
             self.fee_statistics_df.to_csv('ledger_fee_statistics.csv',index=True)
             stellar_offers_json = self.fetch_stellar_offers()
             stellar_offers_df = self.convert_to_dataframe(stellar_offers_json)
         
             ledger_offers = stellar_offers_df
             self.ledger_offers_df=pd.DataFrame(ledger_offers)
             self.ledger_offers_df.to_csv('ledger_offers.csv',index=True)

             self.ledger_statistics =self.server.trades().order(desc=True).limit(100).call().popitem()[-1]['records']
             self.ledger_statistics_df=pd.DataFrame(self.ledger_statistics,columns=['trade_id','price','amount','price_r','amount_r'])
             self.ledger_statistics_df.to_csv('ledger_trades.csv',index=True)

             
             transaction =self.server.transactions().limit(100).order(desc=True).call().popitem()[-1]
             transaction_df =pd.DataFrame(transaction)

             transaction_df.to_csv('ledger_transaction.csv')
          
             self.claimable=self.server.claimable_balances().limit(100).order(desc=True).call().popitem()[-1]['records']
             self.claimable_df=pd.DataFrame(self.claimable)
           
             self.claimable_df.to_csv('ledger_claimable.csv',index=True)


             self.ledger_payments =self.server.payments().order(desc=True).limit(50).call().popitem()[-1]['records']
             self.ledger_payments_df=pd.DataFrame(self.ledger_payments,columns=['payment_id','from_account','to_account','amount'])
             self.ledger_payments_df.to_csv('ledger_payments.csv',index=True)

             self.ledger_effects =self.server.effects().order(desc=True).limit(100).call().popitem()[-1]
             self.ledger_effects_df=pd.DataFrame(self.ledger_effects,columns=['effect_id','account','type','amount'])
             self.ledger_effects_df.to_csv('ledger_effects.csv',index=True)
           

    # Create the first Asset instance (selling asset)
             selling_asset = stellar_sdk.Asset(
                 code=self.counter_asset_code,
                 issuer=self.counter_asset_issuer
             )  # Replace with the actual issuer's address

             # Create the second Asset instance (buying asset)
             
             buying_asset = stellar_sdk.Asset("XLM")  # Replace with the actual issuer's address
             # Create symbols
             self.symbol= selling_asset.code + '_' + buying_asset.code

             # Create asset list

             self.asset_list =self.get_asset_list()
            
      
        
            # Generate trades signal
             signal=self.get_signal(symbol= self.symbol)
        
             self.server_msg['message'] = 'symbol :'+ self.symbol +'  signal :'+ str(signal)

             # Define the order details
             sell_amount = "56.0"  # Amount of selling asset
             sell_price =  "7.3" # Price in terms of selling asset\stellar_sdk.price.Price, str, decimal.Decimal

            #Create the sell operation
             self.selling_operation = stellar_sdk.manage_sell_offer.ManageSellOffer(selling=stellar_sdk.Asset.native(), buying=stellar_sdk.Asset(code="USDC",issuer=self.counter_asset_issuer),amount=sell_amount, price=sell_price,offer_id=random.randint(1, 100000000))
             #Create the buy operation
             self.buying_operation = stellar_sdk.manage_buy_offer.ManageBuyOffer(selling=stellar_sdk.Asset(code=self.counter_asset_code,issuer=self.counter_asset_issuer), buying=stellar_sdk.Asset.native(), amount=sell_amount, price=sell_price,      offer_id=random.randint(1, 100000000) )
             #Operations
             self.operations = [self.selling_operation, self.buying_operation]
       

             # Price in terms of buying asset

             # 8,"{'_links': {'self': {'href': 'https://horizon.stellar.org/operations/213579248934166529'}, 'transaction': {'href': 'https://horizon.stellar.org/transactions/9f950a624cd78d2caf2dd487ea40a1001d48a5fcd2ed1fcc46bc46a90c9021b0'}, 'effects': {'href': 'https://horizon.stellar.org/operations/213579248934166529/effects'}, 'succeeds': {'href': 'https://horizon.stellar.org/effects?order=desc&cursor=213579248934166529'}, 'precedes': {'href': 'https://horizon.stellar.org/effects?order=asc&cursor=213579248934166529'}}, 'id': '213579248934166529', 'paging_token': '213579248934166529', 'transaction_successful': True, 'source_account': 'GBOSFTR67PFCJOTLH7AKSXA7YERDTRW2TTOE4O43YEDVTLBYPVYZVP27', 'type': 'manage_buy_offer', 'type_i': 12, 'created_at': '2024-01-01T19:32:48Z', 'transaction_hash': '9f950a624cd78d2caf2dd487ea40a1001d48a5fcd2ed1fcc46bc46a90c9021b0', 'amount': '864.1097498', 'price': '0.0054391', 'price_r': {'n': 54391, 'd': 10000000}, 'buying_asset_type': 'credit_alphanum4', 'buying_asset_code': 'SBI', 'buying_asset_issuer': 'GDU5NJWUJJCVZ25ET5ISGKZR5HQSUB6ZA6KOQ3474S3BS2LUKW7SSSXD', 'selling_asset_type': 'native', 'offer_id': '1438663537'}"
             self.operation2=self.server.operations().limit(100).order(desc=True).call().popitem()[-1]
             self.operation2_df=pd.DataFrame( self.operation2,columns=['transaction', 'effects','succeeds', 'precedes', 'id', 'paging_token', 'transaction_successful','source_account', 'type', 'type_i', 'created_at', 'transaction_hash', 'amount', 'price', 'price_r', 'buying_asset_type', 'buying_asset_code', 'buying_asset_issuer','selling_asset_type','selling_asset_code','selling_asset_issuer', 'offer_id'])      
             self.operation2_df.to_csv('ledger_operations.csv',index=True)
    
             # Build the transaction
             try:
             
                if signal == 'buy' or signal == 1:
             # Build Buying  transaction
                   transaction = stellar_sdk.transaction_builder.TransactionBuilder(v1=True,
                   source_account=self.account,
                   network_passphrase=self.stellar_network,
                base_fee=100).append_operation(self.buying_operation).add_time_bounds(min_time=self.min_time, max_time=self.max_time).build()
                   transaction.sign(signer=self.secret_key)
              # Submit the transaction to the Stellar network
            #        response = self.server.submit_transaction(transaction)
            #   # Check the transaction result
            #        if response !=None and response["successful"]:
            #         print("Buy order placed successfully!")
            #         self.server_msg['message'] ='Buy order placed successfully! Transaction hash:'+ response["hash"]
            #         print("Transaction hash:", response["hash"])
            #        else:
            #              print("Buy order failed. Error:", response["result_xdr"].__str__())
            #              self.server_msg['message'] ='Buy order failed. Error:'+ response["result_xdr"].__str__()

                elif signal =='sell' or signal == -1:
              # Build selling the transaction
                   transaction = stellar_sdk.transaction_builder.TransactionBuilder(v1=True,
                      source_account=self.account, network_passphrase=self.stellar_network,
                    base_fee=100).append_operation(self.selling_operation).add_time_bounds(min_time=self.min_time, max_time=self.max_time).build()
                   transaction.sign(signer=self.secret_key)
            #      response = self.server.submit_transaction(transaction)
              

            #   #Check the transaction result
            #        if response["successful"] :
            #          print("Sell order placed successfully!")
            #          self.server_msg['message'] ='Sell order placed successfully! Transaction hash:'+ response["hash"].__str__()
            #          print("Transaction hash:", response["hash"])
            #        else:
            #            print("Sell order failed. Error:", response["result_xdr"])
            #            self.server_msg['message'] ='Sell order failed. Error:'+ response["result_xdr"].__str__()
             except Exception as e:
              self.server_msg['message'] = 'Transaction:'+str(e)

             self.logger.info(self.server_msg['message'])

             time.sleep(1)

    def stop(self):
        self.running = False
    
        self.server_msg['message'] = 'Trading bot stopped'
        if self.server!= None:

            if self.thread!= None:
                self.thread.join()
            self.server.close()

    def order_send(self, order):
        self.logger.info('Sending order:' + str(order))

   
    def trailing_stop_loss(self, symbol: str, price: float, stop_loss: float):
        self.logger.info('Trailing stop loss:' + str(symbol) + '' + str(price) + '' + str(stop_loss))
        if price < stop_loss:
            return True
        else:
            return False
        

    def create_account_dataframe(self, account):
   
    # Extract balances
     balances = account

    # Create a list of dictionaries to store balance information
     account_df=pd.DataFrame(balances,index=[0])
     return account_df



    def account_balance(self):
        endpoint = f"{self.stellar_horizon_url}/accounts/{self.account_id}/balances"
        response = requests.get(endpoint, timeout=5000)
        if response.status_code == 200:
            return response.json()
        else:
         
            self.server_msg['message']= " Error:" + str(response.status_code) + " " + str(response.reason)
            self.logger.error(self.server_msg['message'])
            return None
        

    def account_update(self, balance):

        self.balance = balance
    
    # Function to fetch asset information
    def get_assets(self, asset_code=None, asset_issuer=None, limit=None, order=None):
        params = {
            "asset_code": asset_code,
            "asset_issuer": asset_issuer,
            "limit": limit,
            "order": order}
        endpoint = f"{self.stellar_horizon_url}/assets"
        response = requests.get(url=endpoint, params=params, timeout=5000)
        if response.status_code == 200:
            return response.json()
        else:
            self.server_msg['message']= " Error:" + str(response.status_code) + " " + str(response.reason)
        return None
    # Function to fetch trade aggregations
    def get_trade_aggregations(self,
                               base=stellar_sdk.Asset.native(),
                               
                              
                               counter=None
                                ):
        
        # Create a timer to check the trade aggregations
        trade_aggregations =self.server.trade_aggregations(           
            base= stellar_sdk.Asset(code=base.code, issuer=base.issuer),
            counter= stellar_sdk.Asset(code=counter.code, issuer=counter.issuer),

           offset= self.offset,# 
           resolution= self.resolution # Critical period in milliseconds (60 seconds) do not remove any data

        ).limit(100).call().popitem()[-1]['records']
    
        return trade_aggregations
    
    def start(self):

        # Initialize the thread timer
        self.thread_timer = threading.Timer(5000, self.get_stellar_candles, args=())
        self.thread_timer.daemon = True
        self.thread_timer.start()
        self.logger.info('Bot started  ')
        self.server_msg['message'] = 'Bot started @'+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.thread.start()
        


    def login(self, user_id:str='', secret_key:str=''):

        if user_id is None or secret_key is None or user_id == secret_key or user_id == '' or secret_key == '':
            
            self.logger.info('Please enter your user_id and secret_key')
            self.server_msg['message']='Please enter your user_id and secret_key'
            tkinter.Message(master=self.controller, text=self.server_msg['message'], width=100)
            return None
        if self.connected:
            self.account_info = self.Check_account(account_id_=user_id)

            if self.account_info is not None:
             self.account_id = user_id
             self.secret_key = secret_key
           
             self.controller.show_frame(frame="Home")
             self.logger.info('Successfully logged in')
             self.server_msg['message']='Successfully logged in'
             self.connected = True

             return self.account_info
            else:
             self.logger.info('Invalid user_id or secret_key')
             self.server_msg['message']='Invalid user_id or secret_key'
             tkinter.Message(master=self.controller, text=self.server_msg['message'], width=50)
             return False
        else :
            self.logger.info('Please login first')
            self.server_msg['message']='Please login first'
            tkinter.Message(master=self.controller, text=self.server_msg['message'], width=50)
            return False


    def receive_money( self, destination_public_key:str=None, amount:str="10", asset:str=stellar_sdk.Asset.native()):
       
              # Build the transaction
        self.transaction =  stellar_sdk.TransactionBuilder(source_account=self.account, network_passphrase="PUBLIC_NETWORK").append_payment_op(destination=destination_public_key, amount=amount, asset=asset).add_time_bounds(min_time=self.min_time, max_time=self.max_time).build()
        # Sign the transaction
        self.transaction.sign(self.keypair)

        # Submit the transaction envelope to the Stellar network
        try:
            response = self.server.submit_transaction(self.transaction)
            print(f"Transaction hash: {response['hash']}")
            self.server_msg['message'] = 'Transaction hash:'+ response["hash"].__str__()

        except Exception as e:
            print(f"An error occurred: {e}")
            tkinter.Message(master=self.controller, text=self.server_msg['message'], width = 50)
      
    def send_money( self, amount:str="100", asset:str=stellar_sdk.Asset.native(), receiver_address:str=None):
       
           #      self.receiver_public_key="GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA"
           # Build the transaction
           self.transaction =  stellar_sdk.TransactionBuilder(source_account=self.account, network_passphrase="PUBLIC_NETWORK")
           self.transaction.add_extra_signer(self.keypair).append_payment_op(destination=receiver_address, amount=amount, asset=asset).add_time_bounds(min_time=self.min_time, max_time=self.max_time).build()

        
           # Submit the transaction envelope to the Stellar network
           try:
            response = self.server.submit_transaction(self.transaction)
            print(f"Transaction hash: {response['hash']}")
            self.server_msg['message'] = 'Transaction hash:'+ response["hash"].__str__()
           except Exception as e:
             print(f"An error occurred: {e}")
             tkinter.Message(master=self.controller, text=self.server_msg['message'], width = 50)


    def get_stellar_candles(self):
    # Get trade aggregations (candles)
     self.trade_aggregations =      self.get_trade_aggregations(base= self.base_asset,counter= self.counter_asset) 
     if len(self.trade_aggregations) > 0:
      self.start_time =time.time()
         

     print('trade_aggregations',str(self.trade_aggregations))

     # Creating a DataFrame
     candles = pd.DataFrame( self.trade_aggregations , columns=['symbol','timestamp', 'open', 'high', 'low', 'close'
                                                                ,'trade_count','base_volume','counter_volume','avg'
                                                               
  
                                                                ])
     
     candles['timestamp'] = pd.to_datetime(candles['timestamp'], unit='ms')
     con = sqlite3.connect(self.name + '.sql')
     candles.to_sql('candles', con, if_exists='append', index=False, index_label='timestamp')
     
     candles['symbol'] = self.symbol

     # Converting timestamp to datetime
     print('timestamp',str(candles))
     # Converting timestamp to datetime
     candles['timestamp'] = pd.to_datetime(candles['timestamp'], unit= 'ms')

     #Saving candles to a database
     candles.to_csv('candles.csv')
     con=sqlite3.connect(self.name + '.sql')
     candles.to_sql('candles', con=con, if_exists='append', index=False , index_label=False)
    
     return candles
    



  
    def extract_operations_info(self,data):
    # Extracting information from the provided JSON data
     links = data['_links']
     next_link = links['next']['href'] if 'next' in links else None
     prev_link = links['prev']['href'] if 'prev' in links else None

     embedded = data['_embedded']
     records = embedded['records'] if 'records' in embedded else []

     extracted_records = []
     for record in records:
        record_info = {
            'id': record['id'],
            'type': record['type'],
            'created_at': record['created_at'],
            'transaction_hash': record['transaction_hash'],
            'amount': record['amount'],
            'price': record['price'],
            'buying_asset_type': record['buying_asset_type'],
            'selling_asset_type': record['selling_asset_type'],
            'offer_id': record['offer_id'] if 'offer_id' in record else None,
        }
        extracted_records.append(record_info)

     return {
        'next_link': next_link,
        'prev_link': prev_link,
        'records': extracted_records,
    }

    def create_account(self) -> str:
        self.account = stellar_sdk.Keypair.random()
        self.keypair = stellar_sdk.Keypair.from_secret(self.secret_key)
        self.account_id = self.account.public_key
        self.secret_key =  self.keypair.secret
        self.account_info = self.Check_account(account_id_=self.account_id)

        if self.account_info is not None:
            self.logger.info('Successfully created an account')
            self.server_msg['message']='Successfully created an account'
            return self.account_id, self.secret_key
        return self.account_id, self.secret_key
    def fetch_stellar_offers(self):
     url = "https://horizon.stellar.org/offers"
     response = requests.get(url,timeout=5000)
    
     if response.status_code == 200:
        return response.json()
     else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        tkinter.Message(master=self.controller, text=self.server_msg['message'], width = 50)
        
        return None
    def convert_to_dataframe(self,json_data):
     if json_data is not None:
        # Extract relevant information from JSON data into a list of dictionaries
        offers_data = []
        for record in json_data.get('_embedded', {}).get('records', []):
            offer_info = {
                'id': record.get('id'),
                'amount': record.get('amount'),
                'price': record.get('price'),
                'selling_asset_type': record.get('selling').get('asset_type'),
                'selling_asset_code': record.get('selling').get('asset_code'),
                'selling_asset_issuer': record.get('selling').get('asset_issuer'),
                'buying_asset_type': record.get('buying').get('asset_type'),
                'buying_asset_code': record.get('buying').get('asset_code'),
                'buying_asset_issuer': record.get('buying').get('asset_issuer'),
            }
            offers_data.append(offer_info)

        # Convert the list of dictionaries to a Pandas DataFrame
        df = pd.DataFrame(offers_data)
    
        return df
     else:
        return None
    def get_signal(self, symbol: str): 
 
        db = sqlite3.connect(self.name + '.sql')
        #Making sure that the symbol is in the list
        data =pd.read_sql_query(f"SELECT * FROM candles WHERE symbol = '{symbol}'", con=db, index_col='timestamp', parse_dates=True)
        print('data ',data)
       
        if data is None:
            print(f'No data found for {symbol}')
            return 0
        while data.shape[0] < 100:
            print(f'No data found for {symbol}')
            return 0

        
     
        high = data['high'].astype(float)
        low = data['low'].astype(float)
        open = data['open'].astype(float)
        close =data['close'].astype(float)
        volume = data['base_volume'].astype(float)
        volume2 = data['counter_volume'].astype(float)
        volume3 = data['avg'].astype(float)
       
        price =high - (0.236 * (high - low))
        fib_levels = {
            0.236: high - (0.236 * (high - low)),
            0.382: high - (0.382 * (high - low)),
            0.500: high - (0.500 * (high - low)),
            0.618: high - (0.618 * (high - low)),
            0.786: high - (0.786 * (high - low)),
            1.000: high - (1.000 * (high - low)),
            1.214: high - (1.214 * (high - low)),
            1.445: high - (1.445 * (high - low)),
            1.700: high - (1.700 * (high - low))
        }

        if len(fib_levels) <0 or len(price) < 100:
            print(f'No Fibonacci levels found for {symbol}')
            self.server_msg['message'] = f'No Fibonacci levels found for {symbol}'
            return 0
        # for level, fibo_price in fib_levels.items():
        #  if price is not None:
        #     if (price.iloc[-1:] - fibo_price / price.iloc[-1:]) < 0.01:  # You can adjust the threshold as needed
        #      signal = 1  # Buy signal
        #     elif (price.iloc[-1:] - fibo_price) / price.iloc[-1: ] > 0.01:  # You can adjust the threshold as needed
        #      signal = -1 # Sell signal
        #     print(f'Fibonacci Level: {level}')
        #     print(f'Price: {price}')
        #     self.server_msg['message'] = f'Fibonacci Level: {level}, Price: {price}, Signal: {signal}'

        
        self.fib_levels = fib_levels
        new_data=pd.DataFrame( columns=['SMA50', 'SMA200', 'RSI', 'Signal'])
        # Feature Engineering
        new_data['SMA50'] = SMAIndicator( close=close, window=50, fillna=False).sma_indicator()
        
        new_data['SMA200'] = SMAIndicator(close, window=200).sma_indicator()
                                               
        new_data['RSI'] = RSIIndicator(close,  window=14).rsi()
        
        print(new_data.head())
        print(new_data.tail())
        print(new_data.shape)
        print(new_data.dtypes)
        # Labeling
        new_data['Signal'] = np.where(new_data['SMA50'] > new_data['SMA200'], 1, 0)
        new_data.dropna(inplace=True)

        # Features and Target
        features = ['SMA50', 'SMA200', 'RSI']
        print(new_data.head())
        print(new_data.tail())

        X = new_data[features]
        y = new_data['Signal']
        print(X.head())
        print(X.tail())
        print(y.head())
        print(y.tail())
        if X.empty or X.shape[0] < 100:
            print(f' No data found for {symbol}')
            return 0

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, train_size=0.8,
                                                            stratify=y)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    
  
        # Model Training
        model.fit(X_train, y_train) 
       
        print(model.predict(X_test))

 
        # Assuming fibo_signal is initially 0 (no signal)
        signal = []

        # Check if the close price is near any Fibonacci level

     

        # Model Prediction
        y_pred = model.predict(X_test)

        # Model Evaluation
        accuracy = accuracy_score(y_test, y_pred)
        print(f'Model Accuracy: {accuracy}')

        new_data.dropna(inplace=True)

        new_features = new_data[features]
        new_data['Predicted_Signal'] = model.predict(new_features)
        new_data.dropna(inplace=True)

        # Apply Fibonacci signals to the new data
        #new_data['Fibo_Signal'] = signal

        score = accuracy_score(new_data['Signal'], new_data['Predicted_Signal'])
       # fibo_score = accuracy_score(new_data['Signal'], new_data['Fibo_Signal'])
        print(f'Model Accuracy: {score}')
       # print(f'Fibo Signal Accuracy: {fibo_score}')

  
        signal = new_data['Predicted_Signal'].values[-1:]
       # fibo_signal = new_data['Fibo_Signal'].values[-1:]

        # Adjust conditions based on your strategy
        if signal == 1 and accuracy > 95:
            print(f'Signal Buy: {signal}')
            return 1
        elif signal == 0 and accuracy > 95:
            print(f'Signal Sell: {signal}')
            return -1
        # elif fibo_signal == 1:
        #     print(f'Fibo Signal Buy: {fibo_signal}')
        #     return 1
        # elif fibo_signal == -1:
        #     print(f'Fibo Signal Sell: {fibo_signal}')
            return -1

        return 0









   