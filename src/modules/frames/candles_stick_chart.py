<<<<<<< Updated upstream
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from matplotlib import pyplot as plt


def generate_random_xlm_data(start_date, num_days=100):
 date_range = pd.date_range(start=start_date, periods=num_days, freq='D')
 open_price = 0.2
=======
"""
📈 TradingView-Compatible Stellar DEX Candlestick Chart
Meets professional trading chart standards with drawing tools and indicators
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QLabel, QLineEdit, QMessageBox,
    QComboBox, QCheckBox, QWidget
)
from stellar_sdk import Server, Asset, TransactionBuilder, Network
import numpy as np


class DexTradingChart(QFrame):
    """📈 TradingView-Compatible Stellar DEX Candlestick Chart with Drawing Tools & Indicators"""
>>>>>>> Stashed changes

 data=pd.DataFrame(columns=[ 'Open', 'High', 'Low', 'Close', 'Volume'])

 for date in date_range:
    price_change = np.random.normal(loc=0, scale=0.01)
    open_price = open_price + price_change
    open_price = max(open_price, 0.05)
    high_price = open_price + np.random.uniform(0.01, 0.03)
    low_price = open_price - np.random.uniform(0.01, 0.03)
    close_price = open_price + np.random.normal(loc=0, scale=0.005)
    volume = np.random.randint(100000, 500000)
    data['TimeStamp'] = date
    data['Open'] = open_price
    data['High'] = high_price
    data['Low'] = low_price
    data['Close'] = close_price
    data['Volume'] = volume

 return data


class CandlestickChart(QFrame):
    def __init__(self, parent=None, controller=None, df=None):
        super().__init__(parent)
        self.visible_data = generate_random_xlm_data(start_date="2022-01-01")
        self.size_entry = 6
        self.controller = controller

<<<<<<< Updated upstream
        if df is None:
            print("No data provided. Generating random XLM/USDT data...")
            df = self.visible_data
            self.df = df
        self.fig = plt.figure(figsize=(5, 3))
        self.df["Date"] = pd.to_datetime(self.df.index)
        self.df.dropna(inplace=True)
        self.df.fillna(method='ffill', inplace=True)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.fig = plt.figure(figsize=(5, 3))
        self.setup_chart()
        self.zoom_level = 50
        self.current_index = 0
=======
        # Assets
        self.base_asset = Asset.native()  # XLM
        self.counter_asset = Asset("USDC", "GDMTVHLWJTHSUDMZVVMXXH6VJHA2ZV3HNG5LYNAZ6RTWB7GISM6PGTUV")

        # Chart data
        self.df = pd.DataFrame()
        self.fig = None
        self.web_view = None
        
        # Drawing tools state
        self.drawing_mode = None
        self.drawing_points = []
        self.indicators_enabled = {"EMA20": True, "SMA50": True, "RSI": False}
>>>>>>> Stashed changes

        self.setup_ui()

<<<<<<< Updated upstream
    def setup_ui(self):
=======
    # ==================================================================
    # 🧱 UI SETUP
    # ==================================================================
    def _init_ui(self):
        """Initialize UI with professional TradingView-style toolbar and chart container"""
>>>>>>> Stashed changes
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ============================================================
        # Professional toolbar with dark theme
        # ============================================================
        toolbar = QHBoxLayout()
<<<<<<< Updated upstream
        layout.addLayout(toolbar)

        self.add_button(toolbar, "Save Chart", self.save_chart())
        # self.add_button(toolbar, "Buy", self.buy)
        # self.add_button(toolbar, "Sell", self.sell)
        # self.add_label_input(toolbar, "Size:", self.size_entry)
        # self.add_button(toolbar, "Zoom In", self.zoom_in)
        # self.add_button(toolbar, "Zoom Out", self.zoom_out)
        # self.add_button(toolbar, "Previous", self.prev_data)
        # self.add_button(toolbar, "Next", self.next_data)

        self.create_candlestick_chart()

    def create_candlestick_chart(self):
        self.fig, self.ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        self.ax_candle = self.ax[0]
        self.ax_vol = self.ax[1]
        self.fig.patch.set_facecolor('white')



    def add_button(self, toolbar, param, sell):
        button = QPushButton(param)
        button.clicked.connect(sell)
        toolbar.addWidget(button)
        pass

    def setup_chart(self):
        self.fig.autofmt_xdate()
        self.ax.grid(True, color="lightgray", alpha=0.5)
        self.ax_vol.grid(True, color="lightgray", alpha=0.5)
        self.ax.set_ylabel("Price")
        self.ax_vol.set_ylabel("Volume")
        self.ax.set_title("Candlestick Chart")
        self.ax_vol.set_ylabel("Volume")
        self.ax_vol.set_xlabel("Date")

    def save_chart(self):

            self.fig.savefig("chart.png", dpi=300)
            print("Chart saved as chart.png")

            return
=======
        toolbar.setSpacing(10)
        toolbar.setContentsMargins(12, 10, 12, 10)
        
        # Apply toolbar background
        toolbar_widget = QWidget()
        toolbar_widget.setStyleSheet(
            "background-color: #1F2937; border-bottom: 1px solid #374151;"
        )
        toolbar_widget.setLayout(toolbar)
        
        # Refresh and save buttons (with icons)
        self._add_button(toolbar, "🔄 Refresh Data", self._refresh_data, "#10B981")
        self._add_button(toolbar, "💾 Export Chart", self._save_chart, "#3B82F6")
        
        # Timeframe selector (TradingView style)
        timeframe_label = QLabel("📊 Timeframe:")
        timeframe_label.setStyleSheet("color: #D1D5DB; font-weight: 600; font-size: 12px;")
        toolbar.addWidget(timeframe_label)
        
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"])
        self.timeframe_combo.setCurrentText("5m")
        self.timeframe_combo.currentTextChanged.connect(self._on_timeframe_changed)
        self.timeframe_combo.setMaximumWidth(80)
        self.timeframe_combo.setStyleSheet(
            "QComboBox { background-color: #2F3545; color: #D1D5DB; border: 1px solid #374151; "
            "border-radius: 4px; padding: 4px 8px; font-weight: 600; } "
            "QComboBox::drop-down { border: none; } "
            "QComboBox::down-arrow { image: none; }"
        )
        toolbar.addWidget(self.timeframe_combo)
        
        toolbar.addSpacing(15)
        
        # Drawing tools section
        tools_label = QLabel("🖌️ Tools:")
        tools_label.setStyleSheet("color: #D1D5DB; font-weight: 600; font-size: 12px; margin-left: 10px;")
        toolbar.addWidget(tools_label)
        
        self._add_button(toolbar, "📏 Trendline", lambda: self._set_drawing_mode("trendline"), "#8B5CF6")
        self._add_button(toolbar, "📦 Channel", lambda: self._set_drawing_mode("channel"), "#EC4899")
        self._add_button(toolbar, "⬜ Rectangle", lambda: self._set_drawing_mode("rectangle"), "#F59E0B")
        self._add_button(toolbar, "🗑️ Clear", self._clear_drawings, "#EF4444")
        
        toolbar.addSpacing(15)
        
        # Indicators section
        indicators_label = QLabel("📈 Indicators:")
        indicators_label.setStyleSheet("color: #D1D5DB; font-weight: 600; font-size: 12px; margin-left: 10px;")
        toolbar.addWidget(indicators_label)
        
        self.ema_check = QCheckBox("EMA20")
        self.ema_check.setChecked(True)
        self.ema_check.stateChanged.connect(lambda: self._toggle_indicator("EMA20"))
        self.ema_check.setStyleSheet(
            "QCheckBox { color: #D1D5DB; font-weight: 600; } "
            "QCheckBox::indicator { width: 16px; height: 16px; }"
        )
        toolbar.addWidget(self.ema_check)
        
        self.sma_check = QCheckBox("SMA50")
        self.sma_check.setChecked(True)
        self.sma_check.stateChanged.connect(lambda: self._toggle_indicator("SMA50"))
        self.sma_check.setStyleSheet(
            "QCheckBox { color: #D1D5DB; font-weight: 600; } "
            "QCheckBox::indicator { width: 16px; height: 16px; }"
        )
        toolbar.addWidget(self.sma_check)
        
        self.rsi_check = QCheckBox("RSI")
        self.rsi_check.stateChanged.connect(lambda: self._toggle_indicator("RSI"))
        self.rsi_check.setStyleSheet(
            "QCheckBox { color: #D1D5DB; font-weight: 600; } "
            "QCheckBox::indicator { width: 16px; height: 16px; }"
        )
        toolbar.addWidget(self.rsi_check)
        
        toolbar.addStretch()
        
        layout.addWidget(toolbar_widget)
        
        # ============================================================
        # Trade controls (professional styling)
        # ============================================================
        trade_widget = QWidget()
        trade_widget.setStyleSheet(
            "background-color: #1F2937; border-bottom: 1px solid #374151; padding: 8px;"
        )
        trade_layout = QHBoxLayout(trade_widget)
        trade_layout.setSpacing(10)
        trade_layout.setContentsMargins(12, 8, 12, 8)
        
        # Amount input
        amount_label = QLabel("Amount (XLM):")
        amount_label.setStyleSheet("color: #9CA3AF; font-weight: 600; font-size: 11px;")
        trade_layout.addWidget(amount_label)
        
        self.amount_entry = QLineEdit()
        self.amount_entry.setPlaceholderText("0.0")
        self.amount_entry.setMaximumWidth(100)
        self.amount_entry.setStyleSheet(
            "QLineEdit { background-color: #0C0E13; color: #FFFFFF; border: 1px solid #374151; "
            "border-radius: 4px; padding: 6px; font-weight: 600; }"
        )
        trade_layout.addWidget(self.amount_entry)
        
        # Price input
        price_label = QLabel("Price (USDC):")
        price_label.setStyleSheet("color: #9CA3AF; font-weight: 600; font-size: 11px; margin-left: 10px;")
        trade_layout.addWidget(price_label)
        
        self.price_entry = QLineEdit()
        self.price_entry.setPlaceholderText("0.0")
        self.price_entry.setMaximumWidth(100)
        self.price_entry.setStyleSheet(
            "QLineEdit { background-color: #0C0E13; color: #FFFFFF; border: 1px solid #374151; "
            "border-radius: 4px; padding: 6px; font-weight: 600; }"
        )
        trade_layout.addWidget(self.price_entry)
        
        # Trade buttons
        self.buy_btn = QPushButton("🟢 BUY")
        self.buy_btn.clicked.connect(lambda: self._execute_trade("buy"))
        self.buy_btn.setMaximumWidth(100)
        self.buy_btn.setStyleSheet(
            "QPushButton { background-color: #26a69a; color: white; font-weight: 700; border: none; "
            "border-radius: 4px; padding: 8px; } "
            "QPushButton:hover { background-color: #2db8a7; } "
            "QPushButton:pressed { background-color: #1e8680; }"
        )
        trade_layout.addWidget(self.buy_btn)
        
        self.sell_btn = QPushButton("🔴 SELL")
        self.sell_btn.clicked.connect(lambda: self._execute_trade("sell"))
        self.sell_btn.setMaximumWidth(100)
        self.sell_btn.setStyleSheet(
            "QPushButton { background-color: #ef5350; color: white; font-weight: 700; border: none; "
            "border-radius: 4px; padding: 8px; } "
            "QPushButton:hover { background-color: #f16361; } "
            "QPushButton:pressed { background-color: #d93f3a; }"
        )
        trade_layout.addWidget(self.sell_btn)
        
        # Status label
        self.status_label = QLabel("🟢 Status: Ready to trade")
        self.status_label.setStyleSheet("color: #10B981; font-weight: 600; font-size: 12px; margin-left: 20px;")
        trade_layout.addWidget(self.status_label)
        trade_layout.addStretch()
        
        layout.addWidget(trade_widget)
        
        # ============================================================
        # Chart container (with professional background)
        # ============================================================
        self.chart_container = QWidget()
        self.chart_container.setStyleSheet("background-color: #0C0E13;")
        layout.addWidget(self.chart_container, 1)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #0C0E13;")

    def _add_button(self, layout, text, callback, color="#6366F1"):
        """Add styled button to toolbar"""
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setMaximumWidth(120)
        btn.setStyleSheet(
            f"QPushButton {{ background-color: {color}; color: white; font-weight: 700; border: none; "
            f"border-radius: 4px; padding: 6px 12px; font-size: 11px; }} "
            f"QPushButton:hover {{ background-color: #555; border: 1px solid {color}; }} "
            f"QPushButton:pressed {{ background-color: #333; }}"
        )
        layout.addWidget(btn)

    # ==================================================================
    # ⏱ AUTO REFRESH
    # ==================================================================
    def _setup_timer(self):
        """Setup 30-second auto-refresh timer"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh_data)
        self.timer.start(30000)  # 30 seconds

    # ==================================================================
    # 📊 FETCH TRADES + CALCULATE OHLCV
    # ==================================================================
    def _refresh_data(self):
        """Fetch trades from Stellar DEX and calculate OHLCV"""
        try:
            self.status_label.setText("📊 Fetching market data...")
            self.status_label.setStyleSheet("color: #FCD34D; font-weight: 600; font-size: 12px; margin-left: 20px;")
            timeframe = self.timeframe_combo.currentText()
            
            # Fetch trades from Stellar DEX
            # Note: Horizon API limit max is 200 per request
            trades_call = (
                self.server.trades()
                .for_asset_pair(self.base_asset, self.counter_asset)
                .order(desc=True)
                .limit(200)  # Horizon API maximum: 200 per page
                .call()
            )
            
            records = trades_call.get("_embedded", {}).get("records", [])
            if not records:
                self.status_label.setText("⚠️ No trade data available")
                self.status_label.setStyleSheet("color: #FCD34D; font-weight: 600; font-size: 12px; margin-left: 20px;")
                return

            # Build raw trades dataframe
            data = []
            for r in records:
                ts = pd.to_datetime(r["ledger_close_time"])
                price = float(r["price"]["n"]) / float(r["price"]["d"])
                amount = float(r["base_amount"])
                data.append({'timestamp': ts, 'price': price, 'volume': amount})

            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')

            # Resample to requested timeframe
            df_resampled = df.set_index('timestamp').resample(timeframe)
            ohlcv = pd.DataFrame({
                'open': df_resampled['price'].first(),
                'high': df_resampled['price'].max(),
                'low': df_resampled['price'].min(),
                'close': df_resampled['price'].last(),
                'volume': df_resampled['volume'].sum()
            })
            ohlcv = ohlcv.dropna()

            # Calculate technical indicators
            ohlcv['EMA20'] = self._calculate_ema(ohlcv['close'], 20)
            ohlcv['SMA50'] = ohlcv['close'].rolling(window=50).mean()
            ohlcv['RSI'] = self._calculate_rsi(ohlcv['close'], 14)

            self.df = ohlcv
            
            # Update status with market info
            if len(ohlcv) > 0:
                current_price = ohlcv['close'].iloc[-1]
                high = ohlcv['high'].iloc[-1]
                low = ohlcv['low'].iloc[-1]
                change = ohlcv['close'].iloc[-1] - ohlcv['open'].iloc[-1]
                change_pct = (change / ohlcv['open'].iloc[-1] * 100) if ohlcv['open'].iloc[-1] != 0 else 0
                
                change_icon = "📈" if change >= 0 else "📉"
                change_color = "#10B981" if change >= 0 else "#EF4444"
                
                self.status_label.setText(
                    f"🟢 {current_price:.4f} USDC | H: {high:.4f} | L: {low:.4f} | {change_icon} {change_pct:+.2f}% | {len(ohlcv)} candles"
                )
                self.status_label.setStyleSheet(f"color: {change_color}; font-weight: 600; font-size: 12px; margin-left: 20px;")
            else:
                self.status_label.setText("✅ Chart updated")
                self.status_label.setStyleSheet("color: #10B981; font-weight: 600; font-size: 12px; margin-left: 20px;")
            
            self._plot_chart()
        except Exception as e:
            self.status_label.setText(f"❌ Fetch error: {str(e)[:50]}")
            self.status_label.setStyleSheet("color: #EF4444; font-weight: 600; font-size: 12px; margin-left: 20px;")
            import traceback
            traceback.print_exc()

    # ==================================================================
    # 📈 TECHNICAL INDICATORS
    # ==================================================================
    @staticmethod
    def _calculate_ema(series, span):
        """Calculate Exponential Moving Average"""
        return series.ewm(span=span, adjust=False).mean()

    @staticmethod
    def _calculate_rsi(series, period=14):
        """Calculate Relative Strength Index (0-100)"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    # ==================================================================
    # 🧮 PLOT PROFESSIONAL TRADINGVIEW-STYLE CHART
    # ==================================================================
    def _plot_chart(self):
        """Render TradingView-compatible candlestick chart with Plotly"""
        if self.df.empty:
            self.status_label.setText("⚠️ No data to display")
            return

        try:
            # Create subplots: main chart (75%) + volume (25%)
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.12,
                row_heights=[0.75, 0.25],
                subplot_titles=("Price Action", "Volume"),
                specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
            )

            # ============================================================
            # Candlestick trace (professional TradingView styling)
            # ============================================================
            fig.add_trace(
                go.Candlestick(
                    x=self.df.index,
                    open=self.df['open'],
                    high=self.df['high'],
                    low=self.df['low'],
                    close=self.df['close'],
                    name='OHLC',
                    increasing_line_color='#26a69a',      # TradingView green
                    decreasing_line_color='#ef5350',      # TradingView red
                    increasing_fillcolor='#26a69a',
                    decreasing_fillcolor='#ef5350',
                    hovertext=[f"<b>OHLC</b><br>O: ${o:.4f}<br>H: ${h:.4f}<br>L: ${l:.4f}<br>C: ${c:.4f}"
                               for o, h, l, c in zip(self.df['open'], self.df['high'], self.df['low'], self.df['close'])],
                    hoverinfo="text",
                    line=dict(width=1)
                ),
                row=1, col=1
            )

            # ============================================================
            # Volume bars (TradingView color-coded style)
            # ============================================================
            colors = ['#26a69a' if self.df['close'].iloc[i] >= self.df['open'].iloc[i] else '#ef5350'
                      for i in range(len(self.df))]
            fig.add_trace(
                go.Bar(
                    x=self.df.index,
                    y=self.df['volume'],
                    marker_color=colors,
                    name='Volume',
                    hovertext=[f"<b>Volume</b><br>{v:,.0f} XLM" for v in self.df['volume']],
                    hoverinfo="text",
                    opacity=0.8,
                    showlegend=True
                ),
                row=2, col=1
            )

            # ============================================================
            # Technical Indicators
            # ============================================================
            if self.indicators_enabled.get("EMA20") and "EMA20" in self.df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=self.df.index,
                        y=self.df['EMA20'],
                        mode='lines',
                        name='EMA 20',
                        line=dict(color='#FF9500', width=2),
                        hovertemplate='<b>EMA 20</b><br>%{y:.4f}<extra></extra>',
                        opacity=0.9
                    ),
                    row=1, col=1
                )

            if self.indicators_enabled.get("SMA50") and "SMA50" in self.df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=self.df.index,
                        y=self.df['SMA50'],
                        mode='lines',
                        name='SMA 50',
                        line=dict(color='#00D9FF', width=2),
                        hovertemplate='<b>SMA 50</b><br>%{y:.4f}<extra></extra>',
                        opacity=0.85
                    ),
                    row=1, col=1
                )

            if self.indicators_enabled.get("RSI") and "RSI" in self.df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=self.df.index,
                        y=self.df['RSI'],
                        mode='lines',
                        name='RSI(14)',
                        line=dict(color='#9D4EDD', width=1.5),
                        hovertemplate='<b>RSI(14)</b><br>%{y:.1f}<extra></extra>',
                        opacity=0.9
                    ),
                    row=2, col=1
                )

            # ============================================================
            # Layout (Professional TradingView Theme)
            # ============================================================
            timeframe = self.timeframe_combo.currentText()
            fig.update_layout(
                title={
                    'text': f"<b>XLM/USDC</b> | {timeframe} | Stellar DEX Trading Chart",
                    'x': 0.02,
                    'xanchor': 'left',
                    'font': {'size': 16, 'color': '#FFFFFF'}
                },
                template="plotly_dark",
                xaxis_rangeslider_visible=False,
                hovermode='x unified',
                height=700,
                margin=dict(l=70, r=50, t=90, b=80),
                font=dict(size=12, family="Courier New, monospace", color='#D1D5DB'),
                plot_bgcolor='#131722',    # TradingView dark background
                paper_bgcolor='#0C0E13',   # Darker background
                legend=dict(
                    x=0.01,
                    y=0.99,
                    bgcolor='rgba(11, 14, 19, 0.8)',
                    bordercolor='#2F3545',
                    borderwidth=1,
                    font=dict(size=11)
                ),
                showlegend=True,
                dragmode='zoom'
            )

            # ============================================================
            # X-Axis Styling (Time axis)
            # ============================================================
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='#1F2937',
                showline=True,
                linewidth=1,
                linecolor='#2F3545',
                mirror=False,
                zeroline=False,
                row=2, col=1,
                tickfont=dict(size=10, color='#9CA3AF')
            )
            
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='#1F2937',
                showline=False,
                zeroline=False,
                showticklabels=False,
                row=1, col=1
            )

            # ============================================================
            # Y-Axis Styling (Price axis)
            # ============================================================
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='#1F2937',
                showline=True,
                linewidth=1,
                linecolor='#2F3545',
                title_text="<b>Price (USDC)</b>",
                title_font=dict(size=12, color='#D1D5DB'),
                tickfont=dict(size=10, color='#9CA3AF'),
                zeroline=False,
                row=1, col=1
            )

            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor='#1F2937',
                showline=True,
                linewidth=1,
                linecolor='#2F3545',
                title_text="<b>Volume</b>",
                title_font=dict(size=12, color='#D1D5DB'),
                tickfont=dict(size=10, color='#9CA3AF'),
                zeroline=False,
                row=2, col=1
            )

            self.fig = fig
            self._render_chart_to_ui()

        except Exception as e:
            self.status_label.setText(f"❌ Chart error: {str(e)[:50]}")
            import traceback
            traceback.print_exc()

    # ==================================================================
    # 🎨 RENDER PLOTLY TO PYSIDE6
    # ==================================================================
    def _render_chart_to_ui(self):
        """Render Plotly chart in QWebEngineView with dark theme"""
        if self.fig is None:
            return

        try:
            # Clear previous widget
            layout = self.chart_container.layout()
            if layout:
                while layout.count():
                    widget = layout.takeAt(0).widget()
                    if widget:
                        widget.deleteLater()
            else:
                layout = QVBoxLayout(self.chart_container)
                layout.setContentsMargins(0, 0, 0, 0)
                self.chart_container.setLayout(layout)

            # Create web view with Plotly chart
            self.web_view = QWebEngineView()
            
            # Generate HTML with enhanced styling
            html = self.fig.to_html(include_plotlyjs='cdn')
            
            # Inject dark theme CSS
            dark_theme_css = """
            <style>
                body {
                    background-color: #0C0E13;
                    color: #D1D5DB;
                    font-family: 'Courier New', monospace;
                    margin: 0;
                    padding: 0;
                }
                .plotly-graph-div {
                    background-color: #0C0E13 !important;
                }
                .modebar-btn {
                    background-color: #1F2937;
                    border-radius: 4px;
                }
                .modebar-btn:hover {
                    background-color: #374151;
                }
            </style>
            """
            
            # Insert CSS into HTML
            html = html.replace('</head>', dark_theme_css + '</head>')
            
            self.web_view.setHtml(html)
            self.web_view.setStyleSheet("border: none; background-color: #0C0E13;")
            
            layout.addWidget(self.web_view)
            self.status_label.setStyleSheet("color: #10B981; font-weight: 600; font-size: 12px; margin-left: 20px;")
        except Exception as e:
            self.status_label.setText(f"❌ Render error: {str(e)}")
            self.status_label.setStyleSheet("color: #EF4444; font-weight: 600; font-size: 12px; margin-left: 20px;")
            # Fallback: save HTML file
            if self.fig:
                self.fig.write_html("stellar_dex_chart_fallback.html")

    # ==================================================================
    # 🎯 DRAWING TOOLS
    # ==================================================================
    def _set_drawing_mode(self, mode):
        """Toggle drawing mode (trendline, channel, rectangle)"""
        self.drawing_mode = mode if self.drawing_mode != mode else None
        self.drawing_points = []
        status = f"✏️ {mode.upper()} mode active" if self.drawing_mode else "✏️ Drawing OFF"
        self.status_label.setText(status)

    def _clear_drawings(self):
        """Clear all drawing annotations"""
        self.drawing_points = []
        self._plot_chart()
        self.status_label.setText("✅ Drawings cleared")

    def _toggle_indicator(self, indicator_name):
        """Toggle technical indicator visibility"""
        if indicator_name == "EMA20":
            self.indicators_enabled["EMA20"] = self.ema_check.isChecked()
        elif indicator_name == "SMA50":
            self.indicators_enabled["SMA50"] = self.sma_check.isChecked()
        elif indicator_name == "RSI":
            self.indicators_enabled["RSI"] = self.rsi_check.isChecked()
        self._plot_chart()

    def _on_timeframe_changed(self):
        """Handle timeframe selector change"""
        self._refresh_data()

    # ==================================================================
    # 💱 TRADING EXECUTION
    # ==================================================================
    def _execute_trade(self, side):
        """Execute buy or sell order on Stellar DEX"""
        try:
            amount = self.amount_entry.text().strip()
            price = self.price_entry.text().strip()
            
            if not amount or not price:
                self.status_label.setText("⚠️ Enter amount and price to trade")
                self.status_label.setStyleSheet("color: #FCD34D; font-weight: 600; font-size: 12px; margin-left: 20px;")
                QMessageBox.warning(self, "Input Error", "Please enter amount and price")
                return

            amount = float(amount)
            price = float(price)

            # Load account and build transaction
            account = self.server.load_account(self.bot.keypair.public_key)
            tx_builder = TransactionBuilder(
                source_account=account,
                network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
                base_fee=100
            )

            if side == "buy":
                tx_builder.append_manage_buy_offer_op(
                    selling=self.counter_asset,
                    buying=self.base_asset,
                    amount=str(amount),
                    price=str(price),
                )
                action = "BUY"
                action_color = "#26a69a"
            else:
                tx_builder.append_manage_sell_offer_op(
                    selling=self.base_asset,
                    buying=self.counter_asset,
                    amount=str(amount),
                    price=str(price),
                )
                action = "SELL"
                action_color = "#ef5350"

            tx = tx_builder.set_timeout(30).build()
            tx.sign(self.bot.keypair)
            resp = self.server.submit_transaction(tx)

            hash_id = resp.get('hash', 'Unknown')
            
            # Update status
            self.status_label.setText(f"✅ {action} {amount} XLM @ {price} USDC | Hash: {hash_id[:16]}...")
            self.status_label.setStyleSheet(f"color: {action_color}; font-weight: 600; font-size: 12px; margin-left: 20px;")
            
            QMessageBox.information(
                self, "Trade Executed",
                f"✅ {action} order submitted!\n\nAmount: {amount} XLM\nPrice: {price} USDC\n\nHash: {hash_id}"
            )
            self._refresh_data()
        except ValueError:
            self.status_label.setText("❌ Invalid amount or price")
            self.status_label.setStyleSheet("color: #EF4444; font-weight: 600; font-size: 12px; margin-left: 20px;")
            QMessageBox.warning(self, "Invalid Input", "Amount and price must be valid numbers")
        except Exception as e:
            self.status_label.setText(f"❌ Trade failed: {str(e)[:40]}")
            self.status_label.setStyleSheet("color: #EF4444; font-weight: 600; font-size: 12px; margin-left: 20px;")
            QMessageBox.critical(self, "Trade Error", f"Failed to submit order:\n{str(e)}")

    # ==================================================================
    # 💾 SAVE CHART
    # ==================================================================
    def _save_chart(self):
        """Save chart as interactive HTML"""
        try:
            if self.fig:
                filename = "stellar_dex_trading_chart.html"
                self.fig.write_html(filename)
                self.status_label.setText(f"💾 Chart saved to {filename}")
                self.status_label.setStyleSheet("color: #3B82F6; font-weight: 600; font-size: 12px; margin-left: 20px;")
                QMessageBox.information(self, "Success", f"Chart saved to:\n{filename}")
            else:
                self.status_label.setText("⚠️ No chart to save")
                self.status_label.setStyleSheet("color: #FCD34D; font-weight: 600; font-size: 12px; margin-left: 20px;")
        except Exception as e:
            self.status_label.setText(f"❌ Save failed: {str(e)[:40]}")
            self.status_label.setStyleSheet("color: #EF4444; font-weight: 600; font-size: 12px; margin-left: 20px;")
            QMessageBox.critical(self, "Error", f"Failed to save chart:\n{str(e)}")
>>>>>>> Stashed changes
