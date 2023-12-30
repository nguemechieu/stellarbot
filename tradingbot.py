
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


class TradingBot:
    ''' Constructor for the Trading Bot '''    
    def __init__(self, start_bot=False, account_id=None, account_secret='SB2LHKBL24ITV2Y346BU46XPEL45BDAFOOJLZ6SESCJZ6V5JMP7D6G5X',controller=None):   
        self.name = 'TradingBot'
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.addHandler(logging.FileHandler(self.name + '.log'))

        
        self.secret_key=account_secret
        self.account_id = account_id
        
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
     
        self.stellar_network=stellar_sdk.Network.PUBLIC_NETWORK_PASSPHRASE
        
        self.server = stellar_sdk.Server(horizon_url=self.stellar_horizon_url) # Initialize the server
        
        self.keypair = stellar_sdk.Keypair.from_secret(secret=self.secret_key) # Initialize the keypair
        
        # Get User account
        self.account=  self.server.load_account(account_id= self.account_id).raw_data
        
              
        # Create an order builder object
        self.order_tickets = pd.DataFrame(columns=['order_id', 'symbol','price', 'quantity','create_time', 'type'])
        
        self.server_status = threading.Event()
        self.asset_issuers_list = [] # Used to keep track of the asset issuers

        self.assets_list ={'asset_code':'','asset_issuer':'','asset_type':''} # Used to keep track of the asset list
        self.transaction_list = [] # Used to keep track of the transactions
        self.start_bot = start_bot # Used to start the bot
        self.server_msg ={'status': 'off', 'error': None, 'account':[],'data': None,'message': None}
    
        self.balance: float = 0.00
        
        self.balances = []
        self.base_asset_code= stellar_sdk.Asset.native().code
        self.base_asset_issuer = stellar_sdk.Asset.native().issuer

        self.counter_asset_code='USDC'
        self.counter_asset_issuer ="GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"


        self.symbol = self.counter_asset_code+'/'+self.base_asset_code 
       
        print(self.account, self.account_id)
        self.server_data=self.server.data(account_id= self.account_id,data_name= 'balances')
        print(self.server_data)
        self.server_msg['data'] =  self.server_data
        self.server_msg['status'] = 'Server online'
        
        self.asset_list=self.get_asset_list()
            
        current_time = int(time.time())  # Current time in Unix format
        valid_duration = 3600  # Valid for 1 hour (adjust as needed)
        self.min_time = 1631277600# Current time in Unix format
        self.max_time = current_time + valid_duration

          # Create a transaction builder object
        self.transaction = stellar_sdk.transaction_builder.TransactionBuilder(v1=True,                                           
                 source_account=self.account,
                 network_passphrase=self.stellar_network,
                 base_fee=100).add_time_bounds(min_time=self.min_time, max_time=self.max_time)
       
     
        self.account_info = { '_links': {...}, } # The complete account info goes here

        
        #check if internet connection is established
        self.connection = self.check_connection()
        if not self.connection:
            self.logger.info('No internet connection')
           
            self.server_msg['status'] = 'No internet connection'
            return None
        self.thread = threading.Thread(target=self.run, args=( ))
        self.thread.daemon = True
      
        
        if self.start_bot:
           self.logger.info('Bot started  ')
           self.server_msg['message'] = 'Bot started @'+str(time.ctime())

           self.thread.start()
        else:
           self.logger.info('Bot stopped  ')

           self.server_msg['message'] = 'Bot stopped @'+str(time.ctime())
           if self.thread.is_alive():
            self.thread.join()

           
        self.logger.info('Bot started  ')
        self.server_msg['message'] = 'Bot started'
        self.account_df = pd.DataFrame(columns=['Account ID', 'Sequence', 'Home Domain', 'Balance', 'Limit', 'Asset Type', 'Asset Code', 'Asset Issuer'])
        self.account_df.to_csv('account_info.csv', index=False)

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
        print('assets',self.asset_0)


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
        while True:
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

         self.learn=Learning()
         self.learn.symbol= 'XLM'
         self.learn.price= 100
         self.learn.quantity= 100
         self.logger.info('Starting trading bot')
      
         data = self.account

         
       
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


        
      
                
         while True:
             self.logger.info('Trading bot running')


      
            # self.send_money()
           
             self.assets= self.get_asset_list()


             self.asset_df =pd.DataFrame(self.assets,['asset_code','asset_issuer','asset_type'])

             print(str(self.asset_df))


             self.fee_statistics =self.server.fee_stats().limit(10).order(desc=True).call().popitem()[-1]
             self.fee_statistics_df=pd.DataFrame(self.fee_statistics,columns=['fee_asset','fee_asset_issuer','fee_amount','fee_asset_type'])
             self.fee_statistics_df.to_csv('fee_statistics.csv',index=True)

             self.ledger_statistics =self.server.offers().order(desc=True).limit(10).call().popitem()[-1]
             self.ledger_statistics_df=pd.DataFrame(self.ledger_statistics,columns=['offer_id','offer_type','price','amount','price_r','amount_r'])
             self.ledger_statistics_df.to_csv('ledger_offers.csv',index=True)

             self.ledger_statistics =self.server.trades().order(desc=True).limit(10).call().popitem()[-1]
             self.ledger_statistics_df=pd.DataFrame(self.ledger_statistics,columns=['trade_id','price','amount','price_r','amount_r'])
             self.ledger_statistics_df.to_csv('ledger_trades.csv',index=True)

             self.ledger_statistics =self.server.transactions().order(desc=True).limit(10).call().popitem()[-1]
             self.ledger_statistics_df=pd.DataFrame(self.ledger_statistics,columns=['transaction_id','transaction_hash','transaction_type','transaction_result','transaction_fee','transaction_timestamp'])
             self.ledger_statistics_df.to_csv('ledger_transaction.csv',index=True)

             self.ledger_payments =self.server.payments().order(desc=True).limit(10).call().popitem()[-1]
             self.ledger_payments_df=pd.DataFrame(self.ledger_payments,columns=['payment_id','from_account','to_account','amount'])
             self.ledger_payments_df.to_csv('ledger_payments.csv',index=True)

             self.ledger_effects =self.server.effects().order(desc=True).limit(10).call().popitem()[-1]
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

             self.asset_list =pd.DataFrame(self.assets, columns=['asset_type', 'asset_code', 'asset_issuer'])
             self.asset_list.to_csv('asset_list.csv', index=False)
      

             # Create a DataFrame from the bids and asks data
             df = pd.DataFrame( self.order_book['orderbook'], columns=['price', 'amount','bids', 'asks'] )
             df.to_csv('order_book.csv', index=False)

             # Extract and work with the relevant columns
             df['price'] = df['price'].astype(float)
             df['amount'] = df['amount'].astype(float)
             self.learn.price =df['price']
             self.learn.quantity = df['amount']
      
             
            
             # Create a DataFrame and fill it with the data from the server
           
             
             self.candles = self.get_stellar_candles(self.base_asset_code, self.base_asset_issuer, 
                                                self.counter_asset_code, self.counter_asset_issuer
                                                )
            # Generate trades signal
             signal=self.learn.get_signal(symbol= self.symbol,candle_list=self.candles)
             self.logger.info(
                
               'signal :'+ str(signal)
             )

             

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

             self.offers=self.server.offers().limit(10).order(desc=True).call().popitem()[-1]['offers']
             self.offers_df=pd.DataFrame(self.offers,columns=['offer_id','offer_type','price','amount','price_r','amount_r'])
             self.offers_df.to_csv('offers.csv',index=True)
             print('offers :'+str(self.offers_df))

            
             self.operation2=self.server.operations().limit(10).order(desc=True).call().popitem()[-1]['operations']

             self.operation2_df=pd.DataFrame(self.operation2['records'],columns=['operation_id','operation_type','price','amount','price_r','amount_r'])
             self.operation2_df.to_csv('operation2.csv',index=True)
          


             # Build the transaction

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
                print("Transaction hash:", response["hash"])
               else:
                print("Buy order failed. Error:", response["result_xdr"])



             elif signal =='sell' or signal == 2:
              

              # Build selling the transaction

               self.transaction.append_operation(self.selling_operation).build().sign(signer=self.secret_key)


               #Submit the transaction to the Stellar network
 
               response = self.server.submit_transaction(self.transaction,True)
              

              #Check the transaction result
               if response["successful"] :
                print("Sell order placed successfully!")
                print("Transaction hash:", response["hash"])
               else:
                print("Sell order failed. Error:", response["result_xdr"])

               self.transaction_df=pd.DataFrame(self.transaction)
               self.transaction_df.to_csv('transaction.csv')
               print("transaction "+str(self.transaction_df))
        
             self.trades=self.server.trades().limit(10).order(desc=True).call().popitem()[-1]
             self.trade_df =pd.DataFrame(self.trades ,columns=['trade_id','trade_type','price','amount','price_r','amount_r'])

             print('trades :'+str(self.trade_df))
             self.trade_df.to_csv('trades.csv',index=True)           

             self.claimable=self.server.claimable_balances().limit(10).order(desc=True).call().popitem()[-1]
             self.claimable_df=pd.DataFrame(self.claimable,columns=['claimable_id','claimable_type','claimable_balance','claimable_balance_r'])
             print('claimable :'+str(self.claimable_df.tail()))

        
             self.claimable_df.to_csv('claimable.csv',index=True)

             time.sleep(10)

    def stop(self):
        self.logger.info('Stopping trading bot')

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
    def get_trade_aggregations(self,
                               base_asset_code=stellar_sdk.Asset.native().code,
                               base_asset_issuer=stellar_sdk.Asset.native().issuer,
                              
                               counter_asset_code='BTCLN',
                               counter_asset_issuer=None ):
        
        # Create a timer to check the trade aggregations
        trade_aggregations =self.server.trade_aggregations(           
            base= stellar_sdk.Asset(code=base_asset_code, issuer=base_asset_issuer),
            counter= stellar_sdk.Asset(code=counter_asset_code, issuer=counter_asset_issuer),

           offset= 0,
           resolution= 60000 # Critical period in milliseconds (60 seconds) do not remove any data

        ).call().popitem()[-1]['records']
    
        timer = threading.Timer(10000, trade_aggregations)
        timer.daemon = True
        timer.start()
        return trade_aggregations

        


        
        
        

    def login(self, user_id:str='', secret_key:str=''):

        if user_id is None or secret_key is None:
            
            self.logger.info('Please enter your user_id and secret_key')
            self.server_msg['message']='Please enter your user_id and secret_key'
            tkinter.Message(master=self.controller, text=self.server_msg['message'], width=50)
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

        except Exception as e:
            print(f"An error occurred: {e}")
      
    def send_money( self, amount:str="100", asset:str=stellar_sdk.Asset.native(), receiver_address:str=None):
       
           #      self.receiver_public_key="GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA"
           # Build the transaction
           self.transaction =  stellar_sdk.TransactionBuilder(source_account=self.account, network_passphrase="PUBLIC_NETWORK")
           self.transaction.add_extra_signer(self.keypair).append_payment_op(destination=receiver_address, amount=amount, asset=asset).add_time_bounds(min_time=self.min_time, max_time=self.max_time).build()

        
           # Submit the transaction envelope to the Stellar network
           try:
            response = self.server.submit_transaction(self.transaction)
            print(f"Transaction hash: {response['hash']}")
           except Exception as e:
             print(f"An error occurred: {e}")
             tkinter.Message(master=self.controller, text=self.server_msg['message'], width = 50)


    def get_stellar_candles(self,base_asset_code, base_asset_issuer, 
                            counter_asset_code, counter_asset_issuer):
    # Get trade aggregations (candles)
     self.trade_aggregations = self.get_trade_aggregations(base_asset_code=base_asset_code,
                                                            base_asset_issuer=base_asset_issuer, 
                                                           counter_asset_code=counter_asset_code, 
                                                           counter_asset_issuer=counter_asset_issuer)
    




     # Creating a DataFrame
     candles = pd.DataFrame( self.trade_aggregations , columns=['symbol','timestamp', 'open', 'high', 'low', 'close'
                                                                ,'trade_count','base_volume','counter_volume','avg'
                                                               
  
                                                                ])
     
     candles['symbol'] = self.symbol

     # Converting timestamp to datetime
     print('timestamp',str(candles))
     # Converting timestamp to datetime
     candles['timestamp'] = pd.to_datetime(candles['timestamp'], unit= 'ms')

     #Saving candles to a database
     candles.to_csv('candles.csv')
     connection = sqlite3.connect('TradingBot.sql')
     candles.to_sql('candles', con=connection, if_exists='append', index=False )
    
     return candles
