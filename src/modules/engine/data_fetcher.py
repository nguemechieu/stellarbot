import logging
import re
import time
from typing import Optional, List, Dict, Tuple

import pandas as pd
import requests
from numpy import empty
from stellar_sdk import Asset


def extract_n_d(price_ratio_str: str) -> Optional[Tuple[int, int]]:
    """Extract numerator and denominator from the price ratio string."""
    match = re.search(r"\{'n': (\d+), 'd': (\d+)}", price_ratio_str)
    if match:
        return int(match[1]), int(match[2])
    logging.warning(f"Failed to extract n and d from price ratio: {price_ratio_str}")
    return None


def parse_order_data(orders) -> List[Dict]:
    """Parse order data and return structured bid/ask information."""
    parsed_orders = []
    for order in orders:
        try:
            price = float(order.get("price", 0))
            amount = float(order.get("amount", 0))
            price_r_str = str(order.get("price_r", ""))

            if amount <= 0 or price <= 0:
                continue

            n_d = extract_n_d(price_r_str)
            price_ratio = float(n_d[0] / n_d[1]) if n_d else price

            parsed_orders.append({
                "price_r": price_ratio,
                "price": price,
                "amount": amount,
            })
        except Exception as e:
            logging.error(f"Error parsing order: {order}, Error: {e}")
    return parsed_orders


def extract_accounts_values(data) -> dict:

    result = {}
    for account in data:
        result['id'] = account['id']
        result['sequence'] = account['sequence']
        result['balance'] = account['balances'][0]['balance']
        result['asset_type'] = account['balances'][0]['asset_type']
        result['asset_code'] = account['balances'][0]['asset_code']
        result['asset_issuer'] = account['balances'][0]['asset_issuer']
        result['thresholds'] = account['thresholds']
        result['flags'] = account['flags']
        result['signers'] = account['signers']
        result['data'] = account['data']
        result['num_sponsoring'] = account['num_sponsoring']
        result['num_sponsored'] = account['num_sponsored']
        result['paging_token'] = account['paging_token']
        return result


class DataFetcher:
    """
    A class responsible for fetching various data from the Stellar network including market data, 
    transaction history, account balances, offers, effects, and more. It uses the Stellar SDK and 
    the Horizon API to retrieve the information.
    """

    def __init__(self, controller=None):
        """
    Initializes the DataFetcher with a Stellar server connection and a logger.

    Parameters:
    controller: The controller instance containing server and other configurations.
    """
        # Initialize attributes
        self.server_horizon_url = "https://horizon.stellar.org"
        self.order = "desc"
        self.endpoint =None
        self.session = requests.Session()
        self.balances_df = None
        self.buying:Asset
        self.selling: Asset
        self.account = None
        self.data_df = None
        self.balances = None
        self.last_request_time = 0
        self.max_request_frequency = 10  # Requests per minute
        self.offset = 0
        self.orderbook_limit = 100  # Maximum number of orders to retrieve per request

        self.limit = 200  # Maximum number of records to retrieve per request
        self.controller = controller
        self.account_id = controller.account_id

        self.trade_pairs: Dict[str, Tuple[Asset, Asset]] = {
            "USD": (Asset("zztcs", "GBIBNMZYLJ5P4B2YKFWWMJYEF4RP77HUGBZWQBRML74ZYEL5FKDQOOQI"), Asset.native())
          }
        #Set up server and logger
        self.server = self.controller.server
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Initializing DataFetcher...")
        self.assets = self.controller.assets
        self.trade_pairs=self.get_trade_pairs()
        self.logger.info("Trade pairs initialized.")


    def get_trade_pairs(self):
        """Fetch and process trade pairs from the Stellar network."""
        for asset in self.assets:
            if asset['code'] not in self.trade_pairs:
                self.trade_pairs[asset['code']] = (asset, self.assets[0])  # Assume base asset is the first one
                self.logger.info(f"Added trade pair: {asset['code']} -> {self.assets[0]['code']}")
            else:
                self.logger.info(f"Trade pair already exists: {asset['code']} -> {self.assets[0]['code']}")

        return self.trade_pairs


    def get_all_assets(self, cursor=None, max_page=10):
        """Fetch and process assets from the Stellar network with pagination."""
        try:
         # Throttling to ensure we don't exceed the request rate
         limit = min(max_page, 200)  # Stellar API limits to 100 assets per page

         # Prepare the request URL and parameters
         self.endpoint = "/assets"
         self.order = "asc"
         params = {

            'limit': limit,
            'order': self.order
        }

         #https://horizon.stellar.org/assets?cursor=&limit=200&order=asc

         # Send the GET request
         response = self.process_request(self.endpoint, params)
         self.last_request_time = time.time()  # Update the last request time

         if response is None or response.status_code != 200:
            self.logger.error(f"Error fetching assets: {response}")
            return pd.DataFrame()  # Return an empty DataFrame if request failed

         # Parse the JSON response
         data = response.json()
         if isinstance(data, dict) and '_embedded' in data and'records' in data['_embedded']:
             # Process the records and append them to the DataFrame
             assets_df = pd.json_normalize(data['_embedded']['records'])

             # Check if there is a next page (cursor)
             next_cursor = data['_links'].get('next', {}).get('href', None)

             # Recursively fetch next pages if max_page allows
             if next_cursor and max_page > 1:
                 next_cursor_param = next_cursor.split("cursor=")[-1]
                 next_assets_df = self.get_all_assets(cursor=next_cursor_param, max_page=max_page - 1)
                 assets_df = pd.concat([assets_df, next_assets_df], ignore_index=True)

             # Replace NaN with empty strings for better readability
             assets_df.fillna("", inplace=True)

             return assets_df

         else:
             self.logger.error(f"Invalid response from Stellar API: {data}")
             return pd.DataFrame()  # Return an empty DataFrame if the response is invalid


        except Exception as e:
         self.logger.error(f"Error retrieving assets: {e}")
         self.controller.server_msg['message'] = f"Error retrieving assets: {str(e)}"
         return pd.DataFrame()  # Return an empty DataFrame if request failed


    def get_account_balance(self):
        """
        Retrieves the balance of the given Stellar account.

        Parameters:
        account_id (str): The Stellar account ID.

        Returns:
        str: The balance of the account in native currency (XLM).
        list: Empty list if there's an error.
        """
        try:
            accounts = self.get_accounts()
            self.logger.info(f"Account balance retrieved for account: {self.account_id}")
            return accounts[0]['balance']
        except Exception as e:
            self.logger.error(f"Error fetching account balance: {e}")
            raise e



    def get_accounts(self):
        data_ = self.server.accounts().account_id(account_id=self.controller.account_id).for_signer(
            signer=self.controller.secret_key).call()
        self.logger.info(f"Account data retrieved for account: {self.account_id}")
        #Filter out offers with no price
        data_ = [record for record in data_['offers'] if record['price']]
        self.logger.info(f"Filtered offers: {len(data_)}")
        self.logger.info(f"Number of offers: {len(data_)}")
        self.controller.server_msg['message'] = f"Number of offers: {len(data_)} from account: {self.account_id}"
        return data_

    def get_effects(self, account_id):
        return self.server.effects().for_account(account_id).limit(200).call()['_embedded']['records']

    def get_offers(self):
        offers = self.server.offers().limit(200).call()['_embedded'][
            'records']  # Remove the first offer (since it's a test double offer)

        # Remove offers with no price
        offers = [offer for offer in offers if offer['price']]
        self.logger.info(f"Filtered offers: {len(offers)}")
        self.logger.info(f"Number of offers: {len(offers)}")
        self.controller.server_msg['message'] = f"Number of offers: {len(offers)}"
        return offers

    def get_ledger(self):
        return self.server.ledgers().limit(200).call()

    def get_operations(self):
        return self.server.operations().for_account(self.account_id).limit(200).call()['_embedded']['records']

    def get_trades(self):
        trades = self.server.trades().for_account(account_id=self.account_id).for_signer(
            signer=self.controller.secret_key).limit(200).call()['_embedded']['records']
        return trades

    def get_account_transaction_history(self):
        """Fetch the transaction history of a specific account."""
        try:
            transactions = \
            self.server.transactions().for_account(self.account_id).limit(self.limit).call()['_embedded'][
                'records']
            return transactions
        except (KeyError, ValueError) as e:
            self.logger.error(f"Error fetching transaction history: {e}")
            self.controller.server_msg['message'] = f"Error fetching transaction history: {str(e)}"
            return []

    def get_transaction_history(self, account_id):
        self.logger.info("Fetching transaction history")
        return self.get_transaction_history(account_id)

    def get_transaction(self, transaction_id):
        self.logger.info(f"Fetching transaction: {transaction_id}")
        return self.server.transactions().call()

    def get_account_transactions(self, account_id, limit=200):
        self.logger.info(f"Fetching account transactions: {account_id}")
        return self.server.transactions().for_account(account_id).limit(limit).call()['_embedded']['records']

    def get_account_offers(self, account_id, limit=200):
        self.logger.info(f"Fetching account offers: {account_id}")
        return self.server.offers().for_account(account_id).limit(limit).call()['_embedded']['records']

    def get_account_effects(self, account_id, limit=200):
        self.logger.info(f"Fetching account effects: {account_id}")
        return self.server.effects().for_account(account_id).limit(limit).call()['_embedded']['records']

    def get_forex_news(self):
        self.logger.info("Fetching forex news")
        url = "https://newsapi.org/v2/top-headlines"
        parms = {
            "q": "bitcoin",
            "apiKey": "401ac9bf2f34448e876ff0426715db8f",
            "sortBy": "popularity",
            "country": "us"
        }
        response = requests.get(url, parms)
        if response.status_code != 200:
            logging.error(
                f"Error fetching forex news: {response.status_code}"
            )
            return []
        return response.json()['articles']

    def get_portfolio_data(self):
        self.logger.info("Fetching portfolio data")
        portfolio_data = []
        accounts = self.server.accounts().call()["records"]
        for account in accounts["balances"]:
            account_id = account['id']
            account_data = extract_accounts_values(account)
            balance = float(account_data['balance'])
            if balance > 0:
                account_data['transactions'] = self.get_account_transactions(account_id)
                account_data['offers'] = self.get_account_offers(account_id)
                account_data['effects'] = self.get_account_effects(account_id)
                portfolio_data.append(account_data)
        return portfolio_data

    def get_recent_trades(self, limit=200):
        """
        Fetch recent trades for a given asset pair and return as a pandas DataFrame.
        """
        trades = self.server.trades().for_account(account_id=self.account_id).limit(limit).call()
        trades_records = trades["_embedded"]["records"]
        # Convert to pandas DataFrame
        df = pd.DataFrame(trades_records)
        return df


    def get_account_balances(self):
        """
    Fetch the balances of all accounts.

    Returns:
    list: List of balance objects.
    """
        try:
            accounts = (
                self.server.accounts()
                .account_id(account_id=self.controller.account_id)
                .for_signer(signer=self.controller.secret_key)
                .call()["_embedded"]["records"]
            )
            return accounts
        except Exception as e:
            self.logger.error(f"Error fetching account balances: {e}")
            self.controller.server_msg['error'] = f"Error fetching account balances: {e}"
            return []

    def get_all_stellar_candle_data(self):
        """
        Fetch all Stellar candle data.

        Returns:
        list: List of candle data.
        """
        try:
            candle_data = self.server.candles().all().call()
            return candle_data
        except Exception as e:
            self.logger.error(f"Error fetching Stellar candle data: {e}")
            return []

    def get_all_stellar_orderbook_data(self):
        """
        Fetch all Stellar orderbook data.

        Returns:
        list: List of orderbook data.
        """
        try:
            orderbook_data = self.server.order_book().for_account_id(self.account_id).call()
            return orderbook_data
        except Exception as e:
            self.logger.error(f"Error fetching Stellar orderbook data: {e}")
            self.controller.server_msg['error'] = f"Error fetching Stellar orderbook data: {e}"
            return []

    def get_all_stellar_trade_history_data(self):
        """
        Fetch all Stellar trade history data.

        Returns:
        list: List of trade history data.
        """
        try:
            trade_history_data = self.server.trades().for_account_id(self.account_id).call()
            return trade_history_data
        except Exception as e:
            self.logger.error(f"Error fetching Stellar trade history data: {e}")
            self.controller.server_msg['error'] = f"Error fetching Stellar trade history data: {e}"
            return []

    def get_order_book(self, buying: Asset, selling: Asset) -> pd.DataFrame:
     """
    Fetch and parse the order book from the Stellar network.
    Allows the user to switch between different types of orders (e.g., BTC/USDC, XLM/BTCLN).

    Args:
        buying (Asset): The asset being bought (e.g., XLM, BTC).
        selling (Asset): The asset being sold (e.g., USDC, BTCLN).

    Returns:
        pd.DataFrame: A DataFrame containing the parsed order book with columns for price, size, and side.

    Raises:
        Exception: If there is an error during the fetching or parsing process.
     """
     try:
        # Log the selected asset pair
        self.logger.info(f"Fetching order book for {buying.code}/{selling.code}")
        self.controller.server_msg["message"] = f"Fetching order book for {buying.code}/{selling.code}"

        # Fetch the order book data from the Stellar server
        order_book = self.server.orderbook(buying=buying, selling=selling).limit(200).call()

        # Parse the bids and asks from the response
        bids = pd.DataFrame(order_book.get("bids", []))  # Extract bids
        asks = pd.DataFrame(order_book.get("asks", []))  # Extract asks

        # Validate the parsed DataFrames and handle cases where data might be missing
        if bids.empty and asks.empty:
            self.logger.warning(f"No data found in order book for {buying.code}/{selling.code}.")
            self.controller.server_msg["message"] = f"No data found in order book for {buying.code}/{selling.code}."
            return pd.DataFrame(columns=["price", "size", "side"])  # Return an empty DataFrame

        # Assign side labels to bids and asks
        if not bids.empty:
            bids["side"] = "bid"
        if not asks.empty:
            asks["side"] = "ask"

        # Concatenate bids and asks into a single DataFrame
        order_book_df = pd.concat([bids, asks], axis=0, ignore_index=True)

        # Ensure all required columns are present and in the correct format
        expected_columns = {"price", "amount", "side"}
        if not expected_columns.issubset(order_book_df.columns):
            raise KeyError(f"Missing expected columns in order book: {expected_columns - set(order_book_df.columns)}")

        # Rename and format columns
        order_book_df.rename(columns={"amount": "size"}, inplace=True)
        order_book_df = order_book_df[["price", "size", "side"]]
        order_book_df = order_book_df.astype({"price": float, "size": float})

        # Log and return the parsed order book
        self.logger.info("Order book fetched and parsed successfully.")
        self.controller.server_msg["message"] = "Order book fetched and parsed successfully."
        self.controller.server_msg["order_book_bids"] = bids.to_dict(orient="records")
        self.controller.server_msg["order_book_asks"] = asks.to_dict(orient="records")

        return order_book_df

     except KeyError as ke:
        self.logger.error(f"Key error while processing order book: {ke}")
        self.controller.server_msg["message"] = f"Key error: {ke}"
        return pd.DataFrame(columns=["price", "size", "side"])  # Return an empty DataFrame

     except Exception as e:
        self.logger.error(f"Error fetching order book: {e}")
        self.controller.server_msg["message"] = f"Error fetching order book: {e}"
        return pd.DataFrame(columns=["price", "size", "side"])  # Return an empty DataFrame

    def get_market_data(self):
        """Fetch market data for all assets from the Stellar network."""
        self.logger.info("Fetching market data")

        # Fetch all assets from the Stellar network
        self.controller.server_msg["message"] = "Fetching market data"
        assets = self.assets

        if  assets is None or empty(assets):
            self.logger.warning("No assets found on the Stellar network.")
            self.controller.server_msg["message"] = "No assets found on the Stellar network."
            return []

        #  Create Trading pairs
        trading_pairs = [(asset, Asset.native()) for asset in assets] + [(asset, asset) for asset in assets]
        self.logger.info(f"Fetching market data for {trading_pairs} trading pairs.")
        self.controller.server_msg["trading_pairs"] = trading_pairs

        # Fetch order book for each trading pair
        market_data = []
        for trading_pair in trading_pairs:
            base_asset, counter_asset = trading_pair
            market_data.append(self.server.orderbook(buying=base_asset, selling=counter_asset).call())



        # Fetch market data for each trading pair
        market_data = []
        for trading_pair in trading_pairs:
            base_asset, counter_asset = trading_pair
            market_data.append(self.server.orderbook(buying=base_asset, selling=counter_asset).call())

        # Parse market data and create DataFrame
        market_data_df = pd.DataFrame()
        market_data_df["base_asset"] = [pair[0].code for pair in trading_pairs]
        market_data_df["counter_asset"] = [pair[1].code for pair in trading_pairs]
        market_data_df["bids"] = [pd.DataFrame(book["bids"], columns=["price", "size"]) for book in market_data]
        market_data_df["asks"] = [pd.DataFrame(book["asks"], columns=["price", "size"]) for book in market_data]
        market_data_df["base_asset_price"] = [book["bids"][0][0] if book["bids"] else None for book in market_data]
        market_data_df["counter_asset_price"] = [book["asks"][0][0] if book["asks"] else None for book in market_data]
        market_data_df["base_asset_volume"] = [book["bids"][0][1] if book["bids"] else 0 for book in market_data]
        market_data_df["counter_asset_volume"] = [book["asks"][0][1] if book["asks"] else 0 for book in market_data]
        market_data_df["price_change_percentage"] = [
            (book["bids"][0][0] - book["asks"][0][0]) / book["bids"][0][0] * 100 if book["bids"] and book["asks"] else None
            for book in market_data
        ]
        # Log and return the parsed market data
        self.logger.info("Market data fetched and parsed successfully.")
        self.controller.server_msg["message"] = "Market data fetched and parsed successfully."
        self.controller.server_msg["market_data"] = market_data_df.to_dict(orient="records")

        return market_data_df




    def get_payment_history(self):

        # Fetch payment history
        payment_history = self.get_account_payment_history()
        return payment_history
        pass

    def get_account_payment_history(self):
        """
        Fetch the payment history for the account.

        Returns:
        list: A list of payment history records or an empty list in case of an error.
        """
        try:
            # Fetch payment history
            payment_history = self.server.payments().for_account(self.controller.account_id).call()["_embedded"][
                "records"]
            return payment_history
        except Exception as e:
            self.logger.error(f"Error fetching payment history: {e}")
            self.controller.server_msg["error"] = f"Error fetching payment history: {e}"
            return []

    def get_trade_aggregations(self, base_asset, counter_asset,
                               resolution: int = int(time.time() - 86400 * 7),  # 7 days ago
                               start_time: int = int(time.time()) - 86400 * 1,  # 1 day ago
                               end_time: int = int(time.time()) - 86400 * 7,  # 7 days ago
                               limit: int = 200,  # 200 records
                               offset: int = -5  # 0 records offset
                               ):

        try:
            trade_aggregations = self.server.trade_aggregations(base_asset, counter_asset, resolution=resolution,
                                                                start_time=start_time, end_time=end_time,
                                                                offset=offset, limit=limit).order(
                order="desc"
            ).limit(200).call()
            dat = pd.DataFrame(trade_aggregations)
            dat['price'] = dat['price'].astype(float)
            dat['base_volume'] = dat['base_volume'].astype(float)
            dat['counter_volume'] = dat['counter_volume'].astype(float)
            dat['open'] = dat['open'].astype(float)
            dat['high'] = dat['high'].astype(float)
            dat['low'] = dat['low'].astype(float)
            dat['close'] = dat['close'].astype(float)
            dat['time'] = pd.to_datetime(dat['time'], unit='s')
            dat.dropna(inplace=True)
            return dat
        except Exception as e:
            self.logger.error(f"Error fetching trade aggregations: {e}")
            self.controller.server_msg["error"] = f"Error fetching trade aggregations: {e}"
            return {}
    def process_request(self, path, params):
     """
    Performs a GET request to the Stellar Horizon API with the provided parameters.

    Args:
    param (str): The endpoint to make the request to.
    params (dict): The parameters to include in the request.

    Returns:
        requests.Response: The response from the Stellar Horizon API.

     Raises:
        Exception: If the request fails or returns an error status code.
        """
     url = f"{self.controller.server_horizon_url}/{path}"
     response = self.session.get(url, params=params)
     if response.status_code != 200:
        self.logger.error(f"Failed to fetch data: {response.status_code} - {response.text}")
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")
     return response
