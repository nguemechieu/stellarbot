import os

class ThemeManager:
    """Handles loading and switching of application themes."""

    def __init__(self, app, theme_dir="src/assets"):
        self.app = app
        self.theme_dir = theme_dir
        self.current_theme = "dark"

    def apply_theme(self, theme_name: str):
        """Load a theme file (CSS) and apply it to the app."""
        theme_file = os.path.join(self.theme_dir, f"{theme_name}.css")
        if not os.path.exists(theme_file):
            print(f"⚠️ Theme file '{theme_file}' not found.")
            return
        with open(theme_file, "r") as f:
            self.app.setStyleSheet(f.read())
        self.current_theme = theme_name
        print(f"✅ Applied {theme_name} theme")

    def toggle_theme(self):
        """Toggle between dark and light themes."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
