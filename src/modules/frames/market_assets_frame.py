from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QDialog, QFormLayout,
    QTextEdit, QSizePolicy, QMessageBox
)
from stellar_sdk import Asset, TransactionBuilder, Network
import json


class MarketAssetsFrame(QFrame):
    """🌐 Display global Stellar assets, show trusted ones, and manage trustlines."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.server = getattr(self.bot, "server", None)
        self.keypair = getattr(self.bot, "keypair", None)

        self.assets_df = None
        self.trusted_assets = set()

        self._init_ui()
        self.load_trusted_assets()
        self.populate_market_assets()
        self._start_auto_refresh()

    # ------------------------------------------------------------------
    # 🧱 UI
    # ------------------------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        title = QLabel("🌐 Stellar Market Assets")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00E676;")
        layout.addWidget(title)

        # Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Asset Code", "Issuer", "Amount", "Accounts", "Trusted?", "Action"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.cellDoubleClicked.connect(self._show_asset_details)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.table)

        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.setStyleSheet("""
            QFrame { background-color: #0D1117; color: #E0E0E0; }
            QHeaderView::section { background-color: #263238; color: white; font-weight: bold; }
            QTableWidget { gridline-color: #333; selection-background-color: #1976D2; }
            QPushButton { background-color: #1E88E5; color: white; border-radius: 5px; padding: 3px; }
            QPushButton:hover { background-color: #42A5F5; }
        """)

    # ------------------------------------------------------------------
    # 🧩 Load Trusted Assets
    # ------------------------------------------------------------------
    def load_trusted_assets(self):
        """Load assets currently trusted by account."""
        try:
            df = getattr(self.bot, "accounts_df", None)
            if df is not None and not df.empty:
                balances = df.iloc[0].get("balances", [])
                for a in balances:
                    code = a.get("asset_code") or "XLM"
                    issuer = a.get("asset_issuer", "native")
                    self.trusted_assets.add(f"{code}:{issuer}")
            self._set_status("✅ Trusted assets loaded.")
        except Exception as e:
            self._set_status(f"⚠️ Failed to load trusted assets: {e}")

    # ------------------------------------------------------------------
    # 🌍 Fetch Market Assets
    # ------------------------------------------------------------------
    def populate_market_assets(self):
        """Fetch all available assets from Horizon and populate the table."""
        try:
            self._set_status("⏳ Fetching market assets...")
            data = self.server.assets().limit(200).order("desc").call()
            records = data.get("_embedded", {}).get("records", [])
            self.assets_df = records
            self.table.setRowCount(len(records))

            for i, a in enumerate(records):
                code = a.get("asset_code", "N/A")
                issuer = a.get("asset_issuer", "N/A")
                amount = float(a.get("amount", 0))
                accounts = a.get("num_accounts", 0)

                asset_key = f"{code}:{issuer}"
                trusted = asset_key in self.trusted_assets

                # Table items
                self.table.setItem(i, 0, QTableWidgetItem(code))
                self.table.setItem(i, 1, QTableWidgetItem(issuer))
                self.table.setItem(i, 2, QTableWidgetItem(f"{amount:,.2f}"))
                self.table.setItem(i, 3, QTableWidgetItem(str(accounts)))
                self.table.setItem(i, 4, QTableWidgetItem("✅" if trusted else "❌"))

                # Action button
                btn = QPushButton("Untrust" if trusted else "Trust")
                btn.clicked.connect(lambda _, c=code, isr=issuer, t=trusted: self._toggle_trustline(c, isr, t))
                self.table.setCellWidget(i, 5, btn)

                # Row colors
                self.table.item(i, 0).setBackground(
                    QBrush(QColor("#1B5E20" if trusted else "#263238"))
                )

            self._set_status(f"🌍 Loaded {len(records)} market assets.")
        except Exception as e:
            self._set_status(f"❌ Error fetching assets: {e}")

    # ------------------------------------------------------------------
    # 🔁 Auto Refresh
    # ------------------------------------------------------------------
    def _start_auto_refresh(self):
        """Auto-refresh every 60 seconds."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.populate_market_assets)
        self.refresh_timer.start(60000)

    # ------------------------------------------------------------------
    # 🔄 Trust / Untrust
    # ------------------------------------------------------------------
    def _toggle_trustline(self, code: str, issuer: str, trusted: bool):
        """Add or remove a trustline for an asset."""
        try:
            account = self.server.load_account(self.keypair.public_key)
            asset = Asset(code, issuer)
            builder = TransactionBuilder(
                source_account=account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100,
            )
            if trusted:
                self._set_status(f"🧹 Removing trustline for {code}...")
                builder.append_change_trust_op(asset=asset, limit="0")
            else:
                self._set_status(f"🤝 Trusting asset {code}...")
                builder.append_change_trust_op(asset=asset)

            tx = builder.set_timeout(30).build()
            tx.sign(self.keypair)
            resp = self.server.submit_transaction(tx)
            hash_ = resp.get("hash", "N/A")

            QMessageBox.information(self, "Trustline Updated", f"✅ Success!\nTX Hash: {hash_}")
            self.load_trusted_assets()
            self.populate_market_assets()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to update trustline:\n{e}")
            self._set_status(f"❌ {e}")

    # ------------------------------------------------------------------
    # 📜 Asset Details Dialog
    # ------------------------------------------------------------------
    def _show_asset_details(self, row, col):
        """Display JSON details for selected asset."""
        try:
            if not self.assets_df or row >= len(self.assets_df):
                return
            asset = self.assets_df[row]
            dialog = QDialog(self)
            dialog.setWindowTitle("📄 Asset Details")
            dialog.setMinimumSize(500, 400)
            layout = QFormLayout(dialog)

            layout.addRow("Asset Code:", QLabel(asset.get("asset_code", "N/A")))
            layout.addRow("Issuer:", QLabel(asset.get("asset_issuer", "N/A")))
            layout.addRow("Amount:", QLabel(str(asset.get("amount", "0"))))
            layout.addRow("Accounts:", QLabel(str(asset.get("num_accounts", "0"))))

            json_box = QTextEdit(json.dumps(asset, indent=2))
            json_box.setReadOnly(True)
            layout.addRow(QLabel("<b>Raw JSON:</b>"))
            layout.addRow(json_box)

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            layout.addRow(close_btn)

            dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to show asset details:\n{e}")

    # ------------------------------------------------------------------
    # ℹ️ Helper
    # ------------------------------------------------------------------
    def _set_status(self, text):
        self.status_label.setText(text)
