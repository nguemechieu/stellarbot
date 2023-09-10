import json
import logging
import random
import threading
import time
import tkinter

import pandas as pd
import requests


from stellar_sdk import Account, Asset,  Server
import stellar_sdk

from learning import Learning




class TradingBot(object):
    
    def __init__(self, start_bot=True, account_id=None, account_secret=None):   
        self.order_tickets = pd.DataFrame(columns=['order_id', 'symbol','price', 'quantity','create_time', 'type'])
        
        self.stellar_horizon_url = "https://horizon.stellar.org"
        self.base_url ="https://horizon.stellar.org" 
        self.counter_asset_issuer=""
        self.balance: float = 0.00
        self.sequence = 1
        self.home_domain = "https://horizon.stellar.org/"
        self.balances = []
        self.base_asset= Asset.native()
        self.counter_asset='USDC'
        self.counter_asset_issuer ="GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"

        self.account_secret =account_secret
        
        #SDYAPMSEK2N4LYRFROWHE4SK4LFXF2T2OMCU3BVDAJTEAYKHT4ESKOJ6
        #GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY
        
       
        self.account_id =account_id
        #GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY
       
        self.account = Account(account=self.account_id, sequence=self.sequence)

        self.asset_list=pd.DataFrame(self.get_asset_list(), columns=['asset_type', 'asset_code', 'asset_issuer'])
        
    
        self.account_df = pd.DataFrame(columns=['Account ID', 'Sequence', 'Home Domain', 'Balance', 'Limit', 'Asset Type', 'Asset Code', 'Asset Issuer'])
        
        self.name = 'TradingBot'
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.addHandler(logging.FileHandler(self.name + '.log'))
        self.logger.info('TradingBot initialized')
        self.thread =None
      


  

        self.account_info = { '_links': {...}, } # The complete account info goes here

    

        
        #check if internet connection is established
        self.connection = self.check_connection()

        if not self.connection:
            self.logger.info('No internet connection')
       
            return


        
     

        self.thread = threading.Thread(target=self.run)

        if start_bot == True:
          
            self.thread.start()
            self.logger.info('Bot started  :time '+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        
            while self.thread.is_alive():

                        
             if start_bot== False:
               self.logger.info('Bot stopped')
               self.thread.join(timeout=10)


    def get_asset_list(self):
        endpoint = f"{self.base_url}/assets"
        response = requests.get(endpoint)
        if response.status_code == 200:
            data= response.json()
            return data
        else:
            print(response.status_code)
            print(response.text)
            return None
    
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

    
    

    def order_book(self):
     
        endpoint = f"{self.base_url}/accounts/{self.account_id}/orders"
        response = requests.get(endpoint)
        if response.status_code == 200:
            data= response.json()
        else:
            print(response.status_code)
            print(response.text)
            return response.text
     
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
        self.learn=Learning()
        self.learn.symbol= 'XLM'
        self.learn.price= 100
        self.learn.quantity= 100

        self.logger.info('Starting trading bot')
        self.secret_key=self.account_secret
        server = Server(horizon_url=self.base_url)
        self.account=server.load_account(self.account_id)
                
        while True:
             self.logger.info('Trading bot running')
         
      
      
    

             self.fee_statistics =server.fee_stats().call()
             self.fee_statistics_df=pd.DataFrame(self.fee_statistics)
             self.fee_statistics_df.to_csv('fee_statistics.csv',index=False)
         
           

             




             # Create the first Asset instance (selling asset)
             selling_asset = stellar_sdk.Asset(
                 code=self.counter_asset,
                 issuer=self.counter_asset_issuer
             )  # Replace with the actual issuer's address

             # Create the second Asset instance (buying asset)
             buying_asset = stellar_sdk.Asset("XLM")  # Replace with the actual issuer's address
             # Create symbols
             self.symbol= selling_asset.code + '_' + buying_asset.code

             # Create asset list

             self.asset_list =pd.DataFrame( columns=['asset_type', 'asset_code', 'asset_issuer'])
             self.asset_list['asset_type']='selling'
             self.asset_list['asset_code']=selling_asset.code
             self.asset_list['asset_issuer']=selling_asset.issuer
             self.asset_list['asset_type']='buying'
             self.asset_list['asset_code']=buying_asset.code
             self.asset_list['asset_issuer']=buying_asset.issuer

             orderbook = server.orderbook(selling=selling_asset, buying=buying_asset).call()
           

             self.order_book_df=pd.DataFrame(orderbook,columns=[  'symbol','price', 'amount','open','low','high', 'close','volume','date'])
             self.order_book_df['symbol']=buying_asset.code+'_'+selling_asset.code
             self.order_book_df.to_csv('order_book.csv',index=False)

             # Create a DataFrame from the bids and asks data
             df = pd.DataFrame(orderbook['bids'] + orderbook['asks'])

             # Extract and work with the relevant columns
             df['price'] = df['price'].astype(float)
             df['amount'] = df['amount'].astype(float)
             

             self.learn.price = float(df['price'].iloc[-1])
             self.learn.quantity = float(df['amount'].iloc[-1])
             self.learn.candle_list = df['price'].tolist()
             self.learn.candle_list.append(self.learn.price)

             data=pd.DataFrame(columns=['price', 'amount','open','low','high', 'close','volume','date'])

            
             data['price']=df['price']
             data['amount']=df['amount']
            
             data['open']=0
             data['low']=0
             data['high']=0
             data['close']=0
             data['volume']=0
             data['date']=0

             signal=1#self.learn.get_signal(symbol= self.learn.symbol,datas=data)
             self.logger.info(f'Signal: {signal}')

        
             selling_asset = self.counter_asset

             


             # Define the order details
             sell_amount = "10.0"  # Amount of selling asset
             sell_price =  "7.1" # Price in terms of selling asset\stellar_sdk.price.Price, str, decimal.Decimal



             # Price in terms of buying asset

             #Create the sell operation
             self.sell_operation = stellar_sdk.manage_sell_offer.ManageSellOffer(selling=Asset(code=self.counter_asset,issuer=self.counter_asset_issuer), buying=Asset.native(),amount=sell_amount, price=sell_price,offer_id=random.randint(1, 100000000))
             #Create the buy operation
             self.buying_operation = stellar_sdk.manage_buy_offer.ManageBuyOffer(selling=Asset(code=self.counter_asset,issuer=self.counter_asset_issuer), buying=Asset.native(), amount=sell_amount, price=sell_price,      offer_id=random.randint(1, 100000000) )
             #Operations
             self.operations = [self.sell_operation, self.buying_operation]
             self.offers=server.offers().limit(10).order(desc=True).call()

             self.offers_df=pd.DataFrame(self.offers)
             self.offers_df.to_csv('offers.csv',index=False)

             


             self.operation2=server.operations().limit(10).order(desc=True).call()
             self.operation2_df=pd.DataFrame(self.operation2)
             self.operation2_df.to_csv('operation2.csv',index=False)




             # Build the transaction
             self.stellar_network= stellar_sdk.Network.PUBLIC_NETWORK_PASSPHRASE
           
             
             if signal == 'buy' or signal ==1:
               self.logger.info(f'Buying {self.learn.quantity} {self.learn.symbol} at {self.learn.price}')
              # Build Buying  transaction
               # Set TimeBounds
               current_time = int(time.time())  # Current time in Unix format
               valid_duration = 3600  # Valid for 1 hour (adjust as needed)
               min_time = current_time
               max_time = current_time + valid_duration

               transaction = stellar_sdk.transaction_builder.TransactionBuilder(v1=True,
               source_account=self.account,
                 network_passphrase=self.stellar_network,
                 base_fee=100).append_operation(self.buying_operation).add_time_bounds(min_time=min_time, max_time=max_time)
                 
                 
                # Build selling the transaction

               transaction.build().sign(signer=self.secret_key)
              # Submit the transaction to the Stellar network

               response =None# server.submit_transaction( transaction  )

              # Check the transaction result
               if response !=None and response["successful"]:
                print("Buy order placed successfully!")
                print("Transaction hash:", response["hash"])
               else:
                print("Buy order failed. Error:")#, response["result_xdr"])



             elif signal =='sell' or signal == 2:
              

              # Build selling the transaction
              transaction = stellar_sdk.transaction_builder.TransactionBuilder(v1=True,
              source_account=self.account, network_passphrase=self.stellar_network,base_fee=100).append_operation(self.sell_operation).add_time_bounds(min_time=current_time, max_time=current_time + valid_duration)

              transaction.build().sign(signer=self.secret_key)

              # Submit the transaction to the Stellar network
              response = server.submit_transaction(transaction)

              # Check the transaction result
              if response["successful"]:
               print("Sell order placed successfully!")
               print("Transaction hash:", response["hash"])
              else:
               print("Sell order failed. Error:", response["result_xdr"])

               self.transaction_df=pd.DataFrame(transaction)
               self.transaction_df.to_csv('transaction.csv')
               
             


                 

             

            



             # data = json.loads(json_data)

# # Extract specific information
# account_id = data["Trading bot running"]["Account ID"]
# asset_code = data["Trading bot running"]["Asset Code"]
# asset_type = data["Trading bot running"]["Asset Type"]

# bids = data["orderbook"]["bids"]
# asks = data["orderbook"]["asks"]
# base_asset_type = data["orderbook"]["base"]["asset_type"]
# counter_asset_type = data["orderbook"]["counter"]["asset_type"]

# trades = data["trades"]["_embedded"]["records"]

# # Now you can work with the extracted information as needed
# print(f"Account ID: {account_id}")
# print(f"Asset Code: {asset_code}")
# print(f"Asset Type: {asset_type}")
# print(f"Base Asset Type: {base_asset_type}")
# print(f"Counter Asset Type: {counter_asset_type}")

# # Print the first trade record as an example
# if trades:
#     first_trade = trades[0]
#     print("First Trade:")
#     print(f"Trade ID: {first_trade['id']}")
#     print(f"Trade Type: {first_trade['trade_type']}")
#     print(f"Base Amount: {first_trade['base_amount']}")
#     print(f"Counter Amount: {first_trade['counter_amount']}")
#     print(f"Price (n/d): {first_trade['price']['n']}/{first_trade['price']['d']}")
# else:
#     print("No trade records found.")









             self.trades=server.trades().limit(10).order(desc=True).call() 
             self.trade_df =pd.DataFrame(self.trades )
           

             self.claimable=server.claimable_balances().limit(10).order(desc=True).call()
             self.claimable_df=pd.DataFrame(self.claimable)
             
   


        
             time.sleep(10)

    def stop(self):
        self.logger.info('Stopping trading bot')
        self.trad

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
        endpoint = f"{self.base_url}/accounts/{self.account_id}/balances"
        response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.status_code)
            print(response.text)
            return None

        
        

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
                               base_asset_code=Asset.native(),
                               base_asset_issuer=None,
                               counter_asset_type= 0,
                               counter_asset_code='BTCLN',
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

    