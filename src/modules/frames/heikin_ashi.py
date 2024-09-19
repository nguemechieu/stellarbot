import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget

class HeikinAshi(QWidget):
    def __init__(self, parent=None, controller=None,df=None):
        """Initialize the Heikin-Ashi chart frame."""
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(
            0, 0,1530,780
        )
        if df is None:
            df = {}

        # Data preparation: Creating a pandas DataFrame from the input data
        self.df = pd.DataFrame(df)

        # Calculate Heikin-Ashi values
        self.calculate_heikin_ashi()

        # Create and display the Heikin-Ashi chart
        self.create_heikin_ashi_chart()

    def calculate_heikin_ashi(self):
        """Calculate Heikin-Ashi values."""
        df = self.df.copy()

        # Create columns for Heikin-Ashi calculation
        df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
        df['HA_Open'] = (df['Open'].shift(1) + df['Close'].shift(1)) / 2
        df['HA_Open'].fillna(df['Open'], inplace=True)  # Fill NaN for first row
        df['HA_High'] = df[['High', 'HA_Open', 'HA_Close']].max(axis=1)
        df['HA_Low'] = df[['Low', 'HA_Open', 'HA_Close']].min(axis=1)

        self.df = df

    def create_heikin_ashi_chart(self):
        """Display the Heikin-Ashi chart in the PyQt frame."""
        fig, ax = plt.subplots(figsize=(8, 6))

        # Convert Date column to matplotlib's date format
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        ha_data = self.df[['Date', 'HA_Open', 'HA_High', 'HA_Low', 'HA_Close']].values

        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # Plot Heikin-Ashi Candlestick
        self.plot_heikin_ashi_candlestick(ax, ha_data)

        ax.set_title('Heikin-Ashi Chart')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')

        # Embed the chart into the PyQt layout using FigureCanvasQTAgg
        self.canvas = FigureCanvas(fig)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_heikin_ashi_candlestick(self, ax, ha_data):
        """Plot Heikin-Ashi candlestick chart."""
        for date, ha_open, ha_high, ha_low, ha_close in ha_data:
            color = 'green' if ha_close >= ha_open else 'red'

            # Draw the high-low line
            ax.plot([date, date], [ha_low, ha_high], color=color)

            # Draw the open-close rectangle (candlestick body)
            ax.add_patch(Rectangle(
                (mdates.date2num(date).max() - 0.2, ha_open), 0.4, ha_close - ha_open, color=color, alpha=0.6))

