import logging

import requests
from stellar_sdk import Server, Asset


class DataFetcher:
    """
    A class responsible for fetching various data from the Stellar network including market data, 
    transaction history, account balances, offers, effects, and more. It uses the Stellar SDK and 
    the Horizon API to retrieve the information.
    """

    def __init__(self, server: Server):
        """
        Initializes the DataFetcher with a Stellar server connection and a logger.

        Parameters:
        server (Server): An instance of Stella's Server object to interact with Horizon.
        """
        self.server = server
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.info("DataFetcher initialized")

    def get_account_balance(self, account_id: str):
        """
        Retrieves the balance of the given Stellar account.

        Parameters:
        account_id (str): The Stellar account ID.

        Returns:
        str: The balance of the account in native currency (XLM).
        list: Empty list if there's an error.
        """
        try:
            account = self.server.accounts().account_id(account_id).call()
            self.logger.info(f"Account balance retrieved for account: {account_id}")
            return account['balances'][0]['balance']
        except Exception as e:
            self.logger.error(f"Error fetching account balance: {e}")
            return None

    def get_current_price(self, base_asset:Asset, counter_asset:Asset):
        """
        Retrieves the current price for a given asset pair based on the highest bid in the order book.

        Parameters:
        base_asset (Asset): The base asset (e.g., XLM).
        counter_asset (Asset): The counter asset (e.g., USD).

        Returns:
        float: The price of the base asset in terms of the counter asset.
        0: If there's an error or no bids in the order book.
        """
        try:
            orderbook = self.get_orderbook(base_asset, counter_asset)
            if not orderbook:
                self.logger.error("No order book available"+ f" for {base_asset} and {counter_asset}"+ str(orderbook))
                return 0  # No order book available
            if 'bids' not in orderbook or len(orderbook['bids']) <= 0:
                return None  # No bids available in the order book
            price = orderbook['bids'][0]['price']
            self.logger.info(f"Current price retrieved for {base_asset} and {counter_asset}: {price}")
            return float(price)  # Return price as a float
        except Exception as e:
            self.logger.error(f"Error fetching current price: {e}")
            return 0

    def get_assets(self):
        """
        Fetches all assets available on the Stellar network.

        Returns:
        dict: A JSON object containing asset data.
        list: Empty list if there's an error.
        """
        try:
            asset = self.server.assets().limit(200).call()

            self.logger.info("Assets retrieved")
            return asset
        except Exception as e:
            self.logger.error(f"Error fetching asset data: {e}")
            return None

    def get_accounts(self):

        response = requests.get(
            f"https://horizon.stellar.org/accounts/{self.server.accounts().account_id}"
        )
        if response.status_code != 200:
            logging.error( f"Error fetching account data: {response.status_code}")

            return []

        return response.json()

    def get_effects(self, account_id):
        return self.server.effects().for_account(account_id).limit(200).call()['_embedded']['records']

    def get_offers(self):
        offers=self.server.offers().limit(200).call()['_embedded']['records']  # Remove the first offer (since it's a dummy offer)
        print(f"Fetched offers for account: "+offers)

        return offers

    def get_orderbook(self, base_asset, counter_asset):
        return self.server.orderbook(base_asset, counter_asset).call()

    def get_ledger(self):
        return self.server.ledgers().limit(200).call()

    def get_operations(self, account_id):
        return self.server.operations().for_account(account_id).limit(200).call()['_embedded']['records']

    def get_trades(self, account_id):
        trades = self.server.trades().for_account(account_id).limit(200).call()['_embedded']['records']
        return trades

    def get_account_transaction_history(self, account_id, limit=200):
        """Fetch the transaction history of a specific account."""
        try:
            transactions = self.server.transactions().for_account(account_id).limit(limit).call()['_embedded'][
                'records']
            return transactions
        except (KeyError, ValueError) as e:
            self._extracted_from_get_account_assets_9(
                'Error fetching account transaction history: ', e
            )

    def extract_accounts_values(self, data) -> dict:

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

    def get_transaction_history(self, account_id):
        self.logger.info("Fetching transaction history")
        return self.get_transaction_history(account_id)

    def get_transaction(self, transaction_id):
        self.logger.info(f"Fetching transaction: {transaction_id}")
        return self.server.transactions().call()

    def get_account_assets(self, account_id):
        self.logger.info(f"Fetching account assets: {account_id}")
        return self.server.accounts().account_id(account_id).call()['assets']

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

    def get_market_data(self):
        self.logger.info("Fetching market data")
        url = "https://api.binance.us/api/v3/ticker/24hr"
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(
                f"Error fetching market data: {response.status_code}"
            )
            return []
        return response.json()

    def _extracted_from_get_account_assets_9(self, param, e):
        logging.error(f"{param}{e}")
        pass

    def _extracted_from_get_account_transactions_10(self, param, e):
        logging.error(f"{param}{e}")
        pass

    def get_portfolio_data(self):
        self.logger.info("Fetching portfolio data")
        portfolio_data = []
        accounts = self.server.accounts().call()["records"]
        for account in accounts["balances"]:
            account_id = account['id']
            account_data = self.extract_accounts_values(account)
            balance = float(account_data['balance'])
            if balance > 0:
                account_data['transactions'] = self.get_account_transactions(account_id)
                account_data['offers'] = self.get_account_offers(account_id)
                account_data['effects'] = self.get_account_effects(account_id)
                portfolio_data.append(account_data)
        return portfolio_data

    def get_trading_signals(self, param, param1):
        self.logger.info("Fetching trading signals")
        #
        # Implement trading signal logic here
        # Example:
        if self.get_current_price(param, param1) > self.get_previous_price(param, param1):
            return "BUY"
        elif self.get_current_price(param, param1) < self.get_previous_price(param, param1):
            return "SELL"
        else:
            return "HOLD"


    def get_previous_price(self, param, param1):

        return self.get_current_price(param,
                                      param1) - 0.01  # Assuming a 1% price decrease for previous price calculation
