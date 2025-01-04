import logging
import threading
import time
from datetime import datetime
from typing import List

import pandas as pd
import requests
import ta
from stellar_sdk import Server, TransactionBuilder, Network, Asset, Keypair

from src.modules.engine.learning import Learning
from src.modules.engine.time_frames import TimeFrame


class EventListener:
    """A simple event listener to notify observers about events."""

    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        """Subscribe a callback to listen for events."""
        self.subscribers.append(callback)

    def unsubscribe(self, callback):
        """Unsubscribe a callback from listening to events."""
        self.subscribers.remove(callback)

    def notify(self, event, data=None):
        """Notify all subscribed callbacks about an event."""
        for subscriber in self.subscribers:
            subscriber(event, data)


def calculate_indicator(ohlcv_data, indicator):
    """
    Calculate the specified indicator for the given OHLCV data.

  :param ohlcv_data: List of OHLCV data points.
  :param indicator: The indicator to calculate (e.g., "close", "high", "low", "volume").
  :return: The calculated indicator value.
   """
    indicator_values = [data[indicator] for data in ohlcv_data]



    if indicator == "close":
        return indicator_values[-1]
    elif indicator == "high":
        return max(indicator_values)
    elif indicator == "low":
        return min(indicator_values)
    elif indicator == "volume":
        return sum(data["volume"] for data in ohlcv_data)
    else:
        raise ValueError(f"Invalid indicator: {indicator}")


class SmartBot:
    def __init__(self, controller):

        self.running = False
        self.logger = self.setup_logger()
        self.lock=threading.Lock()

        self.controller = controller

        self.assets_info = {}
        self.best_ask = 0
        self.best_bid = 0
        self.trades_pairs_df = pd.DataFrame(columns=["base_asset", "counter_asset"])
        self.liquidity_pools_df = pd.DataFrame(
            columns=["base_asset", "counter_asset", "min_amount", "max_amount", "base_liquidity", "counter_liquidity"])
        self.fees_df = pd.DataFrame(columns=[
            "type", "fee_percent", "fee_fixed", "min_fee", "max_fee", "min_withdrawal_fee", "max_withdrawal_fee",
            "min_deposit_fee", "max_deposit_fee"
        ])
        self.transactions_df = pd.DataFrame(
            columns=["id", "created_at", "source_account", "fee_asset", "fee", "amount", "memo", "memo_type"])
        self.trades_df = pd.DataFrame(
            columns=["id", "created_at", "base_asset", "counter_asset", "price", "amount", "buying_asset_amount",
                     "selling_asset_amount"])
        self.claimable_balances_df = pd.DataFrame(columns=["asset", "balance", "available", "pending"])
        self.payments_df = pd.DataFrame(columns=["id", "created_at", "asset", "amount", "destination", "source"])
        self.effects_df = pd.DataFrame(
            columns=["id", "created_at", "type", "asset_type", "asset_code", "asset_issuer", "amount", "price",
                     "funded_account", "source_account"])
        self.operations_df = pd.DataFrame(
            columns=["id", "created_at", "type", "source_account", "funded_account", "amount", "fee_paid", "fee_asset",
                     "source_account_balance", "destination_account_balance"])
        self.ledger_operations_df = pd.DataFrame(
            columns=["id", "created_at", "type", "source_account", "funded_account", "amount", "fee_paid", "fee_asset",
                     "source_account_balance", "destination_account_balance"])
        self.effects_stats = []
        self.operations_stats = []
        self.ledger_operations_stats = []
        self.order_book = {}
        self.claimable_balances = {}
        self.assets ={}


        self.stop_loss = 100
        self.take_profit = 105
        self.account_info ={}
        self.fees = {}
        self.effects = {}
        self.last_request_time = 0
        self.max_requests_per_second = 2
        self.liquidity_pools = {}
        self.trades = {}
        self.offers = {}
        self.fees_stats ={}
        self.lock = threading.Lock()
        self.time_frame = int(TimeFrame.DAY.value)

        self.analyze_results = {}
        self.ohclv_data_ = ()


        self.selected_strategy = "FOREX NEWS"
        self.account_id = controller.account_id
        self.secret_key = controller.secret_key
        self.account_sequence = "0"
        self.balances = {}
        self.handler = None
        self.base_account = None
        self.base_account_keypair = Keypair.from_secret(self.secret_key)
        self.base_account_secret = self.secret_key

        self.channel_accounts = ()

        self.server_msg = controller.server_msg
        self.offers_df=pd.DataFrame(columns=["id", "selling_asset", "buying_asset", "price", "amount", "funded_account", "source_account"])
        self.pool_id = None
        self.horizon_url = "https://horizon.stellar.org"
        self.market_data = {}

        self.server = Server(self.horizon_url)
        self.account = self.server.load_account(self.account_id)
        self.trade_pairs = pd.DataFrame(columns=["base_asset", "counter_asset"])
        self.session = requests.Session()
        self.learning_rate = 0.01
        self.learn_to_trade = True
        self.settings = {}
        self.strategies = {

            "FOREX_NEWS": {
                "period": 20,
                "overbought_threshold": 80,
                "oversold_threshold": 20
            },
            "NEWS_SENTIMENT": {
                "sentiment_model": "sentiment_analysis_model"
            },
            "CUSTOM_INDICATOR": {
                "indicator_function": "custom_indicator_function",
                "period": 5,
                "overbought_threshold": 80,
                "oversold_threshold": 20
            },
            "STOCH": {
                "period": 14,
                "overbought_threshold": 80,
                "oversold_threshold": 20
            },

        }
        self.ai = Learning(self.controller)

        self.logger.info("Bot initialized")

        self.thread = threading.Thread(target=self.run)


        # Fetch claimable balances
        self.claimable_balances = self.server.claimable_balances().order(True).limit(200).call()["_embedded"]["records"]
        self.claimable_balances_df = pd.DataFrame(self.claimable_balances)

        # Fetch the trades
        self.trades = self.server.trades().for_account(self.account_id).order(True).limit(200).call()["_embedded"][
            "records"]
        self.trades_df = pd.DataFrame(self.trades)
        self.logger.info("trades: " + str(self.trades))

        # Fetch the position
        self.payments = self.server.payments().for_account(self.account_id).order(True).limit(200).call()["_embedded"][
            "records"]
        self.payments_df = pd.DataFrame(self.payments)

        # Fetch the transactions
        self.transactions = \
            self.server.transactions().for_account(self.account_id).order(True).limit(200).call()["_embedded"][
                "records"]
        self.transactions_df = pd.DataFrame(self.transactions)

        # Fetch the offers
        self.offers = self.server.offers().for_account(self.account_id).order(True).limit(200).call()["_embedded"][
            "records"]
        self.offers_df = pd.DataFrame(self.offers)
        self.effects = self.server.effects().for_account(self.account_id).order(True).limit(200).call()["_embedded"][
            "records"]
        self.effects_df = pd.DataFrame(self.effects)
        self.fees = self.server.fee_stats().order(True).limit(200).call()
        self.fees_df = pd.DataFrame(self.fees)

        # Fetch liquidity pools
        self.liquidity_pools = self.server.liquidity_pools().for_account(self.account_id).call()["_embedded"]["records"]
        self.liquidity_pools_df = pd.DataFrame(self.liquidity_pools)
        self.logger.info("liquidity_pools: " + str(self.liquidity_pools))
        self.interval_seconds = 60  # 60 seconds interval

        self.news_data=[]#self.get_news_data() or []

        # Event listener setup
        self.event_listener = EventListener()
        self.event_listener.subscribe(self.market_data)

    def extract_balances(self, account_info):
        """
        Extract balance attributes and values from a Stellar account.

        :param account_info: The account info fetched from Horizon (contains asset balances).
        :return: A list of dictionaries with asset_code, balance, and asset_issuer (if applicable).
        """
        balances = []

        # Ensure account_info contains the expected 'balances' field
        if "balances" in account_info:
            for balance in balances:
                # Extract relevant balance data for each asset
                asset_code = balance.get("asset_code", "native")  # Default to 'native' if not specified
                balance_value = balance.get("balance", "0")
                asset_issuer = balance.get("asset_issuer", None)  # Asset issuer is None for native assets

                # Add the extracted balance info to the list
                balances.append({
                    "asset_code": asset_code,
                    "balance": balance_value,
                    "asset_issuer": asset_issuer
                })
                self.balances = balances



        else:
            self.logger.error("No 'balances' field found in the account data")
            self.server_msg['error'] = "No 'balances' field found in the account data"
            self.logger.info(f"Balances: {balances}")

        return balances

    def get_liquidity_pools_by_id(self, liquidity_pool_id: str):
        """
        Fetch a specific liquidity pool by its ID.
        :param liquidity_pool_id: The ID of the liquidity pool.
        :return: The liquidity pool or None if not found.
        """
        try:
            endpoint = "/liquidity_pools"
            params = {
                "liquidity_pool_id": liquidity_pool_id
            }
            response = self.process_requests(endpoint, params=params)
            data = response.json()
            self.logger.info(f"Liquidity Pool: {data}")
            return data

        except Exception as e:
            self.logger.error(f"Error fetching liquidity pool: {e}")
            self.server_msg['error'] = f"Error fetching liquidity pool: {e}"
            return None

    def get_liquidity_pools_effects(self):
        """
        Fetch the effects of a liquidity pool.
        :return: List of effects.
        :rtype: List

        """
        try:
            endpoint = f"/liquidity_pools/{self.pool_id}/effects"
            params = {}
            response = self.process_requests(endpoint, params)
            data = response.json()
            self.logger.info(f"Effects: {data}")
            return data
        except Exception as e:
            self.logger.error(f"Error fetching liquidity pool effects: {e}")
            self.server_msg['error'] = f"Error fetching liquidity pool effects: {e}"
            return []

    def get_liquidity_pools_trades(self):
        """
            Fetch the trades of a liquidity pool.
            :return: List of trades.
            """
        try:
            endpoint = '/liquidity_pools/{self.pool_id}/trades'
            params = {

            }
            response = self.process_requests(endpoint, params)
            data = response.json()
            self.logger.info("Trades: {data}")
            return data

        except Exception as e:
            self.logger.error(f"Error fetching liquidity pool trades: {e}")
            self.server_msg['error'] = f"Error fetching liquidity pool trades: {e}"
            return []

    def get_liquidity_pools_transactions(self):
        """
        Fetch the transactions of a liquidity pool.
        :return: List of transactions.
        """
        try:
            endpoint = f'/liquidity_pools/{self.pool_id}/transactions'
            params = {

            }
            response = self.process_requests(endpoint, params)
            data = response.json()
            self.logger.info(f"Transactions: {data}")
            return data

        except Exception as e:
            self.logger.error(f"Error fetching liquidity pool transactions: {e}")
            self.server_msg['error'] = f"Error fetching liquidity pool transactions: {e}"
            return []

    def get_liquidity_pools_operations(self):
        """
        Fetch the operations of a liquidity pool.
        :return: List of operations.
        """
        try:
            endpoint = f'/liquidity_pools/{self.pool_id}/operations'
            params = {

            }
            response = self.process_requests(endpoint, params)
            data = response.json()
            self.logger.info(f"Operations: {data}")
            return data

        except Exception as e:
            self.logger.error(f"Error fetching liquidity pool operations: {e}")
            self.server_msg['error'] = f"Error fetching liquidity pool operations: {e}"
            return []

    def setup_logger(self):
        """Set up a logger for the bot."""
        self.logger = logging.getLogger("SmartBot")
        self.handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)
        return self.logger

    # List all Assets
    # GET
    # https://horizon.stellar.org/assets

    @property
    def fetch_trade_pairs(self):
        """
      Fetch all assets from the Stellar network and create trading pairs based on user account balances.
      :return: List of trading pairs (base_asset, quote_asset).
      """
        try:
            # Fetch assets from Stellar network
            account_info = self.server.assets().limit(200).order().call()

            if not account_info or 'records' not in account_info['_embedded']:
                self.logger.error("Account data is None or malformed.")
                self.server_msg['error'] = "Account data is None or malformed."
                return []
            self.account_info=data=account_info['_embedded']['records']

            # Create a dictionary of assets and their issuers from the fetched data
            assets = []
            for asset in data:

                if asset['asset_type'] != "native":  # Exclude XLM (native asset)

                    assets.append(Asset(asset['asset_code'], asset[
                        'asset_issuer']))  # Add the asset and its issuer to the list of trading pairs
                    self.logger.info(f'Asset found: {asset['asset_code']} - {asset['asset_issuer']} (user\'s balance)')

                    self.assets=assets

                # If an asset is not in the user's balance, skip it
            # self.logger.info(f"Skipping asset: {asset['asset_code']} - {asset['asset_issuer']} (not in user's balance)")

            if not assets:
                self.logger.info("No assets found .")
                self.server_msg['error'] = "No assets found in the user's account balance."

            # Fetch user balances and filter assets based on the user’s holdings
            user_assets = set()  # Set of assets the user holds
            # Fetch user's account balances'
            self.logger.info(f"Assets: {assets}")
            # Notify subscribers that market data is received
            self.event_listener.notify("market_data_received", assets)
            # Create trading pairs based on user assets
            trade_pairs = []
            for asset_code, asset_issuer in user_assets:
                # Base asset from fetched data
                quote_asset = Asset(asset_code, asset_issuer)
                # Base asset from the user's balance
                base_asset = self.fetch_asset_balance(asset_code)
                # Check if the base asset and quote asset are differently
                # Append the trade pair (base_asset, quote_asset)

                if base_asset.code != quote_asset.code:  # Check if the base asset and quote asset are different
                    # Append the trade pair (base_asset, quote_asset)
                    trade_pairs.append((base_asset, quote_asset))

                # Log the trading pair
                self.logger.info(f"Trading Pair: {base_asset} - {quote_asset}")

            # Return the list of trading pairs
            return trade_pairs
        except Exception as e:
            self.logger.error("Error fetching trade pairs: " + str(e))
            self.server_msg['error'] = "Error fetching trade pairs: {" + str(e) + "}"
            # Return a default trading pair if no assets found in the user's account balance
            return []

    def fetch_market_data(self, trading_pairs, resolution):
        market_data = {}
        ohclv_list = [] # List to store OHCLV data for all pairs

        if not trading_pairs:  # Check if trading_pairs is None or empty
            self.logger.info("No trading pairs provided.")
            self.server_msg['error'] = "No trading pairs provided."
            return market_data, ()

        try:
            for trade_pair in trading_pairs:
                base_asset, quote_asset = trade_pair[0], trade_pair[1]  # Extract base and quote assets

                # Skip pairs where base and quote assets are the same
                if base_asset.code == quote_asset.code and base_asset.issuer == quote_asset.issuer:
                    continue

                try:
                    # Fetch the order book for the trading pair
                    endpoint = "/order_book"
                    params = {
                        "selling_asset_type": quote_asset.type,
                        "selling_asset_code": quote_asset.code,
                        "selling_asset_issuer": quote_asset.issuer,
                        "buying_asset_type": base_asset.type,
                        "buying_asset_code": base_asset.code,
                        "buying_asset_issuer": base_asset.issuer,
                        "limit": 200  # Limit for order book entries
                    }

                    response = self.process_requests(endpoint, params=params)
                    order_book_data = response.json()

                    # Store the market data for the specific trading pair
                    pair_key = f"{base_asset.code}/{quote_asset.code}"
                    # Store the order book data for the specific trading pair in the market_data dictionary
                    self.logger.info(f"Order Book for {pair_key}: {order_book_data}")


                    # Log market data
                    self.logger.info(f"Market Data for {pair_key}: {order_book_data}")

                    # Create OHCLV data for this pair
                    ohclv = self.create_ohclv(
                        trade_pair=(base_asset, quote_asset),
                        offset_=0,
                        resolution=resolution,
                        start_time=0,
                        end_time=int(datetime.now().timestamp())
                    )
                    ohclv_list.append((pair_key, ohclv))
                    market_data[pair_key] = ohclv

                except Exception as pair_error:
                    self.logger.error(
                        f"Error processing trading pair {base_asset.code}/{quote_asset.code}: {pair_error}")
                    continue  # Skip to the next pair on error

            # Notify subscribers after processing all pairs
            self.event_listener.notify("market_data_received")

        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            self.server_msg['error'] = f"Error fetching market data: {str(e)}"

        return market_data, ohclv_list

    def on_transaction_created(self, event, data) -> None:
        """
        Callback function that is triggered when a transaction is created.
        :param event: The event that was triggered.
        :param data: The data associated with the event (transaction details).

        """
        if event == "transaction_created":
            self.logger.info(f"Transaction Created: {data}")
            self.on_transaction_executed_(event, data)

        else:
            self.logger.error(f"Unknown event: {event}")

    def on_market_data_received(self, event, data) -> None:
        """
        Callback function that is triggered when market data is received.

        :param event: The event that was triggered.
        :param data: The data associated with the event (market data).
        """

        if event == "market_data_received":
            self.analyze_market(data=data)

        else:
            self.logger.error(f"Unknown event: {event}")

    def on_transaction_executed(self, event, data):
        """
            Callback function that is triggered when a transaction is executed.
            :param event: The event that was triggered.
            :param data: The data associated with the event (transaction details).
            """
        if event == "transaction_executed":
            self.logger.info(f'Transaction Executed: {data}')
            self.on_transaction_created(event, data)

        else:
            self.logger.error(f"Unknown event: {event}")

    def analyze_market(self, data) -> None:
        """
     Analyze market data and decide whether to trade.
     :param data: The market data fetched from Horizon.
     :return: A decision to buy, sell, or hold.
      """

        try:
            # Convert data into DataFrame
            data_df = pd.DataFrame(data)

            # Check if bids and asks are lists and not empty
            if 'bids' in data_df.columns and 'asks' in data_df.columns:
                return

                # Extract the best bid (highest bid price)
            if data_df['bids'] and isinstance(data_df['bids'], list):
                self.best_bid = max(data_df['bids'], key=lambda x: float(x['price']))['price']
            # Extract the best ask (lowest ask price)
            if data_df['asks'] and isinstance(data_df['asks'], list):
                self.best_ask = min(data_df['asks'], key=lambda x: float(x['price']))['price']

            # Convert prices to float for comparison
            best_bid = float(self.best_bid) if self.best_bid else None
            best_ask = float(self.best_ask) if self.best_ask else None

            self.logger.info(f"Best bid: {best_bid}, Best ask: {best_ask}")

            # Trading logic
            trading_pairs = self.trade_pairs
            lot = 100  # This could be dynamically determined based on account balance

            # Buy a decision: If the best ask is below a threshold (buy price)
            if best_ask and best_ask < 0.1:  # threshold for buying
                self.logger.info(f"Buy decision: Ask price {best_ask}")
                # Check balance and execute trade
                self.server_msg['error'] = f"Insufficient balance for {trading_pairs[0]} {trading_pairs[1]}"
                self.execute_trade("buy", best_ask, amount=lot, trading_pairs=trading_pairs)

            # Sell decision: If the best bid is above the threshold (sell price)
            elif best_bid and best_bid > 0.2:  # threshold for selling
                self.logger.info(f"Sell decision: Bid price {best_bid}")
                # Check balance and execute trade
                self.server_msg['error'] = f"Insufficient balance for {trading_pairs[0]} {trading_pairs[1]}"
                self.execute_trade("sell", best_bid, amount=lot, trading_pairs=trading_pairs)

            else:
                self.logger.error("Invalid data format: Missing bids or asks.")
                self.server_msg['error'] = "Invalid data format: Missing bids or asks."

        except Exception as e:
            self.logger.error(f"Error analyzing market data: {e}")
            self.server_msg['error'] = f"Error executing trade: {e}"

    def execute_trade(self, action: str, price: float, amount: float, trading_pairs) -> None:
        """
        Execute a trade on the Stellar network.
        :param trading_pairs:
        :param action: The action to take ('buy' or 'sell').
        :param price: The price to trade at.
        :param amount: The amount to trade.
       """
        try:
            # Extract base and quote assets from a trading pair

            for trade_pair in trading_pairs:
                # Fetch account balance for quote asset (required for buy trades)
                quote_balance = self.get_balance(
                    asset_code=trade_pair[1].code,
                    asset_issuer=trade_pair[1].issuer
                )

                # Fetch account balance for base asset (required for sale trades)

                base_balance = self.get_balance(asset_code=trade_pair[0].code,
                                                asset_issuer=trade_pair[0].issuer)
                if action == "buy" and float(quote_balance) < amount * price:
                    self.logger.info(
                        f'Insufficient balance for {trade_pair.code}. Required: {amount * price}, Available: {quote_balance}')
                    self.server_msg["error"] = f"Insufficient balance for {trade_pair}."
                    return

                elif action == "sell" and float(base_balance) < amount * price:
                    self.logger.info(
                        f"Insufficient balance for {trade_pair[0].code}. Required: {amount}, Available: {base_balance}")
                    self.server_msg["error"] = f"Insufficient balance for {trade_pair[0]}."
                    return

                # Build the transaction
                tx_builder = TransactionBuilder(
                    source_account=self.account,
                    network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                    base_fee=100
                )
                quote_asset = trade_pair[1]
                base_asset = trade_pair[0]
                if quote_asset != base_asset:
                    if action == "buy":

                        tx_builder.append_manage_buy_offer_op(
                            selling=quote_asset,
                            buying=base_asset,
                            amount=str(amount),
                            price=str(price), offer_id=0,
                            source=self.account.account
                        )
                    elif action == "sell":
                        tx_builder.append_manage_sell_offer_op(
                            selling=base_asset,
                            buying=quote_asset,
                            amount=str(amount),
                            price=str(price),
                            offer_id=0,
                            source=self.account.account
                        )
                else:
                    self.logger.error("Invalid action:" + action)
                    self.server_msg["error"] = "Invalid action: " + action
                    return

                # Sign and submit the transaction
                transaction = tx_builder.build()
                transaction.sign(self.secret_key)
                response = self.server.submit_transaction(transaction)

                # Log and update server message
                self.logger.info(f"Trade executed successfully: {response}")
                self.server_msg["status"] = "SUCCESS"
                self.server_msg["message"] = f"Trade executed successfully: {response}"

        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            self.server_msg["error"] = f"Error executing trade: {e}"
            self.server_msg["message"] = f"Error executing trade: {e}"

    def stop(self):
        """
        Stop the trading bot.
        This method will stop the market data polling loop and gracefully disconnect from the Horizon server.
        """
        self.logger.info("Stopping Smart Trading Bot...")
        self.running = False
        self.thread.join()
        self.logger.info("Smart Trading Bot stopped.")
        self.server.close()
        self.logger.info("Stellar SDK disconnected.")
        self.server_msg["status"] = "STOPPED"
        self.server_msg["last_updated"] = time.time()
        self.server_msg["market_data"] = {}
        self.server_msg["balance"] = 0
        self.server_msg["base_account_id"] = self.account_id
        self.server_msg["pool_id"] = None
        self.server_msg["message"] =  "Stellar SDK disconnected. Smart Trading Bot stopped."

    def start(
            self):  # 2 seconds as a default interval between market checks.  # This should be adjusted based on the needs of your trading strategy.
        """
       Start the trading bot.
        This method will continuously check the market data and execute trades based on predefined conditions.
      """
        self.logger.info("Starting Smart Trading Bot...")
        self.running = True
        self.thread.daemon=True
        self.thread.name="StellarBot"
        self.logger.info("Stellar SDK started.")

        # Initialize server message structure
        self.server_msg = {
            "status": "RUNNING",
            "error": "NONE",
            "message": "Stellar SDK started.",
            "last_updated": time.time(),
            "market_data": {},
            "balance": 0,
            "base_account_id": self.account_id,
            "pool_id": None,
            "trading_pair": []
        }
        # Start the market data polling loop
        self.thread.start()
        self.run()

    def process_requests(self, endpoint, params):
        """
        Performs a GET request to the provided endpoint with the provided parameters.
        :param endpoint: The endpoint to make the request to.
        :param params: The parameters to include in the request.
        :return: The response from the API.
        """
        try:
            url = "https://horizon.stellar.org" + endpoint
            res = self.session.get(url, params=params)
            if res.status_code == 200:
                return res
            else:
                self.logger.error(f"Request failed: {res.status_code} - {res.text}")
                self.server_msg["error"] = f"Request failed: {res.status_code} - {res.text}"
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            self.server_msg["error"] = f"Request error: {e}"
            return None

    def get_balance(self, asset_code, asset_issuer):
        """
        Get the balance of a specific asset on the Stellar network.
        :param asset_code: The code of the asset.
        :param asset_issuer: The issuer of the asset.
        :return: The balance of the asset.
        """
        try:

            for balance in self.account_info["balances"]:
                if balance["asset_code"] == asset_code and balance[
                    "asset_issuer"] == asset_issuer:
                    return balance["balance"]
                elif balance["asset_type"] == "native":
                    return balance["balance"]
                else:
                    continue
            return 0
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            self.server_msg["error"] = f"Error getting balance: {e}"
            raise Exception(f"Error getting balance: {e}")

    def watch_liquidity_pool_activity(self):
        for op in (
                self.server.operations()
                        .for_liquidity_pool(liquidity_pool_id=self.account.account.account_id)
                        .cursor("now")
                        .stream()
        ):
            if op["type"] == "liquidity_pool_deposit":
                self.logger.info("Reserves deposited:")
                for r in op["reserves_deposited"]:
                    self.logger.info(f"    {r['amount']} of {r['asset']}")
                self.logger.info(f"    for pool shares: {op['shares_received']}")

    def create_trade_asset(self, code, issuer, code1, issuer1, pool_id):
        asset = Asset(code, issuer)
        asset1 = Asset(code1, issuer1)
        tx = TransactionBuilder(
            source_account=self.account,
            network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
            base_fee=100
        )
        tx.append_create_account_op(destination=self.account.account.account_id, starting_balance="1000")
        tx.append_change_trust_op(asset=asset, limit="1000")
        tx.append_change_trust_op(asset=asset1, limit="1000")
        # liquidity_pool_id: str,
        # max_amount_a: str | Decimal,
        # max_amount_b: str | Decimal,
        # min_price: str | Decimal | Price,
        # max_price: str | Decimal | Price,
        # source: Mixed Account | str | None = None) -> TransactionBuilder

        tx.append_liquidity_pool_deposit_op(
            liquidity_pool_id=pool_id,
            max_amount_a="10",
            max_amount_b="10",
            min_price="0.01",
            max_price="10"
        )
        tx.build().sign(self.secret_key)
        self.server.submit_transaction(tx.build())
        self.logger.info(f"Trade asset '{code}' created successfully.")

        self.pool_id = tx.build().hash
        self.logger.info(f"Liquidity pool ID: {self.pool_id}")
        return self.pool_id

    def channel_account(self):
        # Base account (the account holding the assets)

        self.base_account = self.account
        # Channel accounts (used for sequence numbers and fees)
        channel_secrets = ["CHANNEL_1_SECRET", "CHANNEL_2_SECRET", "CHANNEL_3_SECRET"]
        channel_keypair = [Keypair.from_secret(secret) for secret in channel_secrets]
        channel_accounts = [self.server.load_account(self.account_id)]
        # Payment details
        customer_address = "DESTINATION_PUBLIC_KEY"
        amount_to_send = "10"
        base_fee = 100  # Network base fee in troops (100 troops = 0.00001 XLM)
        # Channel selection
        channel_index = 0  # Select the desired channel
        channel_account = channel_accounts[channel_index]
        channel_keypair = channel_keypair[channel_index]
        # Build the transaction
        transaction = (TransactionBuilder(
            source_account=channel_account,
            network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
            base_fee=base_fee
        )
                       .append_payment_op(
            source=self.base_account.account,
            destination=customer_address,
            asset=Asset.native(),
            amount=amount_to_send,
        )
                       .set_timeout(180)
                       .build()
                       )

        # Sign with both base account and channel account keys
        transaction.sign(self.base_account_keypair)  # Base account must approve the payment
        transaction.sign(channel_keypair)  # Channel account must approve its use as a source

        # Submit the transaction
        try:
            response = self.server.submit_transaction(transaction)
            self.logger.info(f"Transaction successful: {response['hash']}")
            self.server_msg["transaction_hash"] = response["hash"]
        except Exception as e:
            self.logger.error(f"Transaction failed: {e}")
            self.server_msg["error"] = f"Transaction failed: {e}"
            raise e

    def create_account_and_trust(self, public_key, secret_key, asset_code, asset_issuer, starting_balance):
        keypair = Keypair.from_secret(secret_key)
        account = self.server.load_account(public_key)
        transaction = (
            TransactionBuilder(
                source_account=account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100
            )
            .append_create_account_op(destination=public_key, starting_balance=starting_balance)
            .append_change_trust_op(asset=Asset(asset_code, asset_issuer), limit=starting_balance)
            .build()
        )
        transaction.sign(keypair)
        response = self.server.submit_transaction(transaction)
        self.logger.info(f"Account and trust created: {response}")
        self.logger.info(f"Transaction successful: {response['hash']}")
        self.server_msg["transaction_hash"] = response["hash"]
        self.server_msg["message"] = "Account and trust created successfully."

        return response

    def get_liquidity_pools(self, asset1: Asset, asset2: Asset):
        # Set up the Horizon server
        sequence_assets = [asset1, asset2]  # Assets to include in the liquidity pool (in this case, USDC and XLM)
        # Fetch liquidity pools that include the specified assets
        pools = self.server.liquidity_pools().for_reserves(reserves=sequence_assets).call()

        # Iterate through results
        # Note: You can also filter pools based on other criteria such as the minimum amount of liquidity required,
        # the minimum price, or the maximum price.
        # Liquidity Pool ID: GD6433U34463B737263626D7A7A44476D7A46455A43
        # Total Shares: 1,234,567,890
        # - Asset: USDC, Amount: 12345.6789
        # - Asset: XLM, Amount: 1000000000000000000000000
        # Log the results

        self.logger.info(f"Found {len(pools['_embedded']['records'])} liquidity pools.")

        self.logger.info(f"Found {len(pools['_embedded']['records'])} liquidity pools.")
        for pool in pools["_embedded"]["records"]:
            pool_id = pool["id"]
            total_shares = pool["total_shares"]
            reserves = pool["reserves"]
            self.logger.info(f"Liquidity Pool ID: {pool_id}")
            self.logger.info(f"Total Shares: {total_shares}")
            for reserve in reserves:
                self.logger.info(f" - Asset: {reserve['asset']}, Amount: {reserve['amount']}")
                # If no pools are found
                if not pools["_embedded"]["records"]:
                    self.logger.info("No liquidity pools found for the specified assets.")
                    self.server_msg["message"] = "No liquidity pools found for the specified assets."

    def on_transaction_executed_(self, event, data):
        self.logger.info(f"Transaction executed: {event.hash}")
        self.logger.info(f"Transaction result: {data['result']['result']}")
        if data["result"]["result"] == "success":
            self.logger.info(f"Transaction details: {data['result']['transaction']}")
            # Process transaction data as needed
            self.process_transaction_data(data)

        # Check for errors in the transaction
        if "error" in data["result"]:
            self.logger.error(f'Transaction error: {data['result']['error']['message']}')
            self.logger.error(f'Transaction details: {data['result']['transaction']}')
            # Handle transaction error as needed
            self.handle_transaction_error(data)

    def process_transaction_data(self, data):
        # Process transaction data as needed
        transaction_data = data["result"]["transaction"]
        # Example: Extract transaction details
        self.logger.info(f"Transaction details: {transaction_data}")

    def handle_server_message(self, message):
        self.logger.info(f"Server message: {message}")
        self.server_msg["message"] = message
        self.server_msg["success"] = False

    def handle_transaction_error(self, data):
        # Handle transaction error as needed
        error_data = data["result"]["error"]
        # Example: Handle transaction error based on error code
        if error_data["code"] == 20001:
            self.logger.error("Transaction failed due to insufficient funds.")
        elif error_data["code"] == 20002:
            self.logger.error("Transaction failed due to invalid source account.")
        elif error_data["code"] == 20003:
            self.logger.error("Transaction failed due to insufficient balance.")
        elif error_data["code"] == 20029:
            self.logger.error("Transaction failed due to invalid memo.")
        else:
            self.logger.error("Transaction failed due to an unknown error.", error_data)

    def create_trading_pair(self):
        try:

            assets1 = []
            # Get account details
            account_info = self.server.accounts().account_id(self.account_id).limit(200).call()
            self.logger.info(f"Account details: {account_info}")
            self.account_sequence = account_info["sequence"]
            account_balances = account_info.get("balances")

            for balance in account_balances:
                asset_code = balance.get("asset_code", "XLM")
                asset_issuer = balance.get("asset_issuer", Asset.native().issuer)
                assets1.append(Asset(asset_code, asset_issuer))
                self.logger.info(f"Asset: {asset_code}, Issuer: {asset_issuer}")
            # Create a trading pair
            trading_pairs = ()
            for asset1 in assets1:

                if asset1 != Asset.native():
                    trading_pairs += ((asset1, Asset.native()),)
                else:
                    trading_pairs += ((Asset.native(), asset1),)

            self.logger.info(f"Trading pairs: {trading_pairs}")
            return trading_pairs



        except Exception as e:

            self.logger.error(
                f"Error occurred while fetching account information: {e}"
            )
            self.server_msg["message"] = f"Error occurred while creating trading pair: {e}"

            return []

    def create_ohclv(self, trade_pair, resolution: int, start_time: int, end_time: int, offset_=0, max_retries=5,
                     retry_delay=3):
     """
     Fetches OHLCV data for the specified trade pair, resolution, time frame, and offset,
     with handling for API rate limits.

     Args:
        trade_pair (tuple): A tuple containing the base- and counter-currencies (e.g., ('BTC', 'USD')).
        resolution (int): The time resolution for the OHLCV data in seconds.
        start_time (int): The start time for fetching data in Unix timestamp format.
        end_time (int): The end time for fetching data in Unix timestamp format.
        offset_ (int, optional): An optional offset for paginated data fetching. Defaults to 0.
        max_retries (int, optional): Maximum number of retries on rate limit errors. Defaults to 5.
        retry_delay (int, optional): Delay in seconds between retries. Defaults to 1.

     Returns:
        list: A list of tuples, each representing an OHLCV data point with the following fields:
            - time: Timestamp of the data point.
            - open: Opening price.
            - high: Highest price.
            - low: Lowest price.
            - close: Closing price.
            - volume: Counter volume traded.
            - base_volume: Base volume traded.
            - trade_count: Number of trades executed.

     Raises:
        Exception: If the maximum retries are exceeded.
     """
     retries = 0

     if retries <= max_retries:
            try:
                # Fetch aggregated trade data
                responses_ = self.server.trade_aggregations(
                    start_time=start_time,
                    end_time=end_time,
                    resolution=resolution,
                    offset=offset_,
                    base=trade_pair[0],
                    counter=trade_pair[1]
                ).order(True).limit(200).call()

                # Parse the response to extract OHLCV data
                ohclv_data = [
                    (
                        response["time"],
                        response["open"],
                        response["high"],
                        response["low"],
                        response["close"],
                        response["volume"],
                        response["base_volume"],
                        response["trade_count"]
                    )
                    for response in responses_
                ]

                return ohclv_data

            except Exception as e:
                # Handle rate limit or transient errors
                retries += 1
                if retries > max_retries:
                    raise Exception(f"Max retries exceeded: {e}")
                self.logger.info(f"Rate limit hit. Retrying in {retry_delay} seconds... ({retries}/{max_retries})")
                time.sleep(retry_delay)

    def run(self):
        self.logger.info("Running...")
        self.server_msg.update({"status": "RUNNING...", "message": "RUNNING..."})

        # Validate time frame
        valid_time_frames = [60000, 300000, 900000, 3600000, 86400000, 604800000]
        if self.time_frame not in valid_time_frames:
            self.logger.error("Invalid time frame provided.")
            self.server_msg.update({"message": "Invalid time frame provided.", "success": False})
            return

        # Set up trading pairs and fetch initial market data
        try:
            self.logger.info("Setting up trading pairs...")
            self.trade_pairs = self.create_trading_pair()
            self.logger.info("Fetching initial market data...")
            market_data, ohclv = self.fetch_market_data(self.trade_pairs, self.time_frame)

            if not market_data:
                self.logger.error("No market data found for any trade pair.")
                self.server_msg.update({"message": "No market data found for any trade pair.", "success": False})
                return

            self.server_msg.update({
                "ohlcv": ohclv,
                "message": f"Fetched OHLCV data for {len(self.trade_pairs)} pairs.",
                "success": True,
            })

        except Exception as e:
            self.logger.error(f"Error during setup: {e}")
            self.server_msg.update({"message": f"Error during setup: {e}", "success": False})
            return

            # Main monitoring loop
        while True:
            try:
                market_data, ohclv = self.fetch_market_data(self.trade_pairs, self.time_frame)

                # Analyze market data
                self.analyze_and_update(market_data, ohclv)

                # Sleep before the next iteration
                time.sleep(0.5 * self.interval_seconds)

            except Exception as e:
                self.logger.error(f"Error in the main loop: {e}")
                self.server_msg["message"] = f"Error in the main loop: {e}"

    def analyze_and_update(self, market_data, ohclv):
        """
    Analyzes the market data and updates server messages.
     """
        try:
            # Calculate average price and indicators
            for pair_key, data in market_data.items():
                data["average_price"] = data["close"] / data["volume"]
                self.calculate_macd(data)
                self.calculate_rsi(data)

            self.server_msg["market_data"] = market_data
            self.server_msg["ohlcv_data"] = ohclv
            self.logger.info(f"Market data and OHLCV analysis complete for {len(market_data)} pairs.")

        except Exception as e:
            self.logger.error(f"Error during analysis: {e}")
            self.server_msg["message"] = f"Error during analysis: {e}"

    def calculate_macd(self, data):
        """
    Calculates MACD and MACD signal for a given trading pair.
    """
        try:
            ema_fast = ta.EMA(data["close"], timeperiod=12)
            ema_slow = ta.EMA(data["close"], timeperiod=26)
            macd = ema_fast - ema_slow
            macd_signal = ta.EMA(macd, timeperiod=9)
            data.update({"macd": macd, "macd_signal": macd_signal})
        except Exception as e:
            self.logger.error(f"Error calculating MACD: {e}")

    def calculate_rsi(self, data):
        """
    Calculates RSI for a given trading pair.
     """
        try:
            data["rsi"] = ta.RSI(data["close"], timeperiod=14)
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {e}")

    def cancel_order(self, param):
        """
        Cancel an order.
        """
        try:

            self.logger.info(f"Order {param} cancelled.")
            self.server_msg["message"] = f"Order {param} cancelled."
        except Exception as e:
            self.logger.error(f"Error cancelling order {param}: {e}")
            self.server_msg["message"] = f"Error cancelling order {param}: {e}"

    def check_order_executed(self, param):
        """
        Check if an order has been executed.
        """
        try:
            order = self.server.offers().for_account(self.account_id).offer(param).call()["_embedded"]["record"]
            self.logger.info(f"Order {param} status: {order['is_executed']}")
            self.server_msg["message"] = f"Order {param} status: {order['is_executed']}"
            if order["is_executed"]:
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"Error checking order execution: {e}")
            self.server_msg["message"] = f"Error checking order execution: {e}"
            return False

    def fetch_asset_balance(self, asset_code):
        """
        Fetch the balance of a specific asset.
        """
        try:
            balance = self.account_info["_embedded"]["records"]
            self.logger.info(f"Balance of {asset_code} on account {self.account_id}: {balance['balance']}")
            self.server_msg["message"] = f'Balance of {asset_code} on account {self.account_id}: {balance['balance']}'
            return balance["balance"]
        except Exception as e:
            self.logger.error(f"Error fetching asset balance: {e}")
            self.server_msg["message"] = f"Error fetching asset balance: {e}"
            return None

    def get_assets_info(self):
        """
        Fetch information about all assets.
        """

        param = {

            "order": "desc",
            "limit": 200
        }
        response = self.process_requests("/assets", param)
        self.logger.info(f"Assets info: {response}")
        assets_info = {}
        while response.json()["_links"]["next"]:
            next_url = response["_links"]["next"]["href"]
            response = self.process_requests(next_url, param)
            self.logger.info(f"Assets info: {response}")
            for asset in response["_embedded"]["records"]:
                assets_info[asset["_links"]["self"]["href"].split("/")[-1]] = asset
                self.logger.info(f"Asset info: {asset}")
        return assets_info

    def get_news_data(self):
      try:
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json?version=250168734a93f14f790321affe02880f"
        response = requests.get(url)
        if response.status_code!= 200:
            self.logger.error(f"Error fetching news data: {response.status_code}")
            self.server_msg["message"] = f"Error fetching news data: {response.status_code}"
            return None
        news_data = response.json()
        self.logger.info(f"News data: {news_data}")


        return news_data
      except Exception as e:
        self.logger.error(f"Error fetching news data: {e}")
        self.server_msg["message"] = f"Error fetching news data: {e}"
        return {

        }

