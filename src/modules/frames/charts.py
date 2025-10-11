from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QRunnable, QThreadPool, Slot
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout

from src.modules.frames.bar_chart import BarChart
from src.modules.frames.candles_stick_chart import DexTradingChart
from src.modules.frames.heikin_ashi import HeikinAshi
from src.modules.frames.line_chart import LineChart
from src.modules.frames.renko import Renko

class ChartRefreshWorker(QRunnable):
    """Background task to refresh a single chart safely."""

    def __init__(self, chart_widget, callback=None):
        super().__init__()
        self.chart_widget = chart_widget
        self.callback = callback

    def run(self):
        """Run safely in background thread."""
        try:
            if hasattr(self.chart_widget, "_refresh_data"):
                self.chart_widget._refresh_data()
            elif hasattr(self.chart_widget, "refresh_chart"):
                self.chart_widget.refresh_chart()

            if self.callback:
                QtCore.QMetaObject.invokeMethod(
                    self.callback.__self__,
                    self.callback.__name__,
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, f"✅ {type(self.chart_widget).__name__} refreshed successfully")
                )

        except Exception as e:
            import traceback
            traceback.print_exc()
            err_msg = f"❌ {type(self.chart_widget).__name__} failed: {e}"
            if self.callback:
                QtCore.QMetaObject.invokeMethod(
                    self.callback.__self__,
                    self.callback.__name__,
                    QtCore.Qt.QueuedConnection,
                    QtCore.Q_ARG(str, err_msg)
                )



# ---------------------------------------------------------
# 📈 Charts Frame
# ---------------------------------------------------------
class Charts(QFrame):
    """Unified chart manager with threaded sync + live assets from SmartBot."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.trading_mode = 'Manual'
        self.chart_type = "candle"

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

        # UI Layout
        layout = QVBoxLayout(self)
        self.setup_toolbar(layout)
        self.setup_content(layout)

        self.notebook = QtWidgets.QTabWidget()
        layout.addWidget(self.notebook)

        # Populate assets from SmartBot
        self.load_assets_from_smartbot()

        # Add default chart
        self.add_chart()

        # Auto-sync timer
        self.sync_timer = QtCore.QTimer()
        self.sync_timer.timeout.connect(self.sync_all_charts)
        self.sync_timer.start(30000)  # every 30 seconds

    # ---------------------------------------------------------
    # 🧰 Toolbar
    # ---------------------------------------------------------
    def setup_toolbar(self, layout):
        toolbar = QtWidgets.QWidget(self)
        toolbar_layout = QHBoxLayout(toolbar)

        toolbar_layout.addWidget(QtWidgets.QLabel("Select Asset:"))

        self.assets_combobox1 = QtWidgets.QComboBox()
        toolbar_layout.addWidget(self.assets_combobox1)

        self.assets_combobox2 = QtWidgets.QComboBox()
        toolbar_layout.addWidget(self.assets_combobox2)

        toolbar_layout.addWidget(QtWidgets.QLabel("Chart Type:"))
        self.chart_type_combobox = QtWidgets.QComboBox()
        self.chart_type_combobox.addItems(["candle", "line", "bar", "renko", "heikin-ashi"])
        self.chart_type_combobox.currentIndexChanged.connect(self.update_chart_type)
        toolbar_layout.addWidget(self.chart_type_combobox)

        add_btn = QtWidgets.QPushButton("➕ Add Chart")
        add_btn.clicked.connect(self.add_chart)
        toolbar_layout.addWidget(add_btn)

        remove_btn = QtWidgets.QPushButton("❌ Remove Chart")
        remove_btn.clicked.connect(self.remove_chart)
        toolbar_layout.addWidget(remove_btn)

        sync_btn = QtWidgets.QPushButton("🔄 Sync All")
        sync_btn.clicked.connect(self.sync_all_charts)
        toolbar_layout.addWidget(sync_btn)

        self.status_label = QtWidgets.QLabel("Mode: Manual")
        toolbar_layout.addWidget(self.status_label)

        layout.addWidget(toolbar)

    # ---------------------------------------------------------
    def setup_content(self, layout):
        layout.addWidget(QtWidgets.QFrame(self))

    # ---------------------------------------------------------
    # 🌐 Load Assets from SmartBot / Horizon
    # ---------------------------------------------------------
    def load_assets_from_smartbot(self):
        """Populate combo boxes using SmartBot assets or fallback to Horizon."""
        self.assets_combobox1.clear()
        self.assets_combobox2.clear()

        try:
            if self.bot and hasattr(self.bot, "accounts_df"):
                df = self.bot.accounts_df
                if not df.empty and "asset_code" in df.columns:
                    asset_codes = sorted(df["asset_code"].dropna().unique().tolist())
                else:
                    asset_codes = ["XLM", "USDC"]
            else:
                # fallback: minimal call to horizon
                assets_data = self.bot.server.assets().limit(200).call()
                embedded = assets_data.get("_embedded", {}).get("records", [])
                asset_codes = [a.get("asset_code", "XLM") for a in embedded if a.get("asset_code")]

            # populate
            self.assets_combobox1.addItems(asset_codes)
            self.assets_combobox2.addItems(["USDC", "USD", "BTC", "EUR"])
            self.status_label.setText(f"✅ Loaded {len(asset_codes)} assets from SmartBot")
        except Exception as e:
            self.assets_combobox1.addItems(["XLM", "BTC", "ETH"])
            self.assets_combobox2.addItems(["USDC", "USD"])
            self.status_label.setText(f"⚠️ Asset load failed: {e}")

    # ---------------------------------------------------------
    # 🪟 Chart Management
    # ---------------------------------------------------------
    def add_chart(self):
        asset_pair = f"{self.assets_combobox1.currentText()}/{self.assets_combobox2.currentText()}"
        chart_label = f"{asset_pair} - {self.chart_type.upper()}"

        chart_class = self.available_charts.get(self.chart_type)
        if not chart_class:
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid chart type selected.")
            return

        new_tab = QtWidgets.QWidget()
        tab_layout = QVBoxLayout(new_tab)

        try:
            if self.chart_type == "candle":
                chart_widget = chart_class(new_tab, self.controller)  # live
            else:
                chart_widget = chart_class(new_tab, self.controller, self.data)

            tab_layout.addWidget(chart_widget)
            new_tab.chart_widget = chart_widget
            self.notebook.addTab(new_tab, chart_label)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Chart Error", f"Failed to load chart: {e}")

    def update_chart_type(self):
        self.chart_type = self.chart_type_combobox.currentText()
        self.add_chart()

    def remove_chart(self):
        idx = self.notebook.currentIndex()
        if idx >= 0:
            self.notebook.removeTab(idx)
        else:
            QtWidgets.QMessageBox.information(self, "Info", "No charts open to remove.")

    # ---------------------------------------------------------
    # 🔁 Concurrent Synchronization
    # ---------------------------------------------------------
    def sync_all_charts(self):
        """Refresh all charts in parallel using QThreadPool."""
        count = self.notebook.count()
        if count == 0:
            self.status_label.setText("⚠️ No charts to sync.")
            return

        self.status_label.setText(f"🔄 Syncing {count} charts...")

        for i in range(count):
            tab = self.notebook.widget(i)
            chart_widget = getattr(tab, "chart_widget", None)
            if chart_widget:
                worker = ChartRefreshWorker(chart_widget, callback=self._on_chart_synced)
                self.thread_pool.start(worker)

    @Slot(str)
    def _on_chart_synced(self, message: str):
        """Update UI after individual chart completes refresh."""
        self.status_label.setText(message)
