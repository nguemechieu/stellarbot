from datetime import datetime
<<<<<<< Updated upstream
from PIL import Image
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (
    QFrame, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout
)
from qrcode import QRCode  # Ensure you install the qrcode library
from src.modules.frames.market_depth import random_color


=======
from io import BytesIO
from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets, QtCharts
from PySide6.QtWidgets import (
    QFrame, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QSizePolicy, QProgressBar, QTableWidget,
    QTableWidgetItem, QHeaderView, QScrollArea
)
from PySide6.QtCore import QObject, QThread, Signal, Slot, QSize
from PySide6.QtGui import QColor, QFont
from qrcode.main import QRCode


# 🎨 Unified Color Palette
@dataclass
class DashboardStyle:
    bg_dark: str = "#101820"
    panel_bg: str = "#1A2634"
    panel_alt: str = "#212A36"
    accent_green: str = "#00E676"
    accent_red: str = "#E53935"
    accent_yellow: str = "#FFB74D"
    accent_blue: str = "#1976D2"
    accent_purple: str = "#7C4DFF"
    text_primary: str = "#FFFFFF"
    text_secondary: str = "#B0BEC5"
    text_tertiary: str = "#78909C"
    border_color: str = "#37474F"
    success: str = "#4CAF50"
    warning: str = "#FFA726"


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
            if self.controller is not None and hasattr(self.controller.bot, "start"):
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
            border: none;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background-color: #333;
            color: #fff;
            border: 2px solid {color};
        }}
        QPushButton:pressed {{
            background-color: #1a1a1a;
            border: 2px solid {color};
        }}
        QPushButton:disabled {{
            background-color: #555;
            color: #999;
        }}
        """
    )
    btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


def _create_metric_card(title: str, value: str, unit: str = "", style: DashboardStyle = None) -> QGroupBox:
    """Create a styled metric card."""
    if not style:
        style = DashboardStyle()
    
    card = QGroupBox(title)
    card.setStyleSheet(
        f"""
        QGroupBox {{
            border: 1px solid {style.border_color};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: {style.panel_bg};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
            color: {style.text_secondary};
            font-size: 12px;
            font-weight: 600;
        }}
        """
    )
    layout = QVBoxLayout()
    
    value_label = QLabel(value)
    value_label.setStyleSheet(f"color: {style.accent_green}; font-size: 20px; font-weight: 700;")
    value_label.setAlignment(QtCore.Qt.AlignCenter)
    
    unit_label = QLabel(unit)
    unit_label.setStyleSheet(f"color: {style.text_secondary}; font-size: 11px;")
    unit_label.setAlignment(QtCore.Qt.AlignCenter)
    
    layout.addWidget(value_label)
    layout.addWidget(unit_label)
    card.setLayout(layout)
    return card


# 🧭 Main Dashboard
>>>>>>> Stashed changes
class Dashboard(QFrame):
    """Dashboard widget displaying live data, control buttons, and QR code for account_id."""

<<<<<<< Updated upstream
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.stop_button = None
        self.start_button = None
=======
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, controller=None):
        super().__init__(self, parent)
>>>>>>> Stashed changes
        self.controller = controller
        self.timer = None
        self.bot = self.controller.bot
        self.init_ui()
        self.update_dashboard()

    def init_ui(self):
        """Initialize the user interface components."""
        layout = QGridLayout()

        layout.addWidget(QLabel("Last Update: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")), 0, 2, 0, 1)
        layout.addWidget(QLabel("Account ID: " + self.controller.account_id), 1, 0, 0, 2)
        layout.addWidget(QLabel("Scan to Send Money here"), 2, 0, 0, 2)
        layout.addWidget(QLabel("Status: " + self.controller.server_msg.get('status', 'Unknown')), 3, 0, 0, 2)
        layout.addWidget(QLabel("Info: " + self.controller.server_msg.get('info', 'No info available')), 4, 0, 0, 2)
        layout.addWidget(QLabel("Message: " + self.controller.server_msg.get('message', 'No message')), 5, 0, 0, 2)
        layout.update()

        # QR Code Section (Positioned at the top)
        self.create_qr_code_section(layout)
        # Black Canvas Section (Positioned at the top)
        self.create_black_canvas(layout)

        # Control Buttons Section
        self.start_button = QPushButton("START")
        self.stop_button = QPushButton("STOP")
        self.start_button.clicked.connect(self.start_bot, QtCore.Qt.UniqueConnection)
        self.stop_button.clicked.connect(self.stop_bot, QtCore.Qt.UniqueConnection)
        self.update_button_state(True, False)
        self.start_button.setStyleSheet("background-color: green; color: #1e2a38;")
        self.stop_button.setStyleSheet("background-color: red; color: #1e2a38;")

<<<<<<< Updated upstream
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        layout.addLayout(buttons_layout, 2, 1)
        # Performance Stats Section (Positioned lower in the layout)
        self.create_performance_stats(layout)

        self.setLayout(layout)

    def create_qr_code_section(self, layout):
        """Create the QR code section."""
        qr_group = QGroupBox("Account Information")
        qr_group.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #f0f0f0;")
        qr_layout = QVBoxLayout(qr_group)

        # QR Code Generation
        qr = QRCode(version=1, box_size=10, border=2)
        qr.add_data(self.controller.account_id)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")
        qr_img.save("temp_qr.png")

=======
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # === HEADER ===
        header = self._create_header()
        main_layout.addLayout(header)

        # === TOP METRICS ROW ===
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(10)
        self.metric_cards = {
            "balance": _create_metric_card("💰 Balance", "$0.00", "USD", self.style),
            "trades": _create_metric_card("📊 Total Trades", "0", "trades", self.style),
            "profit": _create_metric_card("📈 Profit", "$0.00", "USD", self.style),
            "winrate": _create_metric_card("🎯 Win Rate", "0%", "", self.style),
        }
        for card in self.metric_cards.values():
            metrics_layout.addWidget(card)
        main_layout.addLayout(metrics_layout)

        # === MIDDLE SECTION: Message + Status + Chart ===
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(10)
        
        # Left: QR + Message
        left_column = QVBoxLayout()
        left_column.setSpacing(8)
        self.qr_group = self._create_qr_section(self._get_account_id())
        self.msg_group = self._create_message_panel()
        left_column.addWidget(self.qr_group)
        left_column.addWidget(self.msg_group)
        left_column.addStretch()
        
        # Right: Chart
        self.chart_group = self._create_chart_panel()
        
        middle_layout.addLayout(left_column)
        middle_layout.addWidget(self.chart_group, 1)
        main_layout.addLayout(middle_layout, 1)

        # === BOTTOM: Activity Log ===
        activity_section = self._create_activity_log()
        main_layout.addWidget(activity_section, 1)

        # === FOOTER: Controls ===
        main_layout.addLayout(self._create_controls())

        self.setLayout(main_layout)

    def _create_header(self) -> QHBoxLayout:
        """Create header with title and time."""
        header_layout = QHBoxLayout()
        
        title = QLabel("StellarBot Pro Dashboard")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color:{self.style.accent_blue};")
        
        self.lbl_time = QLabel(self._now())
        self.lbl_time.setAlignment(QtCore.Qt.AlignRight)
        time_font = QFont()
        time_font.setPointSize(11)
        self.lbl_time.setFont(time_font)
        self.lbl_time.setStyleSheet(f"color:{self.style.text_secondary};")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_time)
        
        return header_layout
    
    def _get_account_id(self) -> str:
        """Safely retrieve account ID."""
        return getattr(self.controller, "account_id", "N/A")

    # ------------------------------------------------------------------
    # 🧩 UI Sections
    # ------------------------------------------------------------------
    def _create_qr_section(self, data: str) -> QGroupBox:
        """Create QR code section with improved styling."""
        group = QGroupBox("📲 Account QR")
        group.setStyleSheet(
            f"""
            QGroupBox {{
                border: 1px solid {self.style.border_color};
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: {self.style.panel_bg};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: {self.style.text_secondary};
                font-weight: 600;
            }}
            """
        )
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
>>>>>>> Stashed changes
        qr_label = QLabel()
        qr_pixmap = QtGui.QPixmap("temp_qr.png").scaled(150, 150, QtCore.Qt.KeepAspectRatio)
        qr_label.setPixmap(qr_pixmap)
        qr_label.setAlignment(QtCore.Qt.AlignCenter)
<<<<<<< Updated upstream

        account_label = QLabel(f"Account ID: {self.controller.account_id}")
        account_label.setAlignment(QtCore.Qt.AlignCenter)
        account_label.setStyleSheet("font-size: 14px; font-weight: bold;")

        qr_layout.addWidget(account_label)
        qr_layout.addWidget(qr_label)
        layout.addWidget(qr_group, 0,1)

    def create_black_canvas(self, layout):
        """Create the black canvas section for server messages."""
        canvas_group = QGroupBox("Server Messages")

        canvas_group.setStyleSheet("background-color: black; color: white; font-size: 14px;")
        canvas_layout = QVBoxLayout(canvas_group)
        canvas_layout.setAlignment(QtCore.Qt.AlignTop)

        for key in ['status', 'info', 'message', 'error']:
            label = QLabel(self.controller.server_msg.get(key, ""))
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("font-size: 12px;")
            canvas_layout.addWidget(label)
        layout.addWidget(canvas_group , 1, 1)

    def create_performance_stats(self, layout_):
        """Create a section to show performance stats such as total trades, profit, and win rate."""
        stats_group = QGroupBox("Performance Stats")
        stats_group.setStyleSheet("font-size: 16px; font-weight: bold; background-color: green; color: white;")
        stats_layout = QVBoxLayout(stats_group)

        for stat in ["Total Trades", "Profit", "Win Rate"]:
            label_ = QLabel(f"{stat}: 0")
            label_.setObjectName(stat)
            stats_layout.addWidget(label_)


        layout_.addWidget(stats_group,  1, 2)

=======
        
        text = QLabel("Scan to send funds")
        text.setAlignment(QtCore.Qt.AlignCenter)
        text.setStyleSheet(f"color: {self.style.text_secondary}; font-size: 11px;")
        
        layout.addWidget(qr_label)
        layout.addWidget(text)
        group.setLayout(layout)
        return group

    def _create_message_panel(self) -> QGroupBox:
        """Create consolidated status panel with improved design."""
        group = QGroupBox("🤖 Bot Status")
        group.setStyleSheet(
            f"""
            QGroupBox {{
                border: 1px solid {self.style.border_color};
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: {self.style.panel_bg};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: {self.style.text_secondary};
                font-weight: 600;
            }}
            """
        )
        layout = QVBoxLayout(spacing=10)
        
        self.lbl_status = QLabel("Status: ⏹ STOPPED")
        self.lbl_status.setStyleSheet(f"font-size:13px; font-weight:600; color: {self.style.text_primary};")
        layout.addWidget(self.lbl_status)
        
        self.lbl_message = QLabel("Ready for trading")
        self.lbl_message.setStyleSheet(f"font-size:12px; color:{self.style.accent_blue};")
        self.lbl_message.setWordWrap(True)
        layout.addWidget(self.lbl_message)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(6)
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: none;
                background: {self.style.panel_alt};
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {self.style.accent_green};
                border-radius: 3px;
            }}
            """
        )
        layout.addWidget(self.progress_bar)
        
        layout.addStretch(1)
        group.setLayout(layout)
        return group

    def _create_activity_log(self) -> QGroupBox:
        """Create trading activity log with recent trades."""
        group = QGroupBox("📋 Recent Activity")
        group.setStyleSheet(
            f"""
            QGroupBox {{
                border: 1px solid {self.style.border_color};
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: {self.style.panel_bg};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: {self.style.text_secondary};
                font-weight: 600;
            }}
            """
        )
        layout = QVBoxLayout()
        
        self.activity_table = QTableWidget(0, 5)
        self.activity_table.setHorizontalHeaderLabels(["Time", "Type", "Asset", "Amount", "Status"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.activity_table.setMaximumHeight(150)
        self.activity_table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {self.style.panel_alt};
                alternate-background-color: {self.style.bg_dark};
                border: none;
                gridline-color: {self.style.border_color};
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {self.style.panel_bg};
                color: {self.style.text_secondary};
                padding: 5px;
                border: none;
                font-weight: 600;
                font-size: 11px;
            }}
            """
        )
        self.activity_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.activity_table)
        group.setLayout(layout)
        return group

    def _create_chart_panel(self) -> QGroupBox:
        """Create profit trend chart with improved styling."""
        group = QGroupBox("📈 Profit Trend (24h)")
        group.setStyleSheet(
            f"""
            QGroupBox {{
                border: 1px solid {self.style.border_color};
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: {self.style.panel_bg};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: {self.style.text_secondary};
                font-weight: 600;
            }}
            """
        )
        layout = QVBoxLayout()

        chart = QtCharts.QChart()
        chart.addSeries(self.performance_series)
        chart.createDefaultAxes()
        
        # Style axes
        chart.axisX(self.performance_series).setTitleText("Updates")
        chart.axisY(self.performance_series).setTitleText("Profit (USD)")
        chart.axisX(self.performance_series).setLabelsColor(QColor(self.style.text_secondary))
        chart.axisY(self.performance_series).setLabelsColor(QColor(self.style.text_secondary))
        chart.setBackgroundBrush(QtGui.QColor(self.style.panel_alt))
        chart.setTitleBrush(QtGui.QBrush(QtGui.QColor(self.style.accent_green)))
        chart.legend().hide()
        
        # Style the series
        self.performance_series.setColor(QColor(self.style.accent_green))
        
        self.chart_view = QtCharts.QChartView(chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(250)
        layout.addWidget(self.chart_view)
        group.setLayout(layout)
        return group

    def _create_controls(self) -> QHBoxLayout:
        """Create control buttons with enhanced styling."""
        layout = QHBoxLayout(spacing=10)
        
        self.btn_start = QPushButton("▶ Start Bot")
        self.btn_stop = QPushButton("⏹ Stop Bot")
        self.btn_backtest = QPushButton("🧠 Run Backtest")
        self.btn_clear_log = QPushButton("🗑️ Clear Log")
        
        _apply_button_style(self.btn_start, self.style.accent_green)
        _apply_button_style(self.btn_stop, self.style.accent_red)
        _apply_button_style(self.btn_backtest, self.style.accent_blue)
        _apply_button_style(self.btn_clear_log, self.style.accent_yellow)
        
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_backtest)
        layout.addWidget(self.btn_clear_log)
        layout.addStretch(1)
        return layout

    # ------------------------------------------------------------------
    # ⚙️ Signals & Timers
    # ------------------------------------------------------------------
    def _connect_signals(self):
        self.btn_start.clicked.connect(self.start_bot)
        self.btn_stop.clicked.connect(self.stop_bot)
        self.btn_backtest.clicked.connect(self.on_backtest_clicked)
        self.btn_clear_log.clicked.connect(self.clear_activity_log)
        self.update_signal.connect(self._refresh_dashboard)
>>>>>>> Stashed changes

    def update_dashboard(self):
        """Update the dashboard with live data."""
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_live_data)
        self.timer.start(1000)  # Update every second

    def update_live_data(self):
        """Fetch and display live data on the dashboard."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = self.controller.server_msg.get('status', 'Unknown')
        info = self.controller.server_msg.get('info', 'No info available')
        message = self.controller.server_msg.get('message', 'No message')

        # Update Performance Stats
        self.update_performance_stats()

    def update_performance_stats(self):
        """Update the performance stats section with live data."""
        stats = self.controller.server_msg.get('performance_stats', {})
        for stat, value in stats.items():
            label = self.findChild(QLabel, stat)
            if label:
                label.setText(f"{stat}: {value}")

    def start_bot(self):
        """Start the bot."""
        self.bot.start()

    def stop_bot(self):
        """Stop the bot."""
        self.bot.stop()


<<<<<<< Updated upstream
    def update_button_state(self, start_enabled, stop_enabled):
        """Enable or disable control buttons."""
        self.start_button.setEnabled(start_enabled)
        self.stop_button.setEnabled(stop_enabled)
        if start_enabled:
            self.controller.server_msg['status'] = 'STOP'
=======
    # ------------------------------------------------------------------
    # 🔄 Updates & Chart
    # ------------------------------------------------------------------
    def _fetch_updates(self):
        msg = getattr(self.controller, "server_msg", {}) or {}
        msg["time"] = self._now()
        self.update_signal.emit(msg)

    def _refresh_dashboard(self, msg: dict):
        """Refresh all dashboard metrics and displays."""
        # Update time
        self.lbl_time.setText(msg.get("time", self._now()))
        
        # Update status
        status = msg.get('status', 'Unknown')
        error = msg.get('error', None)
        status_icon = "🟢" if status == "RUNNING" else "⏹"
        if error:
            self.lbl_status.setText(f"Status: {status_icon} {status} | Error: {error}")
            self.lbl_status.setStyleSheet(f"font-size:13px; font-weight:600; color: {self.style.accent_red};")
        else:
            self.lbl_status.setText(f"Status: {status_icon} {status}")
            self.lbl_status.setStyleSheet(f"font-size:13px; font-weight:600; color: {self.style.accent_green};")
        
        self.lbl_message.setText(msg.get('message', 'Ready for trading'))

        # Update performance stats with metric cards
        stats = msg.get("performance_stats", {})
        self._update_metric_cards(stats)

        # Update chart
        profit = stats.get("Profit (USD)", 0)
        self._update_chart(float(profit))

    def _update_metric_cards(self, stats: dict):
        """Update metric card displays with formatted values."""
        # Balance
        balance = stats.get("Balance", 0)
        self.metric_cards["balance"].findChildren(QLabel)[0].setText(f"${float(balance):,.2f}")
        
        # Total Trades
        trades = stats.get("Total Trades", 0)
        self.metric_cards["trades"].findChildren(QLabel)[0].setText(str(int(trades)))
        
        # Profit
        profit = stats.get("Profit (USD)", 0)
        profit_label = self.metric_cards["profit"].findChildren(QLabel)[0]
        profit_label.setText(f"${float(profit):,.2f}")
        # Color based on profit/loss
        color = self.style.accent_green if float(profit) >= 0 else self.style.accent_red
        profit_label.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 700;")
        
        # Win Rate
        winrate = stats.get("Win Rate (%)", 0)
        self.metric_cards["winrate"].findChildren(QLabel)[0].setText(f"{float(winrate):.1f}%")

    def _update_chart(self, value: float):
        """Append live profit to chart."""
        if len(self.performance_points) > 100:
            self.performance_points.pop(0)
        self.performance_points.append(value)
        self.performance_series.clear()
        for i, val in enumerate(self.performance_points):
            self.performance_series.append(i, val)
    
    def add_activity_log_entry(self, time: str, activity_type: str, asset: str, amount: str, status: str):
        """Add entry to activity log table."""
        row = self.activity_table.rowCount()
        self.activity_table.insertRow(row)
        
        items = [
            QTableWidgetItem(time),
            QTableWidgetItem(activity_type),
            QTableWidgetItem(asset),
            QTableWidgetItem(amount),
            QTableWidgetItem(status)
        ]
        
        # Color code status
        status_color = self.style.accent_green if status == "Success" else (self.style.accent_yellow if status == "Pending" else self.style.accent_red)
        
        for col, item in enumerate(items):
            item.setStyleSheet(f"color: {self.style.text_primary};")
            if col == 4:  # Status column
                item.setStyleSheet(f"color: {status_color}; font-weight: 600;")
            self.activity_table.setItem(row, col, item)
        
        # Keep only last 50 entries
        while self.activity_table.rowCount() > 50:
            self.activity_table.removeRow(0)
        
        # Scroll to bottom
        self.activity_table.scrollToBottom()
    
    def clear_activity_log(self):
        """Clear the activity log."""
        self.activity_table.setRowCount(0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _update_message(self, text: str, error: bool = False):
        """Update message display with appropriate color."""
        color = self.style.accent_red if error else self.style.accent_green
        self.lbl_message.setStyleSheet(f"color:{color}; font-weight:600; padding:3px;")
        self.lbl_message.setText(text)

    def _on_bot_status(self, text: str):
        self.lbl_status.setText(f"Status: {text}")
        self._update_message(text)
        self.progress_bar.setVisible("Starting" in text)

    def _on_bot_error(self, text: str):
        self.lbl_status.setText(f"Status: Error - {text}")
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
    
    # ------------------------------------------------------------------
    # 🧹 Cleanup & Resource Management
    # ------------------------------------------------------------------
    def cleanup(self):
        """Ensure all threads are properly stopped before closing"""
        # Stop the update timer
        if self.timer:
            self.timer.stop()
        
        # Gracefully stop bot if running
        if self._bot_worker and self._bot_worker.running:
            self._bot_worker.running = False
            try:
                if self.bot and hasattr(self.bot, 'stop'):
                    self.bot.stop()
            except Exception:
                pass
        
        # Wait for thread to finish
        if self._bot_thread and self._bot_thread.isRunning():
            self._bot_thread.quit()
            self._bot_thread.wait(5000)  # Wait up to 5 seconds
    
    def closeEvent(self, event):
        """Handle window close event with proper cleanup"""
        self.cleanup()
        super().closeEvent(event)
    
    def __del__(self):
        """Destructor to ensure cleanup on garbage collection"""
        try:
            self.cleanup()
        except Exception:
            pass
>>>>>>> Stashed changes
