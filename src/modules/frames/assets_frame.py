from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QColor, QBrush, QFont, QIcon
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QDialog, QFormLayout, QTextEdit, QPushButton, QSizePolicy,
    QLineEdit, QComboBox, QSpinBox
)
import json


class AssetsFrame(QFrame):
    """💎 Professional Stellar Assets Dashboard - View all balances and trustlines."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        
        # Asset cache and filtering
        self.all_assets = []
        self.filtered_assets = []
        self.sort_column = 1
        self.sort_order = Qt.DescendingOrder

        # Apply professional dark theme
        self.setStyleSheet("""
            QFrame {
                background-color: #0C0E13;
                color: #D1D5DB;
            }
            QLabel {
                color: #D1D5DB;
            }
            QLineEdit {
                background-color: #1F2937;
                color: #D1D5DB;
                border: 1px solid #374151;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
            }
            QComboBox {
                background-color: #1F2937;
                color: #D1D5DB;
                border: 1px solid #374151;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QHeaderView::section {
                background-color: #1F2937;
                color: #D1D5DB;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #374151;
            }
            QTableWidget {
                gridline-color: #374151;
                background-color: #131722;
                alternate-background-color: #1A1F2E;
                selection-background-color: #2563EB;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)

        self.setGeometry(0, 0, 1530, 900)
        self._init_ui()
        self._start_auto_refresh()
        self.populate_table()

    # ------------------------------------------------------------------
    # 🧱 UI Setup
    # ------------------------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # === Header ===
        header_layout = QHBoxLayout()
        title = QLabel("💎 Account Assets Dashboard")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #3B82F6; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # === Filter Toolbar ===
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        filter_label = QLabel("🔍 Search:")
        filter_label.setStyleSheet("color: #9CA3AF; font-weight: 600;")
        filter_layout.addWidget(filter_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by asset code or issuer...")
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self._filter_assets)
        filter_layout.addWidget(self.search_input)

        type_label = QLabel("Type:")
        type_label.setStyleSheet("color: #9CA3AF; font-weight: 600;")
        filter_layout.addWidget(type_label)

        self.type_filter = QComboBox()
        self.type_filter.addItems(["All", "Native", "Credit"])
        self.type_filter.setMaximumWidth(120)
        self.type_filter.currentTextChanged.connect(self._filter_assets)
        filter_layout.addWidget(self.type_filter)

        filter_layout.addSpacing(10)
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMaximumWidth(100)
        refresh_btn.clicked.connect(self.populate_table)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        filter_layout.addWidget(refresh_btn)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # === Stats Bar ===
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.total_balance_label = QLabel("Total Balance: $0.00")
        self.total_balance_label.setStyleSheet("color: #10B981; font-weight: 600; font-size: 12px;")
        stats_layout.addWidget(self.total_balance_label)
        
        self.native_label = QLabel("Native: 0")
        self.native_label.setStyleSheet("color: #3B82F6; font-weight: 600; font-size: 12px;")
        stats_layout.addWidget(self.native_label)
        
        self.credit_label = QLabel("Credit: 0")
        self.credit_label.setStyleSheet("color: #8B5CF6; font-weight: 600; font-size: 12px;")
        stats_layout.addWidget(self.credit_label)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # === Table ===
        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Asset", "Balance", "Type", "Issuer", "Limit", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(False)  # Custom sorting
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.cellDoubleClicked.connect(self._show_asset_details)
        layout.addWidget(self.table, 1)

        # === Placeholder ===
        self.placeholder = QLabel("⏳ Loading assets...")
        self.placeholder.setAlignment(Qt.AlignCenter)
        self.placeholder.setStyleSheet("color: #9CA3AF; font-size: 12px;")
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
                self.native_label.setText("Native: 0")
                self.credit_label.setText("Credit: 0")
                self.total_balance_label.setText("Total Balance: $0.00")
                return

            account_data = df.iloc[0].to_dict()
            balances = account_data.get("balances", [])
            if not balances:
                self.table.setRowCount(0)
                self.placeholder.setText("No assets found for this account.")
                self.placeholder.show()
                self.native_label.setText("Native: 0")
                self.credit_label.setText("Credit: 0")
                self.total_balance_label.setText("Total Balance: $0.00")
                return

            self.placeholder.hide()
            self.all_assets = balances
            self._filter_assets()  # Apply current filters

        except Exception as e:
            print(f"[AssetsFrame] populate_table error: {e}")
            self.placeholder.setText(f"Error loading assets: {e}")
            self.placeholder.show()
            self.native_label.setText("Native: Error")
            self.credit_label.setText("Credit: Error")

    def _filter_assets(self):
        """Apply search and type filters to assets."""
        try:
            search_text = self.search_input.text().lower().strip()
            type_filter = self.type_filter.currentText()
            
            # Filter assets
            filtered = []
            native_count = 0
            credit_count = 0
            total_xlm_value = 0.0
            
            for asset in self.all_assets:
                asset_code = asset.get("asset_code", "XLM")
                asset_type = asset.get("asset_type", "native")
                issuer = asset.get("asset_issuer", "Native")
                balance = float(asset.get("balance", 0.0))
                
                # Apply type filter
                if type_filter == "Native" and asset_type != "native":
                    continue
                if type_filter == "Credit" and asset_type != "credit_alphanum4" and asset_type != "credit_alphanum12":
                    continue
                
                # Apply search filter
                if search_text:
                    if search_text not in asset_code.lower() and search_text not in issuer.lower():
                        continue
                
                filtered.append(asset)
                
                # Count types
                if asset_type == "native":
                    native_count += 1
                    total_xlm_value += balance
                else:
                    credit_count += 1
            
            # Update stats
            self.native_label.setText(f"Native: {native_count}")
            self.credit_label.setText(f"Credit: {credit_count}")
            self.total_balance_label.setText(f"Total Balance: ${total_xlm_value:,.2f} XLM")
            
            # Populate table with filtered assets
            self.table.setRowCount(len(filtered))
            
            for i, asset in enumerate(filtered):
                asset_code = asset.get("asset_code", "XLM")
                balance = float(asset.get("balance", 0.0))
                asset_type = asset.get("asset_type", "native")
                issuer = asset.get("asset_issuer", "Native")
                limit = asset.get("limit", "—")
                
                # Status indicator
                status = "✅ Active" if balance > 0 else "⏸️ Empty"
                
                # Asset name
                code_item = QTableWidgetItem(asset_code)
                code_item.setFont(QFont("Courier", 11, QFont.Bold))
                if asset_type == "native":
                    code_item.setForeground(QBrush(QColor("#10B981")))
                    code_item.setBackground(QBrush(QColor("#1B5E20")))
                else:
                    code_item.setForeground(QBrush(QColor("#60A5FA")))
                    code_item.setBackground(QBrush(QColor("#1E3A8A")))
                self.table.setItem(i, 0, code_item)
                
                # Balance
                balance_item = QTableWidgetItem(f"{balance:,.6f}")
                balance_item.setFont(QFont("Courier", 10, QFont.Bold))
                balance_color = QColor("#10B981") if balance > 0 else QColor("#9CA3AF")
                balance_item.setForeground(QBrush(balance_color))
                self.table.setItem(i, 1, balance_item)
                
                # Type
                type_item = QTableWidgetItem(asset_type.replace("credit_", ""))
                type_item.setStyleSheet("color: #D1D5DB;")
                self.table.setItem(i, 2, type_item)
                
                # Issuer
                issuer_item = QTableWidgetItem(issuer[:20] + "..." if len(issuer) > 20 else issuer)
                issuer_item.setStyleSheet("color: #9CA3AF; font-size: 10px;")
                issuer_item.setToolTip(issuer)
                self.table.setItem(i, 3, issuer_item)
                
                # Limit
                limit_item = QTableWidgetItem(str(limit))
                limit_item.setStyleSheet("color: #D1D5DB;")
                self.table.setItem(i, 4, limit_item)
                
                # Status
                status_item = QTableWidgetItem(status)
                status_color = QColor("#10B981") if balance > 0 else QColor("#6B7280")
                status_item.setForeground(QBrush(status_color))
                self.table.setItem(i, 5, status_item)
                
                # Tooltip for all columns
                tooltip = (
                    f"Asset: {asset_code}\n"
                    f"Balance: {balance:,.6f}\n"
                    f"Type: {asset_type}\n"
                    f"Issuer: {issuer}\n"
                    f"Limit: {limit}\n"
                    f"Double-click for details"
                )
                for col in range(6):
                    item = self.table.item(i, col)
                    if item:
                        item.setToolTip(tooltip)
        
        except Exception as e:
            print(f"[AssetsFrame] _filter_assets error: {e}")

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
        """Show comprehensive details of selected asset in a professional dialog."""
        try:
            if row >= len(self.all_assets):
                return

            asset = self.all_assets[row]
            asset_code = asset.get("asset_code", "XLM")
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"💎 Asset Details - {asset_code}")
            dialog.setMinimumSize(600, 700)
            dialog.setStyleSheet(self.styleSheet())
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(12)
            layout.setContentsMargins(16, 16, 16, 16)
            
            # Title
            title = QLabel(f"Asset: {asset_code}")
            title_font = QFont()
            title_font.setPointSize(14)
            title_font.setBold(True)
            title.setFont(title_font)
            title.setStyleSheet("color: #3B82F6; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title)
            
            # Properties form
            form_layout = QFormLayout()
            form_layout.setSpacing(10)
            
            # Asset Code
            code_label = QLabel(asset_code)
            code_label.setStyleSheet("color: #10B981; font-weight: 600;")
            form_layout.addRow("Code:", code_label)
            
            # Type
            type_val = asset.get("asset_type", "native").replace("credit_", "")
            type_label = QLabel(type_val.upper())
            type_color = "#10B981" if type_val == "native" else "#60A5FA"
            type_label.setStyleSheet(f"color: {type_color}; font-weight: 600;")
            form_layout.addRow("Type:", type_label)
            
            # Balance
            balance = float(asset.get("balance", 0.0))
            balance_label = QLabel(f"{balance:,.6f}")
            balance_label.setStyleSheet("color: #10B981; font-weight: 600; font-family: Courier;")
            form_layout.addRow("Balance:", balance_label)
            
            # Limit
            limit = asset.get("limit", "Unlimited")
            limit_label = QLabel(str(limit))
            limit_label.setStyleSheet("color: #D1D5DB;")
            form_layout.addRow("Limit:", limit_label)
            
            # Issuer
            issuer = asset.get("asset_issuer", "Native")
            issuer_label = QLabel(issuer)
            issuer_label.setWordWrap(True)
            issuer_label.setStyleSheet("color: #9CA3AF; font-family: Courier; font-size: 10px;")
            issuer_label.setToolTip(issuer)
            form_layout.addRow("Issuer:", issuer_label)
            
            # Last Modified
            last_modified = asset.get("last_modified_time", "N/A")
            mod_label = QLabel(last_modified)
            mod_label.setStyleSheet("color: #9CA3AF;")
            form_layout.addRow("Modified:", mod_label)
            
            layout.addLayout(form_layout)
            layout.addSpacing(10)
            
            # Raw JSON
            json_title = QLabel("📋 Raw JSON Data:")
            json_title.setStyleSheet("color: #D1D5DB; font-weight: 600; margin-top: 10px;")
            layout.addWidget(json_title)
            
            json_text = json.dumps(asset, indent=2)
            json_box = QTextEdit(json_text)
            json_box.setReadOnly(True)
            json_box.setStyleSheet("""
                QTextEdit {
                    background-color: #0C0E13;
                    color: #D1D5DB;
                    border: 1px solid #374151;
                    border-radius: 4px;
                    font-family: Courier;
                    font-size: 10px;
                    padding: 8px;
                }
            """)
            json_box.setMinimumHeight(200)
            layout.addWidget(json_box)
            
            layout.addStretch()
            
            # Buttons
            button_layout = QHBoxLayout()
            copy_btn = QPushButton("📋 Copy JSON")
            copy_btn.setMaximumWidth(120)
            copy_btn.clicked.connect(lambda: self._copy_to_clipboard(json_text))
            copy_btn.setStyleSheet("""
                QPushButton {
                    background-color: #8B5CF6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #7C3AED; }
            """)
            button_layout.addWidget(copy_btn)
            
            button_layout.addStretch()
            
            close_btn = QPushButton("Close")
            close_btn.setMaximumWidth(100)
            close_btn.clicked.connect(dialog.close)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            dialog.exec()
            
        except Exception as e:
            print(f"[AssetsFrame] Error showing asset details: {e}")
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        from PySide6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
