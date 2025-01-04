from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QComboBox, QTableWidget, QTableWidgetItem
from stellar_sdk import Asset


class TrustedAsset(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Trusted Asset widget."""
        super().__init__(parent)
        self.create_button = None
        self.controller = controller  # Store reference to the controller (if needed)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.asset_table = None
        self.title_label = None
        self.asset_select_combo = None
        self.add_asset_button = None
        self.asset_select_combo = QComboBox(self)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI for listing and selecting trusted assets."""
        # Layout
        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel("Select Trusted Asset")
        layout.addWidget(self.title_label)

        # Table for trusted assets (Asset, Code, Issuer)
        self.asset_table = QTableWidget(self)
        self.asset_table.setColumnCount(3)  # Columns: Asset, Code, Issuer
        self.asset_table.setHorizontalHeaderLabels(["Asset", "Code", "Issuer"])

        # Sample assets for demonstration (in a real app, fetch these from a data source)
        assets_data = [
            ("XLM", "XLM", "GABR23DHTY4DQU3RE34V1234T4B2"),
            ("BTC", "BTC", "GD26D2DW6T2J7T7ETR4F4F2TQ6TZ"),
            ("ETH", "ETH", "GCTMHRJNKFN34X23BR6RTY26T26V"),
            ("USDT", "USDT", "GAFD34D8G4VR9FN87D4FG2J7H23B"),
            ("ADA", "ADA", "GFS43KJH8D3G4SH23R6L74T77EJ")
        ]

        # Add data to the table
        for row, (asset, code, issuer) in enumerate(assets_data):
            self.asset_table.insertRow(row)
            self.asset_table.setItem(row, 0, QTableWidgetItem(asset))
            self.asset_table.setItem(row, 1, QTableWidgetItem(code))
            self.asset_table.setItem(row, 2, QTableWidgetItem(issuer))

        layout.addWidget(self.asset_table)

        # Button to create trusted line on ledger
        self.create_button = QPushButton("Create Trusted Line", self)
        self.create_button.clicked.connect(self.create_trusted_line)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_trusted_line(self):
        """Create a trust line with the selected asset and issuer."""
        # Get selected row
        selected_row = self.asset_table.currentRow()

        if selected_row == -1:
            # No row selected
            return

        # Get asset and issuer data from the table
        selected_asset_name = self.asset_table.item(selected_row, 0).text()
        asset_code = self.asset_table.item(selected_row, 1).text()
        asset_issuer = self.asset_table.item(selected_row, 2).text()

        # Create the Asset object (use code and issuer from table)
        asset = Asset(asset_code, asset_issuer)

        # Call the controller to create the trust line
        self.controller.bot.create_trusted_line(asset)

    def get_trusted_assets(self):
        """Fetch and return a list of trusted assets."""
        return self.controller.bot.get_trusted_assets()
