from enum import Enum


class OrderTypes(Enum):
    """Enum to represent different order types."""
    MARKET = "Market"
    LIMIT = "Limit"
    STOP_LOSS = "Stop Loss"