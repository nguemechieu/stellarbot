from __future__ import annotations
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Callable

import pandas as pd
from stellar_sdk import (
    Server, Asset, Keypair, TransactionBuilder, Network,
    ManageSellOffer, exceptions as stellar_exceptions
)
from ta.momentum import RSIIndicator
from ta.trend import MACD


# ===============================================================
# EVENT SYSTEM
# ===============================================================
class EventListener:
    def __init__(self):
        self._subs: Dict[str, List[Callable]] = {}

    def subscribe(self, name: str, fn: Callable):
        self._subs.setdefault(name, []).append(fn)

    def notify(self, name: str, data=None):
        for fn in self._subs.get(name, []):
            try:
                fn(name, data)
            except Exception as e:
                print(f"[Event Error] {fn}: {e}")


# ===============================================================
# SMARTBOT (with Backtesting)
# ===============================================================
class SmartBot:
    """Automated Stellar trading bot with real transaction execution and backtesting."""

    VALID_RESOLUTIONS = [60000, 300000, 900000, 3600000, 86400000, 604800000]

    def __init__(self, controller, test_mode: bool = True):

        self.controller = controller
        self.logger = self._setup_logger()
        self.last_tx_update =  time.time()

        # Stellar setup
        self.server = Server("https://horizon.stellar.org")
        self.account_id = controller.account_id
        self.secret_key = controller.secret_key
        self.keypair = Keypair.from_secret(self.secret_key)


        # Flags
        self.test_mode = test_mode
        self.running = False
        self.interval_seconds = 60
        self.resolution = 3600000  # 1h default

        # Assets
        self.selling = Asset.native()
        self.buying = Asset("USDC", "GDMTVHLWJTHSUDMZVVMXXH6VJHA2ZV3HNG5LYNAZ6RTWB7GISM6PGTUV")



        # Thread control
        self.thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()


        # Data containers
        self.payments=pd.DataFrame()
        self._on_payments()
        self.offers_df=pd.DataFrame()
        self._on_offers()
        self.trade_pairs: List[Tuple[Asset, Asset]] = []
        self.market_data: Dict[str, pd.DataFrame] = {}
        self.trade_history = pd.DataFrame(columns=["pair", "side", "amount", "price", "result", "timestamp"])
        self.backtest_results = pd.DataFrame()

        self.accounts_balances_df=pd.DataFrame()
        self._on_account_balances()
        self.orders_df=pd.DataFrame()
        self._on_orders()
        self.liquidity_df=pd.DataFrame()
        self._on_liquidity_pool()
        self.transaction_df=pd.DataFrame()
        self._on_transactions()
        self.effects_df=pd.DataFrame()
        self._on_effects()
        self.ledger_df=pd.DataFrame()
        self._on_ledger()

        # Event system
        self.events = EventListener()
        self.events.subscribe("market_update", self._on_market_update)

        self.logger.info(f"✅ SmartBot initialized (test_mode={self.test_mode}).")
        self.events.notify("payments_update", {"count": len(self.payments_df)})

    # ===============================================================
    # LOGGING
    # ===============================================================
    def _setup_logger(self):
        self.logger = logging.getLogger("SmartBot")
        if not self.logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            self.logger.addHandler(h)
        self.logger.setLevel(logging.INFO)
        return self.logger

    # ===============================================================
    # THREAD CONTROL
    # ===============================================================
    def start(self):
        if self.running:
            self.logger.warning("SmartBot already running.")
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, name="SmartBotThread", daemon=True)
        self.thread.start()
        self.logger.info("🚀 SmartBot started.")

    def stop(self):
        self.running = False
        self.logger.info("🛑 Stopping SmartBot...")
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        self.logger.info("✅ SmartBot stopped.")

    # ===============================================================
    # MAIN LOOP
    # ===============================================================
    def _run_loop(self):
        try:
            self.trade_pairs = self._create_trading_pairs()
            self.logger.info(f"Trading {len(self.trade_pairs)} pairs.")
            while self.running:
                cycle_start = time.time()
                for base, quote in self.trade_pairs:
                    try:
                        pair_name = f"{base.code}/{quote.code}"
                        df = self._fetch_ohlcv(base, quote)
                        if df is not None and not df.empty:
                            self._apply_indicators(df)
                            signal = self._strategy_macd_rsi(df, pair_name)
                            if signal:
                                self.execute_trade(signal)
                    except Exception as e:
                        self.logger.error(f"Loop error for {base.code}/{quote.code}: {e}")

                elapsed = time.time() - cycle_start
                time.sleep(max(0, self.interval_seconds - elapsed))
        except Exception as e:
            self.logger.exception(f"Fatal bot error: {e}")
        finally:
            self.running = False
            self.logger.info("SmartBot loop exited safely.")

    # ===============================================================
    # STRATEGY
    # ===============================================================
    def _strategy_macd_rsi(self, df: pd.DataFrame, pair: str) -> Optional[dict]:
        """RSI + MACD crossover strategy."""
        last = df.iloc[-1]
        macd, signal, rsi = last["MACD"], last["Signal"], last["RSI"]
        if macd > signal and rsi < 30:
            return {"pair": pair, "side": "BUY", "amount": 10, "price": last["close"]}
        elif macd < signal and rsi > 70:
            return {"pair": pair, "side": "SELL", "amount": 10, "price": last["close"]}
        return None

    # ===============================================================
    # BACKTESTING
    # ===============================================================
    def backtest(self, base: Asset, quote: Asset, days: int = 7):
        """Run backtest over past `days` days for a given pair."""
        self.logger.info(f"🧠 Running backtest for {base.code}/{quote.code} over {days} days...")
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)

        df = self._fetch_ohlcv(base, quote, start_time, end_time)
        if df is None or df.empty:
            self.logger.warning("⚠️ No data for backtest.")
            return None

        self._apply_indicators(df)

        balance, position, pnl = 1000.0, 0.0, 0.0
        trade_log = []

        for i in range(1, len(df)):
            macd, signal, rsi = df.loc[i, "MACD"], df.loc[i, "Signal"], df.loc[i, "RSI"]
            close_price = df.loc[i, "close"]

            # Simple rule: buy on bullish crossover, sell on bearish
            if macd > signal and rsi < 30 and balance > 0:
                position = balance / close_price
                balance = 0
                trade_log.append(("BUY", close_price))
            elif macd < signal and rsi > 70 and position > 0:
                balance = position * close_price
                position = 0
                trade_log.append(("SELL", close_price))

        # Final PnL
        total_value = balance + position * df.iloc[-1]["close"]
        pnl = total_value - 1000.0
        roi = (total_value / 1000.0 - 1) * 100

        self.backtest_results = pd.DataFrame(trade_log, columns=["Action", "Price"])
        self.logger.info(f"💰 Backtest Result: PnL={pnl:.2f} XLM | ROI={roi:.2f}%")

        return {
            "pair": f"{base.code}/{quote.code}",
            "pnl": pnl,
            "roi": roi,
            "trades": len(trade_log),
            "final_value": total_value,
        }

    # ===============================================================
    # MARKET DATA
    # ===============================================================
    def _fetch_ohlcv(self, base: Asset, quote: Asset, start_time=None, end_time=None) -> Optional[pd.DataFrame]:
        try:
            if end_time is None:
                end_time = int(datetime.now().timestamp() * 1000)
            if start_time is None:
                start_time = end_time - 24 * 3600 * 1000

            if self.resolution not in self.VALID_RESOLUTIONS:
                self.logger.warning(f"⚠️ Invalid resolution {self.resolution}, defaulting to 1h (3600000).")
                self.resolution = 3600000

            data = self.server.trade_aggregations(
                base=base, counter=quote,
                start_time=start_time, end_time=end_time,
                resolution=self.resolution
            ).call()

            records = data.get("_embedded", {}).get("records", [])
            if not records:
                return pd.DataFrame()

            print(records)
            df = pd.DataFrame(records)
            df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].apply(pd.to_numeric)

            df["timestamp"] = pd.to_datetime(df["timestamp"].astype(float) / 1000, unit="s", utc=True)

            return df
        except Exception as e:
            self.logger.error(f"Fetch error: {e}")
            return None

    # ===============================================================
    # INDICATORS
    # ===============================================================
    def _apply_indicators(self, df: pd.DataFrame):
        try:
            df["RSI"] = RSIIndicator(df["close"], window=14).rsi()
            macd = MACD(df["close"])
            df["MACD"], df["Signal"] = macd.macd(), macd.macd_signal()
        except Exception as e:
            self.logger.error(f"Indicator calc failed: {e}")

    # ===============================================================
    # EXECUTION
    # ===============================================================
    def execute_trade(self, signal: dict):
        """Execute real or simulated Stellar trade."""
        side, pair, amount, price = signal["side"], signal["pair"], signal["amount"], signal["price"]
        self.logger.info(f"🔹 Executing {side} {amount} @ {price} on {pair}")

        if self.test_mode:
            self.logger.info("🧪 TEST MODE: Simulated trade.")
            self._record_trade(pair, side, amount, price, "SIMULATED", "OK")
            return

        try:
            account = self.server.load_account(self.keypair.public_key)
            builder = TransactionBuilder(account, Network.PUBLIC_NETWORK_PASSPHRASE, base_fee=100)

            offer = ManageSellOffer(
                selling=self.selling,
                buying=self.buying,
                amount=str(amount),
                price=str(price),
                offer_id=0
            )
            builder.append_operation(offer)
            tx = builder.set_timeout(30).build()
            tx.sign(self.keypair)
            resp = self.server.submit_transaction(tx)
            self._record_trade(pair, side, amount, price, resp["hash"], "SUCCESS")
        except Exception as e:
            self._record_trade(pair, side, amount, price, "N/A", "FAILED")
            self.logger.error(f"Trade failed: {e}")

    def _record_trade(self, pair, side, amount, price, tx_hash, result):
        record = {
            "pair": pair, "side": side, "amount": amount,
            "price": price, "hash": tx_hash,
            "result": result, "timestamp": datetime.now()
        }
        with self._lock:
            self.trade_history = pd.concat([self.trade_history, pd.DataFrame([record])], ignore_index=True)

    # ===============================================================
    # HELPERS
    # ===============================================================
    def _create_trading_pairs(self):
        try:
            balances = self.server.accounts().account_id(self.account_id).call()["balances"]
            assets = [
                Asset(b["asset_code"], b["asset_issuer"])
                for b in balances if b.get("asset_type") != "native"
            ]
            pairs = [(Asset.native(), a) for a in assets]
            self.logger.info(f"Created {len(pairs)} pairs.")
            return pairs
        except Exception as e:
            self.logger.error(f"Pair creation failed: {e}")
            return []

    def _on_market_update(self, event, data):
        msg = f"Market updated at {data['timestamp']}"
        self.controller.server_msg.update({"status": "RUNNING", "message": msg})
        self.logger.info(msg)

    def _on_transactions(self):
      """
        Fetch the latest transactions from the Stellar Horizon server
        and store them in a DataFrame.
        """
      try:
        if time.time() - self.last_tx_update > 300:  # every 5 minutes
          self._on_transactions()
          self.last_tx_update = time.time()

    #Fetch from Horizon (limit to recent ones)
        response = self.server.transactions().for_account(self.account_id).order(desc=True).call()

        # Extract records safely
        records = response.get("_embedded", {}).get("records", [])
        if not records:
            self.logger.info("No transactions found.")

            return

        # Convert to DataFrame
        self.transaction_df = pd.DataFrame(records)

        # Optional: format or filter relevant fields
        if not self.transaction_df.empty:
            self.transaction_df = self.transaction_df[
                ["id", "hash", "created_at", "successful", "source_account", "operation_count"]
            ]

        self.logger.info(f"✅ Transactions updated at {datetime.now()} | {len(self.transaction_df)} records loaded.")

        # Notify UI or event listener
        if hasattr(self, "events"):
            self.events.notify("transactions_update", {
                "count": len(self.transaction_df),
                "timestamp": datetime.now().isoformat()
            })

      except Exception as e:
        self.logger.error(f"❌ Error updating transactions: {e}", exc_info=True)
        self.transaction_df = pd.DataFrame()
    def _on_account_balances(self):
        """
        Safely fetch account balances from the Stellar Horizon API and
        convert them into a well-formatted DataFrame.
        """
        try:
         # Fetch the account details from Horizon
         account_data = self.server.accounts().account_id(self.account_id).call()
         balances = account_data.get("balances", [])

         if not balances:
            self.logger.warning("No balances found for this account.")
            self.accounts_balances = pd.DataFrame()
            return self.accounts_balances

         # Convert to DataFrame
         df = pd.DataFrame(balances)

        # Normalize column names for clarity
         if "asset_type" in df.columns:
            df.rename(columns={
                "asset_type": "type",
                "asset_code": "code",
                "asset_issuer": "issuer",
                "balance": "balance"
            }, inplace=True)

        # Convert numeric balance fields
         df["balance"] = pd.to_numeric(df["balance"], errors="coerce").fillna(0.0)

        # Reorder columns for readability
         columns = ["type", "code", "issuer", "balance"]
         df = df[[c for c in columns if c in df.columns]]

         # Store internally
         self.accounts_balances_df = df

        # Log summary
         self.logger.info(f"✅ Account balances updated — {len(df)} assets found.")



        except Exception as e:
         self.logger.error(f"❌ Error fetching account balances: {e}", exc_info=True)
         self.accounts_balances_df = pd.DataFrame()


    def _on_payments(self):
     """
        Fetch recent payment operations for this account from the Horizon API.
        Updates self.payments_df with formatted data for UI display.
        """
     try:
        self.logger.info(f"📦 Fetching payments for account {self.account_id}...")

        # Fetch recent payments for the account
        response = (
            self.server.payments()
            .for_account(self.account_id)
            .limit(100)
            .order(desc=True)
            .call()
        )

        # Extract records safely
        records = response.get("_embedded", {}).get("records", [])
        if not records:
            self.logger.info("No recent payments found.")
            self.payments_df = pd.DataFrame()

            return self.payments_df

        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Select and normalize key columns
        cols_to_keep = [
           "timestamp", "id", "type", "created_at", "from", "to",
            "asset_type", "asset_code", "amount", "transaction_hash"
        ]
        df = df[[c for c in cols_to_keep if c in df.columns]]

        # Clean up and format
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

        # Sort newest → oldest
        df.sort_values(by="created_at", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Save internally
        self.payments_df = df

        # Log summary
        self.logger.info(f"✅ Payments updated: {len(df)} transactions loaded.")

        return df

     except Exception as e:
        self.logger.error(f"❌ Error fetching payments: {e}", exc_info=True)
        self.payments_df = pd.DataFrame()
        return self.payments_df


    def _on_offers(self):
     """Fetch all current offers for the account and store as a DataFrame."""
     try:
        # Fetch raw offers from Horizon
        response = self.server.offers().call()

        # Extract embedded records
        records = response.get("_embedded", {}).get("records", [])
        if not records:
            self.logger.info("No offers found for this account.")
            self.offers_df = pd.DataFrame()
            return

        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Select only the relevant columns for display
        keep_cols = [
            "id", "seller", "selling", "buying", "amount",
            "price", "last_modified_time", "last_modified_ledger"
        ]
        for col in keep_cols:
            if col not in df.columns:
                df[col] = None  # Add missing if not present

        self.offers_df = df[keep_cols].copy()

        # Log and notify controller/UI
        self.logger.info(f"✅ Loaded {len(self.offers_df)} active offers from Horizon.")

        # Optional: notify UI layer
        if hasattr(self, "events"):
            self.events.notify("offers_update", {
                "timestamp": datetime.now().isoformat(),
                "count": len(self.offers_df)
            })

     except Exception as e:
        self.logger.error(f"Error fetching offers: {e}")
        self.offers_df = pd.DataFrame()

    def _on_liquidity_pool(self):
      """Fetch liquidity pools associated with this account and store as a DataFrame."""
      try:
        # Fetch liquidity pools from Horizon
        response = (
            self.server.liquidity_pools()
            .for_account(self.account_id)
            .limit(200)  .order(desc=True)
            .call()
        )

        # Extract pool records
        records = response.get("_embedded", {}).get("records", [])
        if not records:
            self.logger.info("No liquidity pools found for this account.")
            self.liquidity_df = pd.DataFrame()
            return

        # Convert records to DataFrame
        df = pd.DataFrame(records)

        # Extract relevant columns
        keep_cols = [
            "id", "fee_bp", "total_trustlines", "total_shares",
            "reserves", "paging_token", "last_modified_time"
        ]
        for col in keep_cols:
            if col not in df.columns:
                df[col] = None  # Ensure all expected columns exist

        # Flatten reserve data if available
        if "reserves" in df.columns:
            df["asset_A"] = df["reserves"].apply(
                lambda x: x[0].get("asset") if isinstance(x, list) and len(x) > 0 else None
            )
            df["asset_B"] = df["reserves"].apply(
                lambda x: x[1].get("asset") if isinstance(x, list) and len(x) > 1 else None
            )
            df.drop(columns=["reserves"], inplace=True)

        self.liquidity_df = df[keep_cols + ["asset_A", "asset_B"]].copy()
        self.logger.info(f"✅ Loaded {len(self.liquidity_df)} liquidity pools.")

        # Optionally notify UI
        if hasattr(self, "events"):
            self.events.notify("liquidity_update", {
                "timestamp": datetime.now().isoformat(),
                "count": len(self.liquidity_df)
            })

      except Exception as e:
        self.logger.error(f"Error fetching liquidity pools: {e}")
        self.liquidity_df = pd.DataFrame()

    def _on_effects(self):
     """Fetch account effects (balance changes, trustline updates, etc.) and store them as a DataFrame."""
     try:
        # Fetch the latest effects from Horizon
        response = (
            self.server.effects()
           .for_account(self.account_id)

            .order(desc=True)
            .call()
        )

        # Extract records safely
        records = response.get("_embedded", {}).get("records", [])
        if not records:
            self.logger.info("No effects found for this account.")
            self.effects_df = pd.DataFrame()
            return

        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Select relevant columns if they exist
        keep_cols = [
            "id",
            "type",
            "type_i",
            "account",
            "created_at",
            "paging_token",
            "amount",
            "asset_type",
            "asset_code",
            "asset_issuer"
        ]
        for col in keep_cols:
            if col not in df.columns:
                df[col] = None  # ensure all exist

        # Clean and sort
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        df.sort_values("created_at", ascending=False, inplace=True)

        self.effects_df = df[keep_cols].copy()
        self.logger.info(f"✅ Loaded {len(self.effects_df)} effects from Horizon.")

        # Notify the UI if event system is active
        if hasattr(self, "events"):
            self.events.notify("effects_update", {
                "timestamp": datetime.now().isoformat(),
                "count": len(self.effects_df)
            })

     except Exception as e:
        self.logger.error(f"Error fetching effects data: {e}")
        self.effects_df = pd.DataFrame()


    def _on_ledger(self):
     """Fetch the most recent ledgers from the Stellar network and store them as a DataFrame."""
     try:
        # Query the latest ledgers from Horizon
        response = (
            self.server.ledgers()
            .limit(100)              # fetch last 100 ledgers
            .order(desc=True)
            .call()
        )

        # Extract records
        records = response.get("_embedded", {}).get("records", [])
        if not records:
            self.logger.info("No ledger data found.")
            self.ledger_df = pd.DataFrame()
            return

        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Keep relevant columns
        keep_cols = [
            "sequence",
            "hash",
            "prev_hash",
            "transaction_count",
            "operation_count",
            "closed_at",
            "total_coins",
            "fee_pool",
            "base_fee_in_stroops",
            "base_reserve_in_stroops",
            "max_tx_set_size"
        ]

        # Ensure all columns exist even if Horizon omits some
        for col in keep_cols:
            if col not in df.columns:
                df[col] = None

        # Clean and format
        df["closed_at"] = pd.to_datetime(df["closed_at"], errors="coerce")
        df.sort_values("sequence", ascending=False, inplace=True)

        # Assign to class
        self.ledger_df = df[keep_cols].copy()
        self.logger.info(f"✅ Loaded {len(self.ledger_df)} ledgers from Horizon.")

        # Optional: Notify the UI via events
        if hasattr(self, "events"):
            self.events.notify("ledger_update", {
                "timestamp": datetime.now().isoformat(),
                "last_sequence": int(df.iloc[0]['sequence']),
                "count": len(df)
            })

     except Exception as e:
        self.logger.error(f"Error fetching ledger data: {e}")
        self.ledger_df = pd.DataFrame()

    def _on_orders(self):
     """Fetch and store active open orders (offers) for the current Stellar account."""
     try:
        # Fetch active offers (orders) for this account
        response = (
            self.server.offers()
            .for_account(self.account_id)

            .order(desc=True)
            .call()
        )

        records = response.get("_embedded", {}).get("records", [])
        if not records:
            self.logger.info("No active orders found.")
            self.orders_df = pd.DataFrame()
            return

        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Keep relevant columns for analysis and display
        keep_cols = [
            "id",
            "paging_token",
            "seller",
            "selling",
            "buying",
            "amount",
            "price",
            "price_r",
            "last_modified_ledger",
            "last_modified_time"
        ]

        for col in keep_cols:
            if col not in df.columns:
                df[col] = None

        # Expand nested 'selling' and 'buying' asset objects
        if "selling" in df.columns:
            df["selling_code"] = df["selling"].apply(lambda x: x.get("asset_code", "XLM") if isinstance(x, dict) else "N/A")
            df["selling_issuer"] = df["selling"].apply(lambda x: x.get("asset_issuer", "") if isinstance(x, dict) else "")
        if "buying" in df.columns:
            df["buying_code"] = df["buying"].apply(lambda x: x.get("asset_code", "XLM") if isinstance(x, dict) else "N/A")
            df["buying_issuer"] = df["buying"].apply(lambda x: x.get("asset_issuer", "") if isinstance(x, dict) else "")

        # Clean columns
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["last_modified_time"] = pd.to_datetime(df["last_modified_time"], errors="coerce")

        # Sort newest first
        df.sort_values("last_modified_time", ascending=False, inplace=True)

        # Assign to bot instance
        self.orders_df = df.copy()
        self.logger.info(f"✅ Loaded {len(self.orders_df)} open orders.")

        # Optionally notify UI or listeners
        if hasattr(self, "events"):
            self.events.notify("orders_update", {
                "timestamp": datetime.now().isoformat(),
                "count": len(df)
            })

     except Exception as e:
        self.logger.error(f"Error fetching open orders: {e}")
        self.orders_df = pd.DataFrame()


