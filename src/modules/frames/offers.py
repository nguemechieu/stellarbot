from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QDialog, QFormLayout, QPushButton, QTextEdit, QSizePolicy
)
import json
import random


# ------------------------------------------------------------------
# 🎨 Utility helpers
# ------------------------------------------------------------------
def random_color():
    """Return a random soft background color."""
    colors = ["#263238", "#37474F", "#455A64", "#546E7A", "#607D8B"]
    return random.choice(colors)


def calculate_change(price: float) -> float:
    """Mock simulated percentage change until live feed integrated."""
    return random.uniform(-5, 5)


def analyze_offer(change: float) -> str:
    """Basic offer signal interpretation."""
    if change < -2:
        return "Strong Sell"
    elif change > 2:
        return "Strong Buy"
    return "Neutral"


# ------------------------------------------------------------------
# 💹 Offers Frame
# ------------------------------------------------------------------
class Offers(QFrame):
    """Display and analyze Stellar network offers in real-time."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)

        self.setStyleSheet("""
            QFrame { background-color: #0D1117; color: #E0E0E0; }
            QLabel { color: #00E676; }
            QHeaderView::section { background-color: #263238; color: #FFFFFF; font-weight: bold; }
            QTableWidget { gridline-color: #333; selection-background-color: #1976D2; font-size: 13px; }
        """)

        self.setGeometry(0, 0, 1530, 780)
        self.offers_df = getattr(self.bot, "offers_df", {})

        self._init_ui()
        self._start_auto_refresh()

    # ------------------------------------------------------------------
    # 🧱 UI Setup
    # ------------------------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("💹 Active Stellar Offers")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #00E676;")
        layout.addWidget(title)

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Market", "Price", "Volume", "Change (%)", "Signal"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.cellDoubleClicked.connect(self._show_offer_details)
        layout.addWidget(self.table)

        self.placeholder = QLabel("⏳ Loading offers...")
        self.placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.placeholder)

        self.setLayout(layout)
        self.populate_table()

    # ------------------------------------------------------------------
    # 🧮 Table Population
    # ------------------------------------------------------------------
    def populate_table(self):
        """Fill table with cached offer data from SmartBot."""
        try:
            df = getattr(self.bot, "offers_df", None)
            if df is None or df.empty:
                self.table.setRowCount(0)
                self.placeholder.setText("No offers available.")
                self.placeholder.show()
                return

            self.placeholder.hide()

            expected_cols = ["seller", "selling", "buying", "amount", "price", "id"]
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None

            self.table.setRowCount(len(df))
            for i, offer in enumerate(df.itertuples()):
                try:
                    selling = getattr(offer, "selling", {}) or {}
                    buying = getattr(offer, "buying", {}) or {}

                    sell_code = selling.get("asset_code", "XLM")
                    buy_code = buying.get("asset_code", "USDC")
                    market = f"{sell_code}/{buy_code}"

                    price = float(getattr(offer, "price", 0.0))
                    volume = float(getattr(offer, "amount", 0.0))
                    change = calculate_change(price)
                    signal = analyze_offer(change)

                    # --- Populate cells ---
                    self.table.setItem(i, 0, QTableWidgetItem(market))
                    self.table.setItem(i, 1, QTableWidgetItem(f"{price:.5f}"))
                    self.table.setItem(i, 2, QTableWidgetItem(f"{volume:.2f}"))
                    self.table.setItem(i, 3, QTableWidgetItem(f"{change:+.2f}%"))
                    self.table.setItem(i, 4, QTableWidgetItem(signal))

                    # --- Colors ---
                    bg_color = QColor(random_color())
                    self.table.item(i, 0).setBackground(QBrush(bg_color))

                    change_color = QColor("#4CAF50") if change > 0 else QColor("#F44336")
                    self.table.item(i, 3).setForeground(QBrush(change_color))

                    signal_item = self.table.item(i, 4)
                    if "Buy" in signal:
                        signal_item.setForeground(QColor("#00E676"))
                    elif "Sell" in signal:
                        signal_item.setForeground(QColor("#E53935"))
                    else:
                        signal_item.setForeground(QColor("#B0BEC5"))

                    # --- Tooltip with quick summary ---
                    tooltip = (
                        f"Seller: {getattr(offer, 'seller', 'N/A')}\n"
                        f"Price: {price}\nVolume: {volume}\nSignal: {signal}"
                    )
                    for col in range(5):
                        item = self.table.item(i, col)
                        if item:
                            item.setToolTip(tooltip)

                except Exception as e:
                    print(f"[Offers] Row {i} error: {e}")

        except Exception as e:
            print(f"[Offers] populate_table() error: {e}")

    # ------------------------------------------------------------------
    # 🔁 Auto Refresh
    # ------------------------------------------------------------------
    def _start_auto_refresh(self):
        """Auto-refresh offers every 30 seconds."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.populate_table)
        self.refresh_timer.start(30000)

    # ------------------------------------------------------------------
    # 📜 Offer Details Dialog
    # ------------------------------------------------------------------
    def _show_offer_details(self, row, col):
        """Display selected offer in a detailed dialog."""
        try:
            df = getattr(self.bot, "offers_df", None)
            if df is None or df.empty or row >= len(df):
                return

            offer = df.iloc[row].to_dict()

            dialog = QDialog(self)
            dialog.setWindowTitle("📄 Offer Details")
            dialog.setMinimumSize(600, 400)

            layout = QFormLayout(dialog)
            layout.addRow("Seller:", QLabel(str(offer.get("seller", "Unknown"))))
            layout.addRow("Offer ID:", QLabel(str(offer.get("id", "N/A"))))
            layout.addRow("Price:", QLabel(str(offer.get("price", "N/A"))))
            layout.addRow("Amount:", QLabel(str(offer.get("amount", "N/A"))))

            selling_json = json.dumps(offer.get("selling", {}), indent=2)
            buying_json = json.dumps(offer.get("buying", {}), indent=2)

            sell_box = QTextEdit(selling_json)
            sell_box.setReadOnly(True)
            buy_box = QTextEdit(buying_json)
            buy_box.setReadOnly(True)

            layout.addRow(QLabel("<b>Selling Asset:</b>"))
            layout.addRow(sell_box)
            layout.addRow(QLabel("<b>Buying Asset:</b>"))
            layout.addRow(buy_box)

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            layout.addRow(close_btn)

            dialog.exec()

        except Exception as e:
            print(f"[Offers] Error showing details: {e}")
