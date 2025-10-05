from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame


class Payments(QFrame):
    """Display and auto-refresh Stellar payment history in a table."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.bot = getattr(controller, "bot", None)
        self.payments_table = None

        # Frame appearance
        self.setGeometry(100, 50, 1530, 780)
        self.setStyleSheet("""
            font-size: 16px;
            border: 1px solid #333;
            color: #eee;
            padding: 20px;
            background-color: #121212;
        """)

        # Build UI
        self.create_widgets()

        # Initialize update timer
        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self.update_payments_data)
        self.refresh_timer.start(60000)  # every 60 seconds

        # Load first batch of data
        self.update_payments_data()

    # ----------------------------------------------------------------------
    # UI CREATION
    # ----------------------------------------------------------------------
    def create_widgets(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Header label
        header = QtWidgets.QLabel("💸 Recent Payments (Auto-refresh every 60s)")
        header.setStyleSheet("font-size: 22px; font-weight: bold; color: #00ff99;")
        layout.addWidget(header, alignment=QtCore.Qt.AlignCenter)

        # Payments table
        self.payments_table = QtWidgets.QTableWidget()
        self.payments_table.setColumnCount(11)
        self.payments_table.setHorizontalHeaderLabels([
            "ID", "Account", "From", "To", "Amount", "Asset Type",
            "Asset Code", "Asset Issuer", "Created At", "Memo Type", "Memo"


        ])
        self.payments_table.setSortingEnabled(True)
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.horizontalHeader().setStretchLastSection(True)
        self.payments_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.payments_table)

        self.setLayout(layout)

    # ----------------------------------------------------------------------
    # DATA FETCH + UPDATE
    # ----------------------------------------------------------------------
    def update_payments_data(self):
        """Fetch and populate the payments table."""
        try:
            df = self.get_payments_data()
            if df is None or df.empty:
                self._show_no_data()
                return

            # Limit to 200 latest rows for performance
            df = df.head(200).copy()

            self.payments_table.setRowCount(len(df))

            for row_idx, row in enumerate(df.itertuples()):
                values = [
                    getattr(row, "id", "N/A"),
                    getattr(row, "account", "N/A"),
                    getattr(row, "from_", getattr(row, "from", "N/A")),  # handle reserved word 'from'
                    getattr(row, "to", "N/A"),
                    getattr(row, "amount", "N/A"),
                    getattr(row, "asset_type", "N/A"),
                    getattr(row, "asset_code", "N/A"),
                    getattr(row, "asset_issuer", "N/A"),
                    getattr(row, "created_at", "N/A")[:19],
                    getattr(row, "memo_type", "N/A"),
                    getattr(row, "memo", "N/A"),
                ]

                for col, value in enumerate(values):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    self.payments_table.setItem(row_idx, col, item)

                # Highlight asset type
                asset_type = getattr(row, "asset_type", "")
                if asset_type != "native":
                    self.payments_table.item(row_idx, 5).setBackground(QColor(40, 40, 60))

                # Color “Amount” cell
                try:
                    amt = float(getattr(row, "amount", 0))
                    color = QColor(0, 255, 100) if amt > 0 else QColor(255, 80, 80)
                    self.payments_table.item(row_idx, 4).setForeground(color)
                except ValueError:
                    pass

        except Exception as e:
            print(f"[Payments] Error updating data: {e}")

    def get_payments_data(self):
        """Return payment DataFrame from SmartBot if available."""
        try:
            if self.bot and hasattr(self.bot, "payments_df"):
                return self.bot.payments_df
        except Exception as e:
            print(f"[Payments] Error fetching payments data: {e}")
        return None

    # ----------------------------------------------------------------------
    # UTILITIES
    # ----------------------------------------------------------------------
    def _show_no_data(self):
        """Display placeholder when no payment data available."""
        self.payments_table.setRowCount(0)
        self.payments_table.setRowCount(1)
        item = QtWidgets.QTableWidgetItem("No payment records found.")
        item.setForeground(QColor("#888"))
        self.payments_table.setItem(0, 0, item)
        self.payments_table.setSpan(0, 0, 1, self.payments_table.columnCount())
