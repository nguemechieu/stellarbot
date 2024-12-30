import logging
import time
from datetime import datetime
from threading import Thread

import numpy as np
import pandas as pd
import requests
from pandas import DataFrame
from stellar_sdk import Server, Asset, TransactionBuilder, Network, Transaction
from textblob import TextBlob

from src.modules.classes.blockchain_asset import BlockchainAsset
from src.modules.classes.indicator_utility import generate_ppo_signal, generate_kdj_signal, generate_aroon_signal, \
    generate_uo_signal, generate_bbands_signal, generate_trix_signal, generate_adx_signal, generate_ema_signal, \
    generate_sma_crossover_signal, generate_bollinger_bands_signal, generate_macd_signal, generate_cmf_signal, \
    generate_stoch_signal, generate_sar_signal, generate_rsi_signal, generate_ichimoku_signal, generate_dmi_signal, \
    generate_willr_signal, generate_atr_signal, generate_custom_indicator_signal
from src.modules.classes.learning import Learning
from src.modules.classes.order_types import OrderTypes
from src.modules.classes.telegram import TelegramBot
from src.modules.classes.time_frames import TimeFrame
from src.modules.classes.trade_side import TradeSide
from src.modules.classes.trade_signal import TradeSignal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_asset_data():
    return {
        "price": 0.0,
        "balance": 0.0,
        "offers": 0,
        "effects": 0,
        "transactions": 0,
        "orderbook": {"bids": [], "asks": []},
        "candles": [],
        "trades": [],
        "balances": {},
        "ledger": {"operations": []},
        "transaction_history": [],
        "transaction_details": {},
        "account_details": {
            "balances": [],
            "offers": [],
            "effects": [],
            "transactions": []
        }
    }


def check_buy_sell_signals(df):
    """
    Check for buy/sell signals based on SMA crossover.
    """
    if df['SMA_Short'].iloc[-1] > df['SMA_Long'].iloc[-1] and \
            df['SMA_Short'].iloc[-2] <= df['SMA_Long'].iloc[-2]:
        return "BUY"
    elif df['SMA_Short'].iloc[-1] < df['SMA_Long'].iloc[-1] and \
            df['SMA_Short'].iloc[-2] >= df['SMA_Long'].iloc[-2]:
        return "SELL"
    return None


class MoneyManagement:
    def __init__(self, controller):
        """
        Initializes the MoneyManagement class with the given controller.
        """
        self.controller = controller
        self.logger = controller.logger.getLogger(__name__)

        # Initialize balance-related attributes

        self.assets_balances = self._fetch_assets_balances()
        self.transactions_count = 0
        self.assets_balances_count = len(self.assets_balances)

    def _fetch_balance(self):
        """Fetch and return the balance for the specified asset."""
        try:
            return self.controller.assets_balances[self.controller.asset]
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            return 0  # Default to 0 if fetching balance fails

    def _fetch_assets_balances(self):
        """Fetch and return all asset balances."""
        try:
            return self.controller.bot.get_assets_balances()
        except Exception as e:
            self.logger.error(f"Error fetching assets balances: {e}")
            return {}  # Return empty dictionary if fetching fails


    def update_assets_balances(self):
        """Updates the asset balances and their count."""
        self.assets_balances = self._fetch_assets_balances()
        self.assets_balances_count = len(self.assets_balances)
        self.logger.info(f"Updated asset balances: {self.assets_balances_count} assets found.")

    def check_balance(self, asset):
        """
        Checks if the current balance is greater than or equal to zero.
        Returns True if the balance is valid, False otherwise.
        """
        if self.assets_balances[asset] < 0:
            self.logger.warning(f"Balance check failed: {self.assets_balances[asset]} is negative!")
            return False
        return True

    def calculate_quantity(self, base_asset, counter_asset):
        """
        Calculates the quantity of the base asset available for trading.

        Parameters:
        - base_asset (str): The asset for which quantity is to be calculated.
        - counter_asset (str): The asset against which the base asset is traded.

        Returns:
        - float: The quantity of the base asset available for trading.
        """
        if base_asset not in self.assets_balances:
            self.logger.warning(f"Asset {base_asset} not found in available balances.")
            return 0  # Return 0 if the asset is not found

        available_balance = self.assets_balances[base_asset].get('balance', 0)
        asset_price = self.assets_balances[base_asset].get('price', 1)  # Default to 1 to avoid division by zero

        if asset_price == 0:
            self.logger.error(f"Price for {base_asset} is zero. Cannot calculate quantity.")
            return 0  # Avoid division by zero

        quantity = available_balance / asset_price
        self.logger.info(f"Calculated quantity for {base_asset}: {quantity} {counter_asset}")
        return quantity

    def get_balance(self, asset):
        """Returns the current balance."""
        return  self.assets_balances.get(asset, {}).get('balance', 0)

    def get_assets_balances(self):
        """Returns the current assets balance."""
        return self.assets_balances

    def get_transaction_count(self):
        """Returns the transaction count."""
        return self.transactions_count

    def get_assets_balances_count(self):
        """Returns the count of available assets balances."""
        return self.assets_balances_count


class SmartTradingBot(Server):
    def __init__(self, controller):
        super().__init__(controller)

        # Initialize basic attributes
        self.last_request_time = datetime.now()
        self.order = None
        self.money_management = MoneyManagement(controller)
        self.learn_how_to_trade = True
        self.endpoint = None
        self.thread = None
        self.chat_id =controller.chat_id
        self.blockchain_assets = None
        self.controller = controller
        self.asset = controller.asset
        self.account_id = controller.account_id
        self.secret_key = controller.secret_key
        self.telegram_token = controller.telegram_token
        self.logger = logger

        # Initialize dataframes and counts
        self.operations_count = 0
        self.trades_count = None
        self.assets_count = 0
        self.assets_balances_count = None
        self.transactions_count = 0

        # Bot states and signals
        self.keep_running = False
        self.selected_strategy = 'FOREX_NEWS'
        self.server_msg = {
            'message': '',
            'status': 'IdLE',
            'message_type': 'info',
            'action': 'update_trade_signal'
        }

        # Trading data
        self.order_book = {"bids": [], "asks": []}
        self.trade_signals = []
        self.last_buy_price = 0
        self.last_sell_price = 0
        self.asset_pairs = []
        self.assets_df = None
        self.asset_pairs_df = None

        # Initialize external services
        self.telegram = TelegramBot(self.telegram_token)
        self.ai = Learning(self)

        # Initialize bot
        self._initialize_bot()

    def _initialize_bot(self):
        """Handle all initialization steps."""
        try:
            # Initialize account, assets, and trading data
            self._initialize_account()
            self._initialize_assets()
            self._initialize_operations()
            self._initialize_balances()
            self._initialize_transactions()

            # Additional setup
            self.logger.info("Smart trading bot initialized.")
            self.server_msg['message'] = f"Smart trading bot initialized for {self.account_id}."
            self.server_msg['action'] = 'update_trade_signal'

            # Initialize strategies and Telegram Bot
            self.strategies = self.load_strategies(self.asset_pairs_df)

            # Initialize Telegram and log info
            self.logger.info("Telegram Bot initialized")

        except Exception as e:
            self._handle_initialization_error(e)

    def _initialize_account(self):
        """Load and log account details."""
        self.account = self.load_account(account_id=self.account_id)
        self.account_details = self.accounts().call()['_embedded']['records'][0]
        self.logger.info(f"Account details: {self.account_details}")
        self.server_msg['message'] = f"Account details: {self.account_details}"

    def _initialize_assets(self):
        """Load assets and asset pairs."""
        self.assets1 = self.get_all_assets()
        self.assets_count = len(self.assets1)
        self.assets_df = DataFrame(self.assets1)
        self._populate_asset_pairs()

    def _populate_asset_pairs(self):
        """Populate asset pairs."""
        for asset in self.assets1:
            if asset['asset_type'] == 'credit_alphanum4' and asset['asset_code'] != 'XLM':
                base_asset = Asset(asset['asset_code'], asset['asset_issuer'])
                counter_asset = Asset.native()
                self.asset_pairs.append((base_asset, counter_asset))
        self.asset_pairs_df = DataFrame([{"base_asset": pair[0].code, "counter_asset": pair[1].code}
                                         for pair in self.asset_pairs])
        self.asset_pairs_df.to_csv('stellarbot_assets.csv', index=False)

    def _initialize_operations(self):
        """Load operations and trades."""
        self.operations = self.operations().for_account(self.account_id).call()
        self.operations_count = len(self.operations)
        self.operations_df = DataFrame(self.operations)
        self.operations_df.set_index('id', inplace=True)
        self.operations_df.to_csv('stellar_bot.operations.csv')

    def _initialize_balances(self):
        """Load balances."""
        self.balances = self.balances().for_account(self.account_id).call()
        self.balances_count = len(self.balances)
        self.balances_df = DataFrame(self.balances)
        self.balances_df.set_index('asset_type', inplace=True)
        self.balances_df.to_csv('stellar_bot.balances.csv')

    def _initialize_transactions(self):
        """Load transactions."""
        self.transactions = self.transactions().for_account(self.account_id).call()
        self.transactions_count = len(self.transactions)
        self.transactions_df = DataFrame(self.transactions)
        self.transactions_df.set_index('id', inplace=True)
        self.transactions_df.to_csv('stellar_bot.transactions.csv')

    def _handle_initialization_error(self, error):
        """Handle errors during bot initialization."""
        self.logger.error(f"Error initializing StellarBot: {str(error)}")
        self.server_msg['message'] = f"Error initializing StellarBot: {str(error)}"
        self.server_msg['message_type'] = 'error'
        self.server_msg['action'] = 'update_trade_signal'

    def start(self):
        """Start the bot and run the trading logic."""
        self.logger.info("TradingBot started.")
        self.server_msg['message'] = f"TradingBot started for {self.account_id}."
        self._fetch_initial_trading_data()
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.daemon = self.keep_running
        self.run()

    def _fetch_initial_trading_data(self):
        """Fetch initial trading data for operations, trades, and balances."""
        self.trades = self.trades().for_account(self.account_id).call()
        self.trades_count = len(self.trades)
        self.trades_df = DataFrame(self.trades)
        self.trades_df.set_index('id', inplace=True)
        self.trades_df.to_csv('stellar_bot.trades.csv')

        self.assets_balances = self.balances().for_account(self.account_id).call()
        self.assets_balances_count = len(self.assets_balances)
        self.assets_balances_df = DataFrame(self.assets_balances)
        self.assets_balances_df.to_csv('stellar_bot.assets_balances.csv')

        self.server_msg['message'] = f"Operations: {self.operations_count}, Trades: {self.trades_count}."
        self.server_msg['action'] = 'update_trade_signal'

    def stop(self):
        """Stop the bot."""
        self.logger.info("TradingBot stopped.")
        self.server_msg['message'] = f"TradingBot stopped for {self.account_id}."
        self.server_msg['action'] = 'update_trade_signal'
        self.thread.join()

    # Bot Actions
    def gennerate_trade_signals(self, selected_trade_strategy, interval: TimeFrame, lookback: int = 100):
        """Generate trade signals based on the selected strategy."""
        if selected_trade_strategy not in self.strategies:
            raise ValueError(f"Invalid trade strategy: {selected_trade_strategy}")

        trade_strategy = self.strategies[selected_trade_strategy]
        self.asset = trade_strategy['asset']
        self.logger.info(f"Generating trade signals for {self.asset}.")
        return self.gennerate_trade_signals(trade_strategy['name'], interval, lookback)

    def fetch_historical_data(self, interval: TimeFrame, lookback: int = 100, base_asset: Asset = Asset(code='USDC', issuer='GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN'), counter_asset: Asset = Asset.native()):
        """Fetch historical market data for trading."""
        try:
            klines = self.get_historical_klines(
                base_asset=base_asset, counter_asset=counter_asset,
                resolution=interval.value,
                end_time=int(time.time() * 1000),
                limit=lookback,
                start_time=int(time.time() - (interval.value * lookback)) * 1000
            )
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                'quote_asset_volume', 'number_of_trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype(float)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            self.logger.info("Historical data fetched successfully.")

            # Create and save BlockchainAsset object
            self.blockchain_assets = BlockchainAsset(
                code=base_asset.code,
                issuer=base_asset.issuer,
                current_price=df['close'].iloc[-1],
                amount=df['close'].iloc[-1] * df['volume'].iloc[-1],
                image=f"https://www.coingecko.com/api/v3/coins/markets?ids={base_asset.code}&vs_currencies=usd",
                homepage=f"https://www.coingecko.com/en/coins/{base_asset.code}"
            )
            self.blockchain_assets.save_asset_info()
            self.blockchain_assets.get_asset_info_df()

            return df
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
            return pd.DataFrame()


    def calculate_moving_averages(self, df, short_window: int = 9, long_window: int = 21):
        """
        Calculate moving averages.
        """
        df['SMA_Short'] = df['close'].rolling(window=short_window).mean()
        df['SMA_Long'] = df['close'].rolling(window=long_window).mean()
        self.logger.info("Moving averages calculated.")
        return df

    def place_order(self,
                    base_asset: Asset = Asset(code='USDC',
                                              issuer="GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN"),
                    counter_asset: Asset = Asset.native(),
                    price: float = 0.06,
                    quantity: int = 100,
                    order_type: OrderTypes = OrderTypes.LIMIT,
                    side=TradeSide.BUY,
                    ) -> dict or None:

        """
        Place a buy or sell order.
        """
        try:
            order = self.create_order(
                base_asset=base_asset,
                counter_asset=counter_asset
                ,
                price=price,
                side=side,
                order_type=order_type,

                quantity=quantity
            )
            self.logger.info(f"Order placed: {side} {quantity} {self.asset}.")
            self.telegram.send_message(message=f"Order placed: {side} {quantity} {self.asset}.",
                                       chat_id=self.chat_id)
            return order
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            self.telegram.send_message(message=f"Error placing order: {e}", chat_id=self.chat_id)
            return None

    def run(self):
        """
        Run the bot.
        """
        self.logger.info("TradingBot is running...")
        while True:
            if not self.keep_running:
                self.logger.info("TradingBot stopped.")
                break
            df = self.fetch_historical_data(TimeFrame.ONE_MINUTE, 100)

            self.logger.info(f"Historical data fetched for {self.asset}.")
            self.logger.info("Data shape: {df.shape}")

            if df.empty:
                self.logger.info("No historical data available.")
                continue

            asset_pairs = self.asset_pairs_df
            if isinstance(asset_pairs[0]['base_asset']['code'], int):
                self.logger.info("No assets available for trading.")
                asset_pairs.pop(0)
                continue

            for index, row in asset_pairs:

                base_asset = Asset(
                    code=row['code'],
                    issuer=row['issuer']
                )
                counter_asset = Asset.native()

                quantity = self.money_management.calculate_quantity(base_asset, counter_asset)

                for strategy in self.strategies.values():
                    if strategy['name'] == self.selected_strategy:
                        self.logger.info(f"Running strategy: {strategy['name']}.")
                        signal = self.gennerate_trade_signals(strategy['name'], TimeFrame.ONE_MINUTE)

                        if self.learn_how_to_trade:
                            self.logger.info(f"Learning from data completed for strategy: {strategy['name']}.")

                            signal = self.ai.learn_from_data(df)
                            self.logger.info(f"Learning completed for strategy: {strategy['name']}.")

                        # Check for buy/sell signals
                        if signal == TradeSignal.BUY:
                            price = df['close'].iloc[-1]
                            self.last_buy_price = price
                            self.place_order(base_asset, counter_asset, price,quantity, OrderTypes.LIMIT,
                                             TradeSide.BUY)
                        elif signal == TradeSignal.SELL:
                            price = df['close'].iloc[-1]
                            self.last_sell_price = price
                            self.place_order(base_asset, counter_asset, price, quantity, OrderTypes.LIMIT,
                                             TradeSide.SELL)
                        elif signal == TradeSignal.HOLD:
                            self.logger.info(f"Strategy: {strategy['name']} is holding.")
            time.sleep(60)  # Wait for the next candle

    def create_order(self,
                     base_asset: Asset,
                     counter_asset: Asset,
                     price: float,
                     side: TradeSide,
                     order_type: OrderTypes,
                     quantity: int
                     ):
        """
        Create an order using the Stellar SDK.
        """
        #Validate input parameters
        if not (1 <= price <= 100000000):
            raise ValueError('Invalid price')
        if not (1 <= quantity <= 10000000):
            raise ValueError('Invalid quantity')
        if not (OrderTypes.MARKET in [order_type]):
            raise ValueError('Invalid order type')
        if not (TradeSide.BUY in [side] or TradeSide.SELL in [side]):
            raise ValueError('Invalid side')

        # Create the order using the Stellar SDK
        # Note: Replace 'account_id', 'asset_code', 'asset_issuer', 'price', 'order_amount', and 'order_price' with your actual values
        # Also, replace 'order_creator' with the actual function that creates the order using the Stellar SDK
        # Example:
        # self.order_creator = self.server.submit_orde

        return self.order_creator(
            account_id=self.account_id,
            asset_code=base_asset.code,
            asset_issuer=base_asset.issuer,
            counter_asset_code=counter_asset.code,
            counter_asset_issuer=counter_asset.issuer,
            amount=quantity,  # Quantity is fixed to 1
            side=side,
            price=price  # The Price is fixed to 1 Satoshi
        )

    def get_historical_klines(self,
                              base_asset: Asset = Asset.native(),
                              counter_asset: Asset = Asset.native(),
                              resolution: int = TimeFrame.HOUR,
                              start_time: int = (time.time() - 86400 * 7),  # 7 days ago
                              end_time: int = (
                                      time.time()  # Now
                              ),
                              limit: int = 200
                              ) -> list:
        """
            Get historical klines.
        :param base_asset:
        :param counter_asset:
        :param resolution:
        :param start_time:
        :param end_time:
        :param limit:
        :return:
        """
        aggregation = self.trade_aggregations(
            resolution=resolution,
            start_time=start_time,
            end_time=end_time,
            offset=limit,
            base=base_asset,
            counter=counter_asset).limit(limit).call()['_embedded']['records']

        aggregation_df = pd.DataFrame(aggregation, columns=['time', 'open', 'high', 'low', 'close',
                                                            'volume', 'trade_count', 'base_volume', 'base_asset_volume',
                                                            'counter_asset_volume', 'ignored'
                                                            ])
        aggregation_df['time'] = pd.to_datetime(aggregation_df['time'], unit='s')
        return aggregation_df.to_dict(orient='records')

    def get_account(self, account_id):

        try:
            account = self.accounts().account_id(account_id).limit(1).call()
            return account
        except Exception as e:
            self.logger.error(f"Error fetching account: {e}")
            return None

    def order_creator(self,
                      account_id: str,
                      asset_code: str,
                      asset_issuer: str,
                      counter_asset_code: str,
                      counter_asset_issuer: str,
                      amount: float,
                      side: TradeSide,
                      price: float = 1.0) -> Transaction:

        #Check if the account has enough balances for the order
        account_balance = self.get_account(account_id)['balances'][0]['balance']
        if float(account_balance) < float(amount):
            self.logger.error(f"Insufficient balance to place order.")
            self.telegram.send_message(
                message=f"Insufficient balance to place order.Your current balance is {account_balance} and the order amount is {amount}.",
                chat_id=self.chat_id)
            raise ValueError(
                "Insufficient balance ! Your current balance is {account_balance} and the order amount is {order_amount}.")

        # Create the order
        # Note: Replace 'account_id', 'asset_code', 'asset_issuer', 'counter_asset_code', 'counter_asset_issuer', 'amount', 'price', 'order_amount', and 'order_price' with your actual values
        # Also, replace 'order_creator' with the actual function that creates the order using the Stellar SDK
        transactions_builder = TransactionBuilder(source_account=self.account,
                                                  network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE
                                                  )
        if side == TradeSide.BUY:

            transactions_builder.append_manage_buy_offer_op(source=self.account.account,
                                                            amount=str(amount),
                                                            price=str(price),
                                                            offer_id=0,
                                                            buying=Asset(asset_code, asset_issuer),
                                                            selling=Asset(counter_asset_code, counter_asset_issuer)
                                                            ).add_text_memo("StellarBot@BUY ORDER" + " @ " + str(price))

        elif side == TradeSide.SELL:
            transactions_builder.append_manage_sell_offer_op(
                source=self.account.account,
                amount=str(amount),
                price=str(price),
                offer_id=0,
                buying=Asset(asset_code, asset_issuer),
                selling=Asset(counter_asset_code, counter_asset_issuer)
            ).add_text_memo("StellarBot@SELL ORDER" + " @ " + str(price))

        transactions_builder.build().sign(signer=self.secret_key)
        resposnr = self.submit_transaction(transactions_builder.build()).popitem()
        if resposnr[1]['status'] == 'FAILURE':
            self.logger.error(f"Error submitting transaction: {resposnr[1]['error']['message']}")
            self.telegram.send_message(message=f"Error submitting transaction: {resposnr[1]['error']['message']}",
                                       chat_id=self.chat_id)
            raise ValueError(f"Error submitting transaction: {resposnr[1]['error']['message']}")
        else:
            self.logger.info(f"Order placed successfully: {resposnr[1]['hash']}")
        self.logger.info(f"Account balance: {self.get_account(account_id)['balances'][0]['balance']}")
        self.logger.info(f"Account sequence: {self.get_account(account_id)['sequence']}")
        self.telegram.send_message(message=f"Order placed successfully: {resposnr[1]['hash']}", chat_id=self.chat_id)

        return resposnr[1]

    def load_strategies(self, trading_pairs):
        # Load and initialize strategies
        signal_settings = {
            "short_window": 9,
            "long_window": 21,
            "ema_short_period": 5,
            "ema_long_period": 20,
            "bbands_period": 20,
            "bbands_std_dev": 2,
            "rsi_period": 14,
            "adx_period": 14,
            "ema_period": 20,
            "bbands_multiplier": 2,
            "trix_period": 9,
            "ppo_fast_period": 12,
            "ppo_slow_period": 26,
            "ppo_signal_period": 9,
            "kdj_fast_period": 9,
            "kdj_slow_period": 3

        }
        for base, counter in trading_pairs.items():
            base = Asset.native()
            counter = Asset(
                code=counter.code,
                issuer=counter.issuer)

            ohclv_data = pd.DataFrame(self.get_historical_klines(base_asset=base, counter_asset=counter,
                                                                 resolution=TimeFrame.HOUR.get_seconds(), limit=100))
            strategies = {
                (base, counter): {'SMA_Crossover': self.strategies_config('SMA_Crossover', signal_settings, ohclv_data),
                                  'Bollinger_Bands': self.strategies_config('Bollinger_Bands', signal_settings,
                                                                            ohclv_data),
                                  'MACD': self.strategies_config('MACD', signal_settings, ohclv_data),
                                  'RSI': self.strategies_config('RSI', signal_settings, ohclv_data),
                                  'ADX': self.strategies_config('ADX', signal_settings, ohclv_data),
                                  'EMA': self.strategies_config('EMA', signal_settings, ohclv_data),
                                  'BBANDS': self.strategies_config('BBANDS', signal_settings, ohclv_data),
                                  'TRIX': self.strategies_config('TRIX', signal_settings, ohclv_data),
                                  'PPO': self.strategies_config('PPO', signal_settings, ohclv_data),
                                  'KDJ': self.strategies_config('KDJ', signal_settings, ohclv_data),
                                  'AROON': self.strategies_config('AROON', signal_settings, ohclv_data),
                                  'UO': self.strategies_config('UO', signal_settings, ohclv_data),
                                  'WILLIAMS_R': self.strategies_config('WILLIAMS_R', signal_settings, ohclv_data),
                                  'ATR': self.strategies_config('ATR', signal_settings, ohclv_data),
                                  'CMF': self.strategies_config('CMF', signal_settings, ohclv_data),
                                  'STOCH': self.strategies_config('STOCH', signal_settings, ohclv_data),
                                  'SAR': self.strategies_config('SAR', signal_settings, ohclv_data),
                                  'ichi_FUKUSHIMA': self.strategies_config('ichi_FUKUSHIMA', signal_settings,
                                                                           ohclv_data),
                                  'DMI': self.strategies_config('DMI', signal_settings, ohclv_data),
                                  'CUSTOM_INDICATOR': self.strategies_config('CUSTOM_INDICATOR', signal_settings,
                                                                             ohclv_data),
                                  'NEWS_SENTIMENT': self.strategies_config('NEWS_SENTIMENT', signal_settings,
                                                                           ohclv_data),
                                  'FOREX_NEWS': self.strategies_config('FOREX_NEWS', signal_settings, ohclv_data), }
                }

            return strategies

    def strategies_config(self, selected_strategy, signal_setting: dict, ohclv_data: DataFrame) -> dict:
        """
        Load and initialize strategies configuration
        :param selected_strategy:
        :param signal_setting:
        :param ohclv_data:
        :return:
        :param selected_strategy:
        :param signal_setting:
        :param ohclv_data:
        :return:
        """

        # Load and initialize strategies configuration
        _param = selected_strategy
        if _param == 'SMA_Crossover':
            self.logger.info("Loading SMA_Crossover strategy configuration...")
            return generate_sma_crossover_signal(signal_setting, ohclv_data)
        elif _param == 'Bollinger_Bands':
            self.logger.info("Loading Bollinger_Bands strategy configuration...")
            return generate_bollinger_bands_signal(signal_setting, ohclv_data)
        elif _param == 'MACD':
            self.logger.info("Loading MACD strategy configuration...")
            return generate_macd_signal(signal_setting, ohclv_data)
        elif _param == 'RSI':
            self.logger.info("Loading RSI strategy configuration...")
            return generate_rsi_signal(signal_setting, ohclv_data)
        elif _param == 'ADX':
            self.logger.info("Loading ADX strategy configuration...")
            return generate_adx_signal(signal_setting, ohclv_data)
        elif _param == 'EMA':
            self.logger.info("Loading EMA strategy configuration...")
            return generate_ema_signal(signal_setting, ohclv_data)
        elif _param == 'BBANDS':
            self.logger.info("Loading BBANDS strategy configuration...")
            return generate_bbands_signal(signal_setting, ohclv_data)
        elif _param == 'TRIX':
            self.logger.info("Loading TRIX strategy configuration...")
            return generate_trix_signal(signal_setting, ohclv_data)
        elif _param == 'PPO':
            self.logger.info("Loading PPO strategy configuration...")
            return generate_ppo_signal(signal_setting, ohclv_data)
        elif _param == 'KDJ':
            self.logger.info("Loading KDJ strategy configuration...")
            return generate_kdj_signal(signal_setting, ohclv_data)
        elif _param == 'AROON':
            self.logger.info("Loading AROON strategy configuration...")
            return generate_aroon_signal(signal_setting, ohclv_data)
        elif _param == 'UO':
            self.logger.info("Loading UO strategy configuration...")
            return generate_uo_signal(signal_setting, ohclv_data)
        elif _param == 'WILLIAMS_R':
            self.logger.info("Loading WILLIAMS_R strategy configuration...")
            return generate_willr_signal(signal_setting, ohclv_data)
        elif _param == 'ATR':
            self.logger.info("Loading ATR strategy configuration...")
            return generate_atr_signal(signal_setting, ohclv_data)
        elif _param == 'CMF':
            self.logger.info("Loading CMF strategy configuration...")
            return generate_cmf_signal(signal_setting, ohclv_data)
        elif _param == 'STOCH':
            self.logger.info("Loading STOCH strategy configuration...")
            return generate_stoch_signal(signal_setting, ohclv_data)
        elif _param == 'SAR':
            self.logger.info("Loading SAR strategy configuration...")
            return generate_sar_signal(signal_setting, ohclv_data)
        elif _param == 'ichi_FUKUSHIMA':
            self.logger.info("Loading ICHI_FUKUSHIMA strategy configuration...")
            return generate_ichimoku_signal(signal_setting, ohclv_data)
        elif _param == 'DMI':
            self.logger.info("Loading DMI strategy configuration...")
            return generate_dmi_signal(signal_setting, ohclv_data)
        elif _param == 'CUSTOM_INDICATOR':
            self.logger.info("Loading CUSTOM_INDICATOR strategy configuration...")
            return generate_custom_indicator_signal(signal_setting, ohclv_data)
        elif _param == 'NEWS_SENTIMENT':
            self.logger.info("Loading NEWS_SENTIMENT strategy configuration...")
            return self.generate_news_sentiment_signal(signal_setting, ohclv_data)
        elif _param == 'FOREX_NEWS':
            self.logger.info("Loading FOREX_NEWS strategy configuration...")
            return self.generate_forex_news_signal(signal_setting, ohclv_data)
        else:
            self.logger.error("Unsupported strategy: %s", _param)
            raise ValueError("Unsupported strategy: %s" % _param)

    def get_price(self, base_asset, counter_asset, side):
        #Fetch the current price of a given asset from live orderbook
        orderbook = self.get_orderbook(base_asset, counter_asset)
        if side == 'buy':
            return orderbook['asks'][0][0]
        elif side == 'sell':
            return orderbook['bids'][0][0]
        else:
            self.logger.error(f"Invalid side: {side}")
            return None

        #

    def get_orderbook(self, base_asset: Asset, counter_asset: Asset):
        # Fetch live orderbook for a given asset
        orderbook = self.orderbook(buying=base_asset, selling=counter_asset).limit(200).call()["records"]

        bids = [(float(order['price']), float(order['size'])) for order in orderbook if order['side'] == 'buy']
        asks = [(float(order['price']), float(order['size'])) for order in orderbook if order['side'] == 'sell']
        return {'bids': bids, 'asks': asks}

    def generate_news_sentiment_signal(self, signal_setting, ohclv_data):
        #  News sentiment strategy logic
        data = ohclv_data.copy()
        # Add news sentiment data to the dataframe here
        news = self.news_sentiment_data(
            xquery=signal_setting['base_asset']["code"])  # Replace with actual news sentiment data
        data['News_Sentiment'] = news['sentiment']  # Replace 'sentiment' with actual news sentiment column name
        data['News_Sentiment_Signal'] = np.where(data['News_Sentiment'] > signal_setting['overbought_threshold'], 1,
                                                 np.where(data['News_Sentiment'] < signal_setting['oversold_threshold'],
                                                          -1, 0))
        data['Position'] = data['News_Sentiment_Signal'].diff()
        return data[['close', 'News_Sentiment', 'News_Sentiment_Signal', 'Position']].tail(1).to_dict(orient='records')[
            0]

    def news_sentiment_data(self, xquery, rate_limit=10):
        """
        Fetch and process news sentiment data with rate limiting.

        :param xquery: The topic or keyword to search for news articles.
        :param rate_limit: The number of requests allowed per minute.
        :return: A list of dictionaries containing news articles and their sentiment scores.
        """
        news_url = "https://newsapi.org/v2/everything"
        api_key = "401ac9bf2f34448e876ff0426715db8f"  # Replace with your actual API key
        query1 = xquery or "bitcoin"  # Default to 'bitcoin' if no query is provided
        delay = 60 / rate_limit  # Calculate delay between requests to enforce rate limiting

        try:
            # Make a request to the news API
            response = requests.get(
                news_url,
                params={
                    "q": query1,  # Search query
                    "language": "en",  # Language filter
                    "apiKey": api_key  # API key
                },
            )

            # Raise an exception for HTTP errors
            response.raise_for_status()

            # Parse the JSON response
            articles = response.json().get("articles", [])
            sentiment_data = []

            for article in articles:
                # Enforce rate limiting between processing articles
                time.sleep(delay)

                # Extract the content and analyze sentiment
                content = article.get("content", "")
                title = article.get("title", "")
                description = article.get("description", "")
                text = f"{title}. {description}. {content}"

                # Sentiment analysis using TextBlob
                sentiment = TextBlob(text).sentiment.polarity

                sentiment_data.append({
                    "title": title,
                    "description": description,
                    "content": content,
                    "sentiment": sentiment,
                })
                # Log the fetched article and its sentiment score
                self.logger.info(f"Fetched article: {title} - Sentiment: {sentiment}")

            return pd.DataFrame(sentiment_data)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching news sentiment data: {e}")
            return []
        except Exception as ex:
            self.logger.error(f"An unexpected error occurred: {ex}")
            return []

    def generate_forex_news_signal(self, signal_setting, ohclv_data):
        #  Forex news strategy logic
        data = ohclv_data.copy()
        # Add forex news data to the dataframe here
        news = self.forex_news_data()  # Replace with actual forex news data
        data['Forex_News'] = news['sentiment']  # Replace'sentiment' with actual forex news sentiment column name
        data['Forex_News_Signal'] = np.where(data['Forex_News'] > signal_setting['overbought_threshold'], 1,
                                             np.where(data['Forex_News'] < signal_setting['oversold_threshold'], -1, 0))
        data['Position'] = data['Forex_News_Signal'].diff()
        return data[['close', 'Forex_News', 'Forex_News_Signal', 'Position']].tail(1).to_dict(orient='records')[0]

    def forex_news_data(self):
        # Fetch and process forex news data. from forex factory Api
        forex_news_url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json?version=380b2a9805f3b491b3e7c6e9d86e66c7"

        try:
            response = requests.get(
                forex_news_url,
                headers={

                },
            )
            # Raise an exception for HTTP errors
            response.raise_for_status()

            # Parse the JSON response
            news_data = response.json().get("data", {})
            news_articles = news_data.get("articles", [])
            sentiment_data = []

            for article in news_articles:
                # Extract the content and analyze sentiment
                content = article.get("content", "")
                sentiment = TextBlob(content).sentiment.polarity

                sentiment_data.append({
                    "title": article.get("title", ""),
                    "date": article.get("date", ""),
                    "sentiment": article.get("impact", ""),
                    "forecast": article.get("forecast", ""),
                    "previous": article.get("previous", "")})
                self.logger.info(f"Fetched forex news article: {article['title']} - Sentiment: {sentiment}")
            return pd.DataFrame(sentiment_data)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching forex news data: {e}")
        return []




    def get_all_assets(self, max_page=10, limit_per_page=200):
        """Fetch all assets from the Stellar network with pagination."""
        try:
            all_assets = []
            cursor = None
            page_count = 0

            # Loop through the pages and fetch assets
            while page_count < max_page:
                params = {'limit': limit_per_page, 'order': 'asc'}

                if cursor:
                    params['cursor'] = cursor

                # Make the request to fetch assets
                response = self.process_request(self.endpoint, params)
                self.last_request_time = time.time()  # Update the last request time

                # Check if the response is valid
                if not response or response.status_code != 200:
                    self.logger.error(f"Error fetching assets: {response}")
                    return pd.DataFrame()  # Return an empty DataFrame if request failed

                # Parse the JSON response
                data = response.json()

                # Check if data is in the expected format
                if '_embedded' in data and 'records' in data['_embedded']:
                    assets = data['_embedded']['records']
                    all_assets.extend(assets)  # Append assets to the list

                    # Get the cursor for the next page if available
                    cursor = data['_links'].get('next', {}).get('href', None)
                    if not cursor:  # If there is no next page, stop the loop
                        break

                    page_count += 1
                else:
                    self.logger.error(f"Invalid response format: {data}")
                    break

            # If we have assets, process them into a DataFrame
            if all_assets:
                assets_df = pd.json_normalize(all_assets)  # Normalize JSON data into a DataFrame
                assets_df.fillna("", inplace=True)  # Replace NaN with empty strings for better readability
                return assets_df
            else:
                self.logger.warning("No assets found.")
                return pd.DataFrame()

        except Exception as e:
            self.logger.error(f"Error retrieving assets: {e}")
            return pd.DataFrame()  # Return an empty DataFrame if request failed

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
        url = f"{"//horizon.stellar.org"}/{path}"
        response = requests.get(url, params=params)
        if response.status_code != 200:
            self.logger.error(f"Failed to fetch data: {response.status_code} - {response.text}")
            raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")
        return response

    def balances(self):
        """Fetch and process balances from the Stellar network."""

        self.endpoint = "/accounts"
        self.order = "asc"
        params = {
            'account_id': self.account_id,  # Replace it with your Stellar account ID
            'limit': 100,  # Stellar API limits to 100 accounts per page
            'order': self.order
        }
        response = self.process_request(self.endpoint, params)
        self.last_request_time = time.time()  # Update the last request time
        if response is None or response.status_code != 200:
            self.logger.error(f"Error fetching balances: {response}")
            return pd.DataFrame()  # Return an empty DataFrame if request failed
        data = response.json()
        if isinstance(data, dict) and '_embedded' in data and 'records' in data['_embedded']:
            # Process the records and append them to the DataFrame
            balances_df = pd.json_normalize(data['_embedded']['records'])

            # Replace NaN with empty strings for better readability
            balances_df.fillna("", inplace=True)
            return balances_df

    def get_account_details(self):
        """Fetch and process account details from the Stellar network."""
        self.endpoint = f"/accounts/{self.account_id}"
        response = self.process_request(self.endpoint, {})
        self.last_request_time = time.time()  # Update the last request time
        if response is None or response.status_code != 200:
            self.logger.error(f"Error fetching account details: {response}")
            return pd.DataFrame()  # Return an empty DataFrame if request failed
        data = response.json()
        if isinstance(data, dict):
            # Process the record and append it to the DataFrame
            account_details_df = pd.DataFrame(data, index=[0])

            # Replace NaN with empty strings for better readability
            account_details_df.fillna("", inplace=True)
            return account_details_df

    def listen_status(self):
        while True:

            if self.server_msg['status'] == 'START' or self.server_msg['status'] == 'WAIT' or not self.server_msg[
                                                                                                      'status'] == 'ERROR':
                self.start()
                time.sleep(5)
            elif self.server_msg['status'] == 'STOP':
                self.stop()
                time.sleep(5)
            else:
                continue

    def create_trusted_line(self, asset: Asset):
        """Create a new trustline on the Stellar network."""
        self.endpoint = "/accounts/{}/trustlines".format(self.account_id)
        data = {
            "asset_type": asset.type,
            "asset_code": asset.code,
            "asset_issuer": asset.issuer,
            "limit": "100000000"  # Set the maximum limit to 100,000,000
        }
        response = self.process_request(self.endpoint, data)
        self.last_request_time = time.time()  # Update the last request time
        if response is None or response.status_code != 201:
            self.logger.error(f"Error creating trustline: {response}")
            return False
        return True
