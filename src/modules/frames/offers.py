from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QDialog, QFormLayout, QPushButton, QTextEdit
)
from src.modules.frames.market_depth import random_color
import json


class Offers(QFrame):
    """Display active Stellar offers in a table view."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.table_widget = None
        self.controller = controller
        self.setGeometry(0, 0, 1530, 780)

        self.offers_df = getattr(controller.bot, "offers_df", None)
        self.create_widgets()

    # ------------------------------------------------------------------
    def create_widgets(self):
        layout = QVBoxLayout(self)
        self.title_label = QLabel("💹 Stellar Network Offers", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(self.title_label)

        self.table_widget = QTableWidget(self)
        layout.addWidget(self.table_widget)

        if self.offers_df is not None and not self.offers_df.empty:
            self.populate_table()
            self.table_widget.cellDoubleClicked.connect(self.show_offer_details)
        else:
            placeholder = QLabel("No offers available.")
            placeholder.setAlignment(Qt.AlignCenter)
            layout.addWidget(placeholder)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    def populate_table(self):
        df = self.offers_df
        expected_cols = ["seller", "selling", "buying", "amount", "price", "id"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None

        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["Market", "Price", "Volume", "Change (%)", "Analysis"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_widget.setRowCount(len(df))

        for i, offer in enumerate(df.itertuples()):
            try:
                selling = getattr(offer, "selling", {}) or {}
                buying = getattr(offer, "buying", {}) or {}

                market = f"{selling.get('asset_code', 'XLM')}/{buying.get('asset_code', 'USDC')}"
                price = float(getattr(offer, "price", 0))
                volume = float(getattr(offer, "amount", 0))
                change = self.calculate_change(price)
                analysis = self.analyze_offer(change)

                # Fill rows
                self.table_widget.setItem(i, 0, QTableWidgetItem(market))
                self.table_widget.setItem(i, 1, QTableWidgetItem(f"{price:.5f}"))
                self.table_widget.setItem(i, 2, QTableWidgetItem(f"{volume:.2f}"))
                self.table_widget.setItem(i, 3, QTableWidgetItem(f"{change:.2f}%"))
                self.table_widget.setItem(i, 4, QTableWidgetItem(analysis))

                # Background & color
                bg_color = QColor(random_color())
                self.table_widget.item(i, 0).setBackground(QBrush(bg_color))
                change_color = QColor("#4CAF50") if change > 0 else QColor("#F44336")
                self.table_widget.item(i, 3).setForeground(QBrush(change_color))
            except Exception as e:
                print(f"[Offers] Row {i} error: {e}")

    # ------------------------------------------------------------------
    def calculate_change(self, price):
        """Mock random price change."""
        import random
        return random.uniform(-5, 5)

    def analyze_offer(self, change):
        if change < -2:
            return "Strong Sell"
        elif change > 2:
            return "Strong Buy"
        else:
            return "Neutral"

    # ------------------------------------------------------------------
    def show_offer_details(self, row, col):
        """Open a popup with full offer details."""
        try:
            offer = self.offers_df.iloc[row].to_dict()
            dialog = QDialog(self)
            dialog.setWindowTitle("📄 Offer Details")
            dialog.setMinimumSize(600, 400)

            layout = QFormLayout(dialog)

            # Simple key info
            layout.addRow("Seller:", QLabel(str(offer.get("seller", "Unknown"))))
            layout.addRow("Offer ID:", QLabel(str(offer.get("id", "N/A"))))
            layout.addRow("Price:", QLabel(str(offer.get("price", "N/A"))))
            layout.addRow("Amount:", QLabel(str(offer.get("amount", "N/A"))))

            # Selling & Buying as formatted JSON
            selling_text = json.dumps(offer.get("selling", {}), indent=2)
            buying_text = json.dumps(offer.get("buying", {}), indent=2)

            selling_box = QTextEdit(selling_text)
            selling_box.setReadOnly(True)
            buying_box = QTextEdit(buying_text)
            buying_box.setReadOnly(True)

            layout.addRow(QLabel("<b>Selling Asset:</b>"))
            layout.addRow(selling_box)
            layout.addRow(QLabel("<b>Buying Asset:</b>"))
            layout.addRow(buying_box)

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            layout.addRow(close_btn)

            dialog.exec()
        except Exception as e:
            print(f"[Offers] Error displaying details: {e}")
