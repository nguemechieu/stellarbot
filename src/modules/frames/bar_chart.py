import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
import pandas as pd
import mplfinance as mpf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BarChart(tk.Frame):
    """A Tkinter frame for displaying a bar chart using mplfinance."""

    def __init__(self, parent, controller=None, df=None):
        """Initialize the Bar chart frame."""
        super().__init__(parent)
        self.controller = controller

        # Ensure the 'Date' column is in datetime format before setting it as the index
        self.df = pd.DataFrame(df)
        self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')  # Convert 'Date' column to datetime
        self.df.dropna(subset=['Date'], inplace=True)  # Remove any rows with invalid dates
        self.df.set_index('Date', inplace=True)

        # Setup UI components
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI with buttons and chart."""
        toolbar = tk.Frame(self, bd=2, relief=tk.RAISED, bg='gray')
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Buttons for chart management
        add_chart_button = tk.Button(toolbar, text="Add Chart", command=self.add_chart)
        add_chart_button.pack(side=tk.LEFT, padx=5, pady=5)

        remove_chart_button = tk.Button(toolbar, text="Remove Chart", command=self.remove_chart)
        remove_chart_button.pack(side=tk.LEFT, padx=5, pady=5)

        refresh_button = tk.Button(toolbar, text="Refresh Data", command=self.refresh_chart)
        refresh_button.pack(side=tk.LEFT, padx=5, pady=5)

        save_button = tk.Button(toolbar, text="Save Chart", command=self.save_chart)
        save_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Create the bar chart
        self.create_bar_chart()

    def create_bar_chart(self):
        """Create and display the bar chart."""
        try:
            # Generate the bar chart using mplfinance
            self.fig, self.ax = mpf.plot(self.df, type='ohlc', style='charles', title='Bar Chart',
                                         ylabel='Price', volume=True, returnfig=True)

            # Embed the chart into Tkinter using FigureCanvasTkAgg
            self.canvas = FigureCanvasTkAgg(self.fig, master=self)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            print(f"Error generating chart: {e}")
            messagebox.showerror("Error", f"Error generating chart: {e}")

    def add_chart(self):
        """Simulate adding a new chart (placeholder functionality)."""
        print("Add Chart button clicked")

    def remove_chart(self):
        """Simulate removing a chart (placeholder functionality)."""
        print("Remove Chart button clicked")

    def refresh_chart(self):
        """Refresh the chart with updated data."""
        print("Refreshing chart with updated data...")
        self.df['Close'] += 5  # Simulate price change
        self.create_bar_chart()

    def save_chart(self):
        """Save the bar chart as an image."""
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path)
            print(f"Chart saved as {file_path}")
