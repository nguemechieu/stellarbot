from enum import Enum


class TradeSide(Enum):
    """An enumeration for trade side."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
