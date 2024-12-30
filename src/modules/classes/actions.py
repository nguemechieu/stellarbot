from enum import Enum


class Actions(Enum):
    TRADE = 1 # Place a trade order
    ORDER_FILL = 2 # Fill an existing order
    ORDER_CANCEL = 3 # Cancel an existing order
    PAYMENT = 4
    EFFECT = 5
    TRADING_STRATEGY = 6
    ASSET_PORTFOLIO = 7
    ORDER_HISTORY = 8
    TRADING_HISTORY = 9
    TRADING_CHARTS = 10