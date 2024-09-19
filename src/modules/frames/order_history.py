from PyQt5 import QtWidgets

class OrderHistory(QtWidgets.QWidget):
    def __init__(self, parent=None, controller=None):
        """Initialize the Order History widget."""
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(0, 0, 1530, 780)
        self.setStyleSheet("background-color: #F5F5F5;")

        # Main layout for the widget
        layout = QtWidgets.QVBoxLayout(self)

        # Create the order history section
        self.create_widgets(layout)

    def create_widgets(self, layout):
        """Create and arrange the widgets for the order history."""
        # Order History Frame
        order_history_frame = QtWidgets.QFrame(self)
        order_history_frame.setStyleSheet("background-color: #E0E0E0; border: 1px solid #000;")
        order_history_frame.setFixedSize(600, 400)
        layout.addWidget(order_history_frame)

        order_layout = QtWidgets.QVBoxLayout(order_history_frame)

        # Section Title
        order_history_label = QtWidgets.QLabel("Order History", self)
        order_history_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #003366;")
        order_layout.addWidget(order_history_label)

        # Create headers for the order table
        headers = ["Order ID", "Date/Time", "Asset", "Order Type", "Price Executed", "Quantity", "Total Cost/Value", "Order Status"]

        # Header layout
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(10)

        for header in headers:
            header_label = QtWidgets.QLabel(header, self)
            header_label.setStyleSheet("font-size: 10pt; font-weight: bold; color: #003366; background-color: #E0E0E0;")
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
            row_layout = QtWidgets.QHBoxLayout()
            row_layout.setSpacing(10)

            for value in order:
                order_label = QtWidgets.QLabel(value, self)
                order_label.setStyleSheet("font-size: 10pt; background-color: #F7F9F9;")
                row_layout.addWidget(order_label)

            order_layout.addLayout(row_layout)
