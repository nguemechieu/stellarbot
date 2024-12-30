from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout


class OrdersHistory(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Order History widget."""
        super().__init__(parent)
        self.controller = controller

        # Main layout for the widget
        layout = QVBoxLayout()

        # Create the order history section
        self.create_widgets(layout)

    def create_widgets(self, layout):
        """Create and arrange the widgets for the order history."""
        # Order History Frame
        order_history_frame = QFrame(self)

        layout.addWidget(order_history_frame)

        order_layout = QVBoxLayout(order_history_frame)

        # Section Title
        order_history_label = QLabel("Order History", self)
        order_layout.addWidget(order_history_label)

        # Create headers for the order table
        headers = ["Order ID", "Date/Time", "Asset", "Order Type", "Price Executed", "Quantity", "Total Cost/Value", "Order Status"]

        # Header layout
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        for header in headers:
            header_label = QtWidgets.QLabel(header, self)
            header_layout.addWidget(header_label)

        order_layout.addLayout(header_layout)

        # Example order data (would be dynamic in a real scenario)
        order_data = [
            ("12345", "2024-09-10 12:45", "BTC", "Buy", "$25,000", "0.5", "$12,500", "Filled"),
            ("12346", "2024-09-11 14:20", "ETH", "Sell", "$1,800", "2", "$3,600", "Pending"),
            ("12347", "2024-09-12 10:30", "XLM", "Buy", "$0.25", "1000", "$250", "Canceled"),
        ]

        # Populate order data
        for order in order_data:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(10)

            for value in order:
                order_label = QtWidgets.QLabel(value, self)
                row_layout.addWidget(order_label)

            order_layout.addLayout(row_layout)
            order_layout.addSpacing(10)
            order_history_frame.setLayout(order_layout)
