import datetime
from statistics import LinearRegression
import numpy as np
import pandas as pd

from pandas import DataFrame
from sklearn.base import ClassifierMixin
from sklearn.model_selection import train_test_split



class Learning(object):
    def __init__(self):

        self.symbol_list = []
        self.symbol = 'BTCUSDC'
        self.start_date = '2020-01-01'
        self.end_date = datetime.datetime.today().strftime('%Y-%m-%d')
        self.price=100
        self.quantity = 10

        self.candle_list = DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])


    def get_signal(self, symbol: str,datas=None):
        self.symbol_list.append(symbol)
     
  
        # Fetch historical data
        data = pd.DataFrame(datas,columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        # Calculate the price range
        high = data['high'].max()
        low = data['low'].min()

        # Calculate Fibonacci retracement levels
        fib_levels = {
            0.236: high - (0.236 * (high - low)),
            0.382: high - (0.382 * (high - low)),
            0.500: high - (0.500 * (high - low)),
            0.618: high - (0.618 * (high - low)),
            0.786: high - (0.786 * (high - low))
        }

        print(f'Fibonacci Levels: {fib_levels}')

   
        labels = data['close']
        features = data.drop(columns=['close'])
        X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)
        # regressor = LinearRegression( slope=0.3, intercept=0)
  
        
        
        
      
      





        return 0
