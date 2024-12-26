from PyQt5 import QtWidgets, QtCore

class TradingStrategies(QtWidgets.QWidget):
    def __init__(self, parent=None, controller=None):
        """Initialize the Trading Strategies widget."""
        super().__init__(parent)
        self.controller = controller
        
        self.setGeometry(
            0, 0,1530,780
        )
       

        # Layout for the widget
        layout = QtWidgets.QVBoxLayout(self)

        # Create the trading strategies section
        self.create_widgets(layout)

    def create_widgets(self, layout):
        """Create and arrange widgets for the trading strategies section."""
        active_strategies_frame = self.create_frame("#D3D3D3", "Active Strategies")
        layout.addWidget(active_strategies_frame)

        # Active Strategies Headers
        headers = ["Strategy Name", "Description", "Timeframe", "Assets Traded", "Signal Type"]
        header_x_positions = [10, 130, 300, 400, 500]

        # Add header labels
        for i, header in enumerate(headers):
            label = QtWidgets.QLabel(header, self)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #003366;")
            label.setGeometry(header_x_positions[i], 50, 120, 30)
            layout.addWidget(label)

        # Example active strategy data
        active_strategy_data = [
            ("Trend Following", "Follows the prevailing market trend", "Daily", "BTC, ETH", "Buy/Sell Signal"),
            ("Mean Reversion", "Trades when prices deviate from the mean", "4H", "Stocks", "Entry/Exit Signal"),
        ]

        y_position = 80
        for strategy in active_strategy_data:
            for i, value in enumerate(strategy):
                entry = QtWidgets.QLineEdit(value, self)
                entry.setReadOnly(True)
                entry.setAlignment(QtCore.Qt.AlignCenter)
                entry.setGeometry(header_x_positions[i], y_position, 120, 30)
                layout.addWidget(entry)
            y_position += 30

        # Performance section
        performance_frame = self.create_frame("#C8C8C8", "Performance of Strategies")
        layout.addWidget(performance_frame)

        # Performance Headers
        performance_headers = ["Strategy Name", "Total Trades", "% Win", "% Loss", "Net P/L", "Avg Holding Time", "Success Rate"]
        performance_x_positions = [10, 130, 240, 320, 400, 480, 550]

        for i, header in enumerate(performance_headers):
            label = QtWidgets.QLabel(header, self)
            label.setStyleSheet("font-size: 12px; font-weight: bold; color: #003366;")
            label.setGeometry(performance_x_positions[i], 50, 120, 30)
            layout.addWidget(label)

        # Example performance data
        performance_data = [
            ("Trend Following", "150", "60%", "40%", "$5000", "2 Days", "65%"),
            ("Mean Reversion", "120", "55%", "45%", "$2000", "4 Hours", "58%"),
            ("Arbitrage", "80", "45%", "55%", "$1500", "1 Hour", "70%"),
            ("Volatility", "100", "50%", "50%", "$1000", "3 Days", "75%"),
            ("Pair Trading", "180", "65%", "35%", "$2500", "1 Hour", "80%"),
            ("Spread Trading", "75", "40%", "60%", "$1200", "2 Hours", "78%")
        ]

        y_position = 80
        for performance in performance_data:
            for i, value in enumerate(performance):
                entry = QtWidgets.QLineEdit(value, self)
                entry.setReadOnly(True)
                entry.setAlignment(QtCore.Qt.AlignCenter)
                entry.setGeometry(performance_x_positions[i], y_position, 120, 30)
                layout.addWidget(entry)
            y_position += 30

    def create_frame(self, bg_color, title):
        """Create a styled frame with a title label."""
        frame = QtWidgets.QFrame(self)
       # frame.setStyleSheet(f"background-color: {bg_color}; border: 2px solid #003366;")
      #  frame.setFixedSize(600, 250)

        title_label = QtWidgets.QLabel(title, frame)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #003366;")
        title_label.setGeometry(10, 10, 200, 30)

        return frame
