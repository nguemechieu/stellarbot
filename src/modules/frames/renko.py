from PySide6 import QtWidgets
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox
import pandas as pd
import mplfinance as mpf
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Renko(QtWidgets.QWidget):
    """A PyQt5 widget for displaying a Renko chart using mplfinance."""

    def __init__(self, parent=None, controller=None, df=None):
        """Initialize the Renko chart widget."""
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(
            0, 0,1530,780
        )
        # Ensure the 'Date' column is in datetime format
        self.df = pd.DataFrame(df)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df.set_index('Date', inplace=True)

        # Setup UI components
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI with buttons and chart."""
        layout = QVBoxLayout(self)

        # Toolbar layout for buttons
        toolbar = QHBoxLayout()
        layout.addLayout(toolbar)

        # Add Chart Button
        add_chart_button: QPushButton | QPushButton = QPushButton("Add Chart", self)
        add_chart_button.clicked.connect(self.add_chart)
        toolbar.addWidget(add_chart_button)

        # Remove Chart Button
        remove_chart_button = QPushButton("Remove Chart", self)
        remove_chart_button.clicked.connect(self.remove_chart)
        toolbar.addWidget(remove_chart_button)

        # Refresh Button
        refresh_button = QPushButton("Refresh Data", self)
        refresh_button.clicked.connect(self.refresh_chart)
        toolbar.addWidget(refresh_button)

        # Save Button
        save_button = QPushButton("Save Chart", self)
        save_button.clicked.connect(self.save_chart)
        toolbar.addWidget(save_button)

        # Create the Renko chart
        self.create_renko_chart(layout)

    def create_renko_chart(self, layout):
        """Create and display the Renko chart with adjusted ATR length."""
        try:
            # Generate the Renko chart using mplfinance with an adjusted ATR length
            self.fig, self.ax = mpf.plot(self.df, type='renko', style='charles', title='Renko Chart',
                                         ylabel='Price', volume=True, renko_params={'atr_length': 14}, returnfig=True)

            # Embed the chart into PyQt5 using FigureCanvas
            self.canvas = FigureCanvas(self.fig)
            layout.addWidget(self.canvas)

        except ValueError as e:
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
        self.create_renko_chart(QVBoxLayout(self))

    def save_chart(self):
        """Save the Renko chart as an image."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Chart", "", "PNG files (*.png);;All Files (*)", options=options)
        if file_path:
            self.fig.savefig(file_path)
            print(f"Chart saved as {file_path}")
