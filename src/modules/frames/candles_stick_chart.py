import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class CandlestickChart(tk.Frame):
    """A Tkinter frame for displaying a Candlestick chart using mplfinance."""

    def __init__(self, parent, controller=None, df=None):
        """Initialize the Candlestick chart frame."""
        super().__init__(parent)
        self.controller = controller
     
        self.df = pd.DataFrame(df)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df.set_index('Date', inplace=True)

        # Setup UI components
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI with buttons and chart."""
        # Create the toolbar for management buttons
        toolbar = tk.Frame(self, bd=2, relief=tk.RAISED, bg='gray')
        toolbar.pack(side=tk.TOP, fill=tk.X)


        save_button = tk.Button(toolbar, text="Save Chart", command=self.save_chart)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Create the Candlestick chart
        self.create_candlestick_chart()

    def create_candlestick_chart(self):
        """Create and display the Candlestick chart."""
        # Generate the candlestick chart using mplfinance
        self.fig, self.ax = mpf.plot(self.df, type='candle', style='charles', title='Candlestick Chart',
                                     ylabel='Price', volume=True, returnfig=True)

        # Embed the chart into Tkinter using FigureCanvasTkAgg
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

  
    def refresh_chart(self):
        """Refresh the chart with updated data."""
        # In a real scenario, you would fetch new data here and replot the chart.
        print("Refreshing chart with updated data...")
        self.df['Close'] += 5  # Simulate price change
        self.create_candlestick_chart()

    def save_chart(self):
        """Save the candlestick chart as an image."""
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path)
            print(f"Chart saved as {file_path}")

