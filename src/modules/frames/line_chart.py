import sys
import pandas as pd
import mplfinance as mpf
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QPushButton, QFileDialog, QHBoxLayout

class LineChart(QWidget):
    """A PyQt5 widget for displaying a line chart using mplfinance."""

    def __init__(self, parent=None, df=None):
        """Initialize the line chart widget."""
        super().__init__(parent)
        self.setGeometry(
            0, 0,1530,780
        )
        # Ensure the 'Date' column is in datetime format before setting it as the index
        self.df = pd.DataFrame(df)
        self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')  # Convert 'Date' column to datetime
        self.df.dropna(subset=['Date'], inplace=True)
        self.df.set_index('Date', inplace=True)

        # Setup UI components
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI with buttons and chart."""
        # Create layout for the widget
        layout = QVBoxLayout(self)

        # Create toolbar layout for buttons
        toolbar = QHBoxLayout()

        # Buttons for chart management
        add_chart_button = QPushButton("Add Chart", self)
        add_chart_button.clicked.connect(self.add_chart)
        toolbar.addWidget(add_chart_button)

        remove_chart_button = QPushButton("Remove Chart", self)
        remove_chart_button.clicked.connect(self.remove_chart)
        toolbar.addWidget(remove_chart_button)

        refresh_button = QPushButton("Refresh Data", self)
        refresh_button.clicked.connect(self.refresh_chart)
        toolbar.addWidget(refresh_button)

        save_button = QPushButton("Save Chart", self)
        save_button.clicked.connect(self.save_chart)
        toolbar.addWidget(save_button)

        layout.addLayout(toolbar)

        # Create the line chart
        self.create_line_chart()

    def create_line_chart(self):
        """Create and display the line chart."""
        try:
            # Generate the line chart using mplfinance
            self.fig, self.ax = mpf.plot(self.df, type='line', style='charles', title='Line Chart',
                                         ylabel='Price', volume=True, returnfig=True)

            # Embed the chart into PyQt5 using FigureCanvas
            self.canvas = FigureCanvas(self.fig)
            self.layout().addWidget(self.canvas)
            self.canvas.draw()

        except Exception as e:
            print(f"Error generating chart: {e}")

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
        self.create_line_chart()

    def save_chart(self):
        """Save the line chart as an image."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Chart", "", "PNG files (*.png);;All Files (*)")
        if file_path:
            self.fig.savefig(file_path)
            print(f"Chart saved as {file_path}")
