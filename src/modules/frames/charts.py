from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QRunnable, QThreadPool, Slot, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PySide6.QtGui import QFont, QColor

from src.modules.frames.bar_chart import BarChart
from src.modules.frames.candles_stick_chart import DexTradingChart
from src.modules.frames.heikin_ashi import HeikinAshi
from src.modules.frames.line_chart import LineChart
from src.modules.frames.renko import Renko


class ChartRefreshWorker(QRunnable):
    """Background task to refresh a single chart safely."""
    
    refresh_complete = Signal(str, str)  # (chart_name, message)

    def __init__(self, chart_widget, chart_name="Chart", callback=None):
        super().__init__()
        self.chart_widget = chart_widget
        self.chart_name = chart_name
        self.callback = callback

    def run(self):
        """Run safely in background thread."""
        try:
            if hasattr(self.chart_widget, "_refresh_data"):
                self.chart_widget._refresh_data()
            elif hasattr(self.chart_widget, "refresh_chart"):
                self.chart_widget.refresh_chart()

            message = f"✅ {self.chart_name} refreshed"
            if self.callback:
                QtCore.QMetaObject.invokeMethod(
                    self.callback.__self__,
                    self.callback.__name__,
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, message)
                )

        except Exception as e:
            import traceback
            traceback.print_exc()
            message = f"❌ {self.chart_name} failed: {str(e)[:50]}"
            if self.callback:
                QtCore.QMetaObject.invokeMethod(
                    self.callback.__self__,
                    self.callback.__name__,
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, message)
                )



# ---------------------------------------------------------
# 📈 Charts Frame
# ---------------------------------------------------------
class Charts(QFrame):
    """Professional multi-chart dashboard with threaded sync + live assets."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.trading_mode = 'Manual'
        self.chart_type = "candle"
        
        # Chart state tracking
        self.syncing_charts = set()
        self.chart_count = 0

        # Thread pool for background workers
        self.thread_pool = QThreadPool.globalInstance()

        # Chart registry
        self.available_charts = {
            'bar': BarChart,
            'candle': DexTradingChart,
            'heikin-ashi': HeikinAshi,
            'line': LineChart,
            'renko': Renko,
        }

        # Placeholder data for offline charts
        self.data = {
            'Open': [100, 120, 90, 110, 130, 105, 115, 125, 140, 110],
            'High': [110, 130, 105, 125, 145, 115, 125, 135, 150, 120],
            'Low': [90, 100, 85, 95, 115, 85, 95, 105, 120, 90],
            'Close': [105, 125, 100, 115, 135, 105, 115, 125, 140, 115],
            'Volume': [1000, 2000, 1500, 1800, 3000, 1500, 1800, 2500, 500, 1800],
        }

        # Apply dark theme
        self.setStyleSheet("""
            QFrame {
                background-color: #0C0E13;
                color: #D1D5DB;
            }
            QLabel {
                color: #D1D5DB;
            }
            QComboBox {
                background-color: #1F2937;
                color: #D1D5DB;
                border: 1px solid #374151;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QTabWidget::pane {
                border: 1px solid #374151;
            }
            QTabBar::tab {
                background-color: #1F2937;
                color: #D1D5DB;
                padding: 6px 12px;
                border: none;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                background-color: #2563EB;
                border-bottom: 2px solid #3B82F6;
            }
        """)

        # UI Layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # Toolbar
        self.setup_toolbar(main_layout)
        
        # Status bar
        self.setup_status_bar(main_layout)
        
        # Charts notebook
        self.notebook = QtWidgets.QTabWidget()
        self.notebook.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #374151; background-color: #131722; }
            QTabBar::tab { background-color: #1F2937; color: #D1D5DB; padding: 8px 16px; border: none; }
            QTabBar::tab:selected { background-color: #2563EB; color: #FFFFFF; }
        """)
        main_layout.addWidget(self.notebook, 1)

        # Populate assets from SmartBot
        self.load_assets_from_smartbot()

        # Add default chart
        self.add_chart()

        # Auto-sync timer
        self.sync_timer = QtCore.QTimer()
        self.sync_timer.timeout.connect(self.sync_all_charts)
        self.auto_sync_enabled = True
        self.sync_timer.start(30000)  # every 30 seconds

        self.setLayout(main_layout)

    # ---------------------------------------------------------
    # 🧰 Toolbar
    # ---------------------------------------------------------
    def setup_toolbar(self, layout):
        """Create professional toolbar with asset/chart selection."""
        toolbar = QtWidgets.QWidget(self)
        toolbar.setStyleSheet("""
            QWidget {
                background-color: #1F2937;
                border-bottom: 1px solid #374151;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setSpacing(12)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)

        # Asset selection section
        asset_label = QLabel("📊 Asset Pair:")
        asset_label.setStyleSheet("font-weight: 600; color: #D1D5DB;")
        toolbar_layout.addWidget(asset_label)

        self.assets_combobox1 = QtWidgets.QComboBox()
        self.assets_combobox1.setMaximumWidth(100)
        toolbar_layout.addWidget(self.assets_combobox1)

        pair_label = QLabel("/")
        pair_label.setStyleSheet("font-weight: 600; color: #9CA3AF;")
        toolbar_layout.addWidget(pair_label)

        self.assets_combobox2 = QtWidgets.QComboBox()
        self.assets_combobox2.setMaximumWidth(100)
        toolbar_layout.addWidget(self.assets_combobox2)

        # Chart type section
        chart_label = QLabel("| 📈 Type:")
        chart_label.setStyleSheet("font-weight: 600; color: #D1D5DB; margin-left: 15px;")
        toolbar_layout.addWidget(chart_label)
        
        self.chart_type_combobox = QtWidgets.QComboBox()
        self.chart_type_combobox.addItems(["candle", "line", "bar", "renko", "heikin-ashi"])
        self.chart_type_combobox.setMaximumWidth(110)
        self.chart_type_combobox.currentIndexChanged.connect(self.update_chart_type)
        self.chart_type_combobox.setStyleSheet("""
            QComboBox {
                background-color: #0C0E13;
                color: #D1D5DB;
                border: 1px solid #374151;
                border-radius: 4px;
                padding: 4px 8px;
            }
        """)
        toolbar_layout.addWidget(self.chart_type_combobox)

        toolbar_layout.addSpacing(15)

        # Action buttons
        add_btn = QtWidgets.QPushButton("➕ New")
        add_btn.setMaximumWidth(90)
        add_btn.clicked.connect(self.add_chart)
        add_btn.setStyleSheet("""
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
        toolbar_layout.addWidget(add_btn)

        remove_btn = QtWidgets.QPushButton("❌ Close")
        remove_btn.setMaximumWidth(90)
        remove_btn.clicked.connect(self.remove_chart)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #DC2626; }
        """)
        toolbar_layout.addWidget(remove_btn)

        sync_btn = QtWidgets.QPushButton("🔄 Sync Now")
        sync_btn.setMaximumWidth(100)
        sync_btn.clicked.connect(self.sync_all_charts)
        sync_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #2563EB; }
        """)
        toolbar_layout.addWidget(sync_btn)

        # Auto-sync toggle
        self.auto_sync_check = QtWidgets.QCheckBox("🔁 Auto-Sync (30s)")
        self.auto_sync_check.setChecked(True)
        self.auto_sync_check.stateChanged.connect(self._toggle_auto_sync)
        self.auto_sync_check.setStyleSheet("color: #D1D5DB; font-weight: 600;")
        toolbar_layout.addWidget(self.auto_sync_check)

        toolbar_layout.addStretch()
        layout.addWidget(toolbar)

    def setup_status_bar(self, layout):
        """Create status bar showing sync status and chart info."""
        status_widget = QtWidgets.QWidget()
        status_widget.setStyleSheet("""
            QWidget {
                background-color: #131722;
                border-bottom: 1px solid #374151;
            }
        """)
        status_layout = QHBoxLayout(status_widget)
        status_layout.setSpacing(15)
        status_layout.setContentsMargins(12, 6, 12, 6)

        # Status indicator
        self.status_indicator = QLabel("🟢")
        self.status_indicator.setStyleSheet("font-size: 16px;")
        status_layout.addWidget(self.status_indicator)

        # Main status label
        self.status_label = QLabel("Ready to view charts")
        self.status_label.setStyleSheet("color: #10B981; font-weight: 600; font-size: 12px;")
        status_layout.addWidget(self.status_label)

        # Chart count label
        self.chart_count_label = QLabel("Charts: 0")
        self.chart_count_label.setStyleSheet("color: #9CA3AF; font-size: 12px;")
        status_layout.addWidget(self.chart_count_label)

        status_layout.addStretch()

        # Sync status
        self.sync_status_label = QLabel("Auto-sync: ON")
        self.sync_status_label.setStyleSheet("color: #10B981; font-size: 12px; font-weight: 600;")
        status_layout.addWidget(self.sync_status_label)

        layout.addWidget(status_widget)

    # ---------------------------------------------------------
    # 🌐 Load Assets from SmartBot / Horizon
    # ---------------------------------------------------------
    def load_assets_from_smartbot(self):
        """Populate combo boxes using SmartBot assets or fallback to Horizon."""
        self.assets_combobox1.clear()
        self.assets_combobox2.clear()

        try:
            asset_codes = ["XLM", "USDC", "BTC", "ETH"]
            
            if self.bot and hasattr(self.bot, "accounts_df"):
                df = self.bot.accounts_df
                if not df.empty and "asset_code" in df.columns:
                    codes = sorted(df["asset_code"].dropna().unique().tolist())
                    if codes:
                        asset_codes = codes
            elif self.bot and hasattr(self.bot, "server"):
                try:
                    # Fetch top assets from Horizon
                    assets_data = self.bot.server.assets().limit(50).call()
                    embedded = assets_data.get("_embedded", {}).get("records", [])
                    codes = [a.get("asset_code", "XLM") for a in embedded if a.get("asset_code")]
                    if codes:
                        asset_codes = list(dict.fromkeys(codes))[:20]  # Limit to 20, remove dupes
                except Exception as horizon_err:
                    pass  # Use fallback

            # Populate comboboxes
            self.assets_combobox1.addItems(asset_codes)
            self.assets_combobox2.addItems(["USDC", "USD", "BTC", "EUR", "XLM"])
            
            self.status_label.setText(f"✅ Loaded {len(asset_codes)} assets")
            self.status_indicator.setText("🟢")
            self.status_indicator.setStyleSheet("font-size: 16px; color: #10B981;")
        except Exception as e:
            self.assets_combobox1.addItems(["XLM", "BTC", "ETH", "USDC"])
            self.assets_combobox2.addItems(["USDC", "USD"])
            self.status_label.setText(f"⚠️ Using default assets")
            self.status_indicator.setText("🟡")
            self.status_indicator.setStyleSheet("font-size: 16px; color: #FCD34D;")

    # ---------------------------------------------------------
    # 🪟 Chart Management
    # ---------------------------------------------------------
    def add_chart(self):
        """Add new chart tab with selected asset pair and chart type."""
        try:
            asset1 = self.assets_combobox1.currentText() or "XLM"
            asset2 = self.assets_combobox2.currentText() or "USDC"
            asset_pair = f"{asset1}/{asset2}"
            chart_type = self.chart_type_combobox.currentText() or "candle"
            chart_label = f"{asset_pair} ({chart_type[:3].upper()})"

            chart_class = self.available_charts.get(chart_type)
            if not chart_class:
                QMessageBox.warning(self, "Error", f"Invalid chart type: {chart_type}")
                return

            new_tab = QtWidgets.QWidget()
            tab_layout = QVBoxLayout(new_tab)
            tab_layout.setContentsMargins(0, 0, 0, 0)

            if chart_type == "candle":
                chart_widget = chart_class(new_tab, self.controller)
            else:
                chart_widget = chart_class(new_tab, self.controller, self.data)

            tab_layout.addWidget(chart_widget)
            new_tab.chart_widget = chart_widget
            new_tab.chart_name = asset_pair
            new_tab.chart_type = chart_type
            
            self.notebook.addTab(new_tab, chart_label)
            self.chart_count += 1
            self._update_chart_count()
            
            # Auto-refresh new chart
            worker = ChartRefreshWorker(chart_widget, asset_pair, callback=self._on_chart_synced)
            self.thread_pool.start(worker)
            
            self.status_label.setText(f"✅ Added {chart_label}")
            
        except Exception as e:
            self.status_label.setText(f"❌ Chart error: {str(e)[:40]}")
            self.status_indicator.setText("🔴")
            self.status_indicator.setStyleSheet("font-size: 16px; color: #EF4444;")
            QMessageBox.critical(self, "Chart Error", f"Failed to load chart:\n{str(e)}")

    def update_chart_type(self):
        """Update chart type and add new chart."""
        self.chart_type = self.chart_type_combobox.currentText()
        self.add_chart()

    def remove_chart(self):
        """Remove current chart tab."""
        idx = self.notebook.currentIndex()
        if idx >= 0:
            tab = self.notebook.widget(idx)
            tab_name = self.notebook.tabText(idx)
            self.notebook.removeTab(idx)
            self.chart_count -= 1
            self._update_chart_count()
            self.status_label.setText(f"✅ Removed {tab_name}")
        else:
            self.status_label.setText("⚠️ No charts to close")
            self.status_indicator.setText("🟡")
            self.status_indicator.setStyleSheet("font-size: 16px; color: #FCD34D;")

    def _update_chart_count(self):
        """Update chart count display."""
        count = self.notebook.count()
        self.chart_count_label.setText(f"Charts: {count}")

    # ---------------------------------------------------------
    # 🔁 Concurrent Synchronization
    # ---------------------------------------------------------
    def sync_all_charts(self):
        """Refresh all charts in parallel using QThreadPool."""
        count = self.notebook.count()
        if count == 0:
            self.status_label.setText("⚠️ No charts to sync")
            self.status_indicator.setText("🟡")
            self.status_indicator.setStyleSheet("font-size: 16px; color: #FCD34D;")
            return

        self.status_label.setText(f"🔄 Syncing {count} chart(s)...")
        self.status_indicator.setText("🔵")
        self.status_indicator.setStyleSheet("font-size: 16px; color: #3B82F6;")
        self.syncing_charts.clear()

        for i in range(count):
            tab = self.notebook.widget(i)
            chart_widget = getattr(tab, "chart_widget", None)
            chart_name = getattr(tab, "chart_name", f"Chart {i+1}")
            if chart_widget:
                self.syncing_charts.add(chart_name)
                worker = ChartRefreshWorker(chart_widget, chart_name, callback=self._on_chart_synced)
                self.thread_pool.start(worker)

    @Slot(str)
    def _on_chart_synced(self, message: str):
        """Update UI after individual chart completes refresh."""
        if message.startswith("✅"):
            self.status_indicator.setText("🟢")
            self.status_indicator.setStyleSheet("font-size: 16px; color: #10B981;")
            self.status_label.setText(message)
            self.sync_status_label.setStyleSheet("color: #10B981; font-size: 12px; font-weight: 600;")
            self.sync_status_label.setText("Synced: ON")
        else:
            self.status_indicator.setText("🔴")
            self.status_indicator.setStyleSheet("font-size: 16px; color: #EF4444;")
            self.status_label.setText(message)
            self.sync_status_label.setStyleSheet("color: #EF4444; font-size: 12px; font-weight: 600;")
            self.sync_status_label.setText("Sync failed")

    def _toggle_auto_sync(self):
        """Toggle auto-sync on/off."""
        if self.auto_sync_check.isChecked():
            self.auto_sync_enabled = True
            self.sync_timer.start(30000)
            self.sync_status_label.setText("Auto-sync: ON")
            self.sync_status_label.setStyleSheet("color: #10B981; font-size: 12px; font-weight: 600;")
        else:
            self.auto_sync_enabled = False
            self.sync_timer.stop()
            self.sync_status_label.setText("Auto-sync: OFF")
            self.sync_status_label.setStyleSheet("color: #FCD34D; font-size: 12px; font-weight: 600;")
