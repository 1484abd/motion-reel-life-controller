import json
import os

SETTINGS_PATH = "settings.json"
BUTTONS_PATH = "buttons.json"

DEFAULT_SETTINGS = {
    "device_name": "Headset",
    "port": "COM5",
    "mouse_sensitivity": 1.0,
    "movement_sensitivity": 0.1
}

DEFAULT_BUTTONS = {
    "BUTTON,1": "space",
    "BUTTON,2": "shift",
    "BUTTON,3": "e",
    "BUTTON,4": "esc"
}


class Settings:
    def __init__(self):
        self.data = dict(DEFAULT_SETTINGS)
        self.buttons = dict(DEFAULT_BUTTONS)
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r") as f:
                    loaded = json.load(f)
                self.data.update(loaded)
            except (json.JSONDecodeError, OSError):
                pass
        else:
            self.save()

        if os.path.exists(BUTTONS_PATH):
            try:
                with open(BUTTONS_PATH, "r") as f:
                    loaded = json.load(f)
                self.buttons.update(loaded)
            except (json.JSONDecodeError, OSError):
                pass
        else:
            self.save_buttons()

    def save(self):
        with open(SETTINGS_PATH, "w") as f:
            json.dump(self.data, f, indent=2)

    def save_buttons(self):
        with open(BUTTONS_PATH, "w") as f:
            json.dump(self.buttons, f, indent=2)

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def set_button(self, code, action):
        self.buttons[code] = action
        self.save_buttons()

    def action_for(self, code):
        return self.buttons.get(code)
