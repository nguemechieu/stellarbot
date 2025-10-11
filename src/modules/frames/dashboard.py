from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets, QtCharts
from PySide6.QtWidgets import (
    QFrame, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QSizePolicy, QProgressBar
)
from PySide6.QtCore import QObject, QThread, Signal, Slot
from qrcode.main import QRCode


# 🎨 Unified Color Palette
@dataclass
class DashboardStyle:
    bg_dark: str = "#101820"
    panel_bg: str = "#1A2634"
    accent_green: str = "#00E676"
    accent_red: str = "#E53935"
    accent_blue: str = "#1976D2"
    text_primary: str = "#FFFFFF"
    text_secondary: str = "#B0BEC5"


# ⚙️ Background Worker for the SmartBot
class BotWorker(QObject):
    finished = Signal()
    error = Signal(str)
    status = Signal(str)

    def __init__(self,  controller=None):
        super().__init__()

        self.controller = controller
        self.running = False

    @Slot()
    def run(self):
        """Run the trading bot safely in background."""
        self.running = True
        try:
            self.status.emit("🚀 Starting Bot...")
            if self.controller.bot :
                self.controller.bot.start()
            else:
                raise AttributeError("Bot object has no 'start' method.")
            self.status.emit("✅ Bot finished successfully.")
        except Exception as e:
            self.error.emit(f"Bot error: {e}")
        finally:
            self.running = False
            self.finished.emit()


# ✨ Helper for consistent button style
def _apply_button_style(btn: QPushButton, color: str):
    btn.setStyleSheet(
        f"""
        QPushButton {{
            background-color: {color};
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #333;
            color: #fff;
            border: 1px solid {color};
        }}
        """
    )
    btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


# 🧭 Main Dashboard
class Dashboard(QFrame):
    update_signal = QtCore.Signal(dict)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.style = DashboardStyle()

        self.timer = QtCore.QTimer(self)
        self._bot_thread: Optional[QThread] = None
        self._bot_worker: Optional[BotWorker] = None

        self.performance_series = QtCharts.QLineSeries()
        self.performance_points = []

        self._init_ui()
        self._connect_signals()
        self._start_auto_update()

    # ------------------------------------------------------------------
    # 🧱 UI Initialization
    # ------------------------------------------------------------------
    def _init_ui(self):
        self.setStyleSheet(f"background-color:{self.style.bg_dark}; color:{self.style.text_primary};")

        grid = QGridLayout(self)
        grid.setSpacing(14)
        grid.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("StellarBot Pro Dashboard")
        header.setStyleSheet(
            f"font-size:20px; font-weight:700; color:{self.style.accent_blue}; margin-bottom:5px;"
        )
        header.setAlignment(QtCore.Qt.AlignLeft)

        self.lbl_time = QLabel(self._now())
        self.lbl_time.setAlignment(QtCore.Qt.AlignRight)
        self.lbl_time.setStyleSheet("font-size:14px; color:#90CAF9;")

        header_layout = QHBoxLayout()
        header_layout.addWidget(header)
        header_layout.addWidget(self.lbl_time)
        grid.addLayout(header_layout, 0, 0, 1, 3)

        # Account QR + Info
        account_id = getattr(self.controller, "account_id", "N/A")
        self.lbl_account = QLabel(f"Account: {account_id}")
        self.lbl_account.setStyleSheet("font-weight:600; font-size:14px; margin-bottom:10px;")
        grid.addWidget(self.lbl_account, 1, 0, 1, 2)

        self.qr_group = self._create_qr_section(account_id)
        self.msg_group = self._create_message_panel()
        self.stats_group = self._create_stats_panel()
        self.chart_group = self._create_chart_panel()

        grid.addWidget(self.qr_group, 2, 0)
        grid.addWidget(self.msg_group, 2, 1)
        grid.addWidget(self.stats_group, 2, 2)
        grid.addWidget(self.chart_group, 3, 0, 1, 3)
        grid.addLayout(self._create_controls(), 4, 0, 1, 3)

        self.setLayout(grid)

    # ------------------------------------------------------------------
    # 🧩 UI Sections
    # ------------------------------------------------------------------
    def _create_qr_section(self, data: str) -> QGroupBox:
        group = QGroupBox("Account QR")
        group.setStyleSheet(
            "font-size:15px; font-weight:600; color:white; border:1px solid #37474F; border-radius:8px;"
        )
        layout = QVBoxLayout()
        qr_label = QLabel()
        qr_label.setPixmap(self._generate_qr_pixmap(data))
        qr_label.setAlignment(QtCore.Qt.AlignCenter)
        text = QLabel("📲 Scan to send funds")
        text.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(qr_label)
        layout.addWidget(text)
        group.setLayout(layout)
        return group

    def _create_message_panel(self) -> QGroupBox:
        group = QGroupBox("Server Status")
        group.setStyleSheet(
            f"font-size:15px; font-weight:600; background-color:{self.style.panel_bg}; color:white; border-radius:8px;"
        )
        layout = QVBoxLayout(spacing=4)
        self.lbl_status = QLabel("Status: STOPPED")
        self.lbl_info = QLabel("Info: —")
        self.lbl_message = QLabel("Message: —")
        self.lbl_error = QLabel("Error: —")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar {height: 6px; background: #263238;} QProgressBar::chunk {background: #00E676;}")

        for lbl in [self.lbl_status, self.lbl_info, self.lbl_message, self.lbl_error]:
            lbl.setStyleSheet("font-size:13px; padding:3px;")
            layout.addWidget(lbl)

        layout.addWidget(self.progress_bar)
        group.setLayout(layout)
        return group

    def _create_stats_panel(self) -> QGroupBox:
        group = QGroupBox("Performance Metrics")
        group.setStyleSheet("font-size:15px; font-weight:600; background-color:#1B5E20; color:white; border-radius:8px;")
        layout = QVBoxLayout(spacing=4)
        self.stats_labels = {}
        for stat in ["Total Trades", "Profit (USD)", "Win Rate (%)"]:
            lbl = QLabel(f"{stat}: 0")
            lbl.setStyleSheet("font-size:13px; padding:3px;")
            layout.addWidget(lbl)
            self.stats_labels[stat] = lbl
        group.setLayout(layout)
        return group

    def _create_chart_panel(self) -> QGroupBox:
        group = QGroupBox("📈 Profit Trend")
        layout = QVBoxLayout()

        chart = QtCharts.QChart()
        chart.addSeries(self.performance_series)
        chart.createDefaultAxes()
        chart.axisX(self.performance_series).setTitleText("Updates")
        chart.axisY(self.performance_series).setTitleText("Profit (USD)")
        chart.setBackgroundBrush(QtGui.QColor("#0D1117"))
        chart.setTitleBrush(QtGui.QBrush(QtGui.QColor("#BBDEFB")))
        chart.legend().hide()

        self.chart_view = QtCharts.QChartView(chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
        layout.addWidget(self.chart_view)
        group.setLayout(layout)
        return group

    def _create_controls(self) -> QHBoxLayout:
        layout = QHBoxLayout(spacing=10)
        self.btn_start = QPushButton("▶ Start Bot")
        self.btn_stop = QPushButton("⏹ Stop Bot")
        _apply_button_style(self.btn_start, self.style.accent_green)
        _apply_button_style(self.btn_stop, self.style.accent_red)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addStretch(1)
        return layout

    # ------------------------------------------------------------------
    # ⚙️ Signals & Timers
    # ------------------------------------------------------------------
    def _connect_signals(self):
        self.btn_start.clicked.connect(self.start_bot)
        self.btn_stop.clicked.connect(self.stop_bot)
        self.update_signal.connect(self._refresh_dashboard)

    def _start_auto_update(self):
        self.timer.timeout.connect(self._fetch_updates)
        self.timer.start(1000)

    # ------------------------------------------------------------------
    # 🚀 Bot Management
    # ------------------------------------------------------------------
    def start_bot(self):
        """Start the trading bot in a separate thread."""
        if not self.bot:
            return self._update_message("⚠️ Bot not initialized", True)
        if self._bot_thread and self._bot_thread.isRunning():
            return self._update_message("⚙️ Bot already running")

        # Clean up any previous thread
        if self._bot_thread:
            self._bot_thread.quit()
            self._bot_thread.wait()
            self._bot_thread = None

        self._bot_thread = QThread(self)
        self._bot_worker = BotWorker(self.controller)
        self._bot_worker.moveToThread(self._bot_thread)

        self._bot_thread.started.connect(self._bot_worker.run)
        self._bot_worker.status.connect(self._on_bot_status)
        self._bot_worker.error.connect(self._on_bot_error)
        self._bot_worker.finished.connect(self._bot_thread.quit)
        self._bot_worker.finished.connect(self._bot_worker.deleteLater)
        self._bot_thread.finished.connect(self._bot_thread.deleteLater)
        self._bot_worker.finished.connect(lambda: self._set_button_state(False))

        self._set_button_state(True)
        self.progress_bar.setVisible(True)
        self._bot_thread.start()
        self._update_message("🚀 Bot thread launched")

    def stop_bot(self):
        """Stop bot execution gracefully."""
        if self._bot_worker and self._bot_worker.running:
            self._bot_worker.running = False
            if hasattr(self.bot, "stop"):
                try:
                    self.bot.stop()
                    self._update_message("🛑 Bot stopped.")
                except Exception as e:
                    self._update_message(f"Error stopping bot: {e}", True)

        if self._bot_thread and self._bot_thread.isRunning():
            self._bot_thread.quit()
            self._bot_thread.wait(2000)
        self._set_button_state(False)
        self.progress_bar.setVisible(False)

    # ------------------------------------------------------------------
    # 🔄 Updates & Chart
    # ------------------------------------------------------------------
    def _fetch_updates(self):
        msg = getattr(self.controller, "server_msg", {}) or {}
        msg["time"] = self._now()
        self.update_signal.emit(msg)

    def _refresh_dashboard(self, msg: dict):
        self.lbl_time.setText(msg.get("time", self._now()))
        self.lbl_status.setText(f"Status: {msg.get('status', 'Unknown')}")
        self.lbl_info.setText(f"Info: {msg.get('info', 'No info')}")
        self.lbl_message.setText(f"Message: {msg.get('message', '—')}")
        self.lbl_error.setText(f"Error: {msg.get('error', 'None')}")

        stats = msg.get("performance_stats", {})
        for stat, value in stats.items():
            if stat in self.stats_labels:
                self.stats_labels[stat].setText(f"{stat}: {value}")

        # Update chart
        profit = stats.get("Profit (USD)", 0)
        self._update_chart(float(profit))

    def _update_chart(self, value: float):
        """Append live profit to chart."""
        if len(self.performance_points) > 30:
            self.performance_points.pop(0)
        self.performance_points.append(value)
        self.performance_series.clear()
        for i, val in enumerate(self.performance_points):
            self.performance_series.append(i, val)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _update_message(self, text: str, error: bool = False):
        color = self.style.accent_red if error else self.style.accent_green
        self.lbl_message.setStyleSheet(f"color:{color}; font-weight:600;")
        self.lbl_message.setText(f"Message: {text}")

    def _on_bot_status(self, text: str):
        self.lbl_status.setText(f"Status: {text}")
        self._update_message(text)
        self.progress_bar.setVisible("Starting" in text)

    def _on_bot_error(self, text: str):
        self.lbl_error.setText(f"Error: {text}")
        self._update_message(text, True)
        self.progress_bar.setVisible(False)

    def _set_button_state(self, running: bool):
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)

    @staticmethod
    def _generate_qr_pixmap(data: str) -> QtGui.QPixmap:
        qr = QRCode(version=1, box_size=8, border=2)
        qr.add_data(data or "Unknown")
        qr.make(fit=True)
        buf = BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(buf, format="PNG")
        pix = QtGui.QPixmap()
        pix.loadFromData(buf.getvalue())
        return pix.scaled(150, 150, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
