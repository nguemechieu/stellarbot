import os

class ThemeManager:
    """Handles loading and switching of application themes."""

    def __init__(self, app, theme_dir="src/assets"):
        self.app = app
        self.theme_dir = theme_dir
        self.current_theme = "dark"
        # Load minimal theme first for reliability
        self._apply_minimal_theme()

    def _apply_minimal_theme(self):
        """Apply a minimal, reliable stylesheet."""
        minimal_stylesheet = """
            QWidget { background-color: #0F1419; color: #E8F4F8; font-family: "Segoe UI", Arial; }
            QMainWindow { background-color: #0F1419; }
            QPushButton { background-color: #00D4FF; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #00A3CC; }
            QPushButton:pressed { background-color: #0080AA; }
            QLineEdit, QTextEdit { background-color: #1A1F29; color: #E8F4F8; border: 1px solid #00D4FF; padding: 6px; border-radius: 3px; }
            QGroupBox { border: 2px solid #00D4FF; border-radius: 6px; margin-top: 10px; padding-top: 10px; font-weight: bold; color: #00D4FF; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }
            QTableWidget { background-color: #16213E; color: #E8F4F8; border: 1px solid #00D4FF; gridline-color: #242D3C; }
            QTableWidget::item:selected { background-color: #00D4FF; color: #0F1419; }
            QHeaderView::section { background-color: #242D3C; color: #00D4FF; padding: 6px; border: 1px solid #00D4FF; }
            QLabel { color: #E8F4F8; background-color: transparent; }
            QComboBox { background-color: #1A1F29; color: #E8F4F8; border: 1px solid #00D4FF; padding: 6px; border-radius: 3px; }
            QComboBox::drop-down { border: none; width: 20px; }
            QScrollBar:vertical { background-color: #0F1419; width: 12px; }
            QScrollBar::handle:vertical { background-color: #00D4FF; border-radius: 6px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background-color: #00A3CC; }
            QStatusBar { background-color: #242D3C; color: #00D4FF; border-top: 1px solid #00D4FF; }
            QMenuBar { background-color: #242D3C; color: #E8F4F8; }
            QMenuBar::item:selected { background-color: #00D4FF; color: #0F1419; }
            QMenu { background-color: #242D3C; color: #E8F4F8; border: 1px solid #00D4FF; }
            QMenu::item:selected { background-color: #00D4FF; color: #0F1419; }
            QFrame { background-color: #16213E; border: 1px solid #00D4FF; border-radius: 4px; }
        """
        try:
            self.app.setStyleSheet(minimal_stylesheet)
        except Exception as e:
            print(f"⚠️ Failed to set minimal stylesheet: {e}")

    def apply_theme(self, theme_name: str):
        """Load a theme file (CSS) and apply it to the app."""
        theme_file = os.path.join(self.theme_dir, f"{theme_name}.css")
        if not os.path.exists(theme_file):
            print(f"⚠️ Theme file '{theme_file}' not found.")
            return

        try:
            with open(theme_file, "r") as f:
                stylesheet = f.read()
                self.app.setStyleSheet(stylesheet)
            self.current_theme = theme_name
            print(f"✅ Applied {theme_name} theme")
        except Exception as e:
            print(f"⚠️ Failed to parse theme '{theme_name}': {e}")
            print("   Continuing with default styling...")
            # Apply minimal fallback theme
            self.app.setStyleSheet("""
                QWidget { 
                    background-color: #0F1419; 
                    color: #E8F4F8;
                    font-family: "Segoe UI", Arial, sans-serif;
                }
            """)

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
