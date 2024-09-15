from datetime import datetime, timedelta
from threading import Thread
import time
import qrcode
import requests
from stellar_sdk import Account, Server, Keypair, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import NotFoundError
from PIL import Image
from io import BytesIO
import pandas as pd


class StellarClient:
    def __init__(self, db, controller, account_id: str, secret_key: str):
        self.db = db

        self.db.execute('CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY AUTOINCREMENT, asset_code TEXT, asset_issuer TEXT)')
        self.db.commit()
        self.db.execute('CREATE TABLE IF NOT EXISTS trading_pairs (id INTEGER PRIMARY KEY AUTOINCREMENT, base_asset_code TEXT, base_asset_issuer TEXT, counter_asset_code TEXT, counter_asset_issuer TEXT)')
        self.db.commit()

    
            # Fetch Candles data
        self.db.execute('CREATE TABLE IF NOT EXISTS ohlcv_data (id INTEGER PRIMARY KEY AUTOINCREMENT, account_id TEXT, open_time TEXT, close_time TEXT, low TEXT, high TEXT, close TEXT, volume TEXT)')
        self.db.commit()

        self.controller = controller
        self.account_id = account_id
        self.secret_key = secret_key

        self.server_msg = {'message': 'N/A', 'status': 'OFF', 'info': 'N/A'}
        self.assets = []
        self.transaction: TransactionBuilder = None
        self.order_book = None
        self.trade_signal=0
      
        self.horizon_url = "https://horizon.stellar.org"
        
      
        self.server = Server(horizon_url=self.horizon_url)


        if secret_key is None:
            print("Please provide a secret key")
            return

        self.keypair = Keypair.from_secret(secret=self.secret_key)
        self.account = self.server.load_account(account_id=self.keypair.public_key)
        self.accounts = self.get_accounts()
        self.accounts_df = pd.DataFrame(self.accounts)
        print(self.accounts_df)
        self.accounts_df.to_csv('ledger_accounts.csv', index=False)

        self.assets_df = pd.DataFrame()
        self.orders_df = pd.DataFrame()
        self.trades_df = pd.DataFrame()
        self.trade_signal=0
        self.buying = Asset('USDC', issuer='GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN')
        self.selling = Asset.native()
        self.amount = 10
        self.server_msg['message'] = 'Loading assets'
        self.assets = self.get_assets()
        self.assets_df = pd.DataFrame(self.assets)
        self.assets_df.to_csv('ledger_assets.csv', index=False)

        print("Loaded assets", self.assets)
        self.base_assets = Asset.native()
        self.counter_assets = Asset('USDC', issuer='GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN')

        # Loading orderbook
        self.order_book = self.server.orderbook(self.selling, self.buying).call()
        self.order_book_df = pd.DataFrame.from_dict(self.order_book, orient='index')
        self.order_book_df.to_csv('ledger_order_book.csv', index=False)

        self.transaction = TransactionBuilder(self.account, network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE)
        self.server_msg['message'] = 'In progress ...'
        print(f'StellarClient initialized with account: {self.account_id}')

        self.ledger_close_time = int(self.accounts_df['last_modified_ledger'].iloc[0])
        self.current_time = int(time.time())
        self.balances = self.accounts[0]['balances']

        self.valid_duration = 60 * self.ledger_close_time
        self.min_time = 1631277600  # Unix timestamp
        self.max_time = self.current_time + self.valid_duration
        self.timeframe_list = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
        self.timeframe_selected = '1h'
        self.timeframe = int(self.timeframe_list.index(self.timeframe_selected) * 60000)
        print('timeframe', self.timeframe)

        self.resolution = 60000  # 1 minute resolution
        self.start_time = self.current_time
        self.end_time = self.current_time + self.timeframe
        self.offset = 0

        # Generate QR code
        self.generate_qr_code(self.account_id)

        # for k,  pair in self.assets_df.items():
        #     print(f"Processing asset: {pair['asset_code']}")
          
        #     base_asset = Asset.native()
        #     counter_asset = Asset(code=pair['asset_code'], issuer=pair['asset_issuer'])

        #     self.trade_signal = self.get_trading_signals(base_asset, counter_asset)
        #     self.price = self.get_current_price(base_asset, counter_asset)

        #     self.aggregation = self.get_trade_aggregations(base_asset, counter_asset, self.start_time, self.end_time, self.resolution)
        #     self.aggregation_df = pd.DataFrame(self.aggregation)
        #     self.aggregation_df.to_csv('ledger_aggregation.csv', index=False)

        self.offers = self.server.offers().for_account(self.account_id).call()['_embedded']['records']
        self.offers_df = pd.DataFrame(self.offers)
        self.offers_df.to_csv('ledger_offers.csv', mode='a', header=False, index=False)

        self.trades = self.server.trades().for_account(self.account_id).call()['_embedded']['records']
        self.trades_df = pd.DataFrame(self.trades)
        self.trades_df.to_csv('ledger_trades.csv', mode='a', header=False, index=False)

        
        self.server_thread = Thread(target=self.run)
        self.server_thread.daemon = True

    def get_transaction_history(self):
        '''Get Account History'''
        self.server_msg['message'] = 'Getting Account History...'
        try:
            return self._extracted_from_get_transaction_history_5()
        except NotFoundError:
            self.server_msg['message'] = f'Account not found: {self.account_id}'
            return []

    def _extracted_from_get_transaction_history_5(self):
        history = self.server.transactions().for_account(self.account_id).call()['_embedded']['records']
        self.server_msg['message'] = 'Account History Retrieved'

        history_df = pd.DataFrame(history)
        self.server_msg['info'] = 'Account History retrieved successfully'
        return history_df

    def start(self):
        self.server_thread.start()
        self.server_msg['message'] = 'started'
        print(f"StellarClient started with account: {self.account_id}")
        self.server_msg['status'] = 'Live'

    def stop(self):
        self.server_thread.join()
        self.server_msg['message'] = 'StellarClient stopped!'
        self.server_msg['status'] = 'OFF'
        self.server_msg['info'] = 'StellarClient stopped successfully'
        print(f"StellarClient stopped with account: {self.account_id}")

    def run(self):
        while True:
            self.server_msg['message'] = f"StellarClient is connected with account: {self.account_id}"
            self.server_msg['status'] = 'Running...'

           
            
            self.get_transaction_history()

            self.server_msg['info'] = f"StellarClient fetched account OHLCV data for account: {self.account_id}"

            # Initiate a trading operation
            self.trade()

            time.sleep(1)
            break

    def get_account_balances(self, account_id):
        

        return self.accounts_df['balances']

  
# Function to fetch and save transaction data
    def fetch_transactions(self,account_id):
     
        filename="transactions.json"
        try:
            return self._extracted_from_fetch_transactions_6(account_id, filename)
        except requests.exceptions.RequestException as e:
           print(f"Error fetching transactions: {e}")
           return None

    # TODO Rename this here and in `fetch_transactions`
    def _extracted_from_fetch_transactions_6(self, account_id, filename):
        # API URL to fetch transactions for a given Stellar account
        url = f"https://horizon.stellar.org/accounts/{account_id}/transactions"

        # Fetching the data
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Ensure any HTTP errors are caught

        # Convert response to JSON
        transaction_data = response.json()

        # Saving the data to a JSON file
        with open(filename, 'w') as file:
            file.write(response.text)

        print(f"Transaction data saved to {filename}")
        return transaction_data  # Returning data for further use


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

    def trade(self):
        offer_id = 0
        amount = 100  # TODO: Implement logic to calculate the amount based on trading signals

        if self.trade_signal == 1:
            # Create Buying asset operation
            self.server_msg['message'] = f"StellarClient initiated buying operation on pair: {self.base_assets}/{self.counter_assets}"
            trans0 = self.transaction.append_manage_buy_offer_op(selling=self.base_assets, buying=self.counter_assets, price=self.price, amount=str(amount), offer_id=offer_id).build()
            trans0.sign(self.keypair)
            self.server.submit_transaction(trans0)
        elif self.trade_signal == -1:
            # Create Selling asset operation
            self.server_msg['message'] = f"StellarClient initiated selling operation on pair: {self.base_assets}/{self.counter_assets}"
            trans1 = self.transaction.append_manage_sell_offer_op(selling=self.counter_assets, buying=self.base_assets, price=self.price, amount=str(amount), offer_id=offer_id).build()
            trans1.sign(self.keypair)
            self.server.submit_transaction(trans1)

    def get_trade_aggregations(self, base_asset, counter_asset, start_time, end_time, resolution):
        return self.server.trade_aggregations(base_asset, counter_asset, start_time, end_time, resolution).call()['_embedded']['records']

    def generate_qr_code(self, input_string, file_path=None):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(input_string)
        qr.make(fit=True)

        qr_code_image = qr.make_image(fill="black", back_color="white")
        
        if file_path:
            qr_code_image.save(file_path)
        
        return qr_code_image
    
    def get_accounts(self):

     try:
        response =requests.get(url= f"https://horizon.stellar.org/accounts/{self.account_id}") 
    
        return [response.json()]
     except requests.exceptions.RequestException as e:
        print(f"Error fetching accounts: {e}")
        self.server_msg['message']= f"Error fetching accounts: {e}"
        return []

    def get_assets(self):
     try:
        # Setting timeout to 5 seconds
        response = requests.get(url="https://horizon.stellar.org/assets", timeout=5)
        response.raise_for_status()  # Raises HTTPError if the response was unsuccessful
        
        # Extracting data from the JSON response
        json_data = response.json()
        
        # Check if the response contains the assets key
        if 'records' in json_data:
            # Convert to DataFrame
            data = pd.DataFrame.from_dict(json_data)
            
            if not data.empty:
                # Assuming the asset_code and asset_issuer fields exist
                self.assets_df = [data.iloc[0]['asset_code'], data.iloc[0]['asset_issuer']]
                print('Data:', data)
                return self.assets_df
            else:
                print("No assets found.")
                return [Asset.native()]  # Return Stellar native asset if no assets are found
        else:
            print("Unexpected JSON structure.")
            return [Asset.native()]
    
     except requests.exceptions.RequestException as e:
        print(f"Error fetching assets: {e}")
        self.server_msg['message'] = f"Error fetching assets: {e}"
        return [Asset.native()]  # Returning the native asset in case of an error
    
    def get_trading_signals(self, base_asset, counter_asset):

        
     
        return 0
    
    def get_current_price(self, base_asset, counter_asset):
        
        return 0.0
    

    def get_effects_data(self):
        
        effets_data =self.server.effects()
        return effets_data.call()['_embedded']['records']

 