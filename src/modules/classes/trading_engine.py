from datetime import datetime
import logging
import random
import time
import pandas as pd
import requests
from stellar_sdk import Asset, Server, TransactionBuilder, Keypair, Network, TransactionEnvelope

from modules.classes.data_fetcher import DataFetcher

class TradingsEngine:
    def __init__(self, server:Server, keypair: Keypair, account,controller,server_msg):
        super().__init__()

        self.controller = controller

        self.current_time = int(time.time())
        self.start_time = 1609459200000  # January 1, 2021 00:00 UTC
        self.end_time = self.start_time + (3 * 3600000)  # 3 hours later (January 1, 2021 03:00 UTC)
        self.resolution = 3600000  # 1 hour
        self.timeframe_list = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
        self.timeframe_selected = '1h'
        self.timeframe = int(self.timeframe_list.index(self.timeframe_selected) * 60000)
        print('timeframe', self.timeframe)

        self.server = server
        self.keypair = keypair
        self.account = account
        self.logger = logging.getLogger(__name__)
        self.account_id =self.keypair.public_key
        self.order_book= [{
            "selling": Asset('USDC', issuer='GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN'),
            "buying": Asset.native(),
            "price": 1.0,
            "amount": 10000000,
            "created_at": 1609459200,
            "updated_at": 1609459200,
            "order_book_id": 1,
            "order_id": 1,
            "order_type": "buy",
            "order_price": 1.0,
            "order_amount": 10000000,
            "order_status": "open",
            "order_created_at": 1609459200,
            "order_updated_at": 1609459,
            "bids":{},
            "asks":{}
        }]

        self.server_msg=server_msg
        self.price =0.89
        self.amount =10
        self.offer_id =  random.randint(0,1000000)
        self.server_msg['message'] = 'Trading Engine initialized'

  # Initialize Stellar Server
        self.server = server
        self.server_msg =  {
            "message": '',
            "status": '',
            "status_code": 0,
            "info": ''
        }
        self.assets = []
        self.transaction: TransactionBuilder
        self.order_book = None
        self.trade_signal=0


        self.assets_df = pd.DataFrame()
        self.orders_df = pd.DataFrame()
        self.trades_df = pd.DataFrame()
        self.trade_signal=0

        self.amount = 10
        self.server_msg['message'] = 'Loading assets'
        self.data_fetcher =DataFetcher(self.server)
        self.assets = self.data_fetcher.get_assets()

        print("Loaded assets", self.assets)
        self.server_msg['message'] = 'Loaded assets' if self.assets else 'Failed to load assets'

        self.base_asset = Asset.native()
        self.counter_asset = Asset('USDC', issuer='GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN')


        self.transaction_builder = TransactionBuilder(self.account, network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE)
        self.transaction_builder.add_text_memo(memo_text='StellarBot')
       

     

    def process_order_book(self):
        # Implement your order book processing logic here
        self.logger.info("Processing order book")
        # Fetch the order book from the Stellar network
        self.order_books = self.server.orderbook(self.base_asset, self.counter_asset).call()
        # Save the order book data to a file
       
        order_book_df = pd.DataFrame(self.order_books['bids'] + self.order_books['asks'])
        order_book_df.to_csv('ledger_order_book.csv', index=False)
        # print('Order book saved to order_book.csv')
        # Implement your trade signal calculation logic here
        # Example: check if the bid-ask spread is above a certain threshold
        bid_price = self.order_books['bids'][0]['price']
        ask_price = self.order_books['asks'][0]['price']
        spread = ask_price - bid_price
        self.trade_signal = 1 if spread > 0.005 else -1
        print('Trade signal', self.trade_signal)
    
    # Function to calculate the trade signal based on order book data
    def calculate_trade_signal(self):
        #  Calculate the trade signal based on market data
        self.logger.info("Calculating trade signal")
        return self.get_trading_signals(self.base_asset, self.counter_asset)
    
    
    # Function to trade if the trade signal is required
    def trade_if_required(self):
        # Implement your trading logic here (buy/sell based on signals)
        self.logger.info("Trading if required")
        # Example: if the trade signal is 1, buy the asset
        if self.trade_signal == 1:
            self.buy_asset()
        # Example: if the trade signal is -1, sell the asset
        elif self.trade_signal == -1:
            self.sell_asset()
    
    def buy_asset(self):
        # Implement your buying logic here
        self.logger.info("Buying asset")
        # Example: create a buy transaction
        self.transaction_builder.append_manage_buy_offer_op(buying=self.base_asset, selling= self.counter_asset,amount=str(self.amount),price=str(self.price),offer_id=self.offer_id)
        transaction=self.transaction_builder.build()
        transaction.sign(self.keypair)
        self.server_msg['message'] = (
            f'Buying{str(self.amount)}of'
            + self.counter_asset.code
            + 'for'
            + str(self.amount * self.amount)
            + 'of'
            + self.base_asset.code
        )
        self.server.submit_transaction(transaction)
        print('Buy transaction submitted')
        self.server_msg['message'] = 'Buy transaction submitted...'
    
    def sell_asset(self):
        # Implement your selling logic here
        self.logger.info("Selling asset")
        # Example: create a sell transaction
        self.transaction_builder.append_manage_sell_offer_op(buying=self.counter_asset, selling=self.base_asset, amount=str(self.amount), price=str(self.price), offer_id=self.offer_id)
        transaction=self.transaction_builder.build()
        transaction.sign(self.keypair)
        self.server_msg['message'] = (
            f'Selling{str(self.amount)}of'
            + self.counter_asset.code
            + 'for'
            + str(self.amount * self.price)
            + 'of'
            + self.base_asset.code
        )
        self.server.submit_transaction(transaction)
        print('Sell transaction submitted')
        self.server_msg['message'] = 'Sell transaction submitted...'
    
    def process_transactions(self, transaction):
        
        # Implement your transaction processing logic here
        self.logger.info("Processing transaction")
        # Example: save the transaction data to a file
        transaction_df = pd.DataFrame([transaction])
        transaction_df.to_csv('ledger_transactions.csv', mode='a', header=not transaction_df.empty, index=False)
        print('Transaction saved to ledger_transactions.csv')
    

        









    def execute_trading_strategy(self,timeframe_selected:str='1h'):
        # Implement your trading logic here (buy/sell based on signals)
        self.logger.info("Executing trading strategy")
        self.timeframe_list = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
        
        self.timeframe = int(self.timeframe_list.index(timeframe_selected) * 60000)
        print('timeframe', self.timeframe)

        if transactions := self.fetch_transactions(self.account_id):
            self.process_transactions(transactions)
            self.process_order_book()
             
        else:
            self.server_msg['message'] = 'Error fetching transactions'
            self.server_msg['status'] = 'error'
            self.server_msg['status_code'] = 500
        self.trade_signal= self.calculate_trade_signal()
         
        self.trade_if_required()
        



    # Function to fetch and save transaction data
    def fetch_transactions(self,account_id):
        try:
            return [
                self.server.transactions()
                .for_account(account_id=account_id)
                .limit(200)
                .call()
            ]
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            self.server_msg['message'] = f"Error fetching transactions: {str(e)}"
            return []
     
   

# Function to create a professional transaction frame
    def create_transaction_dataframe(self,transaction_data):
        try:
            if 'records' in transaction_data:
                return self._extracted_from_create_transaction_dataframe_(transaction_data)
            print("No transaction records found in the data.")
            self.server_msg['message'] = 'No transaction records found in the data'
            return None
        except Exception as e:
            print(f"Error processing transaction data: {e}")
            self.server_msg['message'] = f"Error processing transaction data{str(e)}"
            return None

    
    def _extracted_from_create_transaction_dataframe_(self, transaction_data):
        transactions = transaction_data['records']

        processed_data = [
            {
                'Transaction ID': tx['id'],
                'Created At': tx['created_at'],
                'Source Account': tx['source_account'],
                'Operation Count': tx['operation_count'],
                'Memo': tx['memo'],
                'Fee Charged': tx['fee_charged'],
                'Successful': tx['successful'],
            }
            for tx in transactions
        ]
        # Create a DataFrame
        df = pd.DataFrame(processed_data)

        # Format the DataFrame professionally
        df['Created At'] = pd.to_datetime(df['Created At'])  # Convert dates
        df['Fee Charged'] = df['Fee Charged'].astype(int) / 10000  # Convert fees to lumens

        # Set display options for better readability
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)

        return df
    def get_offers(self):
        return self.data_fetcher.get_offers(self.account_id)
  

   
    def get_accounts(self):
        return self.data_fetcher.get_accounts(self.account_id)


    def get_assets(self):
        
        return self.data_fetcher.get_assets()
   
    
    def get_trading_signals(self, base_asset, counter_asset):

        current_prices=self.get_current_price(base_asset=base_asset, counter_asset=counter_asset)

        if current_prices == {}:
            return self._extracted_from_get_trading_signals_7(
                'No prices found for pair: ', base_asset, counter_asset
            )
        data=  self.get_market_data(base_asset=base_asset, counter_asset=counter_asset)

        if len(data)==0:

            return self._extracted_from_get_trading_signals_7(
                'No data found for pair: ', base_asset, counter_asset
            )
        price_diff = abs(data['close'] - data['open'])

        if price_diff > data['close'] * 0.02:  # Check if price has increased by 2%
          return 1  # Signal to buy
        elif price_diff > data['close'] * 0.01:  # Check if price has increased by 1%
          return -1  # Signal to sell
        else: # Hold price

          return 0 


    def _extracted_from_get_trading_signals_7(self, arg0, base_asset, counter_asset):
        print(f"{arg0}{base_asset}/{counter_asset}")
        self.server_msg['message'] = f"{arg0}{base_asset}/{counter_asset}"
        return 0 
    


    def get_market_data(self, base_asset:Asset, counter_asset:Asset):


        data =pd.DataFrame(columns=['asset',
            'date',
            'open',
            'high',
            'low',
            'close',
            'volume'
        ])
    

        # Fetch OHLCV from aggregator

        # Replace 'BASE_ASSET' and 'COUNTER_ASSET' with the desired assets

        data0=self.get_trade_aggregations(
            base_asset=base_asset,
           counter_asset= counter_asset,
            start_time=self.start_time, 
            end_time= self.end_time,resolution= self.resolution
        )

        data0=pd.DataFrame(data0)
        data0['asset'] = base_asset
        data=pd.concat([data,data0])
        data=data.sort_values(by='date', ascending=True)
        data.reset_index(drop=True, inplace=True)
        data=data.drop_duplicates(subset=['asset', 'date'], keep='last')
        return data
      

# Define the function to fetch trade aggregation data
    def get_trade_aggregations(self,base_asset, counter_asset, start_time, end_time, resolution):
     url = "https://horizon.stellar.org/trade_aggregations"
    
    # Prepare request parameters
     params = {
        'base_asset_type': base_asset['asset_type'],
        'base_asset_code': base_asset.get('asset_code', None),
        'base_asset_issuer': base_asset.get('asset_issuer', None),
        'counter_asset_type': counter_asset['asset_type'],
        'counter_asset_code': counter_asset.get('asset_code', None),
        'counter_asset_issuer': counter_asset.get('asset_issuer', None),
        'start_time': start_time,
        'end_time': end_time,
        'resolution': resolution
    }
    
    # Filter out None values from the params
     params = {k: v for k, v in params.items() if v is not None}
     
     try:
        # Make the GET request to Stellar Horizon's trade aggregation endpoint
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Return the parsed JSON response
        return response.json()['_embedded']['records']
     except requests.exceptions.RequestException as e:
        print(f"Error fetching trade aggregations: {e}")
        return None

        
     
    def get_current_price(self, base_asset, counter_asset):
        try:
            # Get order book from Stellar Horizon API
            orderbook = self.server.orderbook(base_asset, counter_asset).call()

            if 'bids' not in orderbook or len(orderbook['bids']) <= 0:
                return None  # No bids available in the order book
            price = orderbook['bids'][0]['price']
            return float(price)  # Return price as a float
        except KeyError as e:
           print(f"KeyError: {e}")
           return 0
        except Exception as e:
           print(f"Error fetching price: {e}")
           self.server_msg['message'] = str(e)
           return 0

       
    def send_payment(self,recipient_account_id, amount: float, asset:Asset):
        payment_op = self.transaction.append_payment_op(destination=recipient_account_id, amount=str(amount), asset=asset).build()
        payment_op.sign(self.keypair)
        return self.server.submit_transaction(payment_op)
    

    def get_trades(self):
        return self.data_fetcher.get_trades(self.account_id)
    def manage_trustline(self, asset: Asset, limit: str, authorized: bool = True):
        trust_op = self.transaction.append_change_trust_op(asset=asset, limit=limit,source=self.account).build()
        trust_op.sign(self.keypair)
        return self.server.submit_transaction(trust_op)
    def get_transactions(self)->pd.DataFrame:
        transactions = self.server.transactions().for_account(self.account_id).limit(200).call()['_embedded']['records']

        tr=pd.DataFrame.from_dict(transactions)
        tr.to_csv('ledger_transactions.csv',index= False)
        return transactions
    
        
   
    def create_trust_op(self, asset: Asset, authorize: bool = True):
     """
    Creates a trustline for the specified asset and authorizes the trustline.

    Parameters:
    - asset: The asset for which the trustline is being created.
    - authorize: Whether to authorize the trustline (default is True).
    """
    
    # Ensure the trustor is the account creating the trustline
     trustor = self.account_id  # Your account ID for the trustor (this account)
    
    # Build the transaction
     trust_op = self.transaction.append_change_trust_op(
        asset=asset,  # Create the trustline
        source=trustor  # Trustor is the source account
     ).append_allow_trust_op(
        trustor=trustor,  # Trustor account (same account in this case)
        authorize=authorize,asset_code=asset.code  # Set authorization state (True or False)
       ,  # The asset to authorize
        source=self.account_id  # Source account for authorization
     ).build()
    
    # Sign the transaction with the keypair
     trust_op.sign(self.keypair)
    
    # Submit the transaction
     return self.server.submit_transaction(trust_op)
    