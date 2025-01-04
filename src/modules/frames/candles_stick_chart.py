import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from matplotlib import pyplot as plt


def generate_random_xlm_data(start_date, num_days=100):
 date_range = pd.date_range(start=start_date, periods=num_days, freq='D')
 open_price = 0.2

 data=pd.DataFrame(columns=[ 'Open', 'High', 'Low', 'Close', 'Volume'])

 for date in date_range:
    price_change = np.random.normal(loc=0, scale=0.01)
    open_price = open_price + price_change
    open_price = max(open_price, 0.05)
    high_price = open_price + np.random.uniform(0.01, 0.03)
    low_price = open_price - np.random.uniform(0.01, 0.03)
    close_price = open_price + np.random.normal(loc=0, scale=0.005)
    volume = np.random.randint(100000, 500000)
    data['TimeStamp'] = date
    data['Open'] = open_price
    data['High'] = high_price
    data['Low'] = low_price
    data['Close'] = close_price
    data['Volume'] = volume

 return data


class CandlestickChart(QFrame):
    def __init__(self, parent=None, controller=None, df=None):
        super().__init__(parent)
        self.visible_data = generate_random_xlm_data(start_date="2022-01-01")
        self.size_entry = 6
        self.controller = controller

        if df is None:
            print("No data provided. Generating random XLM/USDT data...")
            df = self.visible_data
            self.df = df
        self.fig = plt.figure(figsize=(5, 3))
        self.df["Date"] = pd.to_datetime(self.df.index)
        self.df.dropna(inplace=True)
        self.df.fillna(method='ffill', inplace=True)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.fig = plt.figure(figsize=(5, 3))
        self.setup_chart()
        self.zoom_level = 50
        self.current_index = 0

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        layout.addLayout(toolbar)

        self.add_button(toolbar, "Save Chart", self.save_chart())
        # self.add_button(toolbar, "Buy", self.buy)
        # self.add_button(toolbar, "Sell", self.sell)
        # self.add_label_input(toolbar, "Size:", self.size_entry)
        # self.add_button(toolbar, "Zoom In", self.zoom_in)
        # self.add_button(toolbar, "Zoom Out", self.zoom_out)
        # self.add_button(toolbar, "Previous", self.prev_data)
        # self.add_button(toolbar, "Next", self.next_data)

        self.create_candlestick_chart()

    def create_candlestick_chart(self):
        self.fig, self.ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        self.ax_candle = self.ax[0]
        self.ax_vol = self.ax[1]
        self.fig.patch.set_facecolor('white')



    def add_button(self, toolbar, param, sell):
        button = QPushButton(param)
        button.clicked.connect(sell)
        toolbar.addWidget(button)
        pass

    def setup_chart(self):
        self.fig.autofmt_xdate()
        self.ax.grid(True, color="lightgray", alpha=0.5)
        self.ax_vol.grid(True, color="lightgray", alpha=0.5)
        self.ax.set_ylabel("Price")
        self.ax_vol.set_ylabel("Volume")
        self.ax.set_title("Candlestick Chart")
        self.ax_vol.set_ylabel("Volume")
        self.ax_vol.set_xlabel("Date")

    def save_chart(self):

            self.fig.savefig("chart.png", dpi=300)
            print("Chart saved as chart.png")

            return