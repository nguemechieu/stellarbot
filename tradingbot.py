import logging
import threading
import time
import tkinter

import pandas as pd
import requests




class TradingBot(object):
    
    def __init__(self, controller):
        self.order_tickets = pd.DataFrame(columns=['order_id', 'symbol','price', 'quantity','create_time', 'type'])
        self.stellar_account_id = None
        self.stellar_account_secret = ""
        self.stellar_horizon_url = "https://horizon.stellar.org"
        self.base_url = "https://horizon.stellar.org"

        self.balance: float = 0.00
        self.account_id ="  "
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

        # Example account info
        self.account_info = {
                  '_links': {...}, } # The complete account info goes here

        self.controller = controller

        self.thread = threading.Thread(target=self.run)
        self.thread.start()

        self.logger.info('Starting trading bot')


   



    def run(self):

        self.stellar_account_id = "GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY"
        self.stellar_account_secret = ""


     

       

        while True:

            self.account_info = self.get_account_info(self.stellar_account_id)

# Create the DataFrame
            self.account_df = self.create_account_dataframe(self.account_info)
            print(self.account_df)
            self.logger.info('Trading bot running')

            assets = self.get_assets(asset_code="USDC",
                                      asset_issuer="centre.io")
            print(assets)
            trade_aggregations = self.get_trade_aggregations(
                base_asset_code="XLM",
                base_asset_issuer="issuer_address_here", 
                counter_asset_code="USDC",
                counter_asset_issuer="centre.io")
            print(trade_aggregations)

            for i in trade_aggregations:
                    
                    print(i)
              # if i["base_asset_code"] == 'BTC' and i["counter_asset_code"] == 'USDC':
                    self.logger.info('Trade aggregation:' + str(i))

                    self.order = {
                        "type": "sell",
                        "selling": {
                            "asset_type": "USDC",
                            "asset_code": "BTC",
                            "asset_issuer": "issuer_address_here",
                            "amount": "0.01",
                            "price": "0.01",
                            "stop_price": "0.023",
                             "take_profit": "0.026",
                        }
                    }

                    # ticket = self.order_send(order)

                    # if ticket != None:
                    #     self.order_tickets.append(ticket)

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
            'balance': float(balance.get('balance',0.0)),
            'limit': float(account_info['balances'][0]['limit']),
            
            'asset_type': balance['asset_type'],
            'asset_code': balance.get('asset_code', None),
            'asset_issuer': balance.get('asset_issuer', None)
        })

    # Create a pandas DataFrame
     dfs = pd.DataFrame({
        'Account ID': [account_id],
        'Sequence': [sequence],
        'Home Domain': [home_domain],
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

    # Input text text = "account info {'_links': {'self': {'href':
    # 'https://horizon.stellar.org/accounts/GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY'},
    # 'transactions': {'href':
    # 'https://horizon.stellar.org/accounts/GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY/transactions{
    # ?cursor,limit,order}', 'templated': True}, 'operations': {'href':
    # 'https://horizon.stellar.org/accounts/GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY/operations{
    # ?cursor,limit,order}', 'templated': True}, 'payments': {'href':
    # 'https://horizon.stellar.org/accounts/GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY/payments{
    # ?cursor,limit,order}', 'templated': True}, 'effects': {'href':
    # 'https://horizon.stellar.org/accounts/GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY/effects{?cursor,
    # limit,order}', 'templated': True}, 'offers': {'href':
    # 'https://horizon.stellar.org/accounts/GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY/offers{?cursor,
    # limit,order}', 'templated': True}, 'trades': {'href':
    # 'https://horizon.stellar.org/accounts/GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY/trades{?cursor,
    # limit,order}', 'templated': True}, 'data': {'href':
    # 'https://horizon.stellar.org/accounts/GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY/data/{key}',
    # 'templated': True}}, 'id': 'GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY', 'account_id':
    # 'GDIQN3BCIF52R5WDMTPWUSN7IM3ZNQYYRWEWR2I7QX7BQUTKYNU2ISDY', 'sequence': '99808404234570907', 'sequence_ledger':
    # 47931980, 'sequence_time': '1693670627', 'subentry_count': 42, 'inflation_destination':
    # 'GDCHDRSDOBRMSUDKRE2C4U4KDLNEATJPIHHR2ORFL5BSD56G4DQXL4VW', 'home_domain': 'lobstr.co', 'last_modified_ledger':
    # 47931980, 'last_modified_time': '2023-09-02T16:03:47Z', 'thresholds': {'low_threshold': 0, 'med_threshold': 0,
    # 'high_threshold': 0}, 'flags': {'auth_required': False, 'auth_revocable': False, 'auth_immutable': False,
    # 'auth_clawback_enabled': False}, 'balances': [{'balance': '0.0000018', 'limit': '922337203685.4775807',
    # 'buying_liabilities': '0.0000000', 'selling_liabilities': '0.0000000', 'last_modified_ledger': 25947399,
    # 'is_authorized': True, 'is_authorized_to_maintain_liabilities': True, 'asset_type': 'credit_alphanum4',
    # 'asset_code': 'ABDT', 'asset_issuer': 'GDZURZR6RZKIQVOWZFWPVAUBMLLBQGXP2K5E5G7PEOV75IYPDFA36WK4'}, {'balance':
    # '0.0000000', 'limit': '922337203685.4775807', 'buying_liabilities': '0.0000000', 'selling_liabilities':
    # '0.0000000', 'last_modified_ledger': 47892556, 'is_authorized': True, 'is_authorized_to_maintain_liabilities':
    # True, 'asset_type': 'credit_alphanum12', 'asset_code': 'aeETH', 'asset_issuer':
    # 'GALLBRBQHAPW5FOVXXHYWR6J4ZDAQ35BMSNADYGBW25VOUHUYRZM4XIL'}, {'balance': '0.0000000',
    # 'limit': '922337203685.4775807', 'buying_liabilities': '0.0000000', 'selling_liabilities': '0.0000000',
    # 'last_modified_ledger': 47892570, 'is_authorized': True, 'is_authorized_to_maintain_liabilities': True,
    # 'asset_type': 'credit_alphanum4', 'asset_code': 'AFR', 'asset_issuer':
    # 'GBX6YI45VU7WNAAKA3RBFDR3I3UKNFHTJPQ5F6KOOKSGYIAM4TRQN54W'}, {'balance': '0.3300000',
    # 'limit': '922337203685.4775807', 'buying_liabilities': '0.0000000', 'selling_liabilities': '0.0000000',
    # 'last_modified_ledger': 38747907, 'is_authorized': True, 'is_authorized_to_maintain_liabilities': True,
    # 'asset_type': 'credit_alphanum12', 'asset_code': 'Aluminium', 'asset_issuer':
    # 'GCOJ237XTC3HYQYQCUBJPNCPKGMMI4ODSBOWAY2MF2D7XFMBCM5CLNQY'}, {'balance': '0.0000000', 'limit': ' Define the
    # Horizon API base URL

    # Function to fetch account information
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
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return " Error:" + str(response.status_code) + " " + str(response.reason)

    # Function to fetch trade aggregations
    def get_trade_aggregations(self,
                               base_asset_type=None,
                               base_asset_code=None,
                               base_asset_issuer=None,
                               counter_asset_type=None,
                               counter_asset_code=None,
                               counter_asset_issuer=None, ):
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

    def login(self, user_id, secret_key):

        if user_id == "" or secret_key == "":
            tkinter.Message(text="Please enter your user_id and secret_key")
            return None

        account_info = self.get_account_info(user_id)

        if account_info is not None:

            self.controller.show_frame(frame="Home")

            return account_info



        else:
            return None

        pass
