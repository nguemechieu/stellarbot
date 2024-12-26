from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFrame


class Offers(QFrame):
    """Widget to display offers from Stellar."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller


        # Main layout for the widget
        layout = QtWidgets.QVBoxLayout(self)

        # Title label
        title_label = QtWidgets.QLabel("Offers", self)
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #343a40;")
        layout.addWidget(title_label)

        # Create the table widget to display the offers
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Offer ID", "Seller", "Selling Asset", "Buying Asset", "Amount", "Price"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Fetch and display offers
        self.update_offers()

        # Automatically update the offers every 60 seconds
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_offers)
        self.timer.start(60000)  # 60 seconds

    def fetch_offers(self):
        """Fetch offer data from Stellar API and populate the table."""
        try:



            # Get the offer data from the trading engine's get_offers() method
            offers_data = self.controller.bot.get_offers()
            if offers_data is None:
                print("No offers found")
                return

            # Clear the current data in the table
            self.table.setRowCount(0)

            # Format and insert offer into the table
            for offer in offers_data:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                
                offer_id = offer.get("id")
                seller = offer.get("seller")
                selling_asset = self.format_asset(offer["selling"])
                buying_asset = self.format_asset(offer["buying"])
                amount = offer.get("amount")
                price = offer.get("price")

                # Insert into the table
                self.table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(offer_id)))
                self.table.setItem(row_position, 1, QtWidgets.QTableWidgetItem(seller))
                self.table.setItem(row_position, 2, QtWidgets.QTableWidgetItem(selling_asset))
                self.table.setItem(row_position, 3, QtWidgets.QTableWidgetItem(buying_asset))
                self.table.setItem(row_position, 4, QtWidgets.QTableWidgetItem(str(amount)))
                self.table.setItem(row_position, 5, QtWidgets.QTableWidgetItem(str(price)))

        except Exception as e:
            print(f"Error fetching offers: {e}")
            self.controller.server_msg['message'] = f"Error fetching offers: {e}"

    def format_asset(self, asset):
        """Helper function to format the asset data."""
        if asset["asset_type"] == "native":
            return "XLM"
        return f'{asset["asset_code"]} ({asset["asset_issuer"][:5]}...)'

    def update_offers(self):
        """Fetch and display new offers since the last update."""
        self.fetch_offers()
