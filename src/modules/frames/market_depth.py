from datetime import datetime

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QListWidgetItem, QListWidget, QWidget
import random

class MarketDepth(QFrame):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        """Initialize the Market Depth widget."""
        self.controller = controller
        self.market_depth_data = self.generate_random_market_depth()  # Generate random market depth data

        # Main layout for the widget
        layout = QVBoxLayout(self)

        self.market_depth_label = QLabel("Market Depth")
        layout.addWidget(self.market_depth_label)

        # Create the market depth section
        self.create_widgets(layout)

    def generate_random_market_depth(self):
        """Generate random market depth data for testing."""
        market_depth = {}
        for i in range(10):  # Generating 10 random price/quantity pairs
            price = round(random.uniform(100, 200), 2)  # Random price between 100 and 200
            quantity = random.randint(1, 1000)  # Random quantity between 1 and 1000
            market_depth[price] = quantity
        return market_depth

    def create_widgets(self, layout):
        """Create and arrange the widgets for the market depth section."""
        # Market Depth Frame
        market_depth_frame = QWidget(self)
        layout.addWidget(market_depth_frame)

        # Market Depth Layout
        market_depth_layout = QVBoxLayout(market_depth_frame)

        # Create a QListWidget to display the market depth
        market_depth_widget = QListWidget()

        # Iterate over the market depth data
        for price, quantity in self.market_depth_data.items():
            item_text = f"Price: {price} | Quantity: {quantity}"

            # Create a QListWidgetItem
            item = QListWidgetItem(item_text)

            # Set random color for the item text


            # Add the item to the list widget
            market_depth_widget.addItem(item)

        # Add the market depth widget to the layout
        market_depth_layout.addWidget(market_depth_widget)


def random_color():
    """Generate a random color for the list items."""
    return f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'
