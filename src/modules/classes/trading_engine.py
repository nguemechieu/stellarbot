import logging
import random
import time
import numpy as np
import pandas as pd
import requests
from stellar_sdk import Asset, Server, Signer, TransactionBuilder, Keypair, Network
import re
from modules.classes.data_fetcher import DataFetcher

class TradingsEngine:
    def __init__(self, server: Server,account_id:str, keypair: Keypair, account, controller, server_msg):
        super().__init__()

        self.controller = controller  # Controller allows us to connect to the server and access hidden functions or parameters
        self.server = server
        self.keypair = keypair
        self.account = account
        self.account_id=account_id
        self.logger = logging.getLogger(__name__)
        self.server_msg = server_msg
        self.base_asset = Asset.native()
        self.counter_asset = Asset('USDC', issuer='GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN')
        
        self.amount = 10
        self.price = 0.89
        self.offer_id = random.randint(0, 1000000)
        self.transaction_builder = TransactionBuilder(self.account, network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE)
        self.transaction_builder.add_text_memo(memo_text='StellarBot')

        # Timeframe and order book settings
        self.current_time = int(time.time())
        self.timeframe_selected = '1h'
        self.timeframe_list = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
        self.timeframe = int(self.timeframe_list.index(self.timeframe_selected) * 60000)
        self.start_time =  0
        self.end_time = self.start_time + (3 * 3600000)  # 3 hours later
        self.resolution = 3600000  # 1 hour
        self.order_book = []  # List of order book entries
        self.last_price = 0  # Last price fetched from the Stellar network
        self.trade_signal = 0

        # Fetch assets using data fetcher
        self.data_fetcher = DataFetcher(self.server)
        self.assets = self.data_fetcher.get_assets()

        self.logger.info("Trading Engine initialized")
        self.server_msg['message'] = 'Trading Engine initialized'

    def process_order_book(self):
        """Process the order book and calculate the trade signal."""
        self.logger.info("Processing order book")
        # Fetch the order book from the Stellar network
        order_books = self.server.orderbook(self.base_asset, self.counter_asset).call().items()
        print( "Order book", order_books)
        
        self.last_price = self.data_fetcher.get_current_price(self.base_asset.code, self.counter_asset.code)
        if 'bids' in order_books and 'asks' in order_books:

            self._extracted_from_process_order_book_9(order_books)
        else:
            self.logger.warning('Order book is empty')
            self.server_msg['message'] = 'Order book is empty'

    # TODO Rename this here and in `process_order_book`
    def _extracted_from_process_order_book_9(self, order_books):
        # Parse the bids and asks
        self.order_book = {
            'bids': self.parse_order_data(order_books['bids']),
            'asks': self.parse_order_data(order_books['asks'])
        }

        # Calculate bid-ask spread
        bid_price = self.order_book['bids'][0]['price'] if self.order_book['bids'] else 0
        ask_price = self.order_book['asks'][0]['price'] if self.order_book['asks'] else 0
        spread = ask_price - bid_price

        # Generate a trade signal based on the spread
        self.trade_signal = 1 if spread > 0.005 else -1
        self.logger.info(f'Trade signal generated: {self.trade_signal}')
        self.server_msg['message'] = f'Trade signal generated: {self.trade_signal}'

    def parse_order_data(self, orders):
        """Parse the order data from Stellar and return structured bid/ask data."""
        parsed_orders = []
        for order in orders:
            price_ratio_str = order['price_r']
            price = float(order['price'])
            amount = float(order['amount'])
            # Ensure the amount is not zero
            if amount == 0:
                continue
            
            # Ensure the price is not zero
            if price == 0:
                continue
            
            # Ensure the price ratio is not zero
            if price_ratio_str == '0':
                continue
            if price_ratio_str == '1':
                continue
            if price_ratio_str == '0.0':
                continue
            if price_ratio_str == '1.0':
                continue

            # Extract n and d from the price ratio (price_r)
            n, d = self.extract_n_d(price_ratio_str)
            price_ratio = float(n/d) if d != 0 else price
            
            parsed_orders.append({
                'price_ratio': price_ratio,
                'price': price,
                'amount': amount
            })
        return parsed_orders

    def extract_n_d(self, price_ratio_str):
        """Extract numerator and denominator from the price_r string."""
        if match := re.search(r"\{'n': (\d+), 'd': (\d+)\}", price_ratio_str):
            numerator = int(match[1])
            denominator = int(match[2])
            return numerator, denominator
        return None, None


    #TO DO: implement
    def calculate_trade_signal(self):
        """Calculate the trade signal based on market data."""
        return 0
    def trade_if_required(self):
        """Execute trades if the trade signal requires action."""
        self.logger.info("Trading if required")
        if self.trade_signal == 1:
            self.buy_asset()
        elif self.trade_signal == -1:
            self.sell_asset()

    def buy_asset(self):
        """Buy an asset based on trade signals."""
        self.logger.info("Buying asset")
        self.transaction_builder.append_manage_buy_offer_op(
            buying=self.base_asset,
            selling=self.counter_asset,
            amount=str(self.amount),
            price=str(self.price),
            offer_id=self.offer_id
        )
        self.submit_transaction('Buy transaction submitted')
        self.server_msg['message'] = 'Buy transaction'
        self.offer_id += 1

    def sell_asset(self):
        """Sell an asset based on trade signals."""
        self.logger.info("Selling asset")
        self.transaction_builder.append_manage_sell_offer_op(
            buying=self.counter_asset,
            selling=self.base_asset,
            amount=str(self.amount),
            price=str(self.price),
            offer_id=self.offer_id
        )
        self.offer_id += 1

        self.submit_transaction('Sell transaction submitted')
        self.server_msg['message'] = 'Sell transaction'

    def submit_transaction(self, msg):
        """Submit the transaction and log the result."""
        transaction = self.transaction_builder.build()
        transaction.sign(self.keypair)
        self.server.submit_transaction(transaction)
        self.logger.info(msg)
        self.server_msg['message'] = msg

    def get_trading_signals(self, base_asset, counter_asset):
        """Get trading signals based on the market data."""
        current_prices = self.get_current_price(base_asset, counter_asset)
        if not current_prices:
            return 0
        
        data0=self.get_market_data(base_asset, counter_asset)
        print(data0)

        if data0 is not None:
            data = data0[-50:] 
            return 0 

        data=pd.DataFrame(data0, columns= [
            'close', 'high', 'low', 'open', 'volume'
        ])
        data['return'] = data['close'].pct_change()
        data['return_rolling_mean'] = data['return'].rolling(window=10).mean()
        data['return_rolling_std'] = data['return'].rolling(window=10).std()
        data['signal'] = np.where(
            data['return_rolling_mean'] < data['return_rolling_mean'].shift(1)
            & data['return_rolling_std'] > data['return_rolling_std'].shift(1),
            -1,
            np.where( 
                data['return_rolling_mean'] > data['return_rolling_mean'].shift(1)
                & data['return_rolling_std'] < data['return_rolling_std'].shift(1),
                1,
                np.where(
                    data['return_rolling_mean'] < data['return_rolling_mean'].shift(1)
                    & data['return_rolling_std'] > data['return_rolling_std'].shift(1),
                    -1,
                    0  # No change in mean or standard deviation
                )
            )  # No change in mean or standard deviation
        )
          
        return 0

    def get_current_price(self, base_asset, counter_asset):
        """Fetch the current price from the Stellar order book."""
        try:
            orderbook = self.server.orderbook(base_asset, counter_asset).call()
            if 'bids' not in orderbook or len(orderbook['bids']) <= 0:
                return None  # No bids available
            return float(orderbook['bids'][0]['price'])  # Return bid price as a float
        except (KeyError, ValueError) as e:
            return self._extracted_from_get_account_assets_9('Error fetching price: ', e)

    def get_market_data(self, base_asset, counter_asset):
        """Fetch market data from Stellar."""
        data= self.server.trade_aggregations(
            base=base_asset,
            counter=counter_asset,
            start_time=self.start_time,
            end_time=self.end_time,
            resolution=self.resolution
        )

        if data is None:
            print(
                f"No market data available for asset {base_asset} in orderbook {counter_asset}"
            )

            self.server_msg['info'] = (
                f"No market data available for asset {base_asset} in orderbook {counter_asset}"
            )

            return [] # No market data available
    
    def update_timeframe(self, timeframe_selected):
        """Update the timeframe and order book settings."""
        self.logger.info(f"Updating timeframe to {timeframe_selected}")
        self.timeframe_selected = timeframe_selected
        self.timeframe = int(self.timeframe_list.index(timeframe_selected) * 60000)
        self.start_time = self.current_time - (3 * 3600000)  # 3 hours ago
        self.end_time = self.current_time + (3 * 3600000)  # 3 hours later
        self.order_book = []  # Reset order book for new timeframe
    


    def get_offers(self):
        """Fetch all offers for a specific asset pair."""
        try:
            offers = self.server.offers().call()['_embedded']['records']
            return offers
        except (KeyError, ValueError) as e:
            return self._extracted_from_get_account_assets_9('Error fetching offers: ', e)
    
    def get_account_balance(self, account_id):
        """Fetch the balance of a specific account."""
        response = requests.get('https://horizon.stellar.org/accounts/' + account_id
                                )
        if response.status_code != 200:
            return self._extracted_from_get_account_assets_6(
                'Error fetching account balance: ', response
            )
        return response.json()['balances'][0]['balance']  # Return the first balance as a float, as Stellar only supports one asset per account
    


    def get_account_assets(self, account_id):
        """Fetch the assets of a specific Stellar account."""
        try:
            return self._extracted_from_get_account_assets_5(account_id)
        except Exception as e:
           self.logger.error(f"Error fetching account assets: {str(e)}")
           self.server_msg['message'] = f"Error fetching account assets: {str(e)}"
           return None

    # TODO Rename this here and in `get_account_assets`
    def _extracted_from_get_account_assets_5(self, account_id):
        # Send request to Stellar Horizon API to get account details
        url = f'https://horizon.stellar.org/accounts/{account_id}'
        response = requests.get(url)

        if response.status_code != 200:
            return self._extracted_from_get_account_assets_6(
                'Error fetching account assets: ', response
            )
        # Parse the JSON data from the response
        data = response.json()

        # Extract balances from the account data
        assets = []
        if 'balances' in data:
            for balance in data['balances']:
                asset_type = balance.get('asset_type', 'native')
                asset_code = balance.get('asset_code', 'XLM') if asset_type != 'native' else 'XLM'
                asset_issuer = balance.get('asset_issuer', 'Stellar Network') if asset_type != 'native' else 'Stellar Network'
                balance_amount = balance.get('balance', '0')

                # Append the asset details to the assets list
                assets.append({
                    'asset_code': asset_code,
                    'asset_issuer': asset_issuer,
                    'balance': balance_amount,
                    'asset_type': asset_type
                })

        # Log the success and return the extracted assets
        self.logger.info(f"Fetched {len(assets)} assets for account {account_id}")
        self.server_msg['info'] = f"Fetched {len(assets)} assets for account {account_id}"
        return assets

    # TODO Rename this here and in `get_account_balance` and `get_account_assets`
    def _extracted_from_get_account_assets_6(self, arg0, response):
        self.logger.error(f'{arg0}{response.status_code}')
        self.server_msg['message'] = f'{arg0}{response.status_code}'
        return None

    def get_account_transaction_history(self, account_id, limit=200):
        """Fetch the transaction history of a specific account."""
        try:
            transactions = self.server.transactions().for_account(account_id).limit(limit).call()['_embedded']['records']
            return transactions
        except (KeyError, ValueError) as e:
            return self._extracted_from_get_account_assets_9(
                'Error fetching account transaction history: ', e
            )
    
  

    # TODO Rename this here and in `get_current_price`, `get_offers`, `get_account_balance`, `get_account_transaction_history` and `get_account_assets`
    def _extracted_from_get_account_assets_9(self, arg0, e):
        self.logger.error(f"{arg0}{e}")
        self.server_msg['message'] = f"{arg0}{str(e)}"
        return None
        
    
    def execute_trading_strategy(self,time_frame):
        self.update_timeframe(time_frame)
        self.get_account_assets(self.account_id)
        self.get_offers()
        self.get_account_balance(self.account_id)
        self.get_account_transaction_history(self.account_id)
        self.calculate_trade_signal()
        self.trade_if_required()
    

    def send_payment(self,amount: float,asset:Asset,recipients_address):
        """Send a payment to a recipient."""
        transaction= self.transaction_builder.append_payment_op(recipients_address,asset,str(amount), self.account).build()

        try:
            transaction.sign(self.keypair)
            self.server.submit_transaction(transaction)
            self.logger.info(f"Payment of {amount} {asset} sent to {recipients_address}")
            self.server_msg['info'] = f"Payment of {amount} {asset} sent to {recipients_address}"
        except (requests.exceptions.HTTPError, ValueError) as e:
            self.logger.error(f"Error sending payment: {str(e)}")
            self.server_msg['message'] = f"Error sending payment: {str(e)}"