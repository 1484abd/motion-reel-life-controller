import tkinter as tk
from tkinter import ttk, messagebox

from room import RoomMap
from settings import Settings
from tracker import Tracker
from bluetooth import BluetoothLink
from mapper import MapperLink
from controls import OutputController
from renderer import RoomView

BG = "#12121a"
PANEL = "#1c1c26"
ACCENT = "#5ac8fa"
TEXT = "#e6e6e6"
DIM = "#8a8a95"


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 VR Tracker")
        self.root.geometry("560x640")
        self.root.configure(bg=BG)

        self.room = RoomMap()
        self.settings = Settings()
        self.tracker = Tracker(self.room)
        self.link = BluetoothLink(self.tracker, port=self.settings.get("port"))
        self.mapper_link = MapperLink(self.room, port=self.settings.get("mapper_port"))
        self.controller = OutputController(self.tracker, self.settings)
        self.view = RoomView(self.tracker, self.room)

        self._build_style()
        self._build_layout()

        self.controller.start()
        self.view.start()

        self._refresh()

    def _build_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=PANEL, foreground=TEXT, padding=(14, 6))
        style.map("TNotebook.Tab", background=[("selected", ACCENT)])
        style.configure("TFrame", background=PANEL)
        style.configure("TLabel", background=PANEL, foreground=TEXT)
        style.configure("Header.TLabel", background=BG, foreground=ACCENT, font=("Segoe UI", 14, "bold"))
        style.configure("Value.TLabel", background=PANEL, foreground=ACCENT, font=("Consolas", 11))
        style.configure("TButton", padding=6)
        style.configure("Horizontal.TScale", background=PANEL)

    def _build_layout(self):
        header = tk.Label(self.root, text="VR TRACKING DASHBOARD", bg=BG, fg=ACCENT,
                           font=("Segoe UI", 16, "bold"))
        header.pack(pady=(14, 4))

        status_frame = tk.Frame(self.root, bg=PANEL)
        status_frame.pack(fill="x", padx=14, pady=8)

        self.status_labels = {}
        rows = [
            ("Bluetooth", "conn"),
            ("Tracking", "tracking"),
            ("X", "x"), ("Y", "y"), ("Angle", "angle"),
            ("Front", "front"), ("Right", "right"),
            ("Yaw", "yaw"), ("Pitch", "pitch"), ("Roll", "roll"),
            ("State", "state")
        ]
        for i, (label, key) in enumerate(rows):
            r, c = divmod(i, 2)
            cell = tk.Frame(status_frame, bg=PANEL)
            cell.grid(row=r, column=c, sticky="w", padx=10, pady=4)
            tk.Label(cell, text=f"{label}:", bg=PANEL, fg=DIM, font=("Segoe UI", 10)).pack(side="left")
            val = tk.Label(cell, text="--", bg=PANEL, fg=ACCENT, font=("Consolas", 10, "bold"))
            val.pack(side="left", padx=(6, 0))
            self.status_labels[key] = val

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=14, pady=10)

        self._build_bluetooth_tab(notebook)
        self._build_mouse_tab(notebook)
        self._build_movement_tab(notebook)
        self._build_buttons_tab(notebook)
        self._build_room_tab(notebook)

    def _build_bluetooth_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Bluetooth")

        tk.Label(tab, text="Device name", bg=PANEL, fg=TEXT).pack(anchor="w", padx=12, pady=(14, 2))
        self.device_entry = tk.Entry(tab, bg="#2a2a36", fg=TEXT, insertbackground=TEXT)
        self.device_entry.insert(0, self.settings.get("device_name"))
        self.device_entry.pack(fill="x", padx=12)

        tk.Label(tab, text="Serial port (paired COM / rfcomm)", bg=PANEL, fg=TEXT).pack(anchor="w", padx=12, pady=(14, 2))
        self.port_entry = tk.Entry(tab, bg="#2a2a36", fg=TEXT, insertbackground=TEXT)
        self.port_entry.insert(0, self.settings.get("port"))
        self.port_entry.pack(fill="x", padx=12)

        btn_row = tk.Frame(tab, bg=PANEL)
        btn_row.pack(pady=16)
        ttk.Button(btn_row, text="Connect", command=self._connect).pack(side="left", padx=6)
        ttk.Button(btn_row, text="Disconnect", command=self._disconnect).pack(side="left", padx=6)

        self.bt_status_label = tk.Label(tab, text="Status: Disconnected", bg=PANEL, fg=DIM)
        self.bt_status_label.pack(pady=6)

        self.sim_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(tab, text="Simulation mode (WASD / arrow keys, no ESP32 needed)",
                         variable=self.sim_var, command=self._toggle_sim).pack(pady=10)

    def _build_mouse_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Mouse")

        tk.Label(tab, text="Mouse sensitivity", bg=PANEL, fg=TEXT).pack(anchor="w", padx=12, pady=(20, 2))
        self.mouse_scale = ttk.Scale(tab, from_=0.1, to=3.0, orient="horizontal",
                                      command=self._update_mouse_sensitivity)
        self.mouse_scale.set(self.settings.get("mouse_sensitivity"))
        self.mouse_scale.pack(fill="x", padx=12)
        self.mouse_value_label = tk.Label(tab, text=str(self.settings.get("mouse_sensitivity")),
                                           bg=PANEL, fg=ACCENT)
        self.mouse_value_label.pack(pady=4)

    def _build_movement_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Movement")

        tk.Label(tab, text="Movement sensitivity (seconds of key press per cm)",
                 bg=PANEL, fg=TEXT).pack(anchor="w", padx=12, pady=(20, 2))
        self.move_scale = ttk.Scale(tab, from_=0.01, to=1.0, orient="horizontal",
                                     command=self._update_move_sensitivity)
        self.move_scale.set(self.settings.get("movement_sensitivity"))
        self.move_scale.pack(fill="x", padx=12)
        self.move_value_label = tk.Label(tab, text=str(self.settings.get("movement_sensitivity")),
                                          bg=PANEL, fg=ACCENT)
        self.move_value_label.pack(pady=4)

    def _build_buttons_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Buttons")

        self.button_labels = {}
        for i in range(1, 5):
            code = f"BUTTON,{i}"
            row = tk.Frame(tab, bg=PANEL)
            row.pack(fill="x", padx=12, pady=8)
            tk.Label(row, text=f"Button {i} ->", bg=PANEL, fg=TEXT, width=14, anchor="w").pack(side="left")
            val_label = tk.Label(row, text=self.settings.action_for(code), bg=PANEL, fg=ACCENT, width=12)
            val_label.pack(side="left")
            self.button_labels[code] = val_label
            ttk.Button(row, text="Change", command=lambda c=code: self._change_button(c)).pack(side="left", padx=8)

    def _build_room_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Room Map")

        info = tk.Label(tab, text=f"Width: {self.room.width} cm    Height: {self.room.height} cm",
                         bg=PANEL, fg=TEXT)
        info.pack(pady=(16, 10))
        self.room_info_label = info

        ttk.Button(tab, text="Reload room_map.json", command=self._reload_room).pack(pady=6)

        sep = tk.Frame(tab, bg="#333340", height=1)
        sep.pack(fill="x", padx=12, pady=14)

        tk.Label(tab, text="Room Mapper Beacon", bg=PANEL, fg=ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12)

        tk.Label(tab, text="Serial port (mapper's paired COM / rfcomm)",
                 bg=PANEL, fg=TEXT).pack(anchor="w", padx=12, pady=(10, 2))
        self.mapper_port_entry = tk.Entry(tab, bg="#2a2a36", fg=TEXT, insertbackground=TEXT)
        self.mapper_port_entry.insert(0, self.settings.get("mapper_port"))
        self.mapper_port_entry.pack(fill="x", padx=12)

        btn_row = tk.Frame(tab, bg=PANEL)
        btn_row.pack(pady=12)
        ttk.Button(btn_row, text="Connect Mapper", command=self._connect_mapper).pack(side="left", padx=6)
        ttk.Button(btn_row, text="Disconnect Mapper", command=self._disconnect_mapper).pack(side="left", padx=6)

        self.mapper_status_label = tk.Label(tab, text="Status: Disconnected", bg=PANEL, fg=DIM)
        self.mapper_status_label.pack(pady=4)

        self.mapper_scan_label = tk.Label(tab, text="Last scan: --", bg=PANEL, fg=ACCENT)
        self.mapper_scan_label.pack(pady=4)

    def _connect(self):
        self.settings.set("device_name", self.device_entry.get())
        self.settings.set("port", self.port_entry.get())
        self.link.set_port(self.port_entry.get())
        self.link.start()

    def _disconnect(self):
        self.link.stop()

    def _toggle_sim(self):
        self.view.sim_mode = self.sim_var.get()

    def _connect_mapper(self):
        port = self.mapper_port_entry.get()
        self.settings.set("mapper_port", port)
        self.mapper_link.set_port(port)
        self.mapper_link.start()

    def _disconnect_mapper(self):
        self.mapper_link.stop()

    def _update_mouse_sensitivity(self, val):
        v = round(float(val), 2)
        self.settings.set("mouse_sensitivity", v)
        self.mouse_value_label.config(text=str(v))

    def _update_move_sensitivity(self, val):
        v = round(float(val), 3)
        self.settings.set("movement_sensitivity", v)
        self.move_value_label.config(text=str(v))

    def _change_button(self, code):
        popup = tk.Toplevel(self.root)
        popup.title(f"Change {code}")
        popup.configure(bg=PANEL)
        popup.geometry("260x110")

        tk.Label(popup, text="New key/action:", bg=PANEL, fg=TEXT).pack(pady=(14, 4))
        entry = tk.Entry(popup, bg="#2a2a36", fg=TEXT, insertbackground=TEXT)
        entry.insert(0, self.settings.action_for(code))
        entry.pack(padx=12, fill="x")

        def apply():
            value = entry.get().strip()
            if value:
                self.settings.set_button(code, value)
                self.button_labels[code].config(text=value)
            popup.destroy()

        ttk.Button(popup, text="Save", command=apply).pack(pady=10)

    def _reload_room(self):
        self.room.load()
        self.room_info_label.config(text=f"Width: {self.room.width} cm    Height: {self.room.height} cm")
        messagebox.showinfo("Room Map", "room_map.json reloaded.")

    def _refresh(self):
        snap = self.tracker.snapshot()
        self.status_labels["conn"].config(text="Connected" if snap["connected"] else "Disconnected")
        self.status_labels["tracking"].config(text="ON" if snap["tracking_enabled"] else "OFF")
        self.status_labels["x"].config(text=f"{snap['player_x']:.1f} cm")
        self.status_labels["y"].config(text=f"{snap['player_y']:.1f} cm")
        self.status_labels["angle"].config(text=f"{snap['player_angle']:.1f} deg")
        self.status_labels["front"].config(text=f"{snap['front_distance']:.1f} cm")
        self.status_labels["right"].config(text=f"{snap['right_distance']:.1f} cm")
        self.status_labels["yaw"].config(text=f"{snap['yaw']:.1f} deg")
        self.status_labels["pitch"].config(text=f"{snap['pitch']:.1f} deg")
        self.status_labels["roll"].config(text=f"{snap['roll']:.1f} deg")
        self.status_labels["state"].config(text=snap["player_state"])
        self.bt_status_label.config(text=f"Status: {self.link.status}")

        self.mapper_status_label.config(text=f"Status: {self.mapper_link.status}")
        if self.mapper_link.last_scan:
            w, h = self.mapper_link.last_scan
            self.mapper_scan_label.config(text=f"Last scan: {w:.1f} cm x {h:.1f} cm")
            self.room_info_label.config(text=f"Width: {self.room.width} cm    Height: {self.room.height} cm")

        self.root.after(100, self._refresh)

    def on_close(self):
        self.link.stop()
        self.mapper_link.stop()
        self.controller.stop()
        self.view.stop()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
