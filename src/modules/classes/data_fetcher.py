import pandas as pd
import requests
import logging
from stellar_sdk import Asset, Server

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
        server (Server): An instance of Stellar's Server object to interact with Horizon.
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





    def get_current_price(self, base_asset, counter_asset):
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
            orderbook = self.server.orderbook(base_asset, counter_asset).call()
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
            return []
    
    def get_accounts(self, account_id: str):

        response= requests.get(
            f"https://horizon.stellar.org/accounts/{account_id}"
        )
        if response.status_code!=200:
            logging.error(
                f"Error fetching account data: {response.status_code}"

            )
            
            return []
        
        return response.json()
       

    def get_effects(self, account_id):
        
     return self.server.effects().for_account(account_id).limit(200).call()['_embedded']['records']
        

    def get_offers(self, account_id):
        return self.server.offers().for_account(account_id).limit(200).call()['_embedded']['records']
     
    
    def get_orderbook(self, base_asset, counter_asset):
       return self.server.orderbook(base_asset, counter_asset).call()
        
    
    def get_ledger(self):
        return self.server.ledgers().limit(200).call()
        
    
    def get_operations(self, account_id):
        return self.server.operations().for_account(account_id).limit(200).call()['_embedded']['records']
     
    
    def get_trades(self, account_id):
        trades = self.server.trades().for_account(account_id).limit(200).call()['_embedded']['records']
        return trades
    
   

    def extract_accounts_values(self,data):
      
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


