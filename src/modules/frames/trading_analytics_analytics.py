from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFrame


class  TradingAnalytics(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Performance Analytics widget."""
        super().__init__(parent)
        self.controller = controller

        self.setGeometry(
            10, 10, 1500, 780
        )

        # Main layout for the widget
        layout = QtWidgets.QVBoxLayout(self)

        # Create the performance analytics section
        self.create_widgets(layout)

    def create_widgets(self, layout):
        """Create and arrange widgets for the performance analytics section."""
        
        # Monthly/Yearly Performance Section
        performance_frame = self.create_section_frame("#D6DBDF", "Monthly/Yearly Performance")
        layout.addWidget(performance_frame)

        # Performance Headers
        headers = ["Month/Year", "Starting Balance", "Ending Balance", "% Growth"]
        x_positions = [10, 150, 290, 450]

        # Add headers
        for i, header in enumerate(headers):
            label = QtWidgets.QLabel(header, performance_frame)
            label.setStyleSheet("font-weight: bold; color: #1F618D; font-size: 12pt;")
            label.move(x_positions[i], 50)

        # Example performance data (replace with dynamic data later)
        performance_data = [
            ("January 2024", "$10,000", "$11,000", "10%"),
            ("February 2024", "$11,000", "$12,500", "13.64%"),
        ]

        # Add performance data
        for row_num, perf in enumerate(performance_data):
            y_position = 90 + row_num * 30
            for col_num, value in enumerate(perf):
                entry = QtWidgets.QLineEdit(performance_frame)
                entry.setFixedWidth(100)
                entry.setText(value)
                entry.setReadOnly(True)
                entry.move(x_positions[col_num], y_position)

        # Key Metrics Section
        metrics_frame = self.create_section_frame("#D1F2EB", "Key Metrics")
        layout.addWidget(metrics_frame)

        # Metrics Headers
        metrics_headers = ["ROI (%) by Asset Class", "Trade Win Rate (%)", "Avg Profit/Trade", "Avg Loss/Trade"]
        x_positions_metrics = [10, 150, 290, 450]

        for i, header in enumerate(metrics_headers):
            label = QtWidgets.QLabel(header, metrics_frame)
            label.setStyleSheet("font-weight: bold; color: #1F618D; font-size: 12pt;")
            label.move(x_positions_metrics[i], 50)

        # Example key metrics data (replace with dynamic data later)
        metrics_data = [
            ("12%", "60%", "$200", "$100"),
        ]

        # Add key metrics data
        for metric in metrics_data:
            for col_num, value in enumerate(metric):
                entry = QtWidgets.QLineEdit(metrics_frame)
                entry.setFixedWidth(100)
                entry.setText(value)
                entry.setReadOnly(True)
                entry.move(x_positions_metrics[col_num], 90)

        # Equity Curve Section
        equity_curve_frame = self.create_section_frame("#EBDEF0", "Equity Curve")
        layout.addWidget(equity_curve_frame)

        self._extracted_from_create_section_frame_66(
            "Graph of balance over time will be displayed here.",
            equity_curve_frame,
            "color: #1F618D; font-size: 12pt;",
            50,
        )

    def create_section_frame(self, bg_color, section_title):
        """Helper function to create a section frame with a title."""
        frame = QtWidgets.QFrame(self)
        frame.setStyleSheet(f"background-color: {bg_color}; border: 1px solid #1F618D;")
        frame.setFixedHeight(200)

        self._extracted_from_create_section_frame_66(
            section_title,
            frame,
            "font-weight: bold; color: #1F618D; font-size: 16pt;",
            10,
        )
        return frame

    # TODO Rename this here and in `create_widgets` and `create_section_frame`
    def _extracted_from_create_section_frame_66(self, arg0, arg1, arg2, arg3):
        equity_curve_placeholder = QtWidgets.QLabel(arg0, arg1)
        equity_curve_placeholder.setStyleSheet(arg2)
        equity_curve_placeholder.move(10, arg3)
