from enum import Enum


class Kline(Enum):
    """Enum for Kline types."""
    OHLCV = 1  # Open, High, Low, Close, Volume
    LINEAR = 2  # Linear candles
    CANDLESTICKS = 3  # Candlesticks
    HEIKIN_ASHI = 4  # Heikin-Ashi candles
    RSI = 5  # Relative Strength Index
    BOLLINGER_BANDS = 6  # Bollinger Bands
    MACD = 7  # Moving Average Convergence Divergence
    SAR = 8  # Parabolic SAR
    ADX = 9  # Average Directional Movement Index
    TRIX = 10  # TRIX
    VOLUME_BARS = 11  # Volume Bars
    WILLIAMS_R = 12  # Williams %R
    OBV = 13  # On-Balance Volume
    CHAIKIN_MOMENTUM = 14  # Chaikin Money Flow
    PPO = 15  # Percentage Price Oscillator
    CCI = 16  # Commodity Channel Index
    ICHIMOKU_CLOUD = 17  # Ichimoku Cloud
    T3 = 18  # Triple Exponential Moving Average
    KAMA = 19  # Kaufman Adaptive Moving Average
    MAMA = 20  #MESA Adaptive Moving Average
    TEMA = 21  # Triple Exponential Moving Average (TEMA)
    VEMA = 22  # Volume-Weighted Moving Average (VWMA)
    DEMA = 23  # Double Exponential Moving Average (DEMA)
    EMA = 24  # Exponential Moving Average (EMA)
    SMA = 25  # Simple Moving Average (SMA)
    WMA = 26  # Weighted Moving Average (WMA)
    ATR = 27  # Average True Range (ATR)
    BBANDS = 28  # Bollinger Bands (BBands)
    NATR = 29  # Normalized Average True Range (NATR)
    RSI_14 = 30  # 14-period Relative Strength Index (RSI)
    RSI_6 = 31  # 6-period Relative Strength Index (RSI)