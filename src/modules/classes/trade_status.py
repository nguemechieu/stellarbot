from enum import Enum


class TradeStatus(Enum):
    PENDING = 1
    COMPLETED = 2
    CANCELLED = 3
    EXPIRED = 4
    FAILED = 5
