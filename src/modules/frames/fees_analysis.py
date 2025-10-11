from PySide6.QtWidgets import QFrame, QLabel, QLineEdit, QVBoxLayout, QFormLayout
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt


def _create_title_label(text):
    """Helper function to create a title label."""
    label = QLabel(text)
    label.setFont(QFont("Arial", 16, QFont.Bold))
    label.setAlignment(Qt.AlignLeft)
    label.setStyleSheet("color: #2874A6; font-weight: bold;")  # QSS for title styling
    return label


class FeesAnalysis(QFrame):
    def __init__(self, parent=None, controller=None):
        """Initialize the Fee Analysis widget."""
        super().__init__(parent)
        self.controller = controller

        # Retrieve fee data from the controller
        self.fees_data =   {} # Assuming fees_stats is a property of the controller

        # Set up the layout and UI components
        self._initialize_ui()

    def _initialize_ui(self):
        """Set up the user interface for the Fee Analysis widget."""
        # Main layout
        main_layout = QVBoxLayout()

        # Add title
        title_label = _create_title_label("Fee Analysis")
        main_layout.addWidget(title_label)

        # Add a fee details form
        form_layout = self._create_fee_details_form()
        main_layout.addLayout(form_layout)

        # Set the layout for the widget
        self.setLayout(main_layout)

    def _create_fee_details_form(self):
        """Helper function to create a form layout with fee details."""
        form_layout = QFormLayout(self)

        # Extract relevant details from the fees_data
        fee_charged = self.fees_data.get('fee_charged', {})
        max_fee = self.fees_data.get('max_fee', {})

        # Add fields to the form layout
        form_layout.addRow("Last Ledger:", self._create_readonly_entry(self.fees_data.get('last_ledger', 'N/A')))
        form_layout.addRow("Base Fee (Last Ledger):", self._create_readonly_entry(self.fees_data.get('last_ledger_base_fee', 'N/A')))
        form_layout.addRow("Ledger Capacity Usage:", self._create_readonly_entry(self.fees_data.get('ledger_capacity_usage', 'N/A')))

        # Fee Charged Details
        form_layout.addRow("Fee Charged (Min):", self._create_readonly_entry(fee_charged.get('min', 'N/A')))
        form_layout.addRow("Fee Charged (Max):", self._create_readonly_entry(fee_charged.get('max', 'N/A')))
        form_layout.addRow("Fee Charged (Mode):", self._create_readonly_entry(fee_charged.get('mode', 'N/A')))
        form_layout.addRow("Fee Charged (P99):", self._create_readonly_entry(fee_charged.get('p99', 'N/A')))

        # Max Fee Details
        form_layout.addRow("Max Fee (Min):", self._create_readonly_entry(max_fee.get('min', 'N/A')))
        form_layout.addRow("Max Fee (Max):", self._create_readonly_entry(max_fee.get('max', 'N/A')))
        form_layout.addRow("Max Fee (Mode):", self._create_readonly_entry(max_fee.get('mode', 'N/A')))
        form_layout.addRow("Max Fee (P99):", self._create_readonly_entry(max_fee.get('p99', 'N/A')))

        return form_layout

    def _create_readonly_entry(self, value):
        """Helper function to create a read-only QLineEdit with a pre-filled value."""
        entry = QLineEdit(self)
        entry.setText(str(value))
        entry.setReadOnly(True)
        entry.setAlignment(Qt.AlignCenter)
        return entry



