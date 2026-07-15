import math
import threading
import time

from axis import player_axis


class Tracker:
    def __init__(self, room):
        self.room = room
        self.lock = threading.Lock()

        self.acceleration_x = 0.0
        self.acceleration_y = 0.0
        self.acceleration_z = 0.0

        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0

        self.front_distance = 0.0
        self.right_distance = 0.0

        self.player_state = "STILL"
        self.button_pressed = None
        self.tracking_enabled = False

        self.connected = False
        self.last_packet_time = 0

        self.player_x = 0.0
        self.player_y = 0.0
        self.player_angle = 0.0

        self._prev_yaw = 0.0

    def handle_line(self, raw):
        line = raw.strip()
        if not line:
            return
        parts = [p.strip() for p in line.split(",")]

        try:
            if line == "start":
                with self.lock:
                    self.tracking_enabled = True
                return
            if line == "stop":
                with self.lock:
                    self.tracking_enabled = False
                return
            if line in ("JUMP", "MOVING", "STILL"):
                with self.lock:
                    self.player_state = line
                return
            if parts[0] == "BUTTON" and len(parts) == 2:
                with self.lock:
                    self.button_pressed = f"BUTTON,{parts[1]}"
                return

            if len(parts) < 2:
                return

            label = parts[0]
            value = float(parts[1])

            if label == "Acceleration X":
                self.acceleration_x = value
            elif label == "Acceleration Y":
                self.acceleration_y = value
            elif label == "Acceleration Z":
                self.acceleration_z = value
            elif label == "Yaw":
                self._prev_yaw = self.yaw
                self.yaw = value
            elif label == "Pitch":
                self.pitch = value
            elif label == "Roll":
                self.roll = value
            elif label == "Front":
                self.front_distance = value
            elif label == "Right":
                self.right_distance = value
            else:
                return

            self.last_packet_time = time.time()
            self.connected = True

            if self.tracking_enabled:
                self._update_position()

        except (ValueError, IndexError):
            return

    def _update_position(self):
        with self.lock:
            x0, x1, y0, y1 = self.room.bounds()
            (fx, fy), (rx, ry) = player_axis(self.yaw)

            candidate_x = None
            candidate_y = None

            if abs(fx) >= abs(fy):
                wall_x = x1 if fx >= 0 else x0
                candidate_x = wall_x - self.front_distance * fx
            else:
                wall_y = y1 if fy >= 0 else y0
                candidate_y = wall_y - self.front_distance * fy

            if abs(rx) >= abs(ry):
                wall_x = x1 if rx >= 0 else x0
                px = wall_x - self.right_distance * rx
                candidate_x = px if candidate_x is None else (candidate_x + px) / 2
            else:
                wall_y = y1 if ry >= 0 else y0
                py = wall_y - self.right_distance * ry
                candidate_y = py if candidate_y is None else (candidate_y + py) / 2

            if candidate_x is None:
                candidate_x = self.player_x
            if candidate_y is None:
                candidate_y = self.player_y

            cx, cy = self.room.clamp(candidate_x, candidate_y)
            self.player_x = cx
            self.player_y = cy
            self.player_angle = self.yaw % 360

    def snapshot(self):
        with self.lock:
            return {
                "acceleration_x": self.acceleration_x,
                "acceleration_y": self.acceleration_y,
                "acceleration_z": self.acceleration_z,
                "yaw": self.yaw,
                "pitch": self.pitch,
                "roll": self.roll,
                "front_distance": self.front_distance,
                "right_distance": self.right_distance,
                "player_state": self.player_state,
                "button_pressed": self.button_pressed,
                "tracking_enabled": self.tracking_enabled,
                "connected": self.connected,
                "player_x": self.player_x,
                "player_y": self.player_y,
                "player_angle": self.player_angle
            }

    def clear_button(self):
        with self.lock:
            self.button_pressed = None

    def set_position_manual(self, x, y, angle):
        with self.lock:
            cx, cy = self.room.clamp(x, y)
            self.player_x = cx
            self.player_y = cy
            self.player_angle = angle % 360
