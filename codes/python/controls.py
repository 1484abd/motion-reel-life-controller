import threading
import time

try:
    from pynput.mouse import Controller as MouseController
    from pynput.keyboard import Controller as KeyController, Key
except ImportError:
    MouseController = None
    KeyController = None
    Key = None

KEY_MAP = {
    "space": "space",
    "shift": "shift",
    "esc": "esc",
    "escape": "esc",
    "enter": "enter",
    "ctrl": "ctrl",
    "tab": "tab"
}


class OutputController:
    def __init__(self, tracker, settings):
        self.tracker = tracker
        self.settings = settings
        self.running = False
        self.thread = None
        self.enabled = True

        self.mouse = MouseController() if MouseController else None
        self.keyboard = KeyController() if KeyController else None

        self._last_yaw = None
        self._last_pos = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _resolve_key(self, action):
        if not action:
            return None
        low = action.lower()
        if low in KEY_MAP and Key:
            return getattr(Key, KEY_MAP[low])
        if len(low) == 1:
            return low
        return low

    def _press_key(self, key, duration):
        if not self.keyboard or key is None:
            return
        try:
            self.keyboard.press(key)
            time.sleep(duration)
            self.keyboard.release(key)
        except Exception:
            pass

    def _tap_key(self, key):
        if not self.keyboard or key is None:
            return
        try:
            self.keyboard.press(key)
            time.sleep(0.05)
            self.keyboard.release(key)
        except Exception:
            pass

    def _run(self):
        while self.running:
            snap = self.tracker.snapshot()

            if self.enabled and self.mouse:
                yaw = snap["yaw"]
                if self._last_yaw is not None:
                    delta = yaw - self._last_yaw
                    if delta > 180:
                        delta -= 360
                    elif delta < -180:
                        delta += 360
                    sensitivity = self.settings.get("mouse_sensitivity") or 1.0
                    if abs(delta) > 0.05:
                        dx = int(delta * 8 * sensitivity)
                        cur = self.mouse.position
                        self.mouse.position = (cur[0] + dx, cur[1])
                self._last_yaw = yaw

            if self.enabled and snap["tracking_enabled"]:
                x, y = snap["player_x"], snap["player_y"]
                if self._last_pos is not None:
                    dx = x - self._last_pos[0]
                    dy = y - self._last_pos[1]
                    per_cm = self.settings.get("movement_sensitivity") or 0.1

                    if dy > 1:
                        self._press_key("w", min(abs(dy) * per_cm, 0.3))
                    elif dy < -1:
                        self._press_key("s", min(abs(dy) * per_cm, 0.3))

                    if dx > 1:
                        self._press_key("d", min(abs(dx) * per_cm, 0.3))
                    elif dx < -1:
                        self._press_key("a", min(abs(dx) * per_cm, 0.3))
                self._last_pos = (x, y)

            btn = snap["button_pressed"]
            if btn and self.enabled:
                action = self.settings.action_for(btn)
                key = self._resolve_key(action)
                self._tap_key(key)
                self.tracker.clear_button()

            time.sleep(0.02)
