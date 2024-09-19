from PyQt5 import QtWidgets

class TaxConsiderations(QtWidgets.QWidget):
    def __init__(self, parent=None, controller=None):
        """Initialize the Tax Considerations widget."""
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(0, 0, 1530, 780)
        self.setStyleSheet("background-color: #EAECEE;")

        # Main layout for the widget
        layout = QtWidgets.QVBoxLayout(self)

        # Create the tax considerations section
        self.create_widgets(layout)

    def create_widgets(self, layout):
        """Create and arrange widgets for the tax considerations section."""

        # Tax Considerations Section
        tax_frame = QtWidgets.QFrame(self)
        tax_frame.setStyleSheet("background-color: #D5D8DC; border: 1px solid #1F618D;")
        tax_frame.setFixedHeight(250)
        layout.addWidget(tax_frame)

        tax_layout = QtWidgets.QVBoxLayout(tax_frame)

        self._extracted_from_create_widgets_12(
            "Tax Considerations",
            "font-size: 16pt; font-weight: bold; color: #1F618D;",
            tax_layout,
        )
        self._extracted_from_create_widgets_12(
            "Realized Gains",
            "font-size: 14pt; font-weight: bold; color: #1F618D;",
            tax_layout,
        )
        # Realized Gains table header
        realized_header_layout = QtWidgets.QHBoxLayout()
        realized_header_layout.setSpacing(50)

        self._extracted_from_create_widgets_12(
            "Asset",
            "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;",
            realized_header_layout,
        )
        self._extracted_from_create_widgets_12(
            "Realized P/L",
            "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;",
            realized_header_layout,
        )
        self._extracted_from_create_widgets_12(
            "Date of Sale",
            "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;",
            realized_header_layout,
        )
        self._extracted_from_create_widgets_12(
            "Tax Impact",
            "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;",
            realized_header_layout,
        )
        tax_layout.addLayout(realized_header_layout)

        # Example data for realized gains
        realized_data_layout = QtWidgets.QHBoxLayout()
        asset_entry = QtWidgets.QLabel("Bitcoin", self)
        realized_data_layout.addWidget(asset_entry)

        realized_pl_entry = QtWidgets.QLabel("$1,200", self)
        realized_data_layout.addWidget(realized_pl_entry)

        date_entry = QtWidgets.QLabel("2023-08-15", self)
        realized_data_layout.addWidget(date_entry)

        tax_impact_entry = QtWidgets.QLabel("$360", self)
        realized_data_layout.addWidget(tax_impact_entry)

        tax_layout.addLayout(realized_data_layout)

        self._extracted_from_create_widgets_12(
            "Unrealized Gains/Losses",
            "font-size: 14pt; font-weight: bold; color: #1F618D;",
            tax_layout,
        )
        # Unrealized Gains/Losses table header
        unrealized_header_layout = QtWidgets.QHBoxLayout()
        unrealized_header_layout.setSpacing(50)

        self._extracted_from_create_widgets_12(
            "Asset",
            "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;",
            unrealized_header_layout,
        )
        self._extracted_from_create_widgets_12(
            "Unrealized P/L",
            "font-size: 12pt; font-weight: bold; background-color: #AEB6BF;",
            unrealized_header_layout,
        )
        tax_layout.addLayout(unrealized_header_layout)

        # Example data for unrealized gains/losses
        unrealized_data_layout = QtWidgets.QHBoxLayout()

        unrealized_asset_entry = QtWidgets.QLabel("Ethereum", self)
        unrealized_data_layout.addWidget(unrealized_asset_entry)

        unrealized_pl_entry = QtWidgets.QLabel("$800", self)
        unrealized_data_layout.addWidget(unrealized_pl_entry)

        tax_layout.addLayout(unrealized_data_layout)

    # TODO Rename this here and in `create_widgets`
    def _extracted_from_create_widgets_12(self, arg0, arg1, arg2):
        tax_label = QtWidgets.QLabel(arg0, self)
        tax_label.setStyleSheet(arg1)
        arg2.addWidget(tax_label)
