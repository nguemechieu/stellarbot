from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout, QTextEdit, QPushButton, QSizePolicy
)
import json


class AssetsFrame(QFrame):
    """💎 Displays all Stellar assets (native + trustlines) from SmartBot cache."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)

        self.setStyleSheet("""
            QFrame { background-color: #0D1117; color: #E0E0E0; }
            QLabel { font-size: 16px; color: #00E676; }
            QHeaderView::section { background-color: #263238; color: white; font-weight: bold; }
            QTableWidget { gridline-color: #333; selection-background-color: #1976D2; font-size: 13px; }
        """)

        self.setGeometry(0, 0, 1530, 780)
        self._init_ui()
        self._start_auto_refresh()
        self.populate_table()

    # ------------------------------------------------------------------
    # 🧱 UI Setup
    # ------------------------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("💎 Account Assets Overview")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Asset", "Balance", "Type", "Issuer", "Limit"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.cellDoubleClicked.connect(self._show_asset_details)
        layout.addWidget(self.table)

        self.placeholder = QLabel("⏳ Loading assets...")
        self.placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.placeholder)

        self.setLayout(layout)

    # ------------------------------------------------------------------
    # 📊 Populate Table
    # ------------------------------------------------------------------
    def populate_table(self):
        """Load balances from SmartBot account cache."""
        try:
            df = getattr(self.bot, "accounts_df", None)
            if df is None or df.empty:
                self.table.setRowCount(0)
                self.placeholder.setText("No account data available.")
                self.placeholder.show()
                return

            account_data = df.iloc[0].to_dict()
            balances = account_data.get("balances", [])
            if not balances:
                self.table.setRowCount(0)
                self.placeholder.setText("No assets found for this account.")
                self.placeholder.show()
                return

            self.placeholder.hide()
            self.table.setRowCount(len(balances))

            for i, asset in enumerate(balances):
                asset_code = asset.get("asset_code", "XLM" if asset.get("asset_type") == "native" else asset.get("asset_code"))
                balance = float(asset.get("balance", 0.0))
                asset_type = asset.get("asset_type", "native")
                issuer = asset.get("asset_issuer", "Native")
                limit = asset.get("limit", "—")

                self.table.setItem(i, 0, QTableWidgetItem(str(asset_code)))
                self.table.setItem(i, 1, QTableWidgetItem(f"{balance:,.4f}"))
                self.table.setItem(i, 2, QTableWidgetItem(asset_type))
                self.table.setItem(i, 3, QTableWidgetItem(issuer))
                self.table.setItem(i, 4, QTableWidgetItem(str(limit)))

                # 🎨 Style rows
                if asset_type == "native":
                    self.table.item(i, 0).setBackground(QBrush(QColor("#1B5E20")))
                else:
                    self.table.item(i, 0).setBackground(QBrush(QColor("#283593")))

                # Colorize balance
                color = QColor("#00E676") if balance > 0 else QColor("#F44336")
                self.table.item(i, 1).setForeground(QBrush(color))

                # Tooltip
                tooltip = (
                    f"Asset Code: {asset_code}\n"
                    f"Balance: {balance}\n"
                    f"Issuer: {issuer}\n"
                    f"Type: {asset_type}"
                )
                for col in range(5):
                    item = self.table.item(i, col)
                    if item:
                        item.setToolTip(tooltip)

        except Exception as e:
            print(f"[AssetsFrame] populate_table error: {e}")
            self.placeholder.setText(f"Error loading assets: {e}")
            self.placeholder.show()

    # ------------------------------------------------------------------
    # 🔁 Auto Refresh
    # ------------------------------------------------------------------
    def _start_auto_refresh(self):
        """Refresh every 30 seconds."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.populate_table)
        self.refresh_timer.start(30000)

    # ------------------------------------------------------------------
    # 📜 Asset Details Dialog
    # ------------------------------------------------------------------
    def _show_asset_details(self, row, col):
        """Show full JSON details of selected asset."""
        try:
            df = getattr(self.bot, "accounts_df", None)
            if df is None or df.empty:
                return

            account_data = df.iloc[0].to_dict()
            balances = account_data.get("balances", [])
            if row >= len(balances):
                return

            asset = balances[row]

            dialog = QDialog(self)
            dialog.setWindowTitle("📄 Asset Details")
            dialog.setMinimumSize(500, 400)

            layout = QFormLayout(dialog)
            layout.addRow("Asset Code:", QLabel(asset.get("asset_code", "XLM")))
            layout.addRow("Asset Type:", QLabel(asset.get("asset_type", "native")))
            layout.addRow("Issuer:", QLabel(asset.get("asset_issuer", "Native")))
            layout.addRow("Balance:", QLabel(str(asset.get("balance", "0"))))
            layout.addRow("Limit:", QLabel(str(asset.get("limit", "N/A"))))

            # JSON details
            json_text = json.dumps(asset, indent=2)
            json_box = QTextEdit(json_text)
            json_box.setReadOnly(True)
            layout.addRow(QLabel("<b>Raw Data:</b>"))
            layout.addRow(json_box)

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            layout.addRow(close_btn)

            dialog.exec()
        except Exception as e:
            print(f"[AssetsFrame] Error showing asset details: {e}")
