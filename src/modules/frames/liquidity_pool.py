from PySide6.QtWidgets import (QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHBoxLayout,
                             QLineEdit, QFrame)


class LiquidityPool(QFrame):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.liquidity_df= controller.liquidity_df  # Replace it with actual data

        self.setWindowTitle("Liquidity Pool")
        self.setGeometry(10, 10, 1530, 780)  # Adjusted size for additional columns

        # Main layout
        main_layout = QVBoxLayout()

        # Header section with 'Liquidity Pool' and 'My Position'
        header_layout = QHBoxLayout()

        self.liquidity_label = QLabel("Liquidity Pool")
        self.position_label = QLabel("My Position")
        self.updated_on_label = QLabel("Updated on")

        # Styling headers
        for label in (self.liquidity_label, self.position_label, self.updated_on_label):

            header_layout.addWidget(label)

        main_layout.addLayout(header_layout)


        # Table Section
        self.table = QTableWidget(self)
        self.table.setRowCount(10)  # Placeholder rows
        self.table.setColumnCount(17)  # Total columns for your data structure

        # Set headers
        self.table.setHorizontalHeaderLabels([
            "Pair", "Pool ID", "Total Shares", "My Shares", "Invested A", "Open Profit A",
            "% of Asset A Profit", "Invested B", "Open Profit B", "% of Asset B Profit",
            "% of General Open Profit", "Asset A Code", "Asset A Issuer", "Asset A Amount",
            "Asset B Code", "Asset B Issuer", "Asset B Amount"
        ])

        # Adding placeholder data to rows
        for row in range(10):
            for col in range(17):
                self.table.setItem(row, col, QTableWidgetItem(""))



        # Add table to layout
        main_layout.addWidget(self.table)

        # Account Address Section (Optional)
        self.address_label = QLabel("Account Address")
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Enter your wallet address here")

        # Styling Address Section

        self.address_input.setStyleSheet("""
            border: 1px solid #999; 
            border-radius: 5px; 
            padding: 5px; 
            font-size: 12px;
        """)

        # Adding Address Section to Layout
        main_layout.addWidget(self.address_label)
        main_layout.addWidget(self.address_input)


        # Set main layout
        self.setLayout(main_layout)

