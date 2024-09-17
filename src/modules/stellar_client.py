import os
import time
import qrcode
import logging
from threading import Thread
from stellar_sdk import Server, Keypair
from src.modules.classes.data_fetcher import DataFetcher
from src.trading_engine import TradingEngine

class StellarClient:
    """
    The StellarClient class is responsible for managing interactions with the Stellar blockchain network, 
    including fetching market data, executing trades, and managing accounts. It runs asynchronously in a 
    background thread, allowing continuous data fetching and trade execution.
    """
    
    def __init__(self, controller, account_id: str, secret_key: str):
        """
        Initialize the StellarClient instance with the provided account ID and secret key.

        Parameters:
        - controller: A reference to the main application controller.
        - account_id (str): The Stellar account ID used for transactions.
        - secret_key (str): The secret key used to authenticate transactions on the Stellar network.

        The StellarClient initializes a Stellar server connection, handles QR code generation for the account, 
        and prepares for trading and data fetching by initializing the database and trading engine components.
        """
        try:
            self.controller = controller  # Reference to the main application controller
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            self.db_path = "stellarBot.db"
            self.server_msg = {'message': 'N/A', 'status': 'OFF', 'info': 'N/A'}
            
            # Initialize database manager
           
            self.account_id = account_id
            self.secret_key = secret_key

            # Initialize Stellar Server
            self.server = Server(horizon_url="https://horizon.stellar.org")
            self.keypair = Keypair.from_secret(self.secret_key)
            self.account = self.server.load_account(self.account_id)

            # Data fetching and trading logic components
            self.data_fetcher = DataFetcher(self.server)
            self.trading_engine = TradingEngine(self.server, self.keypair, self.account, controller, self.server_msg)
            
            # Thread management
            self.keep_running = False
            self.server_msg['status'] = 'In Progress'
            self.server_thread = None
            self.time_frame_selected = '1h'

            # Generate QR code for the account
            if self.account_id is not None:
                self.generate_qr_code(account_id=self.account_id)

            self.logger.info(f"Initialized StellarClient with account: {self.account_id}")
            self.server_msg['status'] = 'Started'
        except Exception as e:
            self.logger.error(f"Error initializing StellarClient: {e}")
            self.controller.show_error_message(f"Error initializing StellarClient: {str(e)}")
            raise e

    def start(self):
        """
        Start the Stellar Client by initiating the background thread that continuously fetches market data
        and executes trading strategies. This method prevents multiple instances of the client from running simultaneously.
        """
        if not self.keep_running:
            self.keep_running = True
            self.server_thread = Thread(target=self.run)
            self.server_thread.daemon = True
            self.server_thread.start()  # Start the background thread
            self._update_server_status(
                "StellarClient started", 'Running', 'Trading started...!'
            )
        else:
            self.logger.warning("StellarClient is already running")
            self.server_msg['message'] = 'StellarClient is already running'
            self.server_msg['status'] = 'Running'

    def stop(self):
        """
        Stop the Stellar Client by terminating the background thread that fetches data and executes trades. 
        This method ensures the client is safely shut down.
        """
        self.keep_running = False
        self.server_msg['info'] = 'Stopping server...'
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()  # Ensure the thread exits cleanly
        self._update_server_status(
            "StellarClient stopped", 'Stopped', 'Trading stopped.'
        )

    def _update_server_status(self, log_message: str, status: str, user_message: str):
        """
        Update the server status and log messages.

        Parameters:
        - log_message (str): The message to log.
        - status (str): The updated status of the server.
        - user_message (str): A message to display to the user.
        """
        self.logger.info(log_message)
        self.server_msg['status'] = status
        self.server_msg['message'] = user_message

    def run(self):
        """
        Run the Stellar Client in a loop to continuously fetch market data and execute trading strategies.
        The loop continues as long as the 'keep_running' flag is set to True.
        """
        self.logger.info("StellarClient run loop started")
        self.server_msg['message'] = 'Trade decision started'
        count =0
        while self.keep_running:
            try:
                count += 1
                # Execute trading strategy
                self.trading_engine.execute_trading_strategy(self.time_frame_selected)
                time.sleep(1)  # Wait for 1 second before the next iteration
            except Exception as e:
                self.logger.error(f"Error during run loop: {e}")
                self.server_msg['message'] = f"Error during run loop: {e}"
                self.server_msg['status'] = 'Error'
                break

            self.logger.info("StellarClient run loop stopped")
            self.server_msg['message'] = f'Idle{count}'
             
    def generate_qr_code(self, account_id: str):
        """
        Generate a QR code for the provided Stellar account ID and save it as an image.

        Parameters:
        - account_id (str): The Stellar account ID to encode in the QR code.

        The generated QR code image is saved in the specified file path.
        """
        try:
            return self._extracted_from_generate_qr_code_11(account_id)
        except Exception as e:
            self.logger.error(f"Error generating QR code: {e}")
            self.server_msg['message'] = f'Error generating QR code: {str(e)}'
            return None

    # TODO Rename this here and in `generate_qr_code`
    def _extracted_from_generate_qr_code_11(self, account_id):
        file_path = "src/images/account_id.png"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(account_id)
        qr.make(fit=True)

        qr_code_image = qr.make_image(fill="black", back_color="white")

        # Ensure the directory exists before saving the QR code image
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        qr_code_image.save(file_path)

        self.logger.info(f"QR code generated and saved to {file_path}")
        return qr_code_image
