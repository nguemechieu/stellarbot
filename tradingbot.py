
''' Trading Bot Class '''
import tkinter

import logging
import random
import threading
import time
import stellar_sdk
import cv2
import pandas as pd

import requests
from learning import Learning
import sqlite3
import json

class TradingBot:
    ''' Constructor for the Trading Bot '''    
    def __init__(self, account_id=None, account_secret='SB2LHKBL24ITV2Y346BU46XPEL45BDAFOOJLZ6SESCJZ6V5JMP7D6G5X',controller=None):   
        self.name = 'TradingBot'
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.addHandler(logging.FileHandler(self.name + '.log'))

        
        self.secret_key=account_secret
        self.account_id = account_id
        


        self.server_msg ={'status': 'Loading...', 'error': None, 'account':[],'data': None,'message': None}
        self.candles = pd.DataFrame( columns=[
         'symbol','timestamp', 'open', 'high', 'low', 'close'
                                                                ,'trade_count','base_volume','counter_volume','avg'
        ]) # Used to keep track of the candles

        self.running = False # Used to keep track of the connection status

        self.thread = None # Used to keep track of the connection status

       
        self.assets_list ={'asset_code':'','asset_issuer':'','asset_type':''} # Used to keep track of the asset list
    
        self.base_asset_code= stellar_sdk.Asset.native().code # Used to keep track of the base asset code
        self.base_asset_issuer = stellar_sdk.Asset.native().issuer# Used to keep track of the base asset issuer
        
        self.counter_asset_code='USDC' # Used to keep track of the counter asset code
        self.counter_asset_issuer ="GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN" # Used to keep track of the counter asset issuer



        self.base_asset= stellar_sdk.Asset(self.base_asset_code, self.base_asset_issuer )# Used to keep track of the base asset
        self.counter_asset= stellar_sdk.Asset(self.counter_asset_code, self.counter_asset_issuer )# Used to keep track of the counter asset
        self.symbol = self.base_asset_code+'/'+self.counter_asset_code  # Used to keep track of the symbol

      
        self.db= sqlite3.connect(self.name + '.sql')

        self.db.execute('''CREATE TABLE IF NOT EXISTS order_tickets(order_id TEXT, symbol TEXT,price TEXT, quantity TEXT,create_time TEXT, type TEXT)''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS assets(code TEXT,issuer TEXT,type TEXT)''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS transactions(transaction_id TEXT, from_account TEXT, to_account TEXT, amount TEXT, type TEXT)''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS settings(setting TEXT, value TEXT)''')
        #Saving the account id and secret in the database
        self.db.execute("INSERT INTO settings(setting, value) VALUES ('account_id', '{}')".format(self.account_id))
        self.db.execute("INSERT INTO settings(setting, value) VALUES ('account_secret',' {}')".format(self.secret_key))
        
        self.db.commit()
        self.db.close()

        self.logger.info('Database initialized')
        self.controller=controller # Used to communicate with the  tkinter GUI
        self.logger.info('TradingBot initialized')
        self.stellar_horizon_url = "https://horizon.stellar.org" # Horizon server url
     
        self.stellar_network=stellar_sdk.Network.PUBLIC_NETWORK_PASSPHRASE # Stellar network (public or private)
        
        self.server = stellar_sdk.Server(horizon_url=self.stellar_horizon_url) # Initialize the server
        
        self.keypair = stellar_sdk.Keypair.from_secret(secret=self.secret_key) # Initialize the keypair
        self.connected = False # Used to keep track of the connection status
        self.offset = 0 # Used to keep track of the current offset
        self.resolution = 60000# Used to keep track of the current resolution 60000 (60) seconds = 1 minute
        self.limit = 100 # Used to keep track of the current limit
        self.cursor = 0 # Used to keep track of the current cursor
        self.transactions = [] # Used to keep track of the transactions

        self.asset_issuers_list = [] # Used to keep track of the asset issuers
        self.assets_list ={'asset_code':'','asset_issuer':'','asset_type':''} # Used to keep track of the asset list

        self.memo= 'StellarBot' # Used to keep track of the memo

        self.balance: float = 0.00 # Used to keep track of the account balance
        
        self.balances = [] # Used to keep track of the account balances
        self.orders = [] # Used to keep track of the orders

        self.last_update_time = 0 # Used to keep track of the last update time

        # Get User account information
        self.account=self.server.load_account(account_id= self.account_id)

        self.logger.info('TradingBot initialized')
       
        # Create an order builder object
        self.order_tickets = pd.DataFrame(columns=['order_id', 'symbol','price', 'quantity','create_time', 'type'])
        
        
        self.server_msg['status'] = 'OFFLINE'
     
        self.server_msg['message'] = ' No trading yet!'
        

        # Get the asset list
        self.asset_list=self.get_asset_list()
            
        current_time = int(time.time())  # Current time in Unix format
        valid_duration = 3600  # Valid for 1 hour (adjust as needed)
        self.min_time = 1631277600# Current time in Unix format
        self.max_time = current_time + valid_duration # Current time in Unix format

        self.start_time =0 # Used to keep track of the current start time
        self.end_time = current_time + valid_duration # Used to keep track of the current end time

          # Create a transaction builder object
        self.transaction = stellar_sdk.transaction_builder.TransactionBuilder(v1=True,                                           
                 source_account=self.account,
                 network_passphrase=self.stellar_network,
                 base_fee=100).add_time_bounds(min_time=self.min_time, max_time=self.max_time)
       
     
        self.account_info = { '_links': {...}, } # The complete account info goes here

        
        self.learn=Learning()
        #check if internet connection is established
        self.connection = self.check_connection()
        if not self.connection:
            self.logger.info('No internet connection')
           
            self.server_msg['status'] = 'No internet connection'
         
            return None
      
      
     
      
           
        self.server_msg['status'] = 'ONLINE'
   
        # Get current order book data
        self.order_book = self.server.orderbook(
            selling= stellar_sdk.Asset(self.counter_asset_code, self.counter_asset_issuer),
            buying= stellar_sdk.Asset(self.base_asset_code, self.base_asset_issuer)    
        ).limit(10).call().popitem()[-1]
        print( str(self.order_book))
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
        self.asset_0= self.server.assets().call().popitem()[-1]
     


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
            self.server_msg['account'] =  response._content
            return None

    
    

    
    def check_connection(self):
        while True and self.running:
            try:
                response = requests.get(self.stellar_horizon_url, params={"addr":self.account_id},timeout=5000)
                if response.status_code == 200:
                    print("Connection established")
                    self.logger.info('Connection established')
                    self.server_msg['message'] = 'Connection established'
                    return response.status_code == 200
            except Exception as e:
                print("Connection not established",response.status_code)
                self.logger.info('No internet connection')
                self.server_msg['message'] = 'No internet connection'+e.args[0]
                time.sleep(5)
                return False


    def qr_code_to_text(self,qr_code_image_path):
    # Load the QR code image
     image = cv2.imread(qr_code_image_path)

    # Decode the QR code
     decoded_objects = decode(image)

     if decoded_objects:
        # Extract and return the text from the first QR code found (assuming there's only one)
        return decoded_objects
     else:
        return None
        

    def run(self):
          #client = bigquery.Client(project='tradeadviser',credentials=)


         self.learn.symbol= 'XLM'
         self.learn.price= 100
         self.learn.quantity= 100
         self.logger.info('Starting trading bot')
      
         data = self.Check_account(self.account_id)

         
       
         df2=pd.DataFrame(data['balances'],columns=['balance','limit','buying_liabilities','selling_liabilities','last_modified_ledger','is_authorized','is_authorized','is_authorized_to_maintain_liabilities','asset_type','asset_code','asset_issuer'])
         df2.to_csv('balances.csv',index=False)
         df3=pd.DataFrame(data['signers'],columns=['weight','key','type'])
         df3.to_csv('signers.csv',index=False)
         df4=pd.DataFrame(data['data'],columns=['key','value'])
         df4.to_csv('data.csv',index=False)
         df5=pd.DataFrame(data['_links'],columns=['self','transactions','operations','payments','effects','offers','trades','data'])
         df5.to_csv('_links.csv',index=False)
        
         sequence_number = data["sequence"]
         print( 'sequence_number :'+ str(sequence_number))



         self.sequence=sequence_number


        
      
                
         while True and self.running:
             self.logger.info('Trading bot running')
             self.server_msg['message'] = 'Trading bot running'

          
             self.assets= self.server.assets().order(desc=True).limit(3).call().popitem()[-1]['records']


             asset_df = pd.DataFrame(self.assets,columns=['asset_code', 'asset_issuer', ' asset_type'])

             asset_df.to_csv('asset_list.csv',index=False)

            
             
         
             
             ledger_offer =self.server.offers().order(desc=True).limit(10).call().popitem()[-1]['records']
             ledger_statistics_df=pd.DataFrame(ledger_offer)
             ledger_statistics_df.to_csv('ledger_offers.csv',index=True)


             ledger_payments =self.server.payments().order(desc=True).limit(10).call().popitem()[-1]['records']
             ledger_payments_df=pd.DataFrame(ledger_payments)
             ledger_payments_df.to_csv('ledger_payments.csv',index=True)

             ledger_effects =self.server.effects().order(desc=True).limit(10).call().popitem()[-1]['records']
             ledger_effects_df=pd.DataFrame(ledger_effects)
             ledger_effects_df.to_csv('ledger_effects.csv',index=True)


           

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

             self.asset_list =pd.DataFrame(self.assets, columns=['asset_type', 'asset_code', 'asset_issuer'])
             self.asset_list.to_csv('asset_list.csv', index=False)
      

      
             
            
            
             # Define the order details
             sell_amount = "56.0"  # Amount of selling asset
             sell_price =  "7.2" # Price in terms of selling asset\stellar_sdk.price.Price, str, decimal.Decimal

            #Create the sell operation
             self.selling_operation = stellar_sdk.manage_sell_offer.ManageSellOffer(selling=stellar_sdk.Asset.native(), buying=stellar_sdk.Asset(code="USDC",issuer=self.counter_asset_issuer),amount=sell_amount, price=sell_price,offer_id=random.randint(1, 100000000))
             #Create the buy operation
             self.buying_operation = stellar_sdk.manage_buy_offer.ManageBuyOffer(selling=stellar_sdk.Asset(code=self.counter_asset_code,issuer=self.counter_asset_issuer), buying=stellar_sdk.Asset.native(), amount=sell_amount, price=sell_price,      offer_id=random.randint(1, 100000000) )
             #Operations
             self.operations = [self.selling_operation, self.buying_operation]
       

             # Price in terms of buying asset

          
            
             operation2=self.server.operations().limit(10).order(desc=True).call().popitem()[-1]['records']
      
             operation2_df=pd.DataFrame( operation2)
             operation2_df.to_csv('operation2.csv',index=True)
           

            # Live Trading 
             self.on_tick()



          



    def on_tick(self):
       
             self.server_msg['message'] = 'Trading bot running'
             self.server_msg['status'] = 'Running'
             self.server_msg['sequence'] = self.sequence

        
             self.server_msg['sequence'] = self.sequence
             self.server_msg['time'] = time.time()
        
             trades=self.server.trades().limit(10).order(desc=True).call().popitem()[-1]['records']
             trade_df =pd.DataFrame(trades )
             trade_df.to_csv('trades.csv',index=True)
        

             claimable=self.server.claimable_balances().limit(10).order(desc=True).call().popitem()[-1]['records']
             claimable_df=pd.DataFrame(claimable)
             print('claimable :'+str(claimable_df.tail()))

        
             claimable_df.to_csv('claimable.csv',index=True)

             

             # Build the transaction
             
              # Create a DataFrame and fill it with the data from the server
           
             
            # Generate trades signal
             signal=self.learn.get_signal(symbol= self.symbol,candle_list=self.get_stellar_candles())
             self.logger.info( 'signal :'+ str(signal))


             if signal == 'buy' or signal == 1:
               self.logger.info(f'Buying {self.learn.quantity} {self.learn.symbol} at {self.learn.price}')
              # Build Buying  transaction
               # Set TimeBounds
               
               
              # Submit the transaction to the Stellar network
               self.transaction.append_operation(self.buying_operation).build().sign(signer=self.secret_key)


               response = self.server.submit_transaction(self.transaction)

              # Check the transaction result
               if response !=None and response["successful"]:
                print("Buy order placed successfully!")
                self.server_msg['status'] = 'Success'
                self.server_msg['message'] = ' Buy order placed successfully!'
                print("Transaction hash:", response["hash"])
               else:
                print("Buy order failed. Error:", response["result_xdr"])
                self.server_msg['status'] = 'Failed'
                self.server_msg['message'] ='Buy order failed. Error:'+ response["result_xdr"]



             elif signal =='sell' or signal <=-1:
              

              # Build selling the transaction

               self.transaction.append_operation(self.selling_operation).build().sign(signer=self.secret_key)

               #Submit the transaction to the Stellar network
 
               response = self.server.submit_transaction(self.transaction,True)
              #Check the transaction result
               if response["successful"] :
                print("Sell order placed successfully!")
                self.server_msg['status'] = 'Success'
                self.server_msg['message'] = 'Sell order placed successfully!'
                print("Transaction hash:", response["hash"])
               else:
                print("Sell order failed. Error:", response["result_xdr"])
                self.server_msg['status'] = 'Failed'
                self.server_msg['message'] ='Sell order failed. Error:'+ response["result_xdr"]

               transaction_df=pd.DataFrame(self.transaction)
               transaction_df.to_csv('transaction.csv')
               print("transaction "+str(transaction_df))      

               time.sleep(1)









    def stop(self):
        self.logger.info('Stopping trading bot')
        
        self.server_msg['status'] = 'Stopping trading bot...!' 
        self.server_msg['message'] = 'We are stopping trading bot...'
        self.server_msg['sequence'] = self.sequence
        self.server_msg['time'] = time.time()
        self.running = False
        if self.server!= None:
            self.server.close()
        if self.thread.is_alive():
            self.thread.join()
            self.logger.info('Trading bot stopped')
            self.server_msg['status'] = 'Stopped'
            self.server_msg['message'] = 'Trading bot stopped'
            self.server_msg['sequence'] = self.sequence
        

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
     balance_data = []
     for balance in balances:
        balance_data.append(
           {
            'balance': balance['balance'],
            'limit': 0,
            
            'asset_type': balance['asset_type'],
            'asset_code': balance['asset_code'],
            'asset_issuer': balance['asset_issuer']})


    # Add a row for each balance
     df =pd.DataFrame( columns=['Account ID', 'Sequence', 'Home Domain', 'Balance', 'Limit', 'Asset Type', 'Asset Code', 'Asset Issuer'])
     df['Account ID']=[self.account_id]
     df['Sequence']=[self.sequence]
    # df['Home Domain'] = account_info['home_domain']
     df['Balance']= balance_data[0]['balance']
     df['Limit']=balance_data[0]['limit']
     df['Asset Type'] = balance_data[0]['asset_type']
     df['Asset Code'] = balance_data[0]['asset_code']
     return df
    



    def account_balance(self):
        endpoint = f"{self.stellar_horizon_url}/accounts/{self.account_id}/balances"
        response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.status_code)
            print(response.text)
            return None

        
        

    def account_update(self, balance):

        self.balance = balance
        self.logger.info('Account balance:' + str(self.balance))



    # Function to fetch asset information
    def get_assets(self, asset_code=None, asset_issuer=None, cursor=None, limit=None, order=None):

        self.last_update_time = time.time()
        params = {
            "asset_code": asset_code,
            "asset_issuer": asset_issuer,
            "cursor": cursor,
            "limit": limit,
            "order": order}
        endpoint = f"{self.stellar_horizon_url}/assets"
        response = requests.get(url=endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            self.server_msg['message']= " Error:" + str(response.status_code) + " " + str(response.reason)
        return None
    # Function to fetch trade aggregations
    def get_trade_aggregations(self):
        
     self.logger.info('Fetching trade aggregations')
    

     self.server_msg['message'] = 'Fetching trade aggregations'

     data=self.server.trade_aggregations(base=self.base_asset,
                                                            counter= self.counter_asset, 
                                                            start_time=  self.start_time,
                                                            end_time=   self.end_time,
                                                            offset= self.offset,
                                                            resolution=  self.resolution
                                                          ).call().popitem()[-1]
     return data
    
    

    
    def start(self):
        self.logger.info('Starting bot')
    
        self.server_msg['time'] = time.time()
        self.thread = threading.Thread(target=self.run, args=()) # Start the thread
        while self.thread is None: 
           self.server_msg['message'] = 'Loading Stellar network...'
           time.sleep(1)

        self.thread.daemon = True # Daemonize the thread
        self.running = True
        self.server_msg['message'] = 'Bot started @'+str(time.ctime())
        self.thread.start()
        

    def login(self, user_id:str='', secret_key:str=''):

        if user_id is None or secret_key is None:
            
            self.logger.info('Please enter your user_id and secret_key')
            self.server_msg['message']='Please enter your user_id and secret_key'
            tkinter.Message(master=self.controller, text=self.server_msg['message'], width=50)
            return None
        
        
        self.account_info = self.Check_account(account_id_=user_id)
            
        if self.connected:

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

    ''' Function to receive money from another account '''
    def receive_money( self, destination_public_key:str=None, amount:str="10", asset:str=stellar_sdk.Asset.native()):
       

              # Build the transaction
        self.transaction.append_payment_op(destination=destination_public_key, amount=amount, asset=asset).add_time_bounds(min_time=self.min_time, max_time=self.max_time).add_extra_signer(
            self.keypair
        ).add_memo(self.memo).build()         # Sign the transaction
        

        # Submit the transaction envelope to the Stellar network
        try:
            response = self.server.submit_transaction(self.transaction)
            print(f"Transaction hash: {response['hash']}")
            tkinter.Message(master=self.controller, text=self.server_msg['message'], width = 50)

        except Exception as e:
             print(f"An error occurred: {e}")
             tkinter.Message(master=self.controller, text=self.server_msg['message'], width = 50)
      
    

    ''' Function to send money to another account'''
    def send_money( self, amount:str="100", asset:str=stellar_sdk.Asset.native(), receiver_address:str=None):
       
           #self.receiver_public_key="GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA"
           # Build the transaction
           self.transaction .add_extra_signer(self.keypair).append_payment_op(destination=receiver_address, amount=amount, asset=asset).add_time_bounds(min_time=self.min_time, max_time=self.max_time).add_memo(self.memo).build()        
           # Submit the transaction envelope to the Stellar network
           try:
            response = self.server.submit_transaction(self.transaction)
            print(f"Transaction hash: {response['hash']}")
           except Exception as e:
             print(f"An error occurred: {e}")
             tkinter.Message(master=self.controller, text=self.server_msg['message'], width = 50)

    ''' Function to get trade aggregations (candles)'''
    def get_stellar_candles(self):
    # Get trade aggregations (candles)
   
    
     # Creating a DataFrame
     self.candles = pd.DataFrame(self.get_trade_aggregations(),  columns=['symbol','timestamp', 'open', 'high', 'low', 'close'
                                                                ,'trade_count','base_volume','counter_volume','avg'
                                                                ])

     candles = self.candles
     # Converting timestamp to datetime
     candles['timestamp'] = pd.to_datetime(candles['timestamp'], unit= 'ms')

     #Saving candles to a database
     self.candles.sort_values(by=['timestamp'], inplace=True)
     self.candles['symbol'] = self.symbol
     connection = sqlite3.connect('TradingBot.sql')
     candles.to_sql('candles', con=connection, if_exists='append', index=False )
    
     return candles
  
    # Function to extract operation information
    def extract_operations_info(self,data):
    
     links = data['_links']
     next_link = links['next']['href'] if 'next' in links else None
     prev_link = links['prev']['href'] if 'prev' in links else None

     embedded = data['_embedded']
     records = embedded['records'] if 'records' in embedded else []

    # Extracting relevant information from each record
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


    def get_history(self):
       
        self.server_msg['message'] = 'Fetching history'
        self.server_msg['time'] = time.time()

        data=self.server.transactions().limit(10).call().popitem()[-1]['records']
        self.cursor = data
        self.server_msg['time'] = time.time() - self.server_msg['time']
        self.server_msg['message'] = 'Fetching history'
        return data
    def get_update_time(self):
       
        self.server_msg['message'] = 'Fetching update time' 

        return time.time() - self.last_update_time
    def get_trades(self):
       
        self.server_msg['message'] = 'Fetching trades'
        self.server_msg['time'] = time.time()
        data=self.server.trades().limit(10).call().popitem()[-1]['records']
        self.cursor = data

        return data
    def get_transactions(self):
       
        self.server_msg['message'] = 'Fetching transactions'
        self.server_msg['time'] = time.time()
        data=self.server.transactions().limit(10).call().popitem()[-1]['records']
        self.cursor = data
    
        return data
    def get_accounts(self):
       
        self.server_msg['message'] = 'Fetching accounts'
        self.server_msg['time'] = time.time()
        data=self.server.accounts().limit(10).call().popitem()[-1]['records']
        self.cursor = data
        self.server_msg['time'] = time.time() - self.server_msg['time']        
        return data
    
