from __future__ import annotations
import logging, threading, time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Callable
import pandas as pd
from stellar_sdk import Server, Asset, Keypair, TransactionBuilder, Network, ManageSellOffer
from ta.momentum import RSIIndicator
from ta.trend import MACD


# ===============================================================
# EVENT SYSTEM
# ===============================================================
class EventListener:
    """Lightweight publish/subscribe system for asynchronous updates."""
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
# SMARTBOT CORE
# ===============================================================
class SmartBot:
    """💡 Advanced Stellar Trading Bot — stable, threaded, and UI-ready."""

    def __init__(self, controller):
        self.controller = controller
        self.logger = self._setup_logger()
        self.running = False
        self.test_mode = False
        self.interval_seconds = 60
        self.resolution = 3600000  # 1h

        # --- Stellar Setup ---
        self.server = Server("https://horizon.stellar.org")
        self.account_id = controller.account_id
        self.secret_key = controller.secret_key
        self.keypair = Keypair.from_secret(self.secret_key)
        self.account = self.server.load_account(self.account_id)

        # --- Default pair ---
        self.selling = Asset.native()
        self.buying = Asset("USDC", "GDMTVHLWJTHSUDMZVVMXXH6VJHA2ZV3HNG5LYNAZ6RTWB7GISM6PGTUV")

        # --- State & Lock ---
        self._lock = threading.Lock()
        self.thread: Optional[threading.Thread] = None

        # --- DataFrames ---
        self.assets_df = pd.DataFrame()
        self.accounts_df = pd.DataFrame()
        self.transactions_df = pd.DataFrame()
        self.effects_df = pd.DataFrame()
        self.offers_df = pd.DataFrame()
        self.orderbook_df = pd.DataFrame()
        self.payments_df = pd.DataFrame()
        self.trades_df = pd.DataFrame()
        self.fees_stats_df = pd.DataFrame()
        self.operations_df = pd.DataFrame()
        self.ledger_df = pd.DataFrame()
        self.trade_history = pd.DataFrame(columns=[
            "pair", "side", "amount", "price", "hash", "result", "timestamp"
        ])

        # --- Events ---
        self.events = EventListener()
        self.events.subscribe("market_update", self._on_market_update)

        # --- Initialization ---
        self._initialize_account()
        self.logger.info("✅ SmartBot initialized successfully.")

    # ===============================================================
    # LOGGER
    # ===============================================================
    def _setup_logger(self):
        logger = logging.getLogger("SmartBot")
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    # ===============================================================
    # ACCOUNT INIT
    # ===============================================================
    def _initialize_account(self):
        try:
            self.account = self.server.load_account(self.account_id)
            self.assets_df = pd.DataFrame(self.server.assets().call())
            self.accounts_df = pd.DataFrame([self.server.accounts().account_id(self.account_id).call()])
            self.transactions_df = pd.DataFrame([self.server.transactions().for_account(self.account_id).call()])
            self.effects_df = pd.DataFrame([self.server.effects().for_account(self.account_id).call()])
            self.offers_df = pd.DataFrame([self.server.offers().call()])
            self.orderbook_df = pd.DataFrame([self.server.orderbook(self.selling,self.buying).call()])
            self.payments_df = pd.DataFrame([self.server.payments().for_account(self.account_id).call()])
            self.trades_df = pd.DataFrame([self.server.trades().for_account(self.account_id).call()])
            self.fees_stats_df = pd.DataFrame([self.server.fee_stats().call()])
            self.operations_df = pd.DataFrame([self.server.operations().for_account(self.account_id).call()])
            self.ledger_df = pd.DataFrame([self.server.ledgers().order(desc=True).limit(50).call()])
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")

    # ===============================================================
    # START/STOP
    # ===============================================================
    def start(self):
        """Launch trading loop and data updaters."""
        if self.running:
            self.logger.warning("Bot already running.")
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, name="SmartBotMain", daemon=True)
        self.thread.start()
        self._start_background_updaters()
        self.logger.info("🚀 SmartBot started.")

    def stop(self):
        """Stop trading and background updates."""
        self.running = False
        self.logger.info("🛑 Stopping SmartBot...")
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        self.logger.info("✅ SmartBot stopped.")

    # ===============================================================
    # MAIN LOOP
    # ===============================================================
    def _run_loop(self):
        """Main trading strategy loop."""
        try:
            pairs = self._create_trading_pairs()
            if not pairs:
                self.logger.warning("⚠️ No trading pairs found.")
                return

            while self.running:
                start_time = time.time()
                for base, quote in pairs:
                    df = self._fetch_ohlcv(base, quote)
                    if df is None or df.empty:
                        continue
                    self._apply_indicators(df)
                    signal = self._generate_signal(df, f"{base.code}/{quote.code}")
                    if signal:
                        self.execute_trade(signal)

                    # Notify UI
                    self.events.notify("market_update", {
                        "timestamp": datetime.now(),
                        "pair": f"{base.code}/{quote.code}",
                        "status": "RUNNING"
                    })

                time.sleep(max(0, self.interval_seconds - (time.time() - start_time)))

        except Exception as e:
            self.logger.exception(f"Fatal bot error: {e}")
        finally:
            self.running = False

    # ===============================================================
    # STRATEGY
    # ===============================================================
    def _generate_signal(self, df: pd.DataFrame, pair: str) -> Optional[dict]:
        """Generate trading signal using MACD + RSI."""
        last = df.iloc[-1]
        macd, signal, rsi = last.get("MACD"), last.get("Signal"), last.get("RSI")
        if pd.isna(macd) or pd.isna(signal) or pd.isna(rsi):
            return None

        if macd > signal and rsi < 30:
            return {"pair": pair, "side": "BUY", "amount": 10, "price": last["close"]}
        elif macd < signal and rsi > 70:
            return {"pair": pair, "side": "SELL", "amount": 10, "price": last["close"]}
        return None

    # ===============================================================
    # MARKET DATA
    # ===============================================================
    def _fetch_ohlcv(self, base: Asset, quote: Asset, start_time=None, end_time=None) -> Optional[pd.DataFrame]:
        try:
            end_time = end_time or int(datetime.now().timestamp() * 1000)
            start_time = start_time or end_time - 24 * 3600 * 1000
            data = self.server.trade_aggregations(
                base=base, counter=quote, start_time=start_time, end_time=end_time, resolution=self.resolution
            ).call()
            recs = data.get("_embedded", {}).get("records", [])
            if not recs:
                return pd.DataFrame()
            df = pd.DataFrame(recs)
            for c in ["open", "high", "low", "close"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            df["timestamp"] = pd.to_datetime(df["timestamp"].astype(float) / 1000, unit="s", utc=True)
            return df
        except Exception as e:
            self.logger.warning(f"Fetch error: {e}")
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
            self.logger.warning(f"Indicator error: {e}")

    # ===============================================================
    # EXECUTION
    # ===============================================================
    def execute_trade(self, signal: dict):
        """Execute or simulate a trade."""
        side, pair, amount, price = signal["side"], signal["pair"], signal["amount"], signal["price"]
        self.logger.info(f"🔹 {side} {amount} {pair} @ {price}")
        if self.test_mode:
            self._record_trade(pair, side, amount, price, "TEST", "OK")
            return

        try:
            account = self.server.load_account(self.keypair.public_key)
            txb = TransactionBuilder(account, Network.PUBLIC_NETWORK_PASSPHRASE, base_fee=100)
            offer = ManageSellOffer(
                selling=self.selling, buying=self.buying, amount=str(amount), price=str(price), offer_id=0
            )
            tx = txb.append_operation(offer).set_timeout(30).build()
            tx.sign(self.keypair)
            resp = self.server.submit_transaction(tx)
            self._record_trade(pair, side, amount, price, resp.get("hash"), "SUCCESS")
        except Exception as e:
            self._record_trade(pair, side, amount, price, "N/A", "FAILED")
            self.logger.error(f"Trade failed: {e}")

    def _record_trade(self, pair, side, amount, price, tx_hash, result):
        with self._lock:
            entry = {"pair": pair, "side": side, "amount": amount, "price": price,
                     "hash": tx_hash, "result": result, "timestamp": datetime.now()}
            self.trade_history = pd.concat([self.trade_history, pd.DataFrame([entry])], ignore_index=True)

    # ===============================================================
    # BACKGROUND UPDATERS
    # ===============================================================
    def _start_background_updaters(self):
        """Start async loops to refresh all dataframes."""
        for fn in [self._update_transactions, self._update_effects, self._update_ledger]:
            threading.Thread(target=fn, daemon=True).start()

    def _update_transactions(self):
        while self.running:
            try:
                res = self.server.transactions().for_account(self.account_id).order(desc=True).limit(100).call()
                self.transactions_df = pd.DataFrame(res["_embedded"]["records"])
            except Exception as e:
                self.logger.warning(f"Transaction update failed: {e}")
            time.sleep(300)

    def _update_effects(self):
        while self.running:
            try:
                res = self.server.effects().for_account(self.account_id).order(desc=True).limit(100).call()
                self.effects_df = pd.DataFrame(res["_embedded"]["records"])
            except Exception as e:
                self.logger.warning(f"Effects update failed: {e}")
            time.sleep(600)

    def _update_ledger(self):
        while self.running:
            try:
                res = self.server.ledgers().order(desc=True).limit(50).call()
                self.ledger_df = pd.DataFrame(res["_embedded"]["records"])
            except Exception as e:
                self.logger.warning(f"Ledger update failed: {e}")
            time.sleep(900)

    # ===============================================================
    # HELPERS
    # ===============================================================
    def _create_trading_pairs(self):
        try:
            balances = self.server.accounts().account_id(self.account_id).call()["balances"]
            assets = [
                Asset(b.get("asset_code"), b.get("asset_issuer"))
                for b in balances if b.get("asset_type") != "native"
            ]
            pairs = [(Asset.native(), a) for a in assets]
            self.logger.info(f"Created {len(pairs)} trading pairs.")
            return pairs
        except Exception as e:
            self.logger.error(f"Pair creation failed: {e}")
            return []

    def _on_market_update(self, event, data):
        msg = f"Market updated at {data.get('timestamp', datetime.now())}"
        self.controller.server_msg.update({"status": "RUNNING", "message": msg})
        self.logger.debug(msg)
