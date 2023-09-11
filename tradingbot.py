import json
import logging
import random
import threading
import time
import tkinter

import pandas as pd
import requests


from stellar_sdk import Account, Asset, Keypair,  Server, TransactionBuilder
import stellar_sdk

from learning import Learning




class TradingBot(object):
    
    def __init__(self, start_bot=False, account_id=None, account_secret=None,controller=None):   
        self.order_tickets = pd.DataFrame(columns=['order_id', 'symbol','price', 'quantity','create_time', 'type'])
        self.controller=controller
        self.stellar_horizon_url = "https://horizon.stellar.org"
        self.base_url ="https://horizon.stellar.org" 
        
        self.balance: float = 0.00
        
        self.home_domain = "https://horizon.stellar.org/"
        self.balances = []
        self.base_asset= Asset.native()
        self.counter_asset='USDC'
        self.counter_asset_issuer ="GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"

        self.account_secret =account_secret
        self.secret_key=self.account_secret
        self.account_id = account_id
        
        self.stellar_network=stellar_sdk.Network.PUBLIC_NETWORK_PASSPHRASE
        

        #SDYAPMSEK2N4LYRFROWHE4SK4LFXF2T2OMCU3BVDAJTEAYKHT4ESKOJ6

       
        
      
        self.server = Server(horizon_url=self.base_url)
        #self.keypair = Keypair.from_secret(self.secret_key)

        self.account=  self.server.load_account(account_id= self.account_id)

        self.asset_list=pd.DataFrame(self.get_asset_list(), columns=['asset_type', 'asset_code', 'asset_issuer'])
        self.account_df = pd.DataFrame(columns=['Account ID', 'Sequence', 'Home Domain', 'Balance', 'Limit', 'Asset Type', 'Asset Code', 'Asset Issuer'])
        
            
        current_time = int(time.time())  # Current time in Unix format
        valid_duration = 3600  # Valid for 1 hour (adjust as needed)
        self.min_time =  1631277600
        self.max_time = current_time + valid_duration
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
            tkinter.Message(controller, text='No internet connection')
       
            return


        
     

        self.thread = threading.Thread(target=self.run)

        if start_bot == True:
          
            self.thread.start()
            self.logger.info('Bot started  :time '+ time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        
           
                        
        elif start_bot== False:
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
        


        
        self.horizon_url = "https://horizon.stellar.org"
        self.source_keypair = Keypair.from_secret(secret=self.account_secret).public_key

# Source account address (replace with your actual source account address)
        self.source_account_address = self.source_keypair

# Load source account details, including the current sequence number
        response = requests.get(f"{self.horizon_url}/accounts/{self.source_account_address}")
        data = response.json()
#       data = {
#     "_links": {
#         "self": {"href": "https://horizon.stellar.org/accounts/GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA"},
#         "transactions": {"href": "https://horizon.stellar.org/accounts/GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA/transactions{?cursor,limit,order}", "templated": True},
#         "operations": {"href": "https://horizon.stellar.org/accounts/GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA/operations{?cursor,limit,order}", "templated": True},
#         "payments": {"href": "https://horizon.stellar.org/accounts/GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA/payments{?cursor,limit,order}", "templated": True},
#         "effects": {"href": "https://horizon.stellar.org/accounts/GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA/effects{?cursor,limit,order}", "templated": True},
#         "offers": {"href": "https://horizon.stellar.org/accounts/GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA/offers{?cursor,limit,order}", "templated": True},
#         "trades": {"href": "https://horizon.stellar.org/accounts/GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA/trades{?cursor,limit,order}", "templated": True},
#         "data": {"href": "https://horizon.stellar.org/accounts/GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA/data/{key}", "templated": True}
#     },
#     "id": "GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA",
#     "account_id": "GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA",
#     "sequence": "206391230320345096",
#     "sequence_ledger": 48056508,
#     "sequence_time": "1694394469",
#     "subentry_count": 5,
#     "home_domain": "stellarterm.com",
#     "last_modified_ledger": 48058517,
#     "last_modified_time": "2023-09-11T04:21:29Z",
#     "thresholds": {"low_threshold": 0, "med_threshold": 0, "high_threshold": 0},
#     "flags": {"auth_required": False, "auth_revocable": False, "auth_immutable": False, "auth_clawback_enabled": False},
#     "balances": [
#         {"balance": "0.0000000", "limit": "922337203685.4775807", "buying_liabilities": "0.0000000", "selling_liabilities": "0.0000000", "last_modified_ledger": 48054224, "is_authorized": True, "is_authorized_to_maintain_liabilities": True, "asset_type": "credit_alphanum4", "asset_code": "AQUA", "asset_issuer": "GBNZILSTVQZ4R7IKQDGHYGY2QXL5QOFJYQMXPKWRRM5PAV7Y4M67AQUA"},
#         {"balance": "509.7741220", "limit": "922337203685.4775807", "buying_liabilities": "0.0000000", "selling_liabilities": "0.0000000", "last_modified_ledger": 48056052, "is_authorized": True, "is_authorized_to_maintain_liabilities": True, "asset_type": "credit_alphanum12", "asset_code": "BTCLN", "asset_issuer": "GDPKQ2TSNJOFSEE7XSUXPWRP27H6GFGLWD7JCHNEYYWQVGFA543EVBVT"},
#         {"balance": "0.0000000", "limit": "922337203685.4775807", "buying_liabilities": "0.0000000", "selling_liabilities": "0.0000000", "last_modified_ledger": 48054231, "is_authorized": True, "is_authorized_to_maintain_liabilities": True, "asset_type": "credit_alphanum4", "asset_code": "LTC", "asset_issuer": "GCQVEST7KIWV3KOSNDDUJKEPZLBFWKM7DUS4TCLW2VNVPCBGTDRVTEIT"},
#         {"balance": "0.0000001", "limit": "0.0000001", "buying_liabilities": "0.0000000", "selling_liabilities": "0.0000000", "sponsor": "GA7PT6IPFVC4FGG273ZHGCNGG2O52F3B6CLVSI4SNIYOXLUNIOSFCK4F", "last_modified_ledger": 48056436, "is_authorized": True, "is_authorized_to_maintain_liabilities": True, "is_clawback_enabled": True, "asset_type": "credit_alphanum12", "asset_code": "SQL0001", "asset_issuer": "GDQMNGUDOSMCCN6MD52DPXX4ACECXVODFK2NQQGFXYLGXJFZ2LEEIY35"},
#         {"balance": "0.0000000", "limit": "922337203685.4775807", "buying_liabilities": "0.0000000", "selling_liabilities": "0.0000000", "last_modified_ledger": 48054222, "is_authorized": True, "is_authorized_to_maintain_liabilities": True, "asset_type": "credit_alphanum4", "asset_code": "USDC", "asset_issuer": "GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"},
#         {"balance": "106.9998392", "buying_liabilities": "0.0000000", "selling_liabilities": "0.0000000", "asset_type": "native"}
#     ],
#     "signers": [{"weight": 1, "key": "GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA", "type": "ed25519_public_key"}],
#     "data": {},
#     "num_sponsoring": 0,
#     "num_sponsored": 1,
#     "paging_token": "GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA"
# }


        # df=pd.DataFrame(data,['_links','account_id','sequence','sequence_ledger','sequence_time','subentry_count','home_domain','thresholds','flags','balances','signers','data','num_sponsoring','num_sponsored','paging_token'])
        # df.to_csv('account_info.csv',index=False)
       
        df2=pd.DataFrame(data['balances'],columns=['balance','limit','buying_liabilities','selling_liabilities','last_modified_ledger','is_authorized','is_authorized','is_authorized_to_maintain_liabilities','asset_type','asset_code','asset_issuer'])
        df2.to_csv('balances.csv',index=False)
        df3=pd.DataFrame(data['signers'],columns=['weight','key','type'])
        df3.to_csv('signers.csv',index=False)
        df4=pd.DataFrame(data['data'],columns=['key','value'])
        df4.to_csv('data.csv',index=False)
    
        df8=pd.DataFrame(data['_links'],columns=['self','transactions','operations','payments','effects','offers','trades','data'])
        df8.to_csv('_links.csv',index=False)
        
        sequence_number = data["sequence"]

        print( 'sequence_number :'+ str(sequence_number))



        self.sequence=sequence_number


        
      
                
        while True:
             self.logger.info('Trading bot running')


      
             self.send_money()
             
      
             self.assets= self.get_assets(

                asset_code= self.counter_asset,
                asset_issuer= self.counter_asset_issuer,limit=10
             )

             self.asset_df =pd.DataFrame(self.assets,['asset','asset_issuer'])

             print(str(self.asset_df))


             self.fee_statistics =self.server.fee_stats().limit(10).order(desc=True).call()
             self.fee_statistics_df=pd.DataFrame(self.fee_statistics,columns=['fee_asset','fee_asset_issuer','fee_amount','fee_asset_type'])
             self.fee_statistics_df.to_csv('fee_statistics.csv',index=True)
             
         
           

             




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

             self.orderbook = self.server.orderbook(selling=selling_asset, buying=buying_asset).limit(10).call()
           

             print( str(self.order_book))

             # Create a DataFrame from the bids and asks data
             df = pd.DataFrame(self.orderbook['bids'] + self.orderbook['asks'])

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

             signal=2#self.learn.get_signal(symbol= self.learn.symbol,datas=data)
             self.logger.info(f'Signal: {signal}')

        
             selling_asset = self.counter_asset

             


             # Define the order details
             sell_amount = "56.0"  # Amount of selling asset
             sell_price =  "7.2" # Price in terms of selling asset\stellar_sdk.price.Price, str, decimal.Decimal



             # Price in terms of buying asset

             #Create the sell operation
             self.sell_operation = stellar_sdk.manage_sell_offer.ManageSellOffer(selling=Asset.native(), buying=Asset(code="USDC",issuer=self.counter_asset_issuer),amount=sell_amount, price=sell_price,offer_id=random.randint(1, 100000000))
             #Create the buy operation
             self.buying_operation = stellar_sdk.manage_buy_offer.ManageBuyOffer(selling=Asset(code=self.counter_asset,issuer=self.counter_asset_issuer), buying=Asset.native(), amount=sell_amount, price=sell_price,      offer_id=random.randint(1, 100000000) )
             #Operations
             self.operations = [self.sell_operation, self.buying_operation]
             self.offers=self.server.offers().limit(10).order(desc=True).call()

             self.offers_df=pd.DataFrame(self.offers)
             self.offers_df.to_csv('offers.csv',index=True)

             print('offers :'+str(self.offers_df))

             


             self.operation2=self.server.operations().limit(10).order(desc=True).call()

             self.operation2_df=pd.DataFrame(self.operation2["_embedded"]['records'])
             self.operation2_df.to_csv('operation2.csv',index=True)
             print('operation2 :'+ (str(self.operation2_df.head())))
             print('operation2 :'+ (str(self.operation2_df.tail())))




             # Build the transaction







   

             if signal == 'buy' or signal == 1:
               self.logger.info(f'Buying {self.learn.quantity} {self.learn.symbol} at {self.learn.price}')
              # Build Buying  transaction
               # Set TimeBounds
               

               transaction = stellar_sdk.transaction_builder.TransactionBuilder(v1=True,
               source_account=self.account,
                 network_passphrase=self.stellar_network,
                 base_fee=100).append_operation(self.buying_operation).add_time_bounds(min_time=self.min_time, max_time=self.max_time).build()
               transaction.sign(signer=self.secret_key)
              # Submit the transaction to the Stellar network
              


               response =self.server.submit_transaction( transaction )

              # Check the transaction result
               if response !=None and response["successful"]:
                print("Buy order placed successfully!")
                print("Transaction hash:", response["hash"])
               else:
                print("Buy order failed. Error:", response["result_xdr"])



             elif signal =='sell' or signal == 2:
              

              # Build selling the transaction

              transaction = (stellar_sdk.transaction_builder.TransactionBuilder(v1=True,
               source_account=self.account,
                 network_passphrase=self.stellar_network,
                 base_fee=100).append_operation(self.buying_operation).add_time_bounds(min_time=self.min_time, max_time=self.max_time).build())
           
              
              transaction.sign(signer=self.secret_key)

              
              response = None#self.server.submit_transaction(transaction)

            #   #Check the transaction result
            #   if response["successful"]:
            #    print("Sell order placed successfully!")
            #    print("Transaction hash:", response["hash"])
            #   else:
            #    print("Sell order failed. Error:", response["result_xdr"])

            #    self.transaction_df=pd.DataFrame(transaction)
            #    self.transaction_df.to_csv('transaction.csv')
            #    print("transaction "+str(self.transaction_df))


               
             


                 

             

            







        
             self.trades=self.server.trades().limit(10).order(desc=True).call() 
             self.trade_df =pd.DataFrame(self.trades )

             print('trades :'+str(self.trade_df))
             self.trade_df.to_csv('trades.csv',index=True)



        
           

             self.claimable=self.server.claimable_balances().limit(10).order(desc=True).call()
             self.claimable_df=pd.DataFrame(self.claimable)
             print('claimable :'+str(self.claimable_df.tail()))

        
             self.claimable_df.to_csv('claimable.csv',index=True)

             
   


        
             time.sleep(10)

    def stop(self):
        self.logger.info('Stopping trading bot')

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
     df['Account ID']=[self.account_id]
     df['Sequence']=[self.sequence]
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


    def receive_money( self, address:str=None, amount:str="10", asset:str=Asset.native()):
       
        self.sender_public_key="GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA"
        # Build the transaction
        transaction = ( TransactionBuilder(source_account=self.account, network_passphrase="PUBLIC_NETWORK")
        .append_payment_op(destination=self.sender_public_key, amount=amount, asset=asset).
         
          add_time_bounds(min_time=self.min_time, max_time=self.max_time).build())
            
    def send_money( self, amount:str="10", asset:str=Asset.native(), address:str=None):
       
           self.receiver_public_key="GD37VDNE2C4ASOR5PZ7HKWCY6ESWTZ4ERXMMFE54I5G7WTUSGZNYXNXA"
           # Build the transaction
           transaction = ( TransactionBuilder(source_account=self.account, network_passphrase="PUBLIC_NETWORK")
             .append_payment_op(destination=self.receiver_public_key, amount=amount, asset=asset).
            
              add_time_bounds(min_time=self.min_time, max_time=self.max_time).build())

           # Sign the transaction
           transaction.sign(self.account_secret)

           # Submit the transaction envelope to the Stellar network
           try:
            response = self.server.submit_transaction(transaction)
            print(f"Transaction hash: {response['hash']}")
           except Exception as e:
             print(f"An error occurred: {e}")

    