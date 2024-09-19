from PyQt5 import QtWidgets

from  modules.classes.settings_manager import SettingsManager

class SettingsPreferences(QtWidgets.QWidget):
    def __init__(self, parent=None, controller=None):
        """Initialize the Settings and Preferences widget."""
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(0, 0, 1530, 780)
        

        # Main layout for the widget
        layout = QtWidgets.QVBoxLayout(self)


        # Create the Back button
        back_button = QtWidgets.QPushButton("Back", self)
        back_button.clicked.connect(self.go_back)
        back_button.setStyleSheet("background-color: #2E2E2E; color: white; font-size: 12pt; font-weight: bold; border: none;")
        layout.addWidget(back_button)

        # Create the settings and preferences section
        self.create_widgets(layout)

        # Save the settings and preferences
        save_button = QtWidgets.QPushButton("Save", self)
        save_button.clicked.connect(self.save_settings)
        save_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 12pt; font-weight: bold; border: none;")
        layout.addWidget(save_button)
    def save_settings(self):
        
        """Save the settings and preferences."""
        # Save settings and preferences based on user selection
        for option, var in self.notification_vars.items():
            if var.isChecked():
                print(f"User selected {option} notification")
                # TODO: Implement logic to save user settings and preferences
               # SettingsManager.save_settings({"notification_options": [option for option, var in self.notification_vars.items() if var.isChecked()]})
    def go_back(self):
        """Navigate back to the main dashboard."""
        self.controller.show_frame('Home')

    def create_widgets(self, layout):
        """Create and arrange widgets for the settings and preferences section."""
        # Settings Frame
        settings_frame = QtWidgets.QFrame(self)
        settings_frame.setFixedSize(1500, 700)
        layout.addWidget(settings_frame)

        settings_layout = QtWidgets.QVBoxLayout(settings_frame)

        self._extracted_from_create_widgets_12(
            "Settings & Preferences",
            "font-size: 16pt; font-weight: bold;",
            settings_layout,
        )
        self._extracted_from_create_widgets_12(
            "Trade Notifications",
            "font-size: 14pt; font-weight: bold;",
            settings_layout,
        )
        notification_options = ["Email", "SMS", "In-App"]
        self.notification_vars = {}
        for option in notification_options:
            var = QtWidgets.QCheckBox(option, self)
            var.setStyleSheet("font-size: 12pt;")
            settings_layout.addWidget(var)
            self.notification_vars[option] = var

        self._extracted_from_create_widgets_12(
            "API Integrations",
            "font-size: 14pt; font-weight: bold;",
            settings_layout,
        )
        self.api_entry = QtWidgets.QLineEdit(self)
        self.api_entry.setPlaceholderText("Enter API Key")
        self.api_entry.setFixedWidth(400)
        settings_layout.addWidget(self.api_entry)

        self._extracted_from_create_widgets_12(
            "Automated Trading Bot Status",
            "font-size: 14pt; font-weight: bold;",
            settings_layout,
        )
        self.bot_status_combo = QtWidgets.QComboBox(self)
        self.bot_status_combo.addItems(["Running", "Stopped", "Paused"])
        self.bot_status_combo.setFixedWidth(250)
        settings_layout.addWidget(self.bot_status_combo)

        self._extracted_from_create_widgets_12(
            "Connected Algorithms",
            "font-size: 14pt; font-weight: bold;",
            settings_layout,
        )
        self.algo_stats_button = QtWidgets.QPushButton("View Performance Stats", self)
        self.algo_stats_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 12pt;")
        self.algo_stats_button.clicked.connect(self.show_algo_stats)
        settings_layout.addWidget(self.algo_stats_button)

    # TODO Rename this here and in `create_widgets`
    def _extracted_from_create_widgets_12(self, arg0, arg1, settings_layout):
        # Section Title
        settings_label = QtWidgets.QLabel(arg0, self)
        settings_label.setStyleSheet(arg1)
        settings_layout.addWidget(settings_label)

    def show_algo_stats(self):
        """Display a pop-up with algorithm performance statistics."""
        stats_window = QtWidgets.QDialog(self)
        stats_window.setWindowTitle("Algorithm Performance Stats")
        stats_window.setFixedSize(400, 300)
        
        layout = QtWidgets.QVBoxLayout(stats_window)

        # Example stats - replace with dynamic data
        algo_stats = [
            ("Algorithm 1", "50 trades", "65% Win Rate", "Net P/L: $1500"),
            ("Algorithm 2", "75 trades", "70% Win Rate", "Net P/L: $3000"),
            ("Algorithm 3", "40 trades", "60% Win Rate", "Net P/L: $1200")

        ]

        # Create a grid layout for the performance stats
        grid_layout = QtWidgets.QGridLayout()
        for i, (name, trades, win_rate, pl) in enumerate(algo_stats):
            grid_layout.addWidget(QtWidgets.QLabel(name, stats_window), i, 0)
            grid_layout.addWidget(QtWidgets.QLabel(trades, stats_window), i, 1)
            grid_layout.addWidget(QtWidgets.QLabel(win_rate, stats_window), i, 2)
            grid_layout.addWidget(QtWidgets.QLabel(pl, stats_window), i, 3)

        layout.addLayout(grid_layout)
        stats_window.exec_()
