from PySide6 import QtWidgets,  QtCore
from PySide6.QtWidgets import QFrame


class RiskManagement(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Risk Management widget."""
        super().__init__(parent)

        self.setGeometry(0, 0, 1530, 780)
        self.controller = controller
        # Main layout for the widget
        layout = QtWidgets.QVBoxLayout(self)

        # Create the risk management section
        self.create_widgets(layout)

    def create_widgets(self, layout):
        """Create and arrange widgets for the risk management section."""
        # Risk Management Section
        risk_management_frame = QtWidgets.QFrame(self)
        risk_management_frame.setFixedHeight(200)
        layout.addWidget(risk_management_frame)
        risk_management_layout = QtWidgets.QVBoxLayout(risk_management_frame)
        risk_management_label = QtWidgets.QLabel("Risk Management", self)
        risk_management_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #003366;")
        risk_management_layout.addWidget(risk_management_label, alignment=QtCore.Qt.AlignCenter)

        # Risk Management Headers
        risk_headers = ["Max Risk per Trade (%)", "Max Daily Loss", "Stop-Loss Levels", "Take-Profit Levels"]
        risk_data = ["2%", "$1000", "5%", "10%"]

        # Create labels and entries for risk data
        for header, data in zip(risk_headers, risk_data):
            risk_row_layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(header, self)
            label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #003366;")
            risk_row_layout.addWidget(label)

            entry = QtWidgets.QLineEdit(self)
            entry.setFixedWidth(100)
            entry.setText(data)
            entry.setReadOnly(True)
            risk_row_layout.addWidget(entry)
            risk_management_layout.addLayout(risk_row_layout)

        # Risk Metrics Section
        risk_metrics_frame = QtWidgets.QFrame(self)
        risk_metrics_frame.setStyleSheet("background-color: #C8C8C8; border: 1px solid #003366;")
        risk_metrics_frame.setFixedHeight(200)
        layout.addWidget(risk_metrics_frame)

        risk_metrics_layout = QtWidgets.QVBoxLayout(risk_metrics_frame)
        risk_metrics_label = QtWidgets.QLabel("Risk Metrics", self)
        risk_metrics_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #003366;")
        risk_metrics_layout.addWidget(risk_metrics_label, alignment=QtCore.Qt.AlignCenter)

        # Risk Metrics Headers
        metrics_headers = ["Sharpe Ratio", "Max Drawdown", "Risk-to-Reward Ratio", "Volatility"]
        metrics_data = ["1.5", "15%", "2:1", "12%"]

        # Create labels and entries for metrics data
        for header, data in zip(metrics_headers, metrics_data):
            metrics_row_layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(header, self)
            label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #003366;")
            metrics_row_layout.addWidget(label)
            entry = QtWidgets.QLineEdit(self)
            entry.setFixedWidth(100)
            entry.setText(data)
            entry.setReadOnly(True)
            metrics_row_layout.addWidget(entry)
            risk_metrics_layout.addLayout(metrics_row_layout)
