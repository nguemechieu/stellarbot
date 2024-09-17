import datetime
import time
import tkinter as tk
from tkinter import ttk, messagebox
import mplfinance as mpf
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from modules.frames.bar_chart import BarChart
from modules.frames.candles_stick_chart import CandlestickChart
from modules.frames.heikin_ashi import HeikinAshi
from modules.frames.line_chart import LineChart
from modules.frames.renko import Renko

class TradingCharts(tk.Frame):
    def __init__(self, parent=None, controller=None):
        """Initialize the TradingApp class."""
        super().__init__(parent)
        self.controller = controller
        self.parent = parent

        # Trading mode can be set to 'Manual' or 'Auto'
        self.trading_mode = 'Manual'

        # Default chart type
        self.chart_type = "candle"
       
        # Sample data for testing
        self.data = {
            'Open': [100, 120, 90, 110, 130, 105, 115, 125, 140, 110],
            'High': [110, 130, 105, 125, 145, 115, 125, 135, 150, 120],
            'Low': [90, 100, 85, 95, 115, 85, 95, 105, 120, 90],
            'Close': [105, 125, 100, 115, 135, 105, 115, 125, 140, 115],
            'Volume': [1000, 2000, 1500, 1800, 3000, 1500, 1800, 2500, 500, 1800],
            'Date': [

                '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04',
                '2023-01-05', '2023-01-06', '2023-01-07', '2023-01-08',
                '2023-01-09', '2023-01-10'
            ]
        }

        # Set up the toolbar and content area
        self.setup_toolbar()
        self.setup_content()

        # Create a Notebook widget for managing multiple charts
        self.notebook = ttk.Notebook(parent, width=1530, height=700)
        self.notebook.pack(fill=tk.BOTH, expand=True, ipady=50)

        # Initial chart tab setup
        self.add_chart()
       

    def add_chart(self):
        """Adds a chart to the notebook."""
        selected_asset = self.assets_combobox1.get() + "/" + self.assets_combobox2.get()
        new_tab = ttk.Frame(self.notebook, width=1500, height=300, border=4)
        new_tab.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(new_tab, text=f"{selected_asset} Chart")

        # Add the appropriate chart based on selected chart type
        if self.chart_type == "candle":
            chart = CandlestickChart(new_tab, self.controller, self.data)
            chart.pack()
        elif self.chart_type == "line":
            chart = LineChart(new_tab, self.controller, self.data)
            chart.pack()
        elif self.chart_type == "bar":
            chart = BarChart(new_tab, self.controller, self.data)
            chart.pack()
        elif self.chart_type == "renko":
            chart = Renko(new_tab, self.controller, self.data)
            chart.pack()
        elif self.chart_type == "heikin-ashi":
            chart = HeikinAshi(new_tab, self.controller, self.data)
            chart.pack()
        else:
            messagebox.showerror("Error", "Invalid chart type selected.")
            return

    def update_chart_type(self, event):
        """Update the chart type when the user selects a new option from the ComboBox."""
        self.chart_type = self.chart_type_combobox.get()
        self.add_chart()
            
    def setup_toolbar(self):
        """Sets up the toolbar with various buttons for trading actions."""
        toolbar = tk.Frame(self.parent, bd=3, relief=tk.RAISED, background='purple', height=30, width=1510)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Asset ComboBox for asset selection
        self.assets_combobox1 = ttk.Combobox(toolbar, values=[
            "BTC", "ETH", "LTC", "XRP", "BCH", "ADA", "XLM", "TRX", "DASH", "ZEC", "USD", "USDC", "PAX", "EUR"
        ])
        self.assets_combobox1.current(0)
        self.assets_combobox1.pack(side=tk.LEFT, padx=2, pady=2)

        self.assets_combobox2 = ttk.Combobox(toolbar, values=[
            "USD", "ETH", "LTC", "XRP", "BCH", "ADA", "XLM", "TRX", "DASH", "ZEC", "USD", "USDC", "PAX"
        ])
        self.assets_combobox2.current(0)
        self.assets_combobox2.pack(side=tk.LEFT, padx=2, pady=2)

        # Chart Type ComboBox for chart type selection
        self.chart_type_combobox = ttk.Combobox(toolbar, values=[
            "candle", "line", "bar", "renko", "heikin-ashi"
        ])
        self.chart_type_combobox.current(0)
        self.chart_type_combobox.pack(side=tk.LEFT, padx=2, pady=2)
        self.chart_type_combobox.bind("<<ComboboxSelected>>", self.update_chart_type)

        # Buttons for adding and removing charts
        chart_button = tk.Button(toolbar, text="Add Chart", relief=tk.RAISED, command=self.add_chart)
        chart_button.pack(side=tk.LEFT, padx=2, pady=2)

        remove_chart_button = tk.Button(toolbar, text="Remove Chart", relief=tk.RAISED, command=self.remove_chart)
        remove_chart_button.pack(side=tk.LEFT, padx=2, pady=2)

        # Status Label to display the current mode
        self.status_label = tk.Label(toolbar, text=f"Mode: {self.trading_mode}", bg='green', relief=tk.FLAT)
        self.status_label.pack(side=tk.RIGHT, padx=2, pady=2)

    def setup_content(self):
        """Sets up the main content area where charts will be displayed."""
        content = tk.Frame(self, height=780, width=1500)
        content.pack(fill=tk.BOTH, expand=True)

    def remove_chart(self):
        """Removes the currently selected chart."""
        if len(self.notebook.tabs()) > 0:
            current_tab = self.notebook.select()
            self.notebook.forget(current_tab)
