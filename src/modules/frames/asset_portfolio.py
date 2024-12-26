from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFrame


class Portfolio(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Asset Portfolio widget."""
        super().__init__(parent)

        # Initialize the controller for this widget
        # This allows the widget to communicate with the main application
        # and access its data and methods.
        # Replace this with the actual controller object when using this code in a real application.
        # For example, if you're using a Qt application, you might have something like this:
        # self.controller = QtCore.QObject.connect(parent, QtCore.SIGNAL("update_asset_portfolio_signal"), self.update_asset_portfolio)
        # In the main application, you would emit this signal when the asset portfolio data changes.
        # And in this widget, you would connect to it and update the UI accordingly.
        # self.controller = parent  # In a real application, replace this with the actual controller object.
        #
        # In this example, we're just using a dummy controller for demonstration purposes

        self.controller = controller
        self.setGeometry(
            0, 0,1530,780
        )
        self.setStyleSheet("background-color: #EAECEE;")
        # Main layout for the widget
        layout = QtWidgets.QVBoxLayout(parent)


        # Create and arrange the labels and entries for the asset portfolio
        self.create_widgets(layout)

    def create_widgets(self, layout):
        """Create and arrange widgets for the asset portfolio section."""

        self._extracted_from_create_widgets_5(
            "Asset Portfolio",
            "font-size: 16px; font-weight: bold; color: darkblue;",
            layout,
        )
        self._extracted_from_create_widgets_5(
            "Holdings", "font-size: 14px; font-weight: bold; color: blue;", layout
        )
        # Create a grid layout for the holdings table
        holdings_grid = QtWidgets.QGridLayout()

        # Holdings Table Headers
        headers = ["Asset Name", "Quantity", "Entry Price", "Current Price", "% Change", "Unrealized P/L", "Position Type", "Market"]
        for col, header in enumerate(headers):
            header_label = QtWidgets.QLabel(header)
            header_label.setStyleSheet("font-size: 10px; font-weight: bold; color: gray;")
            holdings_grid.addWidget(header_label, 0, col)

        # Holdings Table Entries (Example Data)
        holdings_data = [
            ["BTC", "2.5", "$10,000", "$12,500", "+25%", "$6,250", "Long", "Crypto"],
            ["AAPL", "100", "$150", "$180", "+20%", "$3,000", "Long", "Stock"],
            ["ETH", "10", "$2,000", "$2,400", "+20%", "$4,000", "Long", "Crypto"],
        ]

        # Populate the grid with holdings data
        for row, holding in enumerate(holdings_data, 1):
            for col, item in enumerate(holding):
                item_label = QtWidgets.QLabel(item)
                holdings_grid.addWidget(item_label, row, col)

        layout.addLayout(holdings_grid)

        self._extracted_from_create_widgets_5(
            "Top 5 Performers (based on ROI)",
            "font-size: 14px; font-weight: bold; color: blue;",
            layout,
        )
        # Top 5 Performers Table Headers
        top_performers_grid = QtWidgets.QGridLayout()

        headers = ["Asset", "ROI", "Profit", "Trade Date"]
        for col, header in enumerate(headers):
            header_label = QtWidgets.QLabel(header)
            header_label.setStyleSheet("font-size: 10px; font-weight: bold; color: gray;")
            top_performers_grid.addWidget(header_label, 0, col)

        # Top Performers Data (Example Data)
        top_performers_data = [
            ["BTC", "+25%", "$6,250", "2024-08-10"],
            ["AAPL", "+20%", "$3,000", "2024-07-15"],
            ["ETH", "+20%", "$4,000", "2024-09-01"],
            ["TSLA", "+15%", "$1,500", "2024-06-12"],
            ["AMZN", "+12%", "$2,200", "2024-08-01"],
        ]

        # Populate the grid with top performers data
        for row, performer in enumerate(top_performers_data, 1):
            for col, item in enumerate(performer):
                item_label = QtWidgets.QLabel(item)
                top_performers_grid.addWidget(item_label, row, col)

        layout.addLayout(top_performers_grid)

    # TODO Rename this here and in `create_widgets`
    def _extracted_from_create_widgets_5(self, arg0, arg1, layout):
        # Section: Asset Portfolio
        portfolio_label = QtWidgets.QLabel(arg0)
        portfolio_label.setStyleSheet(arg1)
        layout.addWidget(portfolio_label)

