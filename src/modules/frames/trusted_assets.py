from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QComboBox
from stellar_sdk import Asset


class TrustedAsset(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Trusted Asset widget."""
        super().__init__(parent)
        self.controller = controller  # Store reference to the controller (if needed)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        self.initUI()

    def initUI(self):
        """Initialize the UI for listing and selecting trusted assets."""
        # Layout
        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel("Select Trusted Asset")
        layout.addWidget(self.title_label)

        # Asset selection (ComboBox or CheckBoxes can be used)
        self.asset_combo = QComboBox(self)
        self.asset_combo.addItems(["XLM", "BTC", "ETH", "USDT", "ADA"])  # Example assets
        layout.addWidget(self.asset_combo)

        # Button to create trusted line on ledger
        self.create_button = QPushButton("Create Trusted Line", self)
        self.create_button.clicked.connect(self.create_trusted_line)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def create_trusted_line(self, asset:Asset) :
            return self.controller.bot.create_trusted_line(asset)


    def get_trusted_assets(self):
        """Fetch and return a list of trusted assets."""
        return self.controller.bot.get_trusted_assets()
