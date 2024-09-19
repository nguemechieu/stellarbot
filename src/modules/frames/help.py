from PyQt5 import QtWidgets, QtCore

class Help(QtWidgets.QWidget):
    """Help Frame providing users with information and resources about the application."""

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.setGeometry(
            0, 0,1530,780
        )
        # Set up the layout for the help frame
        self.setWindowTitle("StellarBot - Help")
        layout = QtWidgets.QVBoxLayout(self)
        
        # Title label
        title_label = QtWidgets.QLabel("StellarBot Help & Resources", self)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("color: #003366; font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)

        # Introduction section
        intro_label = QtWidgets.QLabel(
            "Welcome to the StellarBot Help Center! Here you will find all the resources and "
            "information you need to get started, troubleshoot issues, and explore features."
        )
        intro_label.setStyleSheet("color: #333333; font-size: 16px;")
        intro_label.setWordWrap(True)
        layout.addWidget(intro_label)

        # Add help sections
        self.add_help_sections(layout)

        # Add contact information at the bottom
        contact_label = QtWidgets.QLabel(
            "For additional support, contact us at support@stellarbot.com or visit our "
            "[website](https://stellarbot.com)."
        )
        contact_label.setStyleSheet("color: #003366; font-size: 14px;")
        contact_label.setWordWrap(True)
        layout.addWidget(contact_label)


        #Go Back Button
        back_button = QtWidgets.QPushButton("Back", self)
        back_button.setStyleSheet("background-color: white; color: #1e2a38;")
        back_button.clicked.connect(self.go_back)
        layout.addSpacing(20)  # Add space between sections and back button
        
        back_button.setGeometry(
            1000, 20, 20,20  # Set the position and size of the back button
        )
        layout.addWidget(back_button)
        
    def go_back(self):
        """Handle back button click to navigate to home frame."""
        if self.controller:
            self.controller.show_frame("Home")
        
        

    def add_help_sections(self, layout):
        """Add the sections for help and support resources."""
        
        # 1. Getting Started
        self.add_section(layout, "Getting Started", 
                         "1. Install StellarBot.\n"
                         "2. Enter your account ID and secret key to connect to the Stellar network.\n"
                         "3. Start the bot by clicking the 'START' button on the dashboard.\n"
                         "4. Monitor your trades and view performance analytics in real-time.")

        # 2. Features Overview
        self.add_section(layout, "Features Overview", 
                         "StellarBot includes several features to assist with Stellar network trading:\n"
                         "- **Real-time Market Data**: View real-time price updates and market activity.\n"
                         "- **Automated Trading**: Execute trades automatically based on pre-defined strategies.\n"
                         "- **Performance Analytics**: Analyze your trade history and performance metrics.\n"
                         "- **Manual Trading**: Option to manually buy and sell assets within the app.\n"
                         "- **Notifications**: Get real-time alerts on important market activity.")

        # 3. Common Issues & Troubleshooting
        self.add_section(layout, "Troubleshooting", 
                         "- **Bot not starting**: Ensure your account ID and secret key are correct.\n"
                         "- **Failed trades**: Check if your account has enough balance or if there's an issue with the Stellar network.\n"
                         "- **App freezing or crashing**: Restart the app or check for updates on the official website.")

        # 4. Understanding the Dashboard
        self.add_section(layout, "Understanding the Dashboard", 
                         "The StellarBot dashboard gives you a live view of the market and your trades:\n"
                         "- **Account Summary**: View account balance, recent trades, and open positions.\n"
                         "- **Performance Stats**: Check total trades, profit, and win rate.\n"
                         "- **Control Panel**: Use 'START' to start trading, 'STOP' to pause the bot.\n"
                         "- **Market Overview**: Live charts showing price movements of selected assets.")

        # 5. Advanced Settings
        self.add_section(layout, "Advanced Settings",
                         "- **API Integration**: You can connect third-party APIs to enhance trading functionality.\n"
                         "- **Custom Trading Strategies**: Define your own rules for trading and automate them using StellarBot's engine.\n"
                         "- **Risk Management**: Configure stop-loss and take-profit settings to minimize risks.")

        # 6. FAQ
        self.add_section(layout, "FAQ", 
                         "- **Can I trade multiple assets?** Yes, you can select and trade multiple assets simultaneously.\n"
                         "- **Is StellarBot secure?** Yes, StellarBot uses your private key only to sign transactions, and no data is shared externally.\n"
                         "- **How do I update the app?** Updates are available on our website or through the app's 'Check for Updates' option in the settings.")

    def add_section(self, layout, title, content):
        """Helper function to add a new section with a title and content."""
        section_title = QtWidgets.QLabel(title)
        section_title.setStyleSheet("color: #003366; font-size: 18px; font-weight: bold;")
        layout.addWidget(section_title)

        section_content = QtWidgets.QLabel(content)
        section_content.setStyleSheet("color: #333333; font-size: 14px;")
        section_content.setWordWrap(True)
        layout.addWidget(section_content)

