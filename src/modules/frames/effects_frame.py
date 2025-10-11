import pandas as pd
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QMessageBox
)


class EffectsFrame(QFrame):
    """💫 Displays live account effects from Stellar Horizon (trustlines, trades, etc.)"""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.server = getattr(self.bot, "server", None)

        self.effects_df = getattr(self.bot, "effects_df", pd.DataFrame())
        self.effects_table = None
        self.effects_label = None

        self._init_ui()
        self._populate_effects_table()
        self._start_auto_refresh()

    # ------------------------------------------------------------------
    # 🧱 UI SETUP
    # ------------------------------------------------------------------
    def _init_ui(self):
        self.setStyleSheet("""
            QFrame { background-color: #0D1117; color: #E0E0E0; }
            QLabel { font-size: 18px; font-weight: bold; color: #00E676; }
            QHeaderView::section { background-color: #263238; color: white; font-weight: bold; }
            QTableWidget { gridline-color: #333; selection-background-color: #1976D2; font-size: 13px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.effects_label = QLabel("💫 Stellar Account Effects")
        self.effects_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.effects_label)

        # Table
        self.effects_table = QtWidgets.QTableWidget()
        self.effects_table.setColumnCount(6)
        self.effects_table.setHorizontalHeaderLabels([
            "ID", "Type", "Account", "Created At", "Amount", "Asset Code"
        ])
        self.effects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.effects_table.setAlternatingRowColors(True)
        self.effects_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.effects_table.setSortingEnabled(True)
        layout.addWidget(self.effects_table)

        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    # ------------------------------------------------------------------
    # 🧮 POPULATE TABLE
    # ------------------------------------------------------------------
    def _populate_effects_table(self):
        """Fill the table with data from bot.effects_df or Horizon API."""
        try:
            # Load data
            df = getattr(self.bot, "effects_df", None)
            if df is None or df.empty:
                # Fallback: fetch directly
                res = self.server.effects().for_account(self.bot.account_id).order(desc=True).limit(50).call()
                df = pd.DataFrame(res.get("_embedded", {}).get("records", []))
                self.effects_df = df

            self.effects_table.setRowCount(0)

            for idx, row in df.iterrows():
                self.effects_table.insertRow(idx)
                self._add_effect_row(idx, row)

            self.effects_table.resizeColumnsToContents()
            self._set_status(f"✅ Loaded {len(df)} effects.")

        except Exception as e:
            self._set_status(f"❌ Error loading effects: {e}")

    # ------------------------------------------------------------------
    # 🪶 ADD ROW
    # ------------------------------------------------------------------
    def _add_effect_row(self, idx, row):
        """Add one effect record to the table with proper styling."""
        def safe(value):
            return str(value) if value is not None else "N/A"

        cols = [
            safe(row.get("id")),
            safe(row.get("type")),
            safe(row.get("account")),
            safe(row.get("created_at")),
            safe(row.get("amount")),
            safe(row.get("asset_code")),
        ]

        for c, val in enumerate(cols):
            self.effects_table.setItem(idx, c, QTableWidgetItem(val))

        # Tooltip
        for c in range(6):
            item = self.effects_table.item(idx, c)
            item.setToolTip(f"{self.effects_table.horizontalHeaderItem(c).text()}: {item.text()}")

        # 🎨 Conditional styling
        eff_type = row.get("type", "")
        color_map = {
            "trade": QColor("#4CAF50"),
            "trustline_created": QColor("#2196F3"),
            "trustline_updated": QColor("#FFC107"),
            "account_created": QColor("#9C27B0"),
        }
        bg_color = color_map.get(eff_type, QColor("#263238"))

        for c in range(6):
            self.effects_table.item(idx, c).setBackground(QBrush(bg_color))

    # ------------------------------------------------------------------
    # 🔁 AUTO REFRESH
    # ------------------------------------------------------------------
    def _start_auto_refresh(self):
        """Refresh effects every 10 seconds."""
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self._populate_effects_table)
        self.refresh_timer.start(10000)  # every 10s

    # ------------------------------------------------------------------
    # ℹ️ STATUS
    # ------------------------------------------------------------------
    def _set_status(self, text):
        self.status_label.setText(text)
