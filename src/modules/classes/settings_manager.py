
import json
import os


class SettingsManager:
    """Handles saving and loading user settings."""
    
    SETTINGS_FILE = 'user_settings.json'
    
    @classmethod
    def save_settings(cls, settings):
        """Save settings to a JSON file."""
        with open(cls.SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    
    @classmethod
    def load_settings(cls):
        """Load settings from a JSON file, or return an empty dict if not found."""
        if os.path.exists(cls.SETTINGS_FILE):
            with open(cls.SETTINGS_FILE, 'r') as f:
                return json.load(f)
        return {}