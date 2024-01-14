from stellar_sdk import Server, Keypair, TransactionBuilder, Network,Asset, TransactionEnvelope
import ccxt
import pandas as pd
import threading
import time
import random
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
import numpy as np

import logging

class StellarClient:

    ''' Stellar Client Class '''
    def __init__(self, account_id,secret_key=None):


  
        self.name = 'StellarClient'
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.info(f'Starting {self.name}')

        self.db = sqlite3.connect(self.name+'.sql')

        self.server_msg = {'message': '','status': '','status_code': 0,'info': ''}
        
      
        

        self.horizon_url = 'https://horizon.stellar.org'
        self.server = Server(horizon_url=self.horizon_url)
        self.account_id = account_id
        self.secret_key = secret_key

        self.server_thread = None
        # if secret_key is  None:
        #     self.server_msg['status_code'] = 400
        #     self.server_msg['message'] = 'Please provide a secret key'
        #     self.server_msg['status'] = 'error'
            
        #     return 
        
       
        self.keypair = Keypair.from_secret(secret_key)
        self.account=self.server.load_account(account_id=self.keypair.public_key)


        self.selling=  Asset(code='USDC', issuer='GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN')
        self.buying= Asset.native()
        self.amount=random.randint(1,25)

        #Get assets  and save them into csv file

        self.assets=self.server.assets().limit(100).call().popitem()[-1]['records']

        rows=[]
        columns=[]

        for asset in self.assets:
            if isinstance(asset,dict):
               for key,value in asset.items():
                   rows.append(value)
                   columns.append(key)

            elif isinstance(asset,list):
                for value in asset:
                    rows.append(asset[value])
                    columns.append(value)
            elif isinstance(asset,str):
                rows.append(asset)
                columns.append(asset)
            else:
               
                rows.append(asset)
                columns.append(asset)
         


        self.assets_df = pd.DataFrame(self.assets,columns=columns)
        self.assets_df.to_csv('ledger_assets.csv',index=False)
        self.current_time = int(time.time())
        self.valid_duration =  60*60*24*365*1000 # 3 years
        self.min_time =self.current_time #1631277600# Current time in Unix format
        self.max_time = self.current_time + self.valid_duration # Current time in Unix format
        self.timeframe_list=['1m','5m','15m','30m','1h','2h','4h','6h','8h','12h','1d','3d',' 1w','1M']
        #Converting the timeframe to milliseconds
        self.timeframe_selected = '1m'
        self.timeframe = int( self.timeframe_list.index(self.timeframe_selected) * 60000)
        print('timeframe ',self.timeframe)
        self.resolution = 60000 # 1 minute resolution or timeframe in milliseconds
        self.start_time = time.time()# Initial time in Unix format
        self.end_time = self.current_time + self.timeframe # Current time in Unix
        self.offset = 0 # Used to keep track of the offset of the timeframe in milliseconds
        self.candles = pd.DataFrame(columns=['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'base_volume', 'counter_volume', 'trade_count', 'avg'])

        





       # self.start()
    def get_trade_aggregations(self
                                ):
        
        # Create a timer to check the trade aggregations
        trade_aggregations =self.server.trade_aggregations(           
            base= self.selling,
            counter=self.buying,

           offset= self.offset,# 
           resolution= self.resolution # Critical period in milliseconds (60 seconds) do not remove any data

        ).limit(100).call().popitem()[-1]['records']

        print('trade_aggregations',trade_aggregations)
    
        return trade_aggregations
    def get_stellar_candles(self):
    # Get trade aggregations (candles)
     trade_aggregations =      self.get_trade_aggregations() 
    
         

     print('trade_aggregations',str(trade_aggregations))

     # Creating a DataFrame
     candles = pd.DataFrame( trade_aggregations , columns=['symbol','timestamp', 'open', 'high', 'low', 'close'
                                                                ,'trade_count','base_volume','counter_volume','avg'                             
                                                                ])
     
    
     candles['symbol'] = self.selling.code + '/' + self.buying.code

     # Converting timestamp to datetime
     print('timestamp',str(candles))


     

     #Saving candles to a database
     
     candles['timestamp'] = pd.to_datetime(candles['timestamp'], unit='ms')
     candles.to_csv('ledger_candles.csv', index=False, index_label='timestamp')
     
    
     return candles
    




        
        
     
        

    def start(self):
     
      while True:
        
        self.server_thread = threading.Thread(target=self.run, args=())
        self.server_thread.daemon = True

        
        timer= threading.Timer(self.timeframe, self.server_thread.start)
        timer.daemon = True
        timer.start()
        self.server_msg['status'] = 'running'
        self.server_msg['status_code'] = 200
        self.server_msg['message'] = 'In progress...'
        if  self.server_thread.is_alive() is False:
            self.server_thread.start()
     
        break
    
    def stop(self):
        self.server_msg['status'] ='stopped'
        self.server_msg['status_code'] = 200
        self.server_msg['message'] = 'Stopped...'

        if self.server_thread is not None:
         self.server_thread.join()

    
    
    def get_signal(self, symbol: str): 

        

       
 
        #Making sure that the symbol is in the list
        data =self.get_stellar_candles()       
        #pd.read_sql_query(f"SELECT * FROM candles WHERE symbol = '{symbol}'", con=db, index_col='timestamp', parse_dates=True)
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
      
        
       # self.fib_levels = fib_levels
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

      
        score = accuracy_score(new_data['Signal'], new_data['Predicted_Signal'])
       
        print(f'Model Accuracy: {score}')


  
        signal = new_data['Predicted_Signal'].values[-1:]
     
        # Adjust conditions based on your strategy
        if signal == 1 and accuracy > 95:
            print(f'Signal Buy: {signal}')
            self.server_msg['message'] = f'Signal Buy: {signal}'
            return 1
        elif signal == 0 and accuracy > 95:
            print(f'Signal Sell: {signal}')
            self.server_msg['message'] = f'Signal Sell: {signal}'
            return -1
    

        return 0


      
    def run(self):

        self.server_msg['status'] = 'running' 
        self.trades=self.server.trades().limit(100).call().popitem()[-1]

        self.trades_df = pd.DataFrame.from_dict(self.trades, orient='index')
        self.trades_df.to_csv(
            'trades.csv',
            index=False
        )


        self.offers= self.server.offers().limit(100).call().popitem()[-1]

        self.offers_df = pd.DataFrame.from_dict(self.offers, orient='index')
        self.offers_df.to_csv(
            'offers.csv',
            index=False
        )
        #self.account=self.server.accounts().limit(100).call().popitem()[-1]

      
        order_book= self.server.orderbook(self.selling,self.buying).call().popitem()[-1]
        order_book_df = pd.DataFrame.from_dict(order_book, orient='index')
        order_book_df.to_csv( 'order_book.csv', index=False)

     
     
        print('order_book',order_book_df)
    
        print('account',self.account)
        print('server_msg',self.server_msg)
        

         
# Example fetching live price and candle data
        symbol_to_check = 'XLM/USDT'  # Replace with the symbol you are interested in
        live_price = self.get_live_price(symbol_to_check)
        price = live_price




        print(f"Live Price for {symbol_to_check}: {live_price}")


        self.server_msg['status'] = 'Live Trading'

        self.operation_type =self.get_signal(symbol_to_check)
        if self.operation_type =='sell':

         offeers= self.create_trade_offer( self.buying,self.selling, self.amount, price,'sell')
         print('offer',offeers)
        elif self.operation_type == 'buy':
           offeers= self.create_trade_offer( self.selling,self.buying, -self.amount, price,'buy')
           print('offer',offeers)
        else :
            print(f"No action required for {symbol_to_check}")
            self.server_msg['message'] = f"No action required for {symbol_to_check}"



       
    def get_current_base_fee(self):
  
     base_fee = self.server.fetch_base_fee()
     return base_fee


    def create_trade_offer(self, selling_asset=None, buying_asset=None, amount=0.8, price=0.12,type='sell'):
       

       OPERATION_BASE_FEE = self.get_current_base_fee()
       print(f"OPERATION_BASE_FEE: {OPERATION_BASE_FEE}")
       try:

        if type =='sell':
         transaction = (TransactionBuilder(
                source_account=self.account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=OPERATION_BASE_FEE
            ).add_time_bounds(self.min_time, self.max_time)
            .append_manage_sell_offer_op(
                selling=selling_asset,
                
                buying=buying_asset,
         
                amount=amount,
                price=price
            )
            
            .build())
         transaction.sign(self.keypair)
         res=self.server.submit_transaction(transaction).popitem()[-1]

         print(f"Trade offer placed successfully! Transaction ID: {res}")

         
        elif type == 'buy':
           
            transaction = (TransactionBuilder(
                source_account=self.account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=OPERATION_BASE_FEE
            ).add_time_bounds( self.min_time, self.max_time)
               .append_manage_buy_offer_op(  
                selling=selling_asset,
                buying=buying_asset,
                amount=amount,
                price=price,
                source=self.account).build())


            transaction.sign(self.keypair)
            res=self.server.submit_transaction(transaction).popitem()[-1]

            print(f"Trade offer placed successfully! Transaction ID: {res}")
            self.server_msg['message'] = f"Trade offer placed successfully! Transaction ID: { res}"


       except Exception as e:
           print(f"Failed to place trade offer: {e}")
           self.server_msg['message'] = f"Failed to place trade offer: {e}"
    def cancel_offer(self, offer_id=0, selling=None, buying=None):
        try:
            # Fetch current base fee from the network
    
            transaction = (
                TransactionBuilder(
                    source_account=self.account,
                    network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=self.get_current_base_fee())
                .append_manage_sell_offer_op(
                    selling=selling,  # Native asset (XLM) for selling
                   buying= buying,  # Native asset (XLM) for buying
                    amount='0',  # Set the amount to 0 to clear the offer
                    price='1',  # Set a valid non-zero price
                    offer_id=offer_id,  # Specify the offer ID to cancel
                    
                     source= self.account
                )
                .set_timeout(60)
                .build()
            )

            transaction.sign(self.keypair)

            # Submit the transaction to the Stellar network
            response = self.server.submit_transaction(transaction)

            if response["successful_transaction"]:
                print(f"Offer with ID {offer_id} canceled successfully!")
            else:
                print(f"Failed to cancel offer. Result XDR: {response['result_xdr']}, Extras: {response['extras']}")

        except Exception as e:
            print(f"Failed to cancel offer: {e}")


    def make_payment(self, destination_account=None, asset=None, amount=0.0):
        transaction = TransactionBuilder(
                source_account=self.account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100,
            ).append_payment_op(
                destination=destination_account,
                asset=asset,
               
                amount=amount,source= self.account
            ).set_timeout(5000).build()
        transaction.sign(self.keypair)
        response = self.server.submit_transaction(transaction)


        print(f"Payment made successfully! Transaction ID: {response}")

    def get_live_price(self, symbol):
        exchange = ccxt.binanceus()  # Replace with your preferred exchange
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']

    def get_candle_data(self, symbol, timeframe='1h', limit=10):
        exchange = ccxt.binanceus()  # Replace with your preferred exchange
        candles = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        return candles

    def get_account_balance(self):
        account_balances = self.account
        print(account_balances)
        
        return 890



