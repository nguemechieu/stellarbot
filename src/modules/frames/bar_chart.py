import mplfinance as mpf
import pandas as pd
from pandas import DataFrame
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QMessageBox, QFrame
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class BarChart(QFrame):
    """
    📊 BarChart: OHLC bar chart widget with mplfinance for PySide6.
    Integrates seamlessly into your Charts dashboard and SmartBot data flow.
    """

    def __init__(self, parent=None, controller=None, df=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.canvas = None

        # Initialize and validate data
        self.df = DataFrame(df) if df is not None else pd.DataFrame()
        self._prepare_dataframe()

        # Build UI
        self._init_ui()

    # ------------------------------------------------------------------
    def _prepare_dataframe(self):
        """Ensure DataFrame is in valid OHLCV format."""
        try:
            if "Date" not in self.df.columns:
                raise ValueError("DataFrame missing 'Date' column")

            self.df["Date"] = pd.to_datetime(self.df["Date"], errors="coerce")
            self.df.dropna(subset=["Date"], inplace=True)
            self.df.set_index("Date", inplace=True)
            self.df.sort_index(inplace=True)
        except Exception as e:
            print(f"[BarChart] Data preparation error: {e}")
            self.df = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

    # ------------------------------------------------------------------
    def _init_ui(self):
        """Setup toolbar and chart area."""
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()

        # Buttons
        for text, slot in [
            ("➕ Add Chart", self.add_chart),
            ("❌ Remove Chart", self.remove_chart),
            ("🔄 Refresh Data", self.refresh_chart),
            ("💾 Save Chart", self.save_chart),
        ]:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            toolbar.addWidget(btn)

        layout.addLayout(toolbar)

        # Initialize chart
        self.create_bar_chart()

    # ------------------------------------------------------------------
    def create_bar_chart(self):
        """Draw the mplfinance bar chart."""
        try:
            if self.df.empty:
                QMessageBox.warning(self, "No Data", "No data available for bar chart.")
                return

            # Clear old chart if present
            if self.canvas:
                layout = self.layout()
                layout.removeWidget(self.canvas)
                self.canvas.setParent(None)
                self.canvas.deleteLater()

            # Plot using mplfinance
            fig, _ = mpf.plot(
                self.df,
                type="ohlc",
                style="charles",
                title="Bar Chart",
                ylabel="Price",
                volume=True,
                returnfig=True,
                figsize=(10, 6),
            )

            self.canvas = FigureCanvas(fig)
            self.layout().addWidget(self.canvas)

        except Exception as e:
            print(f"[BarChart] Chart rendering error: {e}")
            QMessageBox.critical(self, "Error", f"Error generating chart:\n{e}")

    # ------------------------------------------------------------------
    def add_chart(self):
        """Placeholder for multi-chart logic (handled by Charts container)."""
        print("[BarChart] Add chart clicked")

    def remove_chart(self):
        """Placeholder for removal logic."""
        print("[BarChart] Remove chart clicked")

    # ------------------------------------------------------------------
    def refresh_chart(self):
        """
        Refresh chart with updated OHLCV data.
        If SmartBot is connected, pull live asset data.
        Otherwise simulate updates.
        """
        try:
            if self.bot and hasattr(self.bot, "get_asset_data"):
                # Example: bot.get_asset_data("XLM/USDC") returns DataFrame
                new_df = self.bot.get_asset_data("XLM/USDC")
                if not new_df.empty:
                    self.df = new_df
            else:
                # Simulated data change
                self.df["Close"] = self.df["Close"] + (pd.Series(range(len(self.df))) % 2 - 0.5) * 2

            self.create_bar_chart()
            print("[BarChart] Chart refreshed successfully")

        except Exception as e:
            print(f"[BarChart] Refresh error: {e}")
            QMessageBox.warning(self, "Warning", f"Failed to refresh chart:\n{e}")

    # ------------------------------------------------------------------
    def save_chart(self):
        """Save chart as image."""
        if not self.canvas:
            QMessageBox.warning(self, "No Chart", "No chart available to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Chart", "", "PNG Files (*.png)")
        if file_path:
            self.canvas.figure.savefig(file_path, dpi=300)
            QMessageBox.information(self, "Saved", f"Chart saved as:\n{file_path}")
            print(f"[BarChart] Saved to {file_path}")
