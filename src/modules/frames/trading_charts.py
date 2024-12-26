from PyQt5 import QtWidgets

from src.modules.frames.bar_chart import BarChart
from src.modules.frames.candles_stick_chart import CandlestickChart
from src.modules.frames.heikin_ashi import HeikinAshi
from src.modules.frames.line_chart import LineChart
from src.modules.frames.renko import Renko


class TradingCharts(QtWidgets.QWidget):
    def __init__(self, parent=None, controller=None):
        """Initialize the TradingCharts class."""
        super().__init__(parent,controller)
        self.status_label = None
        self.assets_combobox2 = None
        self.chart_type_combobox = None
        self.assets_combobox1 = None
        self.controller = controller
        self.trading_mode = 'Manual'
        self.chart_type = "candle"  # Default chart type
        self.charts = {
            'bar': BarChart,
            'candle': CandlestickChart,
            'heikin_ashi': HeikinAshi,
            'line': LineChart,
            'renko': Renko}
        self.setGeometry(
            0, 0, 1540, 780,  # x, y, width, height
    
        )

        # Sample data for testing
        self.data = {
            'Open': [100, 120, 90, 110, 130, 105, 115, 125, 140, 110],
            'High': [110, 130, 105, 125, 145, 115, 125, 135, 150, 120],
            'Low': [90, 100, 85, 95, 115, 85, 95, 105, 120, 90],
            'Close': [105, 125, 100, 115, 135, 105, 115, 125, 140, 115],
            'Volume': [1000, 2000, 1500, 1800, 3000, 1500, 1800, 2500, 500, 1800],
            'Date': [
                '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04',
                '2023-01-05', '2023-01-06', '2023-01-07', '2023-01-08',
                '2023-01-09', '2023-01-10'
            ]
        }

        # Layout for the whole widget
        layout = QtWidgets.QVBoxLayout(self)

        # Setup toolbar and content
        self.setup_toolbar(layout)
        self.setup_content(layout)

        # Create a QTabWidget for managing charts
        self.notebook = QtWidgets.QTabWidget(self)
        self.notebook.setObjectName("notebook")
        self.setGeometry(
            0, 0, 1530, 780,  # x, y, width, height
        )
        layout.addWidget(self.notebook)

        # Add the first chart by default
        self.add_chart()

    def setup_toolbar(self, layout):
        """Sets up the toolbar with controls for asset and chart type selection."""
        toolbar = QtWidgets.QWidget(self)
        toolbar_layout = QtWidgets.QHBoxLayout(toolbar)
      
        # Add asset selectors
        asset_label = QtWidgets.QLabel("Select Asset:", self)
        toolbar_layout.addWidget(asset_label)

        self.assets_combobox1 = QtWidgets.QComboBox(self)
        self.assets_combobox1.addItems(["BTC", "ETH", "LTC", "XRP", "ADA"])
        toolbar_layout.addWidget(self.assets_combobox1)

        self.assets_combobox2 = QtWidgets.QComboBox(self)
        self.assets_combobox2.addItems(["USD", "EUR", "USDT", "BTC"])
        toolbar_layout.addWidget(self.assets_combobox2)

        # Add chart type selector
        chart_type_label = QtWidgets.QLabel("Chart Type:", self)
        toolbar_layout.addWidget(chart_type_label)

        self.chart_type_combobox = QtWidgets.QComboBox(self)
        self.chart_type_combobox.addItems(["candle", "line", "bar", "renko", "heikin-ashi"])
        self.chart_type_combobox.currentIndexChanged.connect(self.update_chart_type)
        toolbar_layout.addWidget(self.chart_type_combobox)

        # Add buttons with icons
        add_chart_button = QtWidgets.QPushButton("Add Chart", self)
        add_chart_button.clicked.connect(self.add_chart)
        toolbar_layout.addWidget(add_chart_button)

        remove_chart_button = QtWidgets.QPushButton("Remove Chart", self)
        remove_chart_button.clicked.connect(self.remove_chart)
        toolbar_layout.addWidget(remove_chart_button)

        # Trading mode status
        self.status_label = QtWidgets.QLabel(f"Mode: {self.trading_mode}", self)
        toolbar_layout.addWidget(self.status_label)
      
     
        layout.addWidget(toolbar)

    def setup_content(self, layout):
        """Sets up the main content area where charts will be displayed."""
        content_frame = QtWidgets.QFrame(self)
        content_frame.setContentsMargins(0, 0, 1540, 780)
        layout.addWidget(content_frame)

    def add_chart(self):
        """Adds a new chart tab to the QTabWidget."""
        selected_asset = f"{self.assets_combobox1.currentText()}/{self.assets_combobox2.currentText()}"

        new_tab = QtWidgets.QWidget()
       # new_tab.setStyleSheet("background-color : #FFFFFF;")
        new_tab.setGeometry( 
            0, 0, 1530, 780  # Set the size of the tab to the full width and height of the content frame
        )
        tab_layout = QtWidgets.QVBoxLayout(new_tab)


        tab_layout.addWidget(QtWidgets.QLabel(f"{selected_asset} Chart", self))

        # Add chart based on selection
        if self.chart_type == "candle":
            CandlestickChart(new_tab, self.controller, self.data)
        elif self.chart_type == "line":
            LineChart(new_tab, self.data)
        elif self.chart_type == "bar":
            BarChart(new_tab, self.controller, self.data)
        elif self.chart_type == "renko":
            Renko(new_tab, self.controller, self.data)
        elif self.chart_type == "heikin-ashi":
            HeikinAshi(new_tab, self.controller, self.data)
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid chart type selected.")
            return

        self.notebook.addTab(new_tab, f"{selected_asset} Chart")

    def update_chart_type(self):
        """Updates the chart type and refreshes the chart when a new type is selected."""
        self.chart_type = self.chart_type_combobox.currentText()
        self.add_chart()

    def remove_chart(self):
        """Removes the currently selected chart tab."""
        if self.notebook.count() > 0:
            self.notebook.removeTab(self.notebook.currentIndex())
        else:
            QtWidgets.QMessageBox.information(self, "Info", "No more charts to remove.")
   