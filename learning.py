import datetime
import sqlite3
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
import numpy as np
import numpy as np







''' This class is used to train and test a model to predict the price'''
class Learning:
    def __init__(self):
        
        self.symbol_list = []
       
        self.start_date = '2020-01-01'
        self.end_date = datetime.datetime.today().strftime('%Y-%m-%d')
        self.interval = '1d'
        self.limit = 1000
        self.price=100
        self.quantity = 10

        self.fibo_msg = {
            
        }
        self.symbol=''
        


    def get_signal(self, symbol: str,candle_list=None):
        self.symbol_list.append(symbol) 
        self.symbol = symbol

        #Fetch each symbol's candles

        
        # Fetch historical data
        data = pd.read_sql(f"SELECT * FROM candles WHERE symbol='{symbol}' AND timestamp BETWEEN '{self.start_date}' AND '{self.end_date}'  ORDER BY timestamp ASC", con=sqlite3.connect('TradingBot.sql'))               
        if data is None:
            return 0
        while data.shape[0] < 100:
            data = candle_list 
            print('shape',data.shape[0])
            return 0                 
                    
        print(data.head(), data.tail())
        #Convert data to float and scale it
        data['open'] = data['open'].apply(lambda x: float(x))
        data['high'] = data['high'].apply(lambda x: float(x))
        data['low'] = data['low'].apply(lambda x: float(x))
        data['close'] = data['close'].apply(lambda x: float(x))    
        data['base_volume'] = data['base_volume'].apply(lambda x: float(x))
        data['counter_volume'] = data['counter_volume'].apply(lambda x: float(x))




        # Calculate the price range
        high = data['high'].max()
        low = data['low'].min()
        price = (float(high) + float(low)) / 2
        print(f'Price: {price}')
        
        # Calculate Fibonacci retracement levels
        fib_levels = {
            0.236: high - (0.236 * (high - low)),
            0.382: high - (0.382 * (high - low)),
            0.500: high - (0.500 * (high - low)),
            0.618: high - (0.618 * (high - low)),
            0.786: high - (0.786 * (high - low))
        }
        self.fibo_msg['fib_levels'] = self.symbol +':'+fib_levels.__str__()+ '\n'

        data.dropna()

        print(f'Fibonacci Levels: {fib_levels}')
      
# Feature Engineering
        data['SMA50'] = SMAIndicator(data['close'], window=50).sma_indicator()
        data['SMA200'] = SMAIndicator(data['close'], window=200).sma_indicator()
        data['RSI'] = RSIIndicator(data['close']).rsi()

# Labeling (example: simple moving average crossover)
        data['Signal'] = np.where(data['SMA50'] > data['SMA200'], 1, 0)

# Drop NaN values introduced by indicator calculations
        data.dropna(inplace=True)

# Features and Target
        features = ['SMA50', 'SMA200', 'RSI']
        X = data[features]
        y = data['Signal']

# Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model Training
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

# Model Prediction
        y_pred = model.predict(X_test)

# Model Evaluation
        accuracy = accuracy_score(y_test, y_pred)
        print(f'Model Accuracy: {accuracy}')

# Signal Generation for New Data
        new_data = pd.read_sql(
            f"SELECT * FROM candles WHERE symbol='{symbol}' AND timestamp BETWEEN '{self.start_date}' AND '{self.end_date}'  ORDER BY timestamp ASC", con=sqlite3.connect('TradingBot.sql')
        )  # Replace with your new data

        
        new_data['SMA50'] =  data['SMA50']
        new_data['SMA200'] =  data['SMA200']
        new_data['RSI'] = data['RSI']
        new_data.dropna(inplace=True)

        new_features = new_data[features]
        new_data['Predicted_Signal'] = model.predict(new_features)
        new_data.dropna(inplace=True)

        score = accuracy_score(data['Signal'], new_data['Predicted_Signal'])
        print(f'Model Accuracy: {score}')


        print(y_pred)
        print(y_test)
        print(X_test)
        print(X_train)
        print(y_train)
        print(X, y)   
        signal = new_data['Predicted_Signal'].values[-1:]


        if signal == 1 and accuracy > 95:

            print(f'Signal Buy: {signal}')
            return 1
        elif signal == 0 and accuracy > 95:
            print(f'Signal Sell: {signal}')
            return -1
        
        
        return 0
