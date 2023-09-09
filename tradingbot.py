import logging
import threading
import time
import tkinter

import pandas as pd
import requests

import asyncio
from stellar_sdk import Account, Asset, Keypair, Server
import json




class TradingBot(object):
    
    def __init__(self, controller):   
        self.order_tickets = pd.DataFrame(columns=['order_id', 'symbol','price', 'quantity','create_time', 'type'])
        
        self.stellar_horizon_url = "https://horizon-testnet.stellar.org"
        self.base_url ="https://horizon-testnet.stellar.org" #"https://horizon.stellar.org"
        self.counter_asset_issuer=""
        self.balance: float = 0.00
        self.sequence = 1
        self.home_domain = "https://horizon-testnet.stellar.org/"
        self.balances = []
        self.base_asset= Asset.native()
        self.counter_asset='USDC'
        self.counter_asset_issuer ="GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"

        self.account_secret ='SDYAPMSEK2N4LYRFROWHE4SK4LFXF2T2OMCU3BVDAJTEAYKHT4ESKOJ6'
        #GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY
        
        self.root_keypair = Keypair.from_secret(secret=self.account_secret)
        self.account_id = 'GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY'



        

        self.assets=pd.DataFrame(columns=['Asset Type', 'Asset Code', 'Asset Issuer'])
        
    
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
     
    
    def Check_account(self, account_id_: str=None) -> dict:
        endpoint = f"{self.base_url}/accounts/{account_id_}"
        response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.status_code)
            print(response.text)
            return None

    
    

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
     
        server = Server(horizon_url=self.base_url)
        account =Account(account=self.root_keypair.public_key,sequence= self.sequence)
        self.logger.info(f'Account: {account}')

        source_account = server.load_account(account_id=self.account_id)

        self.logger.info(f'Account: {source_account}')
        self.logger.info(f'Sequence: {source_account.sequence}')


        server.transactions().limit(10).order(desc=True).call()
        server.
           
                        
                          
        server.ledgers().limit(10).order(desc=True).call()
      
        self.assets=pd.DataFrame(self.get_assets(asset_code='USDC',asset_issuer=self.counter_asset_issuer),columns=['Asset Type', 'Asset Code', 'Asset Issuer'])

        
        self.logger.info(f'Assets: {self.assets}')

        
        


        
        trade_aggregations = self.get_trade_aggregations(base_asset_code=Asset.native(),counter_asset_code='BTC',
                                                          counter_asset_issuer=self.counter_asset_issuer)
                                                          
                
        while True:
            
           


             self.logger.info('Trading bot running')

       
             print(trade_aggregations)

        
                                                                                                   

             for i in trade_aggregations:
                    
               print(i)
            #    if i["base_asset_code"] == 'BTC' and i["counter_asset_code"] == 'USDC':
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

            #         ticket = self.order_send(self.order)

            #         if ticket != None:
            #           self.order_tickets.append(ticket)
                    # while page_records := payments_call_builder.next()["_embedded"]["records"]:
                    #  payments_records += page_records
                    #  print(f"Page {page_count} fetched")
                    #  print(f"data: {page_records}")
                    #  page_count += 1
                    #  print(f"Payments count: {len(payments_records)}")

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
     


    # Extract balances
     balances = account_info['balances']

    # Create a list of dictionaries to store balance information
     balance_data = []
     for balance in balances:
        balance_data.append({
            'balance': float(balance.get('balance',None)),
            'limit': 0,
            
            'asset_type': balance['asset_type'],
            'asset_code': balance.get('asset_code', None),
            'asset_issuer': balance.get('asset_issuer', None)
        })

    # Add a row for each balance
     df =pd.DataFrame( columns=['Account ID', 'Sequence', 'Home Domain', 'Balance', 'Limit', 'Asset Type', 'Asset Code', 'Asset Issuer'])
     df['Account ID']=[account_id]
     df['Sequence']=[sequence]
    # df['Home Domain'] = account_info['home_domain']
     df['Balance']= balance_data[0]['balance']
     df['Limit']=balance_data[0]['limit']
     df['Asset Type'] = balance_data[0]['asset_type']
     df['Asset Code'] = balance_data[0]['asset_code']
     return df
    



    def account_balance(self):

        
        return self.account_info[0]['balance']

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
            self.account_info = self.Check_account(account_id_=user_id)

            if self.account_info is not None:
             self.account_id = user_id
             self.secret_key = secret_key
           
             self.controller.show_frame(frame="Home")
             self.logger.info('Successfully logged in')
             self.connected = True

             return self.account_info
            else:
             return None
        else :
            return tkinter.Message(text='Please check your internet connection')

    