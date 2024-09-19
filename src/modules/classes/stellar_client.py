import os
import time
from tkinter import messagebox
import qrcode
import logging
from threading import Thread
from stellar_sdk import Server, Keypair
from modules.classes.data_fetcher import DataFetcher
from modules.classes.trading_engine import TradingsEngine

class StellarClient:
    """
    StellarClient manages interactions with the Stellar blockchain network, including fetching market data, 
    executing trades, and managing accounts. It runs asynchronously in a background thread, allowing continuous 
    data fetching and trade execution.
    """

    def __init__(self, controller, account_id: str, secret_key: str):
        """
        Initialize StellarClient with account_id and secret_key.
        
        - controller: Main application controller
        - account_id (str): Stellar account ID
        - secret_key (str): Secret key for Stellar account
        """
        try:
            self.controller = controller
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)

            # Initialize account info and check credentials
            self.account_id = account_id
            self.secret_key = secret_key
            self.server_msg = {'message': 'N/A', 'status': 'OFF', 'info': 'N/A'}

            if not self.account_id or not self.secret_key:
                self.server_msg['message'] = 'Please provide an account ID and secret key'
                self.server_msg['status'] = 'error'
                raise ValueError("Missing account ID or secret key.")

            # Initialize Stellar Server
            self.server = Server(horizon_url="https://horizon.stellar.org")
            self.account = self.server.load_account(self.account_id)

            # Initialize data fetching and trading components
            self.data_fetcher = DataFetcher(self.server)
            self.keypair = Keypair.from_secret(self.secret_key)
            self.trading_engine = TradingsEngine(server=self.server,account_id=self.account_id, keypair=self.keypair, account=self.account, controller=controller,server_msg= self.server_msg)

            # Manage background thread for trading
            self.keep_running = False
            self.server_thread = None
            self.time_frame_selected = '1h'

            # Log initialization success
            self.logger.info(f"Initialized StellarClient with account: {self.account_id}")
            self.server_msg['status'] = 'Started'
            self.server_msg['info'] = 'Server started successfully'
        except Exception as e:
            self.logger.error(f"Error initializing StellarClient: {e}")
            messagebox.showerror("Initialization Error", str(e))
            raise e

    def start(self):
        """Start Stellar Client in a background thread for continuous data fetching and trading."""
        if not self.keep_running:
            self.keep_running = True
            self.server_thread = Thread(target=self.run)
            self.server_thread.daemon = True
            self.server_thread.start()
            self._update_server_status("StellarBot started", 'Running', 'Trading started.')
        else:
            self.logger.warning("StellarBot is already running.")
            self.server_msg['message'] = 'StellarBot is already running'
            self.server_msg['status'] = 'Running'

    def stop(self):
        """Stop Stellar Client and gracefully shut down the trading thread."""
        self.keep_running = False
        self.server_msg['info'] = 'Stopping server...'
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()
        self._update_server_status("StellarBot stopped", 'Stopped', 'Trading stopped.')

    def _update_server_status(self, log_message: str, status: str, user_message: str):
        """Update server status in logs and messages."""
        self.logger.info(log_message)
        self.server_msg['status'] = status
        self.server_msg['message'] = user_message

    def run(self):
        """Main loop for continuously fetching market data and executing trading strategies."""
        self.logger.info("StellarClient run loop started.")
        retry_count = 0
        max_retries = 3
        self.server_msg['message'] = 'Trade decision started'

        while self.keep_running:
            try:
                # Execute trading strategy
                self.trading_engine.execute_trading_strategy(self.time_frame_selected)
                time.sleep(1)  # Control the loop's execution pace
                retry_count = 0  # Reset retries on successful execution
            except Exception as e:
                self.logger.error(f"Error during run loop: {e}")
                self.server_msg['message'] = f"Error during run loop: {e}"
                self.server_msg['status'] = 'Error'

                retry_count += 1
                if retry_count >= max_retries:
                    self.logger.error("Max retries reached, stopping StellarBot.")
                    self.stop()  # Stop StellarBot after max retries
                    break
                else:
                    time.sleep(5)  # Wait before retrying

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
