
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import queue
import time
import json
import logging

from gesture_controller import GestureController


class App:

    POLL_MS = 30

    BG = "#10141D"
    PANEL = "#1A2230"
    ACCENT = "#00C2A8"
    TEXT = "#FFFFFF"
    MUTED = "#A0AEC0"

    def __init__(self, root):

        self.root = root
        self.root.title("YouTube Gesture Controller")
        self.root.geometry("1150x760")
        self.root.minsize(950, 650)
        self.root.configure(bg=self.BG)

        self.controller = GestureController()

        self._closing = False
        self._image_item = None
        self._frame_queue = queue.Queue(maxsize=1)
        self.history = []

        self.build_ui()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self._on_exit
        )

        self.root.after(
            self.POLL_MS,
            self._poll_frame_queue
        )

    def build_ui(self):

        header = tk.Frame(
            self.root,
            bg=self.PANEL,
            height=75
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="YT GESTURE CONTROLLER",
            font=("Segoe UI", 20, "bold"),
            fg=self.ACCENT,
            bg=self.PANEL
        ).pack(side="left", padx=25, pady=20)

        self.status_label = tk.Label(
            header,
            text="● OFFLINE",
            font=("Segoe UI", 11, "bold"),
            fg="#FF6B6B",
            bg=self.PANEL
        )

        self.status_label.pack(side="right", padx=25)

        body = tk.Frame(
            self.root,
            bg=self.BG
        )

        body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        left = tk.Frame(
            body,
            bg=self.BG
        )

        left.pack(
            side="left",
            fill="both",
            expand=True
        )

        right = tk.Frame(
            body,
            bg=self.BG,
            width=300
        )

        right.pack(
            side="right",
            fill="y",
            padx=(20, 0)
        )

        tk.Label(
            left,
            text="LIVE CAMERA",
            fg=self.TEXT,
            bg=self.BG,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(0, 10))

        self.canvas = tk.Canvas(
            left,
            width=640,
            height=480,
            bg="#080B11",
            highlightthickness=1,
            highlightbackground="#344054"
        )

        self.canvas.pack(fill="both", expand=True)

        self._placeholder_text_id = self.canvas.create_text(
            320,
            240,
            text="Camera preview will appear here",
            fill=self.MUTED,
            font=("Segoe UI", 15)
        )

        self.create_card(right, "DETECTED ACTION")
        self.action_value = self.card_value

        self.create_card(right, "FINGER COUNT")
        self.finger_value = self.card_value

        self.create_card(right, "HANDEDNESS")
        self.hand_value = self.card_value

        self.create_card(right, "FRAME RATE")
        self.fps_value = self.card_value

        tk.Label(
            right,
            text="CONTROLS",
            fg=self.TEXT,
            bg=self.BG,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(25, 10))

        self.start_btn = self.make_button(
            right,
            "▶  Start Controller",
            self.start_controller
        )

        self.stop_btn = self.make_button(
            right,
            "■  Stop Controller",
            self.stop_controller
        )

        self.stop_btn.config(state="disabled")

        self.lock_btn = self.make_button(
            right,
            "🔒  Lock Gestures",
            self.toggle_lock
        )

        self.make_button(
            right,
            "⚙  Settings",
            self.open_settings
        )

        self.make_button(
            right,
            "☷  Gesture Guide",
            self.open_guide
        )

        self.make_button(
            right,
            "◷  Activity History",
            self.open_history
        )

        self.make_button(
            right,
            "Exit",
            self._on_exit
        )

    def create_card(self, parent, heading):

        card = tk.Frame(
            parent,
            bg=self.PANEL,
            padx=15,
            pady=12
        )

        card.pack(fill="x", pady=6)

        tk.Label(
            card,
            text=heading,
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        self.card_value = tk.Label(
            card,
            text="--",
            bg=self.PANEL,
            fg=self.ACCENT,
            font=("Segoe UI", 16, "bold")
        )

        self.card_value.pack(anchor="w", pady=(5, 0))

    def make_button(self, parent, text, command):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=self.PANEL,
            fg=self.TEXT,
            activebackground=self.ACCENT,
            activeforeground="#000000",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=11,
            cursor="hand2"
        )

        button.pack(fill="x", pady=4)

        return button

    def update_frame(self, frame, action, fingers, hand, fps):

        try:
            if self._frame_queue.full():
                self._frame_queue.get_nowait()

            self._frame_queue.put_nowait(
                (frame, action, fingers, hand, fps)
            )

        except queue.Empty:
            pass
        except queue.Full:
            pass

    def _poll_frame_queue(self):

        if self._closing:
            return

        try:
            data = self._frame_queue.get_nowait()
            self._render(*data)

        except queue.Empty:
            pass

        self.root.after(
            self.POLL_MS,
            self._poll_frame_queue
        )

    def _render(self, frame, action, fingers, hand, fps):

        try:
            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)

            if self._image_item is None:

                self.canvas.delete("all")

                self._image_item = self.canvas.create_image(
                    0,
                    0,
                    anchor=tk.NW,
                    image=imgtk
                )

            else:

                self.canvas.itemconfig(
                    self._image_item,
                    image=imgtk
                )

            self.canvas.image = imgtk

            self.action_value.config(text=action)
            self.finger_value.config(text=str(fingers))
            self.hand_value.config(text=hand)
            self.fps_value.config(text=f"{fps:.1f}")

        except Exception as error:
            logging.warning(f"Render error: {error}")

    def on_action(self, fingers, action):

        entry = {
            "time": time.strftime("%H:%M:%S"),
            "gesture": f"{fingers} Fingers",
            "action": action.replace("_", " ").title()
        }

        self.history.insert(0, entry)
        self.history = self.history[:100]

    def start_controller(self):

        started = self.controller.start(
            self.update_frame,
            self.on_action
        )

        if started:

            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")

            self.status_label.config(
                text="● RUNNING",
                fg=self.ACCENT
            )

        else:

            messagebox.showwarning(
                "Controller",
                "Controller is already running."
            )

    def stop_controller(self):

        self.controller.stop()

        try:
            while True:
                self._frame_queue.get_nowait()
        except queue.Empty:
            pass

        self.canvas.delete("all")
        self._image_item = None

        self.canvas.create_text(
            320,
            240,
            text="Controller Stopped",
            fill=self.MUTED,
            font=("Segoe UI", 16)
        )

        self.action_value.config(text="--")
        self.finger_value.config(text="--")
        self.hand_value.config(text="--")
        self.fps_value.config(text="--")

        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

        self.status_label.config(
            text="● OFFLINE",
            fg="#FF6B6B"
        )

    def toggle_lock(self):

        locked = self.controller.toggle_lock()

        self.lock_btn.config(
            text="🔓  Unlock Gestures" if locked
            else "🔒  Lock Gestures"
        )

    def open_guide(self):

        window = tk.Toplevel(self.root)

        window.title("Gesture Guide")
        window.geometry("450x450")
        window.configure(bg=self.BG)

        tk.Label(
            window,
            text="GESTURE GUIDE",
            bg=self.BG,
            fg=self.ACCENT,
            font=("Segoe UI", 18, "bold")
        ).pack(pady=20)

        gestures = [
            ("✊  0 Fingers", "Mute / Unmute"),
            ("☝  1 Finger", "Seek Forward"),
            ("✌  2 Fingers", "Seek Backward"),
            ("🤟  3 Fingers", "Volume Up"),
            ("🖐  4 Fingers", "Volume Down"),
            ("🖐  5 Fingers", "Play / Pause")
        ]

        for gesture, action in gestures:

            tk.Label(
                window,
                text=f"{gesture}  →  {action}",
                bg=self.PANEL,
                fg=self.TEXT,
                font=("Segoe UI", 12),
                padx=15,
                pady=12
            ).pack(fill="x", padx=20, pady=5)

    def open_history(self):

        window = tk.Toplevel(self.root)

        window.title("Activity History")
        window.geometry("600x450")
        window.configure(bg=self.BG)

        tk.Label(
            window,
            text="GESTURE ACTIVITY HISTORY",
            bg=self.BG,
            fg=self.ACCENT,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=15)

        columns = ("time", "gesture", "action")

        table = ttk.Treeview(
            window,
            columns=columns,
            show="headings"
        )

        for column in columns:
            table.heading(column, text=column.title())
            table.column(column, width=160)

        table.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        for item in self.history:

            table.insert(
                "",
                "end",
                values=(
                    item["time"],
                    item["gesture"],
                    item["action"]
                )
            )

    def open_settings(self):

        window = tk.Toplevel(self.root)

        window.title("Settings")
        window.geometry("420x430")
        window.configure(bg=self.BG)

        tk.Label(
            window,
            text="APPLICATION SETTINGS",
            bg=self.BG,
            fg=self.ACCENT,
            font=("Segoe UI", 16, "bold")
        ).pack(pady=20)

        variables = {}

        settings = [
            ("gesture_delay", "Gesture Delay (seconds)"),
            ("seek_seconds", "Seek Duration (seconds)"),
            ("volume_step", "Volume Step")
        ]

        for key, label in settings:

            tk.Label(
                window,
                text=label,
                bg=self.BG,
                fg=self.TEXT
            ).pack(anchor="w", padx=30, pady=(10, 3))

            variable = tk.StringVar(
                value=str(self.controller.config[key])
            )

            variables[key] = variable

            tk.Entry(
                window,
                textvariable=variable,
                font=("Segoe UI", 11)
            ).pack(fill="x", padx=30)

        voice_var = tk.BooleanVar(
            value=self.controller.config["voice_feedback"]
        )

        tk.Checkbutton(
            window,
            text="Enable Voice Feedback",
            variable=voice_var,
            bg=self.BG,
            fg=self.TEXT,
            selectcolor=self.PANEL,
            activebackground=self.BG
        ).pack(pady=15)

        def save():

            try:

                for key, variable in variables.items():

                    value = float(variable.get())

                    if key == "gesture_delay" and value < 0.1:
                        raise ValueError(
                            "Gesture delay must be at least 0.1."
                        )

                    if key in ("seek_seconds", "volume_step"):

                        if value <= 0 or not value.is_integer():
                            raise ValueError(
                                f"{key} must be a positive integer."
                            )

                        value = int(value)

                    self.controller.config[key] = value

                self.controller.config["voice_feedback"] = voice_var.get()

                with open("config.json", "w") as file:
                    json.dump(
                        self.controller.config,
                        file,
                        indent=4
                    )

                messagebox.showinfo(
                    "Settings",
                    "Settings saved successfully!"
                )

                window.destroy()

            except ValueError as error:

                messagebox.showerror(
                    "Invalid Settings",
                    str(error)
                )

        self.make_button(
            window,
            "Save Settings",
            save
        )

    def _on_exit(self):

        if self._closing:
            return

        self._closing = True

        self.controller.shutdown()

        self.root.destroy()


if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)

    root = tk.Tk()

    app = App(root)

    root.mainloop()
