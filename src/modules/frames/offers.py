from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QFrame

from src.modules.frames.market_depth import random_color


class Offers(QFrame):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(
            0, 0, 1530, 780
        )
        self.offers_df = self.controller.bot.offers_df  # Fetch the offer data from the controller
        self.create_widgets()

    def create_widgets(self):

        layout = QVBoxLayout()
        self.title_label = QLabel("Stellar Network Offers")
        layout.addWidget(self.title_label)
        self.table_widget = QTableWidget()
        self.populate_table()
        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def populate_table(self):
        self.table_widget.setColumnCount(5)
        self.table_widget.setRowCount(len(self.offers_df))
        self.table_widget.setHorizontalHeaderLabels([
            "Market", "Price", "Volume", "Change (%)", "Analysis"
        ])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setAlternatingRowColors(True)
        for i, offer in enumerate(self.offers_df.itertuples()):
            market = offer.market
            price = offer.price
            volume = offer.volume
            change = offer.change
            analysis = self.analyze_offer(change)
            self.table_widget.setItem(i, 0, QTableWidgetItem(market))
            self.table_widget.setItem(i, 1, QTableWidgetItem(str(price)))
            self.table_widget.setItem(i, 2, QTableWidgetItem(str(volume)))
            self.table_widget.setItem(i, 3, QTableWidgetItem(str(change)))
            self.table_widget.setItem(i, 4, QTableWidgetItem(analysis))
            self.table_widget.item(i, 0).setBackgroundColor(random_color())

            # Set custom color for Change column based on positive/negative
            color = "#4CAF50" if change > 0 else "#F44336"
            self.table_widget.item(i, 3).setForeground(Qt.QColor(color))
            # Highlight the volume cells in a different color
            self.table_widget.item(i, 2).setBackgroundColor(Qt.QColor("#f5f5f5"))

    def analyze_offer(self, change):
        if change < -0.05:
            return "Strong Sell"
        elif change > 0.05:
            return "Strong Buy"
        else:
            return "Neutral"


