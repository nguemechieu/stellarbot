from enum import Enum


class TradeSignal(Enum):
    """Enum for trade signals."""
    BUY = 1
    SELL = -1
    HOLD = 0