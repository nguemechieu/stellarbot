class RiskManager:
    def __init__(self, config, exchange):
        self.config = config
        self.exchange = exchange

    def calculate_position_size(self, symbol, risk_pct):
        """Risk a fixed % of account balance."""
        balance = self.exchange.get_balance()
        risk_amount = balance * (risk_pct / 100.0)
        # Suppose we know stop distance in price units:
        stop_dist = self.config["stop_loss_distance"]  # e.g. in X units
        # For example, value_per_unit = price * quantity, so:
        # qty = risk_amount / stop_dist
        price = self.exchange.get_price(symbol)
        qty = risk_amount / (stop_dist * price)
        return qty

    def enforce_limits(self):
        """Stop trading if max drawdown or daily loss exceeded."""
        stats = self.exchange.get_trading_stats()
        if stats["daily_loss"] >= self.config["max_daily_loss_pct"]:
            return False
        return True
