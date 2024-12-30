from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QApplication, QFrame
from PyQt5.QtCore import Qt
import sys

class About(QFrame):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        # Create the layout
        layout = QVBoxLayout()

        # Title label
        title = QLabel("About StellarBot", self)
        title.setStyleSheet("color: white; font-size: 24px; font-family: Helvetica;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # About description
        about_text = """
        StellarBot is an open-source project aimed at providing a 
        comprehensive platform for automated trading on the Stellar network.
        
        This bot leverages machine learning techniques to predict market trends 
        and execute trades based on live data. StellarBot supports various trading 
        pairs and allows users to create or close orders according to their 
        preferences.

        Author: nguemechieu
        GitHub: https://github.com/nguemechieu/stellarbot
        """
        about_label = QLabel(about_text, self)
        about_label.setStyleSheet("color: white; font-size: 14px; font-family: Helvetica;")
        about_label.setAlignment(Qt.AlignLeft)
        about_label.setWordWrap(True)
        layout.addWidget(about_label)

        # Back button to navigate to other frames
        back_button = QPushButton("Back", self)
        back_button.setStyleSheet("background-color: white; color: #1e2a38;")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)

    def go_back(self):
        """Handle back button click to navigate to home frame."""
        if self.controller:
            self.controller.show_frame("Home")
        
        sys.exit()

