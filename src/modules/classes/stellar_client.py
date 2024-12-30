import asyncio
import threading

from stellar_sdk import Network, TransactionBuilder, Asset, Keypair

from src.modules.classes.smart_trading_bot import SmartTradingBot


class StellarClient(SmartTradingBot):
    """
    StellarClient manages interactions with the Stellar blockchain network, including fetching market data,
    executing trades, and managing accounts. It runs asynchronously, allowing continuous
    data fetching, trade execution, and event-driven actions.
    """

    def __init__(self, controller):
        """
        Initializes the StellarClient with essential components and starts the event loop.

        Parameters:
        controller (object): The application controller that provides access to the bot, logger, and server message.
        """
        super().__init__(controller=controller)

        # Initialize logging and server message
        self.logger = controller.logger
        self.server_msg = self.controller.server_msg

        # Log initial setup
        self.logger.info("StellarClient initialized.")

        # Initialize necessary components
        self.controller = controller  # Access to the application controller
        self.network = Network.PUBLIC_NETWORK_PASSPHRASE  # Default Stellar network
        self.event_listeners = {}  # Dictionary for managing event listeners
        self.loop = asyncio.get_event_loop()  # Event loop for async operations
        self.running = True  # Flag to stop the background tasks

        # Start the event loop in a background thread
        threading.Thread(target=self.run_event_loop, daemon=True).start()

    def run_event_loop(self):
        """
        Starts the event loop asynchronously in a separate thread.
        """
        try:
            self.loop.run_until_complete(self.start())
            self.loop.run_forever()
        except Exception as e:
            self.logger.error(f"Error in event loop: {e}")

    async def fetch_account_data(self, account_id):
        """
        Asynchronously fetch account details from Stellar network.

        Parameters:
        account_id (str): The Stellar account ID to fetch data for.

        Returns:
        dict: Account details such as balances, operations, and transactions.
        """
        try:
            account = await self.accounts().account_id(account_id).call()
            self.logger.info(f"Fetched account data for {account_id}")
            return account
        except Exception as e:
            self.logger.error(f"Error fetching account data for {account_id}: {str(e)}")
            return None

    async def fetch_market_data(self, base_asset_code='XLM', counter_asset_code='USDC'):
        """
        Asynchronously fetch market data for a given asset pair.

        Parameters:
        base_asset_code (str): The base asset code (e.g., 'XLM').
        counter_asset_code (str): The counter asset code (e.g., 'USDC').

        Returns:
        dict: Market data such as bid/ask prices, order book, etc.
        """
        try:
            # Simulating market data fetching, adjust based on actual API
            market_data = {
                'base_asset': base_asset_code,
                'counter_asset': counter_asset_code,
                'bid_price': 0.3,  # Example data, replace with real market data fetch
                'ask_price': 0.35  # Example data, replace with real market data fetch
            }
            self.logger.info(f"Fetched market data for {base_asset_code}/{counter_asset_code}")
            return market_data
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return None

    async def execute_trade(self, account_id, base_asset, counter_asset, amount, action='buy'):
        """
        Asynchronously executes a trade on the Stellar network (buy/sell).

        Parameters:
        account_id (str): The Stellar account ID initiating the trade.
        base_asset (Asset): The base asset for the trade.
        counter_asset (Asset): The counter asset for the trade.
        amount (float): The amount of the base asset to buy/sell.
        action (str): 'buy' or 'sell' action.

        Returns:
        bool: True if the trade is successful, False otherwise.
        """
        try:
            # Fetch account data
            account = await self.fetch_account_data(account_id)
            if not account:
                self.logger.error("Account data could not be fetched.")
                return False

            # Build the transaction
            transaction = TransactionBuilder(
                source_account=account,
                network_passphrase=self.network
            )

            if action == 'buy':
                # Add the 'buy' operation (buying base asset with counter asset)
                transaction.append_payment_op(destination=account_id, asset=counter_asset, amount=amount)
            elif action == 'sell':
                # Add the 'sell' operation (selling base asset for counter asset)
                transaction.append_payment_op(destination=account_id, asset=base_asset, amount=amount)
            else:
                self.logger.error(f"Invalid trade action: {action}")
                return False

            # Sign and submit the transaction
            transaction.build().sign(Keypair.random())  # Using a random keypair for simplicity
            response = self.submit_transaction(transaction.build())
            self.logger.info(f"Trade {action} executed: {response}")
            return True
        except Exception as e:
            self.logger.error(f"Error executing trade {action}: {str(e)}")
            return False

    async def monitor_account(self, account_id, interval=60):
        """
        Asynchronously monitors the account's balance and performs actions (e.g., fetch market data, execute trades) at regular intervals.

        Parameters:
        account_id (str): The Stellar account ID to monitor.
        interval (int): Interval in seconds between each monitoring cycle.
        """
        while self.running:
            # Fetch the latest account data
            account_data = await self.fetch_account_data(account_id)
            if account_data:
                self.logger.info(f"Monitoring account {account_id}: {account_data['balances']}")

            # Optionally fetch market data or execute trades
            market_data = await self.fetch_market_data('XLM', 'USDC')
            if market_data:
                self.logger.info(f"Market data: {market_data}")
                # Execute a trade based on market conditions
                await self.execute_trade(account_id, Asset.native(), Asset('USDC', 'GDUQX26QZNOI6KNLFLFSI35VBGIY5YQ6HHYQF5LPJ6XHNE7ZYEBJ7Y67'),
                                         100, action='buy')

            # Wait for the next cycle
            await asyncio.sleep(interval)

    def start_monitoring(self, account_id):
        """
        Starts the asynchronous monitoring of the account in a background thread.

        Parameters:
        account_id (str): The Stellar account ID to monitor.
        """
        # Start monitoring the account in an async event loop
        self.loop.create_task(self.monitor_account(account_id))

    def stop_monitoring(self):
        """
        Stops monitoring the account.
        """
        self.running = False  # Set the flag to stop monitoring
        self.logger.info("Stopping account monitoring.")

    def send_alert(self, message):
        """
        Sends a message via Telegram bot to alert the user.

        Parameters:
        message (str): The message to send to the user.
        """
        if self.telegram:
            self.telegram.send_message(message)
            self.logger.info(f"Sent Telegram alert: {message}")
        else:
            self.logger.warning("Telegram bot is not initialized.")

    def add_event_listener(self, event_name, callback):
        """
        Adds an event listener for a specific event.

        Parameters:
        event_name (str): The name of the event to listen for.
        callback (function): The function to call when the event is triggered.
        """
        if event_name not in self.event_listeners:
            self.event_listeners[event_name] = []
        self.event_listeners[event_name].append(callback)
        self.logger.info(f"Event listener added for {event_name}")

    def trigger_event(self, event_name, data=None):
        """
        Triggers an event, notifying all listeners of the event.

        Parameters:
        event_name (str): The name of the event to trigger.
        data (any): The data to pass to the event listeners.
        """
        if event_name in self.event_listeners:
            for callback in self.event_listeners[event_name]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error triggering event {event_name}: {e}")

    def remove_event_listener(self, event_name, callback):
        """
        Removes a specific event listener for a given event.

        Parameters:
        event_name (str): The name of the event.
        callback (function): The function to remove from the event listeners.
        """
        if event_name in self.event_listeners and callback in self.event_listeners[event_name]:
            self.event_listeners[event_name].remove(callback)
            self.logger.info(f"Event listener removed for {event_name}")
