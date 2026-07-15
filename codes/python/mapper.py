import threading
import time

try:
    import serial
except ImportError:
    serial = None


class MapperLink:
    def __init__(self, room, port="COM6", baud=115200):
        self.room = room
        self.port = port
        self.baud = baud
        self.ser = None
        self.running = False
        self.thread = None
        self.status = "Disconnected"
        self.last_scan = None
        self._pending = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.ser:
            try:
                self.ser.close()
            except Exception:
                pass
        self.status = "Disconnected"

    def set_port(self, port):
        self.port = port

    def _run(self):
        if serial is None:
            self.status = "pyserial not installed"
            return

        while self.running:
            try:
                self.status = "Connecting"
                self.ser = serial.Serial(self.port, self.baud, timeout=1)
                self.status = "Connected"
                self._read_loop()
            except Exception:
                self.status = "Disconnected"
                time.sleep(2)

    def _read_loop(self):
        buffer = b""
        while self.running and self.ser and self.ser.is_open:
            try:
                chunk = self.ser.read(256)
                if not chunk:
                    continue
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    text = line.decode("utf-8", errors="ignore").strip()
                    self._handle_value(text)
            except Exception:
                self.status = "Disconnected"
                break

    def _handle_value(self, text):
        if not text:
            return
        try:
            value = float(text)
        except ValueError:
            return

        if self._pending is None:
            self._pending = value
        else:
            width = self._pending
            height = value
            self._pending = None
            self.room.set_dimensions(width, height)
            self.last_scan = (width, height)
