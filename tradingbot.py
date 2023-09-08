import logging
import threading
import time
import tkinter

import pandas as pd
import requests
from stellar_sdk import Asset, Server
from stellar_sdk import Keypair
import asyncio
from stellar_sdk import Account, Asset, Keypair, Network, TransactionBuilder
import json

from trade import Trade


class TradingBot(object):
    
    def __init__(self, controller):   
        self.order_tickets = pd.DataFrame(columns=['order_id', 'symbol','price', 'quantity','create_time', 'type'])
        self.account_secret = "SDYAPMSEK2N4LYRFROWHE4SK4LFXF2T2OMCU3BVDAJTEAYKHT4ESKOJ6"
        self.account_id='GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY'
        self.stellar_horizon_url = "https://horizon.stellar.org"
        self.base_url = "https://horizon.stellar.org"
        
        self.balance: float = 0.00
        self.sequence = 0
        self.home_domain = ""
        self.balances = []
    
        self.account_df = pd.DataFrame(columns=['Account ID', 'Sequence', 'Home Domain', 'Balance', 'Limit', 'Asset Type', 'Asset Code', 'Asset Issuer'])
        self.name = 'TradingBot'
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.addHandler(logging.FileHandler(self.name + '.log'))
        self.logger.info('TradingBot initialized')
      


  

        self.account_info = {
                  '_links': {...}, } # The complete account info goes here

        self.controller = controller

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

        self.connection = self.check_connection()


        self.logger.info('Starting trading bot')
    
    # Check if connection is established
     
    
    
    

    def order_book(self,json_data):
     data = json.loads(json_data)
     bids = data["bids"]
     asks = data["asks"]
    
     bid_prices = [float(bid["price"]) for bid in bids]
     bid_amounts = [float(bid["amount"]) for bid in bids]
    
     ask_prices = [float(ask["price"]) for ask in asks]
     ask_amounts = [float(ask["amount"]) for ask in asks]
    
     return {
        "bid_prices": bid_prices,
        "bid_amounts": bid_amounts,
        "ask_prices": ask_prices,
        "ask_amounts": ask_amounts
    }

    def check_connection(self):
        while True:
            try:
                response = requests.get(self.base_url, params={"addr":self.account_id})
                print(str(response))
                return True
            except:
                print("Connection not established")
                
                time.sleep(5)
                return False






   


    def run(self):

            
       response = requests.get(self.base_url, params={"addr":self.account_id})
       print(str(response))

       test_asset = Asset("TEST", self.account_id)
       is_native = test_asset.is_native()  # False
       print(is_native)
       

        # server = Server("https://horizon.stellar.org")
        # account_id = "GALAXYVOIDAOPZTDLHILAJQKCVVFMD4IKLXLSZV5YHO7VY74IWZILUTO"
        # raw_resp = server.accounts().account_id(account_id).call()
        # parsed_resp = AccountResponse.model_validate(raw_resp)
        # print(f"Account Sequence: {parsed_resp.sequence}")



       while True:
             root_keypair = Keypair.from_secret(self.account_secret)
             root_account = Account(account=root_keypair.public_key, sequence=1)
             transaction = (TransactionBuilder(
             source_account=root_account,
        # If you want to submit to pubnet, you need to change `network_passphrase` to `Network.PUBLIC_NETWORK_PASSPHRASE`
          network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
        base_fee=100   ).append_payment_op(  # add a payment operation to the transaction
        destination=self.account_id,
        asset=Asset.native(),
        amount=125.5 )
  .append_set_options_op(  # add a set options operation to the transaction
       home_domain="overcat.me"
   )
   .set_timeout(30)
   .build()) 
             













            #  server = Server(horizon_url="https://horizon-testnet.stellar.org")
            #  source = Keypair.from_secret(self.account_secret)
            #  print(str(source))
            #  # print(str(source.can_sign()))
            #  # `account` can also be a muxed account
            #  source_account = server.load_account(account_id=self.account_id)
            #  print(str(source_account))
  
  
 
            #  # get a list of transactions that occurred in ledger 1400
            #  transactions = server.transactions().for_ledger(1400).call()
            #  print(transactions)

        # get a list of transactions submitted by a particular account
            #  transactions = server.transactions().for_account(account_id=self.account_id).call()
            #  print("transactions" + str(transactions))
            #  print(f"Gets all payment operations associated with {self.account_id}.")
            #  payments_records = []
            #  payments_call_builder = (server.payments().for_account(self.account_id).order(desc=False).limit(10))  # limit can be set to a maximum of 200
            #  payments_records += payments_call_builder.call()["_embedded"]["records"]
            #  page_count = 0
            

             self.account_info = self.get_account_info(self.account_id)
            
             self.account_df = self.create_account_dataframe(self.account_info)
             print(self.account_df)
             self.logger.info('Trading bot running')

             assets = self.get_assets(asset_code="BTC",
                                      asset_issuer=None)
             print(assets)
             trade_aggregations = self.get_trade_aggregations( base_asset_code='BTC',counter_asset_code='XLM')
             print(trade_aggregations)

             self.base_asset= Asset.native()
             self.counter_asset='USDC'
             self.counter_asset_issuer ="GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"


             self.order_book= self.get_trade_aggregations(base_asset_code=Asset.native(),counter_asset_code=self.counter_asset,
                                                          counter_asset_issuer=self.counter_asset_issuer
                                                          
                                                          
                                                          )

            #  for i in trade_aggregations:
                    
            #         print(i)
            #   # if i["base_asset_code"] == 'BTC' and i["counter_asset_code"] == 'USDC':
            #         self.logger.info('Trade aggregation:' + str(i))

            #         self.order = {
            #             "type": "sell",
            #             "selling": {
            #                 "asset_type": "USDC",
            #                 "asset_code": "BTC",
            #                 "asset_issuer": "issuer_address_here",
            #                 "amount": "0.01",
            #                 "price": "0.01",
            #                 "stop_price": "0.023",
            #                  "take_profit": "0.026",
            #             }
            #         }

            #         # ticket = self.order_send(order)

            #         # if ticket != None:
            # #         #     self.order_tickets.append(ticket)
            # #  while page_records := payments_call_builder.next()["_embedded"]["records"]:
            # #   payments_records += page_records
            # #   print(f"Page {page_count} fetched")
            # #   print(f"data: {page_records}")
            # #   page_count += 1
            # #   print(f"Payments count: {len(payments_records)}")

             time.sleep(10)

    def stop(self):
        self.logger.info('Stopping trading bot')
        self.thread.join()

    def order_send(self, order):
        self.logger.info('Sending order:' + str(order))

    def cancel_order(self, ticket: int):
        self.logger.info('Cancelling order:' + str(ticket))

    def trailing_stop_loss(self, symbol: str, price: float, stop_loss: float):
        self.logger.info('Trailing stop loss:' + str(symbol) + '' + str(price) + '' + str(stop_loss))
        if price < stop_loss:
            return True
        else:
            return False
        

    def create_account_dataframe(self, account_info):
    # Extract account data
     account_id = account_info['account_id']
     sequence = account_info['sequence']
     home_domain = account_info['home_domain']


    # Extract balances
     balances = account_info['balances']

    # Create a list of dictionaries to store balance information
     balance_data = []
     for balance in balances:
        balance_data.append({
            'balance': float(balance.get('balance',None)),
            'limit': float(account_info['balances'][0]['limit']),
            
            'asset_type': balance['asset_type'],
            'asset_code': balance.get('asset_code', None),
            'asset_issuer': balance.get('asset_issuer', None)
        })

    # Add a row for each balance
     df =pd.DataFrame( columns=['Account ID', 'Sequence', 'Home Domain', 'Balance', 'Limit', 'Asset Type', 'Asset Code', 'Asset Issuer'])
     df['Account ID']=[account_id]
     df['Sequence']=[sequence]
     df['Home Domain']= [home_domain]
     df['Balance']= balance_data[0]['balance']
     df['Limit']=balance_data[0]['limit']
     df['Asset Type'] = balance_data[0]['asset_type']
     df['Asset Code'] = balance_data[0]['asset_code']
     return df



    def account_balance(self, account_id: str):

        for i in self.get_account_info(account_id)['balances']:

            if i['asset_type'] == 'native':
                self.balance = float(i['balance'])
                self.logger.info('Account balance:' + str(self.balance))
                return self.balance
        self.logger.info('Account balance:' + str(self.account_balance))
        return self.balance

    def account_update(self, balance):

        self.balance = balance
        self.logger.info('Account balance:' + str(self.balance))

    def get_account_info(self, account_id_):
        endpoint = f"{self.base_url}/accounts/{account_id_}"
        response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    # Function to fetch asset information
    def get_assets(self, asset_code=None, asset_issuer=None, cursor=None, limit=None, order=None):
        params = {
            "asset_code": asset_code,
            "asset_issuer": asset_issuer,
            "cursor": cursor,
            "limit": limit,
            "order": order}
        endpoint = f"{self.base_url}/assets"
        response = requests.get(url=endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return " Error:" + str(response.status_code) + " " + str(response.reason)

    # Function to fetch trade aggregations
    def get_trade_aggregations(self,
                               base_asset_type=None,
                               base_asset_code='XLM',
                               base_asset_issuer=None,
                               counter_asset_type= 0,
                               counter_asset_code='USDC',
                               counter_asset_issuer=None ):
        params = {
            "base_asset_type": base_asset_type,
            "base_asset_code": base_asset_code,
            "base_asset_issuer": base_asset_issuer,
            "counter_asset_type": counter_asset_type,
            "counter_asset_code": counter_asset_code,
            "counter_asset_issuer": counter_asset_issuer,
        }
        endpoint = f"{self.base_url}/trade_aggregations"
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return " Error:" + str(response.status_code) + " " + str(response.reason)
        


    def login(self, user_id:str=None, secret_key:str=None):

        if user_id == "" or secret_key == "":
            tkinter.Message(text="Please enter your user_id and secret_key")
            return None
        #
        
        if self.connected:
            account_info = self.get_account_info(user_id)

            if account_info is not None:
             self.account_id = user_id
             self.secret_key = secret_key
             self.account_info = account_info
             self.controller.show_frame(frame="Home")
             self.logger.info('Successfully logged in')
             self.run()

             return account_info
            else:
             return None
        else :
            return tkinter.Message(text='Please check your internet connection')

    