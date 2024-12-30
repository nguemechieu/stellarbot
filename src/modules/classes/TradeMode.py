from enum import Enum


class TradeMode(Enum):

    """Enum for the trade mode of the bot."""

    AUTO = 'Auto'
    MANUAL = 'Manual'
    SIMULATION ='Simulation'