from PyQt5.QtWidgets import QFrame, QLabel, QLineEdit, QVBoxLayout, QGridLayout

class AccountOverview(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Account Overview widget."""
        super().__init__(parent)
        self.controller = controller

        # Set the main layout for the widget
        main_layout = QVBoxLayout(self)

        self.account_details = self.controller.account_details # Fetch account details from the bot


        # Create and add the Account Overview section
        account_overview_frame = self.create_section("Account Overview")
        self.populate_account_overview(account_overview_frame)
        main_layout.addWidget(account_overview_frame)
        main_layout.addStretch(1)

        # Create and add the Financial Summary section
        financial_summary_frame = self.create_section("Balances Overview")
        self.populate_balances(financial_summary_frame)
        main_layout.addWidget(financial_summary_frame)

    def create_section(self, title):
        """Create a styled frame section with a title."""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        title_label = QLabel(title, frame)
        layout.addWidget(title_label)
        frame.setLayout(layout)
        return frame

    def populate_account_overview(self, frame):
        """Populate the Account Overview section with account details."""
        layout = QGridLayout(frame)
        account_details = self.controller.account_details # Fetch account details from the bot

        # Define account details fields
        fields = [
            ("Account ID", account_details.get("account_id", "")),
            ("Sequence", account_details.get("sequence", "")),
            ("Subentries", account_details.get("subentry_count", "")),
            ("Last Modified Time", account_details.get("last_modified_time", "")),
            ("Flags", account_details.get("flags", "")),
            ("Home Domain", account_details.get("home_domain", "")),
            ("Memo Type", account_details.get("memo_type", "")),
            ("Memo", account_details.get("memo", ""))
        ]

        # Add labels and values to the layout
        for row, (label_text, value) in enumerate(fields):
            label = QLabel(f"{label_text}:", frame)
            label.setStyleSheet("color: white;")
            entry = QLineEdit(frame)
            entry.setText(value)
            entry.setReadOnly(True)
            layout.addWidget(label, row, 0)
            layout.addWidget(entry, row, 1)

        # Handle complex fields (like thresholds, signers, and sponsorship)
        self.populate_complex_fields(layout, "Thresholds", account_details.get("thresholds", {}), len(fields))
        self.populate_complex_fields(layout, "Signers", account_details.get("signers", []), len(fields) + 1)
        self.populate_complex_fields(layout, "Sponsorship", account_details.get("sponsorship", {}), len(fields) + 2)

        frame.setLayout(layout)

    def populate_complex_fields(self, layout, label, value, row):
        """Handle complex fields like thresholds, signers, and sponsorship."""
        label_widget = QLabel(f"{label}:", self)
        label_widget.setStyleSheet("color: white;")
        layout.addWidget(label_widget, row, 0)

        value_widget = QLineEdit(self)
        value_widget.setText(str(value))
        value_widget.setReadOnly(True)
        layout.addWidget(value_widget, row, 1)

    def populate_balances(self, frame):
        """Populate the Balances Overview section with asset balances."""
        layout = QGridLayout(frame)

        balances = self.account_details.get("balances", [])

        # Add table headers
        headers = ["Asset Code", "Balance", "Type"]
        for col, header in enumerate(headers):
            header_label = QLabel(header, frame)
            header_label.setStyleSheet("color: #003366; font-size: 12px; font-weight: bold;")
            layout.addWidget(header_label, 0, col)

        # Populate balances
        for row, balance in enumerate(balances, start=1):
            asset_code = balance.get("asset_code", "XLM")  # 'XLM' for native asset
            balance_value = balance.get("balance", "0")
            asset_type = balance.get("asset_type", "native")

            layout.addWidget(QLabel(asset_code, frame), row, 0)
            layout.addWidget(QLineEdit(balance_value, frame), row, 1)
            layout.addWidget(QLabel(asset_type, frame), row, 2)

        frame.setLayout(layout)
