import pandas as pd
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QSizePolicy


class Payments(QFrame):
    """💸 Display and refresh recent Stellar payments from SmartBot cache."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.payments_table = None

        # --- Frame setup ---
        self.setGeometry(100, 50, 1530, 780)
        self.setStyleSheet("""
            QFrame { background-color: #0D1117; color: #E0E0E0; }
            QLabel { font-size: 18px; font-weight: bold; color: #00E676; margin: 10px; }
            QHeaderView::section { background-color: #263238; color: white; font-weight: bold; }
            QTableWidget { gridline-color: #333; selection-background-color: #1976D2; font-size: 13px; }
        """)

        self._init_ui()
        self._start_auto_refresh()

    # ------------------------------------------------------------------
    # 🧱 UI SETUP
    # ------------------------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("💸 Recent Payments")
        layout.addWidget(title)

        self.payments_table = QTableWidget(self)
        self.payments_table.setColumnCount(11)
        self.payments_table.setHorizontalHeaderLabels([
            "ID", "Account", "From", "To", "Amount", "Asset Type",
            "Asset Code", "Asset Issuer", "Created At", "Memo Type", "Memo"
        ])
        self.payments_table.horizontalHeader().setStretchLastSection(True)
        self.payments_table.setSortingEnabled(True)
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.payments_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.payments_table)

        self.placeholder = QLabel("⏳ Loading payment data...")
        self.placeholder.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.placeholder)

        self.setLayout(layout)
        self.populate_table()

    # ------------------------------------------------------------------
    # 🔁 Auto-refresh system
    # ------------------------------------------------------------------
    def _start_auto_refresh(self):
        """Auto-refresh payments table every 30 seconds."""
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self.populate_table)
        self.refresh_timer.start(30000)  # 30s interval

    # ------------------------------------------------------------------
    # 📊 Populate payments table
    # ------------------------------------------------------------------
    def populate_table(self):
        """Refresh table from cached bot.payments_df."""
        try:
            if not self.bot:
                self.placeholder.setText("❌ Bot not initialized.")
                return

            df = getattr(self.bot, "payments_df", pd.DataFrame())
            if df is None or df.empty:
                self.placeholder.setText("No payments available.")
                self.payments_table.setRowCount(0)
                return

            self.placeholder.hide()
            records = df.iloc[0].get("_embedded", {}).get("records", []) if "_embedded" in df.columns else []
            payments_df = pd.DataFrame(records)
            if payments_df.empty:
                self.placeholder.setText("No payments found in network.")
                return

            self.payments_table.setRowCount(len(payments_df))

            for i, row in payments_df.iterrows():
                # Extract fields with safe fallbacks
                data = {
                    "id": row.get("id", "N/A"),
                    "account": row.get("account", "N/A"),
                    "from": row.get("from", "N/A"),
                    "to": row.get("to", "N/A"),
                    "amount": row.get("amount", "N/A"),
                    "asset_type": row.get("asset_type", "native"),
                    "asset_code": row.get("asset_code", "XLM" if row.get("asset_type") == "native" else row.get("asset_code")),
                    "asset_issuer": row.get("asset_issuer", "Native"),
                    "created_at": row.get("created_at", "N/A"),
                    "memo_type": row.get("memo_type", "N/A"),
                    "memo": row.get("memo", "—"),
                }

                for col, key in enumerate(data.keys()):
                    item = QTableWidgetItem(str(data[key]))
                    self.payments_table.setItem(i, col, item)

                # 💰 Highlight non-native assets
                if data["asset_type"] != "native":
                    self.payments_table.item(i, 5).setBackground(QColor("#1A237E"))

                # 💲 Amount color logic
                try:
                    amt = float(data["amount"])
                    color = QColor("#4CAF50") if amt > 0 else QColor("#F44336")
                    self.payments_table.item(i, 4).setForeground(color)
                except ValueError:
                    pass

        except Exception as e:
            print(f"[Payments] Error populating table: {e}")

    # ------------------------------------------------------------------
    # 🧾 Manual refresh
    # ------------------------------------------------------------------
    def update_payments_data(self):
        """Force refresh from SmartBot cache (no API calls)."""
        self.populate_table()
