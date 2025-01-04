from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFrame


class TaxConsiderations(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Tax Considerations widget."""
        super().__init__(parent)
        self.controller = controller


        # Main layout for the widget
        layout = QtWidgets.QVBoxLayout(self)

        # Create the tax considerations section
        self.create_widgets(layout)

    def create_widgets(self, layout):
        """Create and arrange widgets for the tax considerations section."""

        # Tax Considerations Section
        tax_frame = QtWidgets.QFrame(self)
        tax_frame.setFixedHeight(250)
        layout.addWidget(tax_frame)

        tax_layout = QtWidgets.QVBoxLayout(tax_frame)

        # Create labels for the tax considerations section
        self.create_label("Tax Considerations", "font-size: 16pt; font-weight: bold; ", tax_layout)
        self.create_label("Realized Gains", "font-size: 14pt; font-weight: bold; ", tax_layout)

        # Realized Gains table header
        realized_header_layout = QtWidgets.QHBoxLayout()
        realized_header_layout.setSpacing(50)

        # Create labels for the table headers
        self.create_label("Asset", "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;", realized_header_layout)
        self.create_label("Realized P/L", "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;", realized_header_layout)
        self.create_label("Date of Sale", "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;", realized_header_layout)
        self.create_label("Tax Impact", "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;", realized_header_layout)
        tax_layout.addLayout(realized_header_layout)

        # Example data for realized gains
        realized_data_layout = QtWidgets.QHBoxLayout()
        self.create_data_row(realized_data_layout, "Bitcoin", "$1,200", "2023-08-15", "$360")
        tax_layout.addLayout(realized_data_layout)

        self.create_label("Unrealized Gains/Losses", "font-size: 14pt; font-weight: bold; color: #1F618D;", tax_layout)

        # Unrealized Gains/Losses table header
        unrealized_header_layout = QtWidgets.QHBoxLayout()
        unrealized_header_layout.setSpacing(50)
        self.create_label("Asset", "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;", unrealized_header_layout)
        self.create_label("Unrealized P/L", "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;", unrealized_header_layout)
        tax_layout.addLayout(unrealized_header_layout)

        # Example data for unrealized gains/losses
        unrealized_data_layout = QtWidgets.QHBoxLayout()
        self.create_data_row(unrealized_data_layout, "Ethereum", "$800", "", "")
        tax_layout.addLayout(unrealized_data_layout)

    def create_label(self, text, style, layout):
        """Helper function to create a styled label."""
        label = QtWidgets.QLabel(text, self)
        label.setStyleSheet(style)
        layout.addWidget(label)

    def create_data_row(self, layout, asset, realized_pl, date_of_sale, tax_impact):
        """Helper function to create a data row for the table."""
        asset_entry = QtWidgets.QLabel(asset, self)
        layout.addWidget(asset_entry)

        realized_pl_entry = QtWidgets.QLabel(realized_pl, self)
        layout.addWidget(realized_pl_entry)

        date_entry = QtWidgets.QLabel(date_of_sale, self)
        layout.addWidget(date_entry)

        tax_impact_entry = QtWidgets.QLabel(tax_impact, self)
        layout.addWidget(tax_impact_entry)
