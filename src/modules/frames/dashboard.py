from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import (
    QFrame, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QSizePolicy
)
from PySide6.QtCore import QObject, QThread, Signal, Slot
from qrcode.main import QRCode


# 🎨 Color Palette
@dataclass
class DashboardStyle:
    bg_dark: str = "#121212"
    panel_bg: str = "#263238"
    accent_green: str = "#00C853"
    accent_red: str = "#D32F2F"
    text_primary: str = "#ffffff"


# ⚙️ Worker to run bot in a separate thread
class BotWorker(QObject):
    finished = Signal()
    error = Signal(str)
    status = Signal(str)

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.running = False

    @Slot()
    def run(self):
        self.running = True
        try:
            self.status.emit("🚀 Bot started.")
            if hasattr(self.bot, "start"):
                self.bot.start()
            else:
                raise AttributeError("Bot object has no 'start' method.")
            self.status.emit("✅ Bot finished successfully.")
        except Exception as e:
            self.error.emit(f"Bot error: {e}")
        finally:
            self.running = False
            self.finished.emit()


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

        self._init_ui()
        self._connect_signals()
        self._start_auto_update()

    # ------------------------------------------------------------------
    # 🧱 UI Initialization
    # ------------------------------------------------------------------
    def _init_ui(self):
        """Create the dashboard layout."""
        self.setStyleSheet(f"background-color:{self.style.bg_dark}; color:{self.style.text_primary};")

        grid = QGridLayout(self)
        grid.setSpacing(12)
        grid.setContentsMargins(20, 20, 20, 20)

        # Header
        self.lbl_time = QLabel(self._now())
        self.lbl_time.setAlignment(QtCore.Qt.AlignRight)
        self.lbl_time.setStyleSheet("font-size:14px; color:#90caf9;")

        account_id = getattr(self.controller, "account_id", "N/A")
        self.lbl_account = QLabel(f"Account ID: {account_id}")
        self.lbl_account.setStyleSheet("font-weight:600; font-size:14px;")

        grid.addWidget(self.lbl_account, 0, 0, 1, 2)
        grid.addWidget(self.lbl_time, 0, 2)

        # Sections
        self.qr_group = self._create_qr_section(account_id)
        self.msg_group = self._create_message_panel()
        self.stats_group = self._create_stats_panel()

        grid.addWidget(self.qr_group, 1, 0, 2, 1)
        grid.addWidget(self.msg_group, 1, 1, 2, 1)

        # ✅ FIXED HERE — addLayout, not addWidget
        grid.addLayout(self._create_controls(), 3, 0, 1, 2)

        grid.addWidget(self.stats_group, 4, 0, 1, 3)
        self.setLayout(grid)

    # ------------------------------------------------------------------
    # 🧩 UI Sections
    # ------------------------------------------------------------------
    def _create_qr_section(self, data: str) -> QGroupBox:
        group = QGroupBox("Account QR")
        group.setStyleSheet("font-size:15px; font-weight:bold;")
        layout = QVBoxLayout()
        qr_label = QLabel()
        qr_label.setPixmap(self._generate_qr_pixmap(data))
        qr_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(qr_label)
        text = QLabel("📲 Scan to send funds")
        text.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(text)
        group.setLayout(layout)
        return group

    def _create_message_panel(self) -> QGroupBox:
        group = QGroupBox("Server Status")
        group.setStyleSheet(
            f"font-size:15px; font-weight:bold; background-color:{self.style.panel_bg}; color:white;"
        )
        layout = QVBoxLayout()
        layout.setSpacing(4)
        self.lbl_status = QLabel("Status: Idle")
        self.lbl_info = QLabel("Info: —")
        self.lbl_message = QLabel("Message: —")
        self.lbl_error = QLabel("Error: —")

        for lbl in [self.lbl_status, self.lbl_info, self.lbl_message, self.lbl_error]:
            lbl.setStyleSheet("font-size:13px; padding:2px;")
            layout.addWidget(lbl)
        group.setLayout(layout)
        return group

    def _create_stats_panel(self) -> QGroupBox:
        group = QGroupBox("Performance")
        group.setStyleSheet("font-size:15px; font-weight:bold; background-color:#1b5e20; color:white;")
        layout = QVBoxLayout()
        layout.setSpacing(3)
        self.stats_labels = {}
        for stat in ["Total Trades", "Profit", "Win Rate"]:
            lbl = QLabel(f"{stat}: 0")
            lbl.setStyleSheet("font-size:13px; padding:3px;")
            layout.addWidget(lbl)
            self.stats_labels[stat] = lbl
        group.setLayout(layout)
        return group

    def _create_controls(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(10)
        self.btn_start = QPushButton("START")
        self.btn_stop = QPushButton("STOP")
        self._apply_button_style(self.btn_start, self.style.accent_green)
        self._apply_button_style(self.btn_stop, self.style.accent_red)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addStretch(1)
        return layout

    # ------------------------------------------------------------------
    # ⚙️ Signals and Timers
    # ------------------------------------------------------------------
    def _connect_signals(self):
        self.btn_start.clicked.connect(self.start_bot)
        self.btn_stop.clicked.connect(self.stop_bot)
        self.update_signal.connect(self._refresh_dashboard)

    def _start_auto_update(self):
        self.timer.timeout.connect(self._fetch_updates)
        self.timer.start(1000)

    # ------------------------------------------------------------------
    # 🚀 Bot Thread Management
    # ------------------------------------------------------------------
    def start_bot(self):
        """Start bot asynchronously."""
        if not self.bot:
            return self._update_message("⚠️ Bot not initialized", True)
        if self._bot_thread and self._bot_thread.isRunning():
            return self._update_message("⚙️ Bot already running", False)

        # Clean up old thread
        self.stop_bot()

        self._bot_thread = QThread()
        self._bot_worker = BotWorker(self.bot)
        self._bot_worker.moveToThread(self._bot_thread)

        self._bot_thread.started.connect(self._bot_worker.run)
        self._bot_worker.status.connect(self._on_bot_status)
        self._bot_worker.error.connect(self._on_bot_error)
        self._bot_worker.finished.connect(self._bot_thread.quit)
        self._bot_worker.finished.connect(self._bot_worker.deleteLater)
        self._bot_thread.finished.connect(self._bot_thread.deleteLater)
        self._bot_worker.finished.connect(lambda: self._set_button_state(False))

        self._set_button_state(True)
        self._bot_thread.start()
        self._update_message("🚀 Bot thread launched")
        return None

    def stop_bot(self):
        """Stop the bot gracefully."""
        if self._bot_worker and self._bot_worker.running:
            self._bot_worker.running = False
            if hasattr(self.bot, "stop"):
                self.bot.stop()
            self._update_message("🛑 Bot stopped.")
        self._set_button_state(False)
        return None

    # ------------------------------------------------------------------
    # 🔄 Dashboard Updates
    # ------------------------------------------------------------------
    def _fetch_updates(self):
        msg = getattr(self.controller, "server_msg", {})
        msg["time"] = self._now()
        self.update_signal.emit(msg)

    def _refresh_dashboard(self, msg: dict):
        self.lbl_time.setText(msg.get("time", self._now()))
        self.lbl_status.setText(f"Status: {msg.get('status', 'Unknown')}")
        self.lbl_info.setText(f"Info: {msg.get('info', 'No info')}")
        self.lbl_message.setText(f"Message: {msg.get('message', '—')}")
        self.lbl_error.setText(f"Error: {msg.get('error', 'None')}")
        for stat, value in msg.get("performance_stats", {}).items():
            if stat in self.stats_labels:
                self.stats_labels[stat].setText(f"{stat}: {value}")

    # ------------------------------------------------------------------
    # 🧰 Helpers
    # ------------------------------------------------------------------
    def _update_message(self, text: str, error: bool = False):
        color = self.style.accent_red if error else self.style.accent_green
        self.lbl_message.setStyleSheet(f"color:{color}; font-weight:600;")
        self.lbl_message.setText(f"Message: {text}")

    def _on_bot_status(self, text: str):
        self.lbl_status.setText(f"Status: {text}")
        self._update_message(text)

    def _on_bot_error(self, text: str):
        self.lbl_error.setText(f"Error: {text}")
        self._update_message(text, True)

    def _set_button_state(self, running: bool):
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)

    def _apply_button_style(self, btn: QPushButton, color: str):
        btn.setStyleSheet(
            f"background-color:{color}; color:white; border:none; padding:8px 16px;"
            f"font-weight:bold; border-radius:6px;"
        )
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    @staticmethod
    def _generate_qr_pixmap(data: str) -> QtGui.QPixmap:
        qr = QRCode(version=1, box_size=8, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        buf = BytesIO()
        qr.make_image(fill_color="black", back_color="white").save(buf, format="PNG")
        pix = QtGui.QPixmap()
        pix.loadFromData(buf.getvalue())# "PNG")
        return pix.scaled(150, 150, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
