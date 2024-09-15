import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
import pandas as pd
import requests
from datetime import datetime

class TradingWindow(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

  # Define layout
        self.pack(fill=tk.BOTH, expand=True)
        
        # Create label for trading pair
        self.pair_label = tk.Label(self, text="Select Trading Pair:", font=("Helvetica", 12))
        self.pair_label.grid(row=0, column=0, padx=10, pady=10)

        # Dropdown for trading pairs
        self.selected_pair = tk.StringVar(value="BTC/USD")
        self.pair_dropdown = ttk.Combobox(self, textvariable=self.selected_pair, values=["BTC/USD", "ETH/USD", "XRP/USD"])
        self.pair_dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.pair_dropdown.bind("<<ComboboxSelected>>", self.update_data)

        # Button to update prices
        self.refresh_button = tk.Button(self, text="Refresh Prices", command=self.update_data)
        self.refresh_button.grid(row=0, column=2, padx=10, pady=10)

        # Create a section for displaying current price
        self.price_label = tk.Label(self, text="Current Price:", font=("Helvetica", 12))
        self.price_label.grid(row=1, column=0, padx=10, pady=10)
        self.price_value = tk.Label(self, text="Loading...", font=("Helvetica", 12))
        self.price_value.grid(row=1, column=1, padx=10, pady=10)

        # Candlestick Chart Area
        self.chart_frame = tk.Frame(self)
        self.chart_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
        self.create_chart()

        # Order Type Selection
        self.order_label = tk.Label(self, text="Select Order Type:", font=("Helvetica", 12))
        self.order_label.grid(row=3, column=0, padx=10, pady=10)
        self.order_type = tk.StringVar(value="Market Order")
        self.order_dropdown = ttk.Combobox(self, textvariable=self.order_type, values=["Market Order", "Limit Order", "Stop Loss"])
        self.order_dropdown.grid(row=3, column=1, padx=10, pady=10)

        # Buttons to create or close orders
        self.create_order_button = tk.Button(self, text="Create Order", command=self.create_order)
        self.create_order_button.grid(row=4, column=0, padx=10, pady=10)
        self.close_order_button = tk.Button(self, text="Close Order", command=self.close_order)
        self.close_order_button.grid(row=4, column=1, padx=10, pady=10)

        # Initialize data update
        self.update_data()

    def create_chart(self):
        """Creates an empty chart initially."""
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_chart(self, ohlc_data):
        """Updates the candlestick chart with new OHLC data."""
        self.ax.clear()  # Clear previous chart
        mpf.plot(ohlc_data, type='candle', ax=self.ax)  # Plot candlestick chart
        self.canvas.draw()

    def fetch_live_data(self, pair):
        """Mock function to fetch live data."""
        # In a real scenario, you'd fetch data from an API.
        response = {
            "BTC/USD": 50000.0,
            "ETH/USD": 3500.0,
            "XRP/USD": 1.25
        }
        return response.get(pair, "N/A")
    
    def fetch_ohlc_data(self, pair):
        """Mock function to fetch OHLC data."""
        # This is mock OHLC data. Replace this with real API data.
        # Format: Date, Open, High, Low, Close, Volume
        data = {
            "Date": [datetime.now().strftime("%Y-%m-%d") for _ in range(5)],
            "Open": [48000, 49000, 50000, 51000, 52000],
            "High": [49000, 50000, 51000, 52000, 53000],
            "Low": [47000, 48000, 49000, 50000, 51000],
            "Close": [49000, 50000, 51000, 52000, 53000],
            "Volume": [1000, 1100, 1200, 1300, 1400]
        }
        return pd.DataFrame(
            data,
            index=pd.to_datetime(data["Date"]),
            columns=["Open", "High", "Low", "Close", "Volume"])

    def update_data(self, event=None):
        """Updates the current price and candlestick chart based on the selected pair."""
        pair = self.selected_pair.get()

        # Update current price
        price = self.fetch_live_data(pair)
        self.price_value.config(text=f"{price} USD")

        # Fetch and update candlestick data
        ohlc_data = self.fetch_ohlc_data(pair)
        self.update_chart(ohlc_data)

    def create_order(self):
        """Handles the creation of orders based on selected order type."""
        order_type = self.order_type.get()
        print(f"Creating a {order_type} for {self.selected_pair.get()}")

    def close_order(self):
        """Handles the closing of orders."""
        print(f"Closing order for {self.selected_pair.get()}")

