from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem, QFrame, QVBoxLayout, QLabel, QTableWidget


class TradingAnalysis(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Trading Analysis widget."""
        super().__init__(parent)
        self.controller = controller

        self.setGeometry(0, 0, 800, 600)
        self.setWindowTitle("Trading Analysis")
        self.setStyleSheet("background-color: #FFFFFF; color: #000000; font-size: 14px;")

        # Main layout for the widget
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Title
        title = QLabel("Market Trading Analysis")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Market", "Price", "Volume", "Change (%)", "Analysis"
        ])

        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Load market analysis data
        self.load_analysis_data()

    def load_analysis_data(self):
        """Load and display market analysis data."""
        try:
            # Mock data for analysis (replace this with actual data from the controller or API)
            data = [
                {"market": "EUR/USD", "price": 1.1234, "volume": 2000, "change": 0.25, "analysis": "Bullish"},
                {"market": "GBP/USD", "price": 1.2543, "volume": 1500, "change": -0.15, "analysis": "Bearish"},
                {"market": "USD/JPY", "price": 109.23, "volume": 3000, "change": 0.12, "analysis": "Neutral"},
                {"market": "AUD/USD", "price": 0.7654, "volume": 1800, "change": 0.40, "analysis": "Bullish"},
                {"market": "USD/CAD", "price": 1.3412, "volume": 2200, "change": -0.30, "analysis": "Bearish"},
            ]

            self.table.setRowCount(len(data))
            for row_idx, entry in enumerate(data):
                self.table.setItem(row_idx, 0, QTableWidgetItem(entry["market"]))
                self.table.setItem(row_idx, 1, QTableWidgetItem(f"{entry['price']:.4f}"))
                self.table.setItem(row_idx, 2, QTableWidgetItem(f"{entry['volume']}"))
                self.table.setItem(row_idx, 3, QTableWidgetItem(f"{entry['change']}%"))
                self.table.setItem(row_idx, 4, QTableWidgetItem(entry["analysis"]))

                # Set custom color for Change column based on positive/negative
                color = "#4CAF50" if entry["change"] > 0 else "#F44336"
                self.table.item(row_idx, 3).setForeground(QtGui.QColor(color))

        except Exception as e:
            raise f"Error loading market analysis data: {e}"
