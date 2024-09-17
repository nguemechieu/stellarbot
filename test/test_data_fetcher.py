import logging
from stellar_sdk import Server, Asset
from src.modules.classes.data_fetcher import DataFetcher

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize the Stellar server (mainnet)
server = Server(horizon_url="https://horizon.stellar.org")

# Initialize the DataFetcher with the server instance
fetcher = DataFetcher(server)

# Define the test account ID (replace with a valid Stellar account)
account_id = 'GBRPYHIL2CI3I5X2VZUGBBQUQKGIAO3DMW2MG7DJ4FPMIXFDCZMVV7O'

# Test the get_account_balance function
def test_get_account_balance():
    balance = fetcher.get_account_balance(account_id)
    print(f"Account Balance for {account_id}: {balance}")

# Test the get_current_price function
def test_get_current_price():
    base_asset = Asset.native()  # XLM
    counter_asset = Asset("USD", "GDUKMGUGDZQK6YH2U8O6XKGVFH7YUG4O3UJ3XCSUHACJSW73E4FDGS4R")  # USD asset
    price = fetcher.get_current_price(base_asset, counter_asset)
    print(f"Current Price (XLM/USD): {price}")

# Test the get_assets function
def test_get_assets():
    assets = fetcher.get_assets()
    print(f"Assets: {assets}")

# Test the get_offers function
def test_get_offers():
    offers = fetcher.get_offers(account_id)
    print(f"Offers for {account_id}: {offers}")

# Test the get_trades function
def test_get_trades():
    trades = fetcher.get_trades(account_id)
    print(f"Trades for {account_id}:")
    print(trades)

# Test the get_transaction_history function
def test_get_transaction_history():
    transactions = fetcher.get_transaction_history(account_id)
    print(f"Transaction History for {account_id}:")
    print(transactions)

# Running all tests
if __name__ == "__main__":
    test_get_account_balance()
    test_get_current_price()
    test_get_assets()
    test_get_offers()
    test_get_trades()
    test_get_transaction_history()
