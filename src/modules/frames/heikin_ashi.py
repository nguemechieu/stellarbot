import tkinter as tk
from tkinter import ttk
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

class HeikinAshi(tk.Frame):
    def __init__(self, parent, controller=None, df : dict= {}):
        """Initialize the Heikin-Ashi chart frame."""
        super().__init__(parent)
        self.controller = controller

     
        self.df = pd.DataFrame(df)

       

        # Calculate Heikin-Ashi values
        self.calculate_heikin_ashi()

        # Create and display the Heikin-Ashi chart
        self.create_heikin_ashi_chart()

    def calculate_heikin_ashi(self):
        """Calculate Heikin-Ashi values."""
        df = self.df.copy()

        # Create columns for Heikin-Ashi
        df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4

        df['HA_Open'] = (df['Open'].shift(1) + df['Close'].shift(1)) / 2
        df['HA_Open'].fillna(df['Open'], inplace=False)  # Fill NaN for first row

        df['HA_High'] = df[['High', 'HA_Open', 'HA_Close']].max(axis=1)
        df['HA_Low'] = df[['Low', 'HA_Open', 'HA_Close']].min(axis=1)

        self.df = df

    def create_heikin_ashi_chart(self):
        """Display the Heikin-Ashi chart in the Tkinter frame."""
        fig, ax = plt.subplots(figsize=(8, 6))

        # Prepare data for matplotlib's candlestick_ohlc
        #self.df['Date'] = self.df['Date'].apply(mdates.date2num)
        ha_data = self.df[['Date', 'HA_Open', 'HA_High', 'HA_Low', 'HA_Close']].values

        ax.xaxis_date()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # Plot Heikin-Ashi Candlestick
        self.plot_heikin_ashi_candlestick(ax, ha_data)

        ax.set_title('Heikin-Ashi Chart')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_heikin_ashi_candlestick(self, ax, ha_data):
        """Plot Heikin-Ashi candlestick chart."""
        for date, ha_open, ha_high, ha_low, ha_close in ha_data:
            color = 'green' if ha_close >= ha_open else 'red'

            # Draw the high-low line
            ax.plot([date, date], [ha_low, ha_high], color=color)

            # Draw the open-close rectangle
            ax.add_patch(Rectangle(
                (date - 0.2, ha_open), 0.4, ha_close - ha_open, color=color, alpha=0.6))

