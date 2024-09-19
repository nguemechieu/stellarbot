from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
import mplfinance as mpf

class CandlestickChart(QtWidgets.QWidget):
    """A PyQt5 widget for displaying a Candlestick chart using mplfinance."""

    def __init__(self, parent=None, controller=None, df=None):
        """Initialize the Candlestick chart widget."""
        super().__init__(parent)
        self.controller = controller


        self.setGeometry(
            10,10,
            1400,
            700
        )
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.zoom_level = 50  # Initial zoom level (number of data points)
        self.current_index = 0  # For navigating through the data

        self.df = pd.DataFrame(df)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df.set_index('Date', inplace=True)

        # Setup UI components
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI with buttons and chart."""
        layout = QtWidgets.QVBoxLayout(self)

        # Create the toolbar for management buttons
        toolbar = QtWidgets.QHBoxLayout()
        layout.addLayout(toolbar)

        save_button = QtWidgets.QPushButton("Save Chart")
        save_button.clicked.connect(self.save_chart)
        toolbar.addWidget(save_button)

        buy_button = QtWidgets.QPushButton("Buy")
        buy_button.clicked.connect(self.buy)
        toolbar.addWidget(buy_button)

        sell_button = QtWidgets.QPushButton("Sell")
        sell_button.clicked.connect(self.sell)
        toolbar.addWidget(sell_button)

        size_label = QtWidgets.QLabel("Size:")
        toolbar.addWidget(size_label)

        self.size_entry = QtWidgets.QLineEdit()
        self.size_entry.setFixedWidth(50)
        toolbar.addWidget(self.size_entry)

        zoom_in_button = QtWidgets.QPushButton("Zoom In")
        zoom_in_button.clicked.connect(self.zoom_in)
        toolbar.addWidget(zoom_in_button)

        zoom_out_button = QtWidgets.QPushButton("Zoom Out")
        zoom_out_button.clicked.connect(self.zoom_out)
        toolbar.addWidget(zoom_out_button)

        prev_button = QtWidgets.QPushButton("Previous")
        prev_button.clicked.connect(self.prev_data)
        toolbar.addWidget(prev_button)

        next_button = QtWidgets.QPushButton("Next")
        next_button.clicked.connect(self.next_data)
        toolbar.addWidget(next_button)

        # Create the Candlestick chart
        self.create_candlestick_chart()

    def create_candlestick_chart(self):
        """Create and display the Candlestick chart."""
        self.fig = plt.figure()
        self.fig.patch.set_facecolor('white')
        self.ax = self.fig.add_subplot(111)
        self.fig.set_facecolor('white')
        self.fig.set_size_inches(12, 8)
        self.ax.set_facecolor('white')

        # Plot only the visible window of data based on zoom_level and current_index
        self.visible_data = self.df.iloc[self.current_index:self.current_index + self.zoom_level]
        self.ax = mpf.plot(self.visible_data, type='candle', style='charles', title='Candlestick Chart',
                           ylabel='Price', volume=True, returnfig=True)

        # Embed the chart into PyQt5 using FigureCanvasQTAgg
        if hasattr(self, 'canvas'):
            self.canvas.deleteLater()  # Delete previous canvas if it exists

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.draw()

        layout = self.layout()
        layout.addWidget(self.canvas)

        # Add the navigation toolbar
        if hasattr(self, 'toolbar'):
            self.toolbar.deleteLater()  # Delete previous toolbar if it exists

      

        # Enable mouse clicks on the chart
        self.canvas.mpl_connect('button_press_event', self.on_click)

    def on_click(self, event):
        # TODO: Implement buy/sell logic based on clicked chart data
        print(f"Clicked at ({event.xdata}, {event.ydata})")
        return False

    def save_chart(self):
        """Save the candlestick chart as an image."""
        file_dialog = QtWidgets.QFileDialog(self)
        file_path, _ = file_dialog.getSaveFileName(self, "Save Chart", "", "PNG files (*.png)")
        if file_path:
            self.fig.savefig(file_path)
            print(f"Chart saved as {file_path}")
            QtWidgets.QMessageBox.information(self, "Chart Saved", "Chart saved successfully.")

    def zoom_in(self):
        """Zoom in by reducing the visible window size."""
        if self.zoom_level > 10:
            self.zoom_level -= 10
        self.create_candlestick_chart()

    def zoom_out(self):
        """Zoom out by increasing the visible window size."""
        if self.zoom_level < len(self.df):
            self.zoom_level += 10
        self.create_candlestick_chart()

    def prev_data(self):
        """Navigate to the previous set of data."""
        if self.current_index - self.zoom_level >= 0:
            self.current_index -= self.zoom_level
        self.create_candlestick_chart()

    def next_data(self):
        """Navigate to the next set of data."""
        if self.current_index + self.zoom_level < len(self.df):
            self.current_index += self.zoom_level
        self.create_candlestick_chart()

    def buy(self):
        """Handle buy button click."""
        size = self.get_size_input()
        print(f"Buy order placed for size: {size}")

    def sell(self):
        """Handle sell button click."""
        size = self.get_size_input()
        print(f"Sell order placed for size: {size}")

    def get_size_input(self):
        """Retrieve the size input value."""
        try:
            return int(self.size_entry.text())
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid size input, defaulting to 1")
            return 1
