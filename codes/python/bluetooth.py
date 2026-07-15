import threading
import time

try:
    import serial
except ImportError:
    serial = None


class BluetoothLink:
    def __init__(self, tracker, port="COM5", baud=115200):
        self.tracker = tracker
        self.port = port
        self.baud = baud
        self.ser = None
        self.running = False
        self.thread = None
        self.status = "Disconnected"

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
        self.tracker.connected = False

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
                self.tracker.connected = True
                self._read_loop()
            except Exception:
                self.status = "Disconnected"
                self.tracker.connected = False
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
                    try:
                        text = line.decode("utf-8", errors="ignore")
                    except UnicodeDecodeError:
                        continue
                    self.tracker.handle_line(text)
            except Exception:
                self.status = "Disconnected"
                self.tracker.connected = False
                break
