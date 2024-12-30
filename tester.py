import logging
import threading
from datetime import datetime

import pandas as pd
import requests
import json

from adodbapi.process_connect_string import process
from hypothesis.extra.pandas import columns
from stellar_sdk import Keypair, Asset


class StellarClient:
    BASE_URL = "https://horizon.stellar.org"

    def __init__(self, account_id, secret_key):
        self.account = None
        self.order = "desc"
        self.session = requests.Session()
        self.orders = None
        self.transaction_history = None
        self.trades = None
        self.balances = None
        self.assets = None
        self.order_book = None
        self.transaction = None
        self.payments = []

        self.account_id = account_id
        self.secret_key = secret_key
        self.logger = logging.getLogger(__name__)

        if not self.validate_account_id():
            raise ValueError("Invalid Stellar Network Account ID")

        if not self.validate_secret_key():
            raise ValueError("Invalid Stellar Network Secret Key")

        self.server_msg = {'message': '', 'status': '', 'last_updated': '', 'data': {},
                           'assets': [], 'balances': [], 'trades': [], 'orders': [],
                           'order_book': {}, 'transaction_history': [], 'info': 'Stellar Client initialized.',
                           'transaction': {}, 'payments': [], 'error': ''}
        self.server_thread = threading.Thread(target=self.fetch_data, daemon=True)

        self.market_data = self.fetch_data()

    def start(self):
        """Starts the Stellar Client in a background thread for continuous data fetching."""
        self.server_thread.start()
        self.server_msg['status'] = 'RUNNING'
        self.server_msg['info'] = 'Trading started.'
        self.logger.info("StellarBot started.")

    def stop(self):
        """Stops the Stellar Client."""
        if self.server_thread.is_alive():
            self.server_thread.join()
            self.server_msg['status'] = 'STOPPED'
            self.server_msg['info'] = 'Trading stopped.'
            self.logger.info("StellarBot stopped.")
        else:
            self.logger.info("StellarBot is already stopped.")
            self.server_msg['info'] = 'Trading already stopped.'

    def get_market_data(self):
        """Fetches all market data from the Stellar Horizon API."""
        url = f"{self.BASE_URL}/"
        response = self.session.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch market data: {response.status_code} - {response.text}")


    def print_market_data(self):
        """Fetches and prints market data from the Stellar Horizon API."""
        try:
            market_data = self.get_market_data()
            self.logger.info(json.dumps(market_data, indent=4))
        except Exception as e:
            self.logger.error(f"Error: {e}")
            self.server_msg['error'] = f"Error fetching market data: {str(e)}"

    def validate_account_id(self):
        """Validates the provided account ID."""
        try:
            Keypair.from_public_key(self.account_id)
            return True
        except Exception:
            return False

    def validate_secret_key(self):
        """Validates the provided secret key."""
        try:
            Keypair.from_secret(self.secret_key)
            return True
        except Exception:
            return False

    def fetch_data(self):
        """Fetches all required data for the Stellar client."""
        self.server_msg['last_updated'] = str(datetime.now())
        self.logger.info("Fetching data...")
        self.logger.info("Fetching assets...")

        self.assets = pd.DataFrame(self.get_account_assets())
        self.assets.columns = ['asset_type', 'asset_code', 'asset_issuer', 'balance']
        self.assets.dropna(inplace=True)
        self.assets.to_csv('stellar_assets.csv', index=False)
        self.logger.info("Fetching account info...")

        self.account = pd.DataFrame(self.get_account_info())
        self.account.columns = ['account_id', 'sequence', 'sub_entry_count', 'thresholds', 'home_domain', 'flags', 'balances']
        self.account.dropna(inplace=True)
        self.account.to_csv('stellar_account.csv', index=False)

        self.logger.info("Fetching balances...")

        self.balances =  self.account["balances"]
        self.balances = self.balances.apply(pd.Series.explode)

        self.logger.info("Fetching trades...")
        self.trades = self.get_account_trades()
        self.trades=pd.DataFrame(self.trades)
        self.trades.columns = ['id', 'paging_token', 'source_account', 'type', 'created_at', 'fee_paid', 'fee_asset', 'amount', 'buying_asset', 'buying_asset_issuer', 'selling_asset', 'selling_asset_issuer']
        self.trades.dropna(inplace=True)
        self.trades.to_csv('stellar_trades.csv', index=False)
        self.logger.info("Fetching orders...")
        self.orders = self.get_account_orders()
        self.orders=pd.DataFrame(self.orders)
        self.orders.columns = ['id', 'paging_token','seller_id', 'buying_asset_type', 'buying_asset_code', 'buying_asset_issuer', 'selling_asset_type', 'selling_asset_code','selling_asset_issuer', 'price', 'amount', 'funded_at', 'flags']

        self.logger.info("Fetching order book...")
        self.order_book = self.get_order_book()
        self.order_book=pd.DataFrame(self.order_book)
        self.order_book.columns = ['bids', 'asks']
        self.order_book['bids'] = self.order_book['bids'].apply(pd.Series.explode)
        self.order_book['asks'] = self.order_book['asks'].apply(pd.Series.explode)
        self.order_book['bids'].columns = ['price', 'amount', 'funded_at', 'flags']
        self.order_book['asks'].columns = ['price', 'amount', 'funded_at', 'flags']
        self.order_book.to_csv('stellar_order_book.csv', index=False)

        self.logger.info("Fetching transaction history...")

        self.transaction_history = self.get_transaction_history()
        self.logger.info("Fetching transaction...")
        self.transaction = self.get_transaction()
        self.transaction=pd.DataFrame(self.transaction)
        self.transaction.columns = ['id', 'paging_token','source_account', 'type', 'created_at', 'fee_paid', 'fee_asset', 'amount', 'buying_asset', 'buying_asset_issuer','selling_asset', 'selling_asset_issuer']
        self.transaction.dropna(inplace=True)
        self.transaction.to_csv('stellar_transaction.csv', index=False)
        self.logger.info("Fetching payments...")

        self.payments = self.get_payments()

        return self.server_msg



    def get_account_assets(self):
        """Fetches the assets associated with the Stellar Network account."""
        endpoint = f"/accounts/{self.account_id}"
        ass=self.process_request(endpoint, params={"limit": 200})

        processed_assets = pd.DataFrame(columns(['asset_type', 'asset_code', 'asset_issuer', 'balance']))
        for k,v in ass:
            yield k, v
            for a in v['assets']:
                yield a['asset_type'], a['asset_code'], a['asset_issuer'], a['balance']
                processed_assets = processed_assets.append({'asset_type': a['asset_type'], 'asset_code': a['asset_code'], 'asset_issuer': a['asset_issuer'], 'balance': a['balance']}, ignore_index=True)

                self.logger.info(processed_assets)
            return processed_assets










    def get_account_offers(self):
        """Fetches the offers associated with the Stellar Network account."""
        endpoint = f"/accounts/{self.account_id}/offers"
        return self.process_request(endpoint, params={"limit": 200})
    def get_account_trades(self):
        """Fetches the trades associated with the Stellar Network account."""
        endpoint = f"/accounts/{self.account_id}/transactions"
        transactions = self.process_request(endpoint, params={"limit": 200})
        return [t for t in transactions if t[['type'] == 'payment']]


    def get_order_book(self, ):
        """Fetches the order book for a specific pair of assets."""
        base_asset, counter_asset = "XLM", "USDC"  # Example: XLM/USD
        endpoint = f"/order_book?selling_asset_type={base_asset}&buying_asset_type={counter_asset}"
        return self.process_request(
            endpoint,
            params={
                "limit": 200,
                "order": self.order,
            }
        )

    def get_transaction(self):
        """Fetches the transaction associated with the Stellar Network account."""
        endpoint = f"/accounts/{self.account_id}/transactions"
        transactions =[self.process_request(endpoint, params={"limit": 200})]
        return transactions[-1] if transactions else None

    def get_payments(self):
        """Fetches the payments associated with the Stellar Network account."""
        endpoint = f"/accounts/{self.account_id}/payments"
        return  self.process_request(endpoint, params={"limit": 200})


    def get_account_orders(self):
        """Fetches the orders associated with the Stellar Network account."""
        endpoint = f"/accounts/{self.account_id}/orders"
        return self.process_request(endpoint, params={"limit": 200})


    def get_transaction_history(self):
         """Fetches the transaction history associated with the Stellar Network account."""

         return  self.process_request("/transactions", params={"limit": 200})



    def get_assets(self, asset_code="XLM", asset_issuer=Asset.native().issuer, cursor=200, limit=200, order="asc"):
     all_assets = []
     params = {
        "asset_code": asset_code,
        "asset_issuer": asset_issuer,
        "cursor": cursor,
        "limit": limit,
        "order": order
    }

     # Remove any parameters that are None
     params = {key: value for key, value in params.items() if value is not None}

     try:
        # Loop through pages of data
        while True:
            response = self.process_request("/assets", params=params)
            response.raise_for_status()

            data = response.json()

            if "embedded" in data and "records" in data["embedded"]:
                all_assets.extend(data["embedded"]["records"])

            # Check if there is another page
            if "_links" in data and "next" in data["_links"]:
                cursor = data["_links"]["next"]["href"]
                params["cursor"] = cursor  # Update cursor for next page
            else:
                break  # No more pages to fetch

        # Convert the collected assets data into a DataFrame
        if all_assets:
            df = pd.DataFrame(all_assets)
            return df
        else:
            self.logger.warning("No assets found after pagination.")
            return pd.DataFrame()  # Return an empty DataFrame if no assets found

     except requests.exceptions.RequestException as e:
        self.logger.error(f"Error fetching asset data: {e}")
        self.server_msg['error'] = f"Error fetching asset data: {str(e)}"
        return pd.DataFrame()  # Return an empty DataFrame in case of an error


    def process_request(self, path, params):
        """
        Performs a GET request to the Stellar Horizon API with the provided parameters.

        Args:
        param (str): The endpoint to make the request to.
        params (dict): The parameters to include in the request.

        Returns:
            requests.Response: The response from the Stellar Horizon API.

        """
        url = f"{self.BASE_URL}/{path}"
        response = self.session.get(url, params=params)
        if response.status_code != 200:
            self.logger.error(f"Failed to fetch data: {response.status_code} - {response.text}")
            raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")
        return response

    def get_account_info(self):
        """Fetches the account information for the provided Stellar account."""
        endpoint = f"/accounts/{self.account_id}"
        return self.process_request(endpoint, params={})
        pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Replace these with actual Stellar account and secret key
    client = StellarClient("GA4CIZX3QJADGZZKI7HUS6WVHBNIX3EUNUW4MZUDPK5FIW2E6LLVVHGU", "SA32UPO2Y7Y5CBJNJ54BUFJLN7H62NV4K26WERPGSO2M6J4GZ7KD6XYH")

    # Fetch and print market data
    print("Fetching Market Data...")
    client.print_market_data()
