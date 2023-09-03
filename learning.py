import pandas as pd

import yfinance as yf
from pandas import DataFrame


class Learning(object):
    def __init__(self):

        self.symbol_list = []
        self.symbol = 'BTCUSDC'
        candle_list = DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])

        self.candle_list = candle_list

        if len(candle_list) == 0:
            self.candle_list = candle_list
        else:
            self.candle_list = candle_list

        pass

    def get_signal(self, symbol: str):
        self.symbol_list.append(symbol)
        symbol = 'AAPL'
        start_date = '2020-01-01'
        end_date = '2021-01-01'
        # Fetch historical data
        data = yf.download(symbol=symbol, start=start_date, end=end_date)
        # Calculate the price range
        high = data['High'].max()
        low = data['Low'].min()

        # Calculate Fibonacci retracement levels
        fib_levels = {
            0.236: high - (0.236 * (high - low)),
            0.382: high - (0.382 * (high - low)),
            0.500: high - (0.500 * (high - low)),
            0.618: high - (0.618 * (high - low)),
            0.786: high - (0.786 * (high - low))
        }

        print(f'Fibonacci Levels: {fib_levels}')

        return 0
