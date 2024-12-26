import logging
import re
from typing import Optional, List, Dict, Tuple

from stellar_sdk import TransactionBuilder, Network
from src.modules.classes.data_fetcher import DataFetcher


def extract_n_d(price_ratio_str: str) -> Optional[Tuple[int, int]]:
    """Extract numerator and denominator from the price ratio string."""
    match = re.search(r"\{'n': (\d+), 'd': (\d+)}", price_ratio_str)
    if match:
        return int(match[1]), int(match[2])
    return None


def parse_order_data(orders: List[Dict]) -> List[Dict]:
    """Parse order data and return structured bid/ask information."""
    parsed_orders = []
    for order in orders:
        try:
            price = float(order.get('price', 0))
            amount = float(order.get('amount', 0))
            price_ratio_str = order.get('price_r', '')

            if amount <= 0 or price <= 0:
                continue

            n, d = extract_n_d(price_ratio_str) or (None, None)
            price_ratio = float(n / d) if d else price

            parsed_orders.append({'price_ratio': price_ratio, 'price': price, 'amount': amount})
        except Exception as e:
            logging.error(f"Error parsing order data: {e}")
    return parsed_orders


class TradingEngine:
    def __init__(self, controller=None):
        self.logger = controller.logger
        self.controller = controller
        self.server = controller.server
        self.keypair = controller.keypair
        self.account = controller.account
        self.base_asset = controller.base_asset
        self.counter_asset = controller.counter_asset
        self.transaction_builder = TransactionBuilder(
            self.account, network_passphrase=Network.TESTNET_NETWORK_PASSPHRASE
        )
        self.amount = controller.amount
        self.price = controller.price
        self.offer_id = 0
        self.trade_signal = 0
        self.order_book = {'bids': [], 'asks': []}
        self.data_fetcher = DataFetcher(self.server)

        self.logger.info("Trading Engine initialized.")
        self.controller.server_msg['message'] = 'Trading Engine initialized.'

    def fetch_order_book(self):
        """Fetch and parse the order book from the Stellar network."""
        try:
            raw_order_book = self.server.orderbook(self.base_asset, self.counter_asset).call()
            self.order_book = {
                'bids': parse_order_data(raw_order_book.get('bids', [])),
                'asks': parse_order_data(raw_order_book.get('asks', []))
            }
            self.logger.info("Order book successfully fetched.")
            self.controller.server_msg['message'] = 'Order book successfully fetched.'
        except Exception as e:
            self.logger.error(f"Error fetching order book: {e}")
            self.controller.server_msg['message'] = f"Error fetching order book: {e}"
            self.order_book = {'bids': [], 'asks': []}

    def calculate_trade_signal(self):
        """Calculate the trade signal based on bid-ask spread."""
        try:
            bids = self.order_book.get('bids', [])
            asks = self.order_book.get('asks', [])
            if not bids or not asks:
                self.logger.warning("No bids or asks available to calculate trade signal.")
                self.controller.server_msg['message'] = 'No bids or asks available to calculate trade signal.'
                return

            bid_price = bids[0]['price']
            ask_price = asks[0]['price']
            spread = ask_price - bid_price

            self.trade_signal = 1 if spread > 0.005 else -1
            self.logger.info(f"Trade signal generated: {self.trade_signal}")
            self.controller.server_msg['message'] = f"Trade signal generated: {self.trade_signal}"
        except Exception as e:
            self.logger.error(f"Error calculating trade signal: {e}")
            self.controller.server_msg['message'] = f"Error calculating trade signal: {e}"

    def execute_trade(self):
        """Execute a trade based on the calculated trade signal."""
        if self.trade_signal == 1:
            self.buy_asset()
        elif self.trade_signal == -1:
            self.sell_asset()
        else:
            self.logger.info("No valid trade signal to execute.")
            self.controller.server_msg['message'] = 'No valid trade signal to execute.'

    def buy_asset(self):
        """Submit a buy offer."""
        try:
            self.transaction_builder.append_manage_buy_offer_op(
                buying=self.base_asset,
                selling=self.counter_asset,
                amount=str(self.amount),
                price=str(self.price),
                offer_id=self.offer_id
            )
            self.submit_transaction("Buy transaction executed.")
            self.logger.info("Buy transaction executed.")
            self.offer_id += 1  # Update offer ID for subsequent transactions
            self.price -= 0.0001  # Update price for subsequent transactions to maintain price ratio
            self.amount += 0.0001  # Update amount for subsequent transactions to maintain price ratio
            self.price = round(self.price, 8)  # Round the price to 8 decimal places
            self.amount = round(self.amount, 8)  # Round the amount to 8 decimal places
            self.logger.info("Buy transaction executed with updated price and amount.")
            self.controller.server_msg['message'] = "Buy transaction executed with updated price and amount."


        except Exception as e:
            self.logger.error(f"Error executing buy transaction: {e}")
            self.controller.server_msg['message'] = f"Error executing buy transaction: {e}"

    def sell_asset(self):
        """Submit a sell offer."""
        try:
            self.transaction_builder.append_manage_sell_offer_op(
                buying=self.counter_asset,
                selling=self.base_asset,
                amount=str(self.amount),
                price=str(self.price),
                offer_id=self.offer_id
            )
            self.submit_transaction("Sell transaction executed.")
            self.logger.info("Sell transaction executed.")
            self.offer_id += 1  # Update offer ID for subsequent transactions
            self.price += 0.0001  # Update price for subsequent transactions to maintain price ratio
            self.amount += 0.0001  # Update amount for subsequent transactions to maintain price ratio
            self.price = round(self.price, 8)  # Round the price to 8 decimal places
            self.amount = round(self.amount, 8)  # Round the amount to 8 decimal places
            self.logger.info("Sell transaction executed with updated price and amount.")
            self.controller.server_msg['message'] = "Sell transaction executed with updated price and amount."
        except Exception as e:
            self.logger.error(f"Error executing sell transaction: {e}")
            self.controller.server_msg['message'] = f"Error executing sell transaction: {e}"

    def submit_transaction(self, message: str):
        """Build and submit the transaction to the Stellar network."""
        try:
            transaction = self.transaction_builder.build()
            transaction.sign(self.keypair)
            response = self.server.submit_transaction(transaction)
            self.logger.info(f"{message} Response: {response}")
            self.controller.server_msg['message'] = f"{message} Response: {response}"
        except Exception as e:
            self.logger.error(f"Transaction submission failed: {e}")
            self.controller.server_msg['message'] = f"Transaction submission failed: {e}"

    def execute_trading_strategy(self):
        """Execute the trading strategy based on the selected time frame."""
        self.fetch_order_book()
        self.calculate_trade_signal()
        self.execute_trade()

