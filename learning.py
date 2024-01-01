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
        self.price = 0
        self.symbol = ''
        self.fibonacci = {}

    def get_signal(self, symbol: str, candle_list=None):
        self.symbol_list.append(symbol)
        self.symbol = symbol
        self.end_date = datetime.datetime.today().strftime('%Y-%m-%d')
        
        # Signal Generation for New Data
        conn = sqlite3.connect('TradingBot'+ '.sql')
        new_data = pd.read_sql(
            f"SELECT * FROM candles WHERE symbol='{symbol}' AND timestamp BETWEEN '{self.start_date}' AND '{self.end_date}'  ORDER BY timestamp ASC",
            con=conn, index_col=None, parse_dates=True
        )

        data = new_data
        if data is None:
            print(f'No data found for {symbol}')
            return 0
        while data.shape[0] < 100:
            print(f'No data found for {symbol}')
            return 0

        print(data.head(), data.tail())
        
        data['open'] = data['open'].apply(lambda x: float(x))
        data['high'] = data['high'].apply(lambda x: float(x))
        data['low'] = data['low'].apply(lambda x: float(x))
        data['close'] = data['close'].apply(lambda x: float(x))
        data['base_volume'] = data['base_volume'].apply(lambda x: float(x))
        data['counter_volume'] = data['counter_volume'].apply(lambda x: float(x))

        new_data = pd.DataFrame(data, columns=['open', 'high', 'low', 'close', 'base_volume', 'counter_volume'])

        high = new_data['high'].max()
        low = new_data['low'].min()
        price = (float(high) + float(low)) / 2
        self.price = price
        print(f'Price: {price}')

        fib_levels = {
            0.236: high - (0.236 * (high - low)),
            0.382: high - (0.382 * (high - low)),
            0.500: high - (0.500 * (high - low)),
            0.618: high - (0.618 * (high - low)),
            0.786: high - (0.786 * (high - low))
        }
        self.fibonacci = fib_levels.__str__()

        new_data.dropna(inplace=True)

        new_data['price'] = data['close']
        new_data['price'] = price

        self.price = price

        # Feature Engineering
        new_data['SMA50'] = SMAIndicator(new_data['close'], window=50).sma_indicator()
        new_data['SMA200'] = SMAIndicator(new_data['close'], window=200).sma_indicator()
        new_data['RSI'] = RSIIndicator(new_data['close']).rsi()

        # Labeling
        new_data['Signal'] = np.where(new_data['SMA50'] > new_data['SMA200'], 1, 0)
        new_data.dropna(inplace=True)

        # Features and Target
        features = ['SMA50', 'SMA200', 'RSI']
        print(new_data.head())
        print(new_data.tail())

        X = new_data[features]
        y = new_data['Signal']

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, train_size=0.8,
                                                            stratify=y)

        # Model Training
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        fib_levels = {
            0.236: high - (0.236 * (high - low)),
            0.382: high - (0.382 * (high - low)),
            0.500: high - (0.500 * (high - low)),
            0.618: high - (0.618 * (high - low)),
            0.786: high - (0.786 * (high - low))
        }

        # Assuming fibo_signal is initially 0 (no signal)
        fibo_signal = 0

        # Check if the close price is near any Fibonacci level
        for level, fibo_price in fib_levels.items():
            if abs(price - fibo_price) / price < 0.01:  # You can adjust the threshold as needed
                fibo_signal = 1  # Buy signal
            elif abs(price - fibo_price) / price < 0.01:
                fibo_signal = -1  # Sell signal

        #

        # Model Prediction
        y_pred = model.predict(X_test)

        # Model Evaluation
        accuracy = accuracy_score(y_test, y_pred)
        print(f'Model Accuracy: {accuracy}')

        new_data.dropna(inplace=True)

        new_features = new_data[features]
        new_data['Predicted_Signal'] = model.predict(new_features)
        new_data.dropna(inplace=True)

        # Apply Fibonacci signals to the new data
        new_data['Fibo_Signal'] = fibo_signal

        score = accuracy_score(new_data['Signal'], new_data['Predicted_Signal'])
        fibo_score = accuracy_score(new_data['Signal'], new_data['Fibo_Signal'])
        print(f'Model Accuracy: {score}')
        print(f'Fibo Signal Accuracy: {fibo_score}')

        # ... (rest of the code)

        signal = new_data['Predicted_Signal'].values[-1:]
        fibo_signal = new_data['Fibo_Signal'].values[-1:]

        # Adjust conditions based on your strategy
        if signal == 1 and accuracy > 95:
            print(f'Signal Buy: {signal}')
            return 1
        elif signal == 0 and accuracy > 95:
            print(f'Signal Sell: {signal}')
            return -1
        elif fibo_signal == 1:
            print(f'Fibo Signal Buy: {fibo_signal}')
            return 1
        elif fibo_signal == -1:
            print(f'Fibo Signal Sell: {fibo_signal}')
            return -1

        return 0