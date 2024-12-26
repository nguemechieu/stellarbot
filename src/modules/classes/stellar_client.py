import logging
import time
from threading import Thread, Lock
from tkinter import messagebox

import qrcode
from stellar_sdk import Server, Keypair

from src.modules.classes.trading_engine import TradingEngine


class StellarClient:
    """
    StellarClient manages interactions with the Stellar blockchain network, including fetching market data,
    executing trades, and managing accounts. It runs asynchronously in a background thread, allowing continuous
    data fetching and trade execution.
    """
    def __init__(self, controller=None):
        """
        Initialize StellarClient with account_id and secret_key.
        - controller: Main application controller
        - horizon_url (str): Stellar Horizon server URL (default is public network)
        """



        try:
            self.controller = controller
            self.logger = controller.logger
            self.horizon_url="https://horizon.stellar.org"
            # Setup file logging
            handler = logging.FileHandler("stellar_client.log")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

            # Thread lock
            self.lock = Lock()

            # Initialize Stellar Server
            self.server = Server(horizon_url=self.horizon_url)

            # Initialize account info and check credentials
            self.account_id = self.controller.account_id
            self.secret_key = self.controller.secret_key
            self.server_msg = self.controller.server_msg
            self.logger.debug("Validating credentials...")
            if not self._validate_credentials():
                self.logger.error("Credentials validation failed.")
                self.server_msg['message'] = 'Initialization failed: Invalid credentials'
                self.server_msg['status'] = 'Error'
                return
            self.account = self.server.load_account(account_id=self.account_id)
            # Initialize data fetching and trading components
            self.keypair = Keypair.from_secret(self.secret_key)
            # Manage background thread for trading
            self.keep_running = False
            self.trading_engine = TradingEngine(controller=self.controller)


            # Log initialization success
            self.logger.info(f"Initialized StellarClient with account: {self.account_id}")
            self.server_msg['status'] = 'Started'
            self.server_msg['info'] = 'Server started successfully'
            self.server_thread = Thread(target=self.run)


        except Exception as e:
            self.logger.error(f"Error initializing StellarClient: {e}")
            messagebox.showerror("Initialization Error", str(e))
            raise e

    def _validate_credentials(self):
        """Validate account ID and secret key."""
        if not self.account_id or not self.secret_key:
            self.server_msg['message'] = 'Please provide an account ID and secret key'
            self.server_msg['status'] = 'Error'
            self.logger.error("Invalid credentials: account_id and secret_key are required")
            return False
        return True

    def start(self):
        """Start Stellar Client in a background thread for continuous data fetching and trading."""
        with self.lock:
            if not self.keep_running:
                self.keep_running = True
                self.server_thread.daemon = self.keep_running
                self.server_thread.start()

                self._update_server_status("StellarBot started", 'RUNNING', 'Trading started.')
            else:
                self.logger.warning("StellarBot is already running.")
                self.server_msg['message'] = 'StellarBot is already running'
                self.server_msg['status'] = 'RUNNING'

    def stop(self):
        """Stop Stellar Client and gracefully shut down the trading thread."""
        with self.lock:
            self.logger.info("Stopping StellarClient...")

            self.keep_running = False
            self.server_msg['info'] = 'Stopping server...'
            if self.server_thread and self.server_thread.is_alive():
                self.server_thread.join()
                self.server_thread=None
                self.server_msg['message'] = 'StellarBot stopped'
            self._update_server_status("StellarBot stopped", 'Stopped', 'Trading stopped.')
            self.logger.info("StellarBot stopped")

    def _update_server_status(self, log_message: str, status: str, user_message: str):
        """Update server status in logs and messages."""
        with self.lock:
            self.logger.info(log_message)
            self.server_msg['status'] = status
            self.server_msg['message'] = user_message

    def run(self):
        """Main loop for continuously fetching market data and executing trading strategies."""
        self.logger.info("StellarClient run loop started.")

        retry_count = 0
        max_retries = 3
        self.server_msg['message'] = 'Trade decision started'
        self.server_msg['status'] = 'RUNNING'
        retry_delay = 5

        while self.keep_running:
            try:
                self.trading_engine.execute_trading_strategy()
                retry_count = 0
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Error during run loop: {e}")
                self.server_msg['message'] = f"Error during run loop: {e}"
                self.server_msg['status'] = 'Error'

                retry_count += 1
                if retry_count >= max_retries:
                    self.logger.error("Max retries reached, stopping StellarBot.")
                    self.stop()
                    break
                delay = min(retry_delay * (2 ** retry_count), 60)
                self.logger.warning(f"Retrying in {delay} seconds...")
                time.sleep(delay)

        self.logger.info("StellarClient run loop stopped")
        self.server_msg['status'] = 'Idle'

    def generate_qr_code(self):
        """Generate a QR code for the account ID."""
        try:
            qr = qrcode.make(self.account_id)
            qr.save(f"{self.account_id}_qr.png")
            self.logger.info(f"QR Code generated for account: {self.account_id}")
        except Exception as e:
            self.logger.error(f"Error generating QR Code: {e}")
            self.server_msg['message'] = f"Error generating QR Code: {str(e)}"

    def is_alive(self):
        """Check if the StellarClient is running."""
        with self.lock:
            return self.keep_running

    def get_trading_signals(self):
        """Fetch trading signals from the trading engine."""
        try:
            symbols = self.get_assets()
            if not symbols:
                self.logger.warning("No assets found for account")
                self.server_msg['message'] = 'No assets found for account'

                return []

            trading_pairs = [(symbol.code, symbol.counterparty) for symbol in symbols]
            signals = [self.trading_engine.data_fetcher.get_trading_signals(pair[0], pair[1]) for pair in trading_pairs]
            return signals
        except Exception as e:
            self.logger.error(f"Error fetching trading signals: {e}")
            self.server_msg['message'] = f"Error fetching trading signals: {str(e)}"
            return []


    def get_account(self):
        """Fetch account balance."""
        try:
            accounts = self.server.accounts().call()
            return accounts

        except Exception as e:
            self.logger.error(f"Error fetching account balance: {e}")
            self.server_msg['message'] = f"Error fetching account: {str(e)}"
            return None

    def get_assets(self ):
        """Fetch account assets."""
        try:
            assets = self.server.assets().call()["_embedded"][ "records"]

            # Filter out assets that are not valid
            assets = [asset for asset in assets if asset["asset_type"] == "credit_alphanum4"]

            # Sort assets by asset code
            assets.sort(key=lambda x: x["asset_code"])

            return assets

        except Exception as e:
            self.logger.error(f"Error fetching account assets: {e}")
            self.server_msg['message'] = f"Error fetching account assets: {str(e)}"
            return None

    def get_effects(self):
        """Fetch account effects."""
        try:
            effects = self.server.effects().call()["_embedded"][ "records"]
            return effects

        except Exception as e:
            self.logger.error(f"Error fetching account effects: {e}")
            self.server_msg['message'] = f"Error fetching account effects: {str(e)}"
            return None

    def get_offers(self):
        """Fetch account offers."""
        try:
            offers = self.server.offers().call()["_embedded"][ "records"]
            return offers

        except Exception as e:
            self.logger.error(f"Error fetching account offers: {e}")
            self.server_msg['message'] = f"Error fetching account offers: {str(e)}"
            return None


    def get_transactions(self):
        """Fetch account transactions."""
        try:
            transactions = self.server.transactions().call()["_embedded"][ "records"]
            return transactions

        except Exception as e:
            self.logger.error(f"Error fetching account transactions: {e}")
            self.server_msg['message'] = f"Error fetching account transactions: {str(e)}"
            return None