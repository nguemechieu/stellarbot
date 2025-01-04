from enum import Enum




class TimeFrame(Enum):
    """Enum for time frames."""

    ONE_MINUTE = 60000 # 1 minute
    FIVE_MINUTES = 300000 # 5 minutes
    TEN_MINUTES = 600000 # 10 minutes
    FIFTEEN_MINUTES = 900000 # 15 minutes
    THIRTY_MINUTES = 1800000 # 30 minutes
    HOUR = 3600000 # 1 hour
    TWO_HOURS = 7200000 # 2 hours
    FOUR_HOURS = 14400000 # 4 hours
    EIGHT_HOURS = 28800000 # 8 hours
    DAY = 86400000 # 1 day
    WEEK = 604800000 # 1 week
    MONTH = 2592000000 # 1 month
    YEAR = 31536000000 # 1 year
    FOREVER = 0 # Forever


    @classmethod
    def get_seconds(cls) -> int:
        """Returns the number of seconds in the specified time frame."""
        return cls.value
