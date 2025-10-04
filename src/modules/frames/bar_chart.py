import mplfinance as mpf
import pandas as pd
from PySide6.QtWidgets import (QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QFrame)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pandas import DataFrame


class BarChart(QFrame):
    """A PyQt5 widget for displaying a bar chart using mplfinance."""

    def __init__(self, parent=None, controller=None, df=None):
        """Initialize the Bar chart widget."""
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(
            0, 0,1530,780
        )

        # Ensure the 'Date' column is in datetime format before setting it as the index
        self.df = DataFrame(df)
        self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')  # Convert 'Date' column to datetime
        self.df.dropna(subset=['Date'], inplace=True)
        self.df.set_index('Date', inplace=True)

        # Setup the UI components
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI with buttons and chart."""
        layout = QVBoxLayout(self)

        # Toolbar for buttons
        toolbar_layout = QHBoxLayout()
        
        # Add chart button
        add_chart_button = QPushButton("Add Chart")
        add_chart_button.clicked.connect(self.add_chart)
        toolbar_layout.addWidget(add_chart_button)

        # Remove chart button
        remove_chart_button = QPushButton("Remove Chart")
        remove_chart_button.clicked.connect(self.remove_chart)
        toolbar_layout.addWidget(remove_chart_button)

        # Refresh button
        refresh_button = QPushButton("Refresh Data")
        refresh_button.clicked.connect(self.refresh_chart)
        toolbar_layout.addWidget(refresh_button)

        # Save chart button
        save_button = QPushButton("Save Chart")
        save_button.clicked.connect(self.save_chart)
        toolbar_layout.addWidget(save_button)

        # Add the toolbar layout to the main layout
        layout.addLayout(toolbar_layout)

        # Create the bar chart
        self.canvas = None
        self.create_bar_chart()

        # Set the main layout
        self.setLayout(layout)

    def create_bar_chart(self):
        """Create and display the bar chart."""
        try:
            # Generate the bar chart using mplfinance
            fig, ax = mpf.plot(self.df, type='ohlc', style='charles', title='Bar Chart',
                               ylabel='Price', volume=True, returnfig=True)

            # Embed the chart into PyQt5 using FigureCanvasQTAgg
            if self.canvas is not None:
                self.layout().removeWidget(self.canvas)
                self.canvas.deleteLater()

            self.canvas = FigureCanvas(fig)
            self.layout().addWidget(self.canvas)

        except Exception as e:
            print(f"Error generating chart: {e}")
            QMessageBox.critical(self, "Error", f"Error generating chart: {e}")

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
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Chart", "", "PNG Files (*.png)")
        if file_path:
            self.canvas.figure.savefig(file_path)
            print(f"Chart saved as {file_path}")


# Example usage if running as a standalone application
if __name__ == "__main__":
    # Sample Data
    df = {
        'Date': pd.date_range(start='2023-01-01', periods=10, freq='D'),
        'Open': [100, 120, 90, 110, 130, 105, 115, 125, 140, 110],
        'High': [110, 130, 105, 125, 145, 115, 125, 135, 150, 120],
        'Low': [90, 100, 85, 95, 115, 85, 95, 105, 120, 90],
        'Close': [105, 125, 100, 115, 135, 105, 115, 125, 140, 115],
        'Volume': [1000, 2000, 1500, 1800, 3000, 1500, 1800, 2500, 500, 1800]
    }

  