import json
from pathlib import Path


CONFIG_FILE = Path("config.json")


class SettingsManager:

    def __init__(self):
        self.settings = self.load()

    def load(self):
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as file:
                return json.load(file)

        return {
            "download_folder": "",
            "theme": "dark",
            "appearance": "system",
            "default_mode": "video"
        }

    def save(self):
        with open(CONFIG_FILE, "w") as file:
            json.dump(self.settings, file, indent=4)

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value
        self.save()