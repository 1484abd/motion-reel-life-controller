import json
import os

DEFAULT_MAP = {
    "width": 500,
    "height": 400,
    "walls": [
        [-250, -200, 250, -200],
        [250, -200, 250, 200],
        [250, 200, -250, 200],
        [-250, 200, -250, -200]
    ],
    "obstacles": []
}


class RoomMap:
    def __init__(self, path="room_map.json"):
        self.path = path
        self.width = DEFAULT_MAP["width"]
        self.height = DEFAULT_MAP["height"]
        self.walls = list(DEFAULT_MAP["walls"])
        self.obstacles = list(DEFAULT_MAP["obstacles"])
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            self.save()
            return
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
            self.width = data.get("width", self.width)
            self.height = data.get("height", self.height)
            self.walls = data.get("walls", self.walls)
            self.obstacles = data.get("obstacles", self.obstacles)
        except (json.JSONDecodeError, OSError):
            self.width = DEFAULT_MAP["width"]
            self.height = DEFAULT_MAP["height"]
            self.walls = list(DEFAULT_MAP["walls"])
            self.obstacles = list(DEFAULT_MAP["obstacles"])

    def save(self):
        data = {
            "width": self.width,
            "height": self.height,
            "walls": self.walls,
            "obstacles": self.obstacles
        }
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def bounds(self):
        hw = self.width / 2
        hh = self.height / 2
        return -hw, hw, -hh, hh

    def clamp(self, x, y):
        x0, x1, y0, y1 = self.bounds()
        return max(x0, min(x1, x)), max(y0, min(y1, y))
