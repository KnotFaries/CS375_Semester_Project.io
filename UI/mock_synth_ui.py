import tkinter as tk
from tkinter import ttk


class NumberInput:
    def __init__(self, initial_value=None):
        self.current_input = ""
        self.value = None
        self.is_active = False
        if initial_value is not None:
            self.set_value(initial_value)

    def start_input(self):
        self.is_active = True
        self.current_input = ""

    def stop_input(self):
        self.is_active = False

    def add_digit(self, digit):
        if not self.is_active:
            return

        allowed_characters = set("0123456789.-")
        if digit not in allowed_characters:
            return

        if digit == "." and "." in self.current_input:
            return

        if digit == "-" and self.current_input:
            return

        self.current_input += digit

    def remove_last(self):
        if not self.is_active or not self.current_input:
            return
        self.current_input = self.current_input[:-1]

    def clear(self):
        self.current_input = ""
        self.value = None

    def parse_value(self):
        if not self.current_input:
            return None

        try:
            self.value = float(self.current_input)
        except ValueError:
            return None
        return self.value

    def set_value(self, value):
        if not isinstance(value, (int, float)):
            return
        self.value = float(value)
        self.current_input = str(value)

    def get_value(self):
        return self.value

    def is_valid(self, minimum=20.0, maximum=20000.0):
        return self.value is not None and minimum <= self.value <= maximum


class KeyInput:
    KEYS_ON_SCREEN = ["A", "W", "S", "E", "D", "F", "T", "G", "Y", "H", "U", "J"]

    def __init__(self):
        self.key_map = {}
        self.active_keys = set()
        self.listener_running = False
        self.last_pressed_key = None

    def setup_key_map(self, dropdown_value=None, text_value=None):
        self.key_map.clear()
        self.active_keys.clear()
        self.last_pressed_key = None
        for key_name in self.KEYS_ON_SCREEN:
            self.key_map[key_name] = key_name

    def on_press(self, key):
        key_name = str(key).upper()
        if key_name in self.key_map and key_name not in self.active_keys:
            self.active_keys.add(key_name)
            self.last_pressed_key = key_name

    def on_release(self, key):
        key_name = str(key).upper()
        self.active_keys.discard(key_name)
        if key_name == self.last_pressed_key:
            self.last_pressed_key = sorted(self.active_keys)[-1] if self.active_keys else None

    def start_listener(self):
        self.listener_running = True

    def stop_listener(self):
        self.listener_running = False

    def get_active_notes(self):
        return [key for key in self.key_map if key in self.active_keys]

    def is_key_active(self, key):
        return str(key).upper() in self.active_keys

    def clear_active_keys(self):
        self.active_keys.clear()
        self.last_pressed_key = None


class SynthMockUI:
    WHITE_KEYS = ["A", "S", "D", "F", "G", "H", "J"]
    BLACK_KEYS = ["W", "E", "T", "Y", "U"]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CS375 Synthesizer UI Mockup")
        self.root.geometry("980x540")
        self.root.configure(bg="#f2efe8")
        self.root.minsize(860, 500)

        self.key_input = KeyInput()
        self.text_box_input = NumberInput()
        self.dropdown_var = tk.StringVar(value="PLACEHOLDER")
        self.text_box_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="")
        self.current_key_var = tk.StringVar(value="Current note: none")
        self.key_widgets = {}

        self.key_input.setup_key_map()

        self._configure_styles()
        self._build_layout()
        self.start_listener()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Card.TFrame", background="#fffaf2")
        style.configure("Header.TLabel", font=("Georgia", 22, "bold"), background="#f2efe8", foreground="#1f2933")
        style.configure("Sub.TLabel", font=("Segoe UI", 10), background="#f2efe8", foreground="#52606d")
        style.configure("CardTitle.TLabel", font=("Segoe UI", 11, "bold"), background="#fffaf2", foreground="#1f2933")
        style.configure("CardBody.TLabel", font=("Segoe UI", 10), background="#fffaf2", foreground="#334e68")
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))

    def _build_layout(self):
        outer = ttk.Frame(self.root, padding=20, style="Card.TFrame")
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        header = ttk.Frame(self.root)
        header.place(x=32, y=22)

        ttk.Label(header, text="Synthesizer UI!! :D", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Visual-only prototype.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        content = tk.Frame(outer, bg="#fffaf2")
        content.pack(fill="both", expand=True)

        left_panel = tk.Frame(content, bg="#fffaf2", width=280)
        left_panel.pack(side="left", fill="y", padx=(8, 20), pady=(52, 8))
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(content, bg="#fffaf2")
        right_panel.pack(side="left", fill="both", expand=True, pady=(52, 8))

        self._build_controls(left_panel)
        self._build_keyboard(right_panel)

    def _build_controls(self, parent):
        config_card = tk.Frame(parent, bg="#f8f2e7", bd=0, highlightthickness=1, highlightbackground="#dfd2bd")
        config_card.pack(fill="x", pady=(0, 14))

        ttk.Label(config_card, text="Quick Controls", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(14, 4))
        ttk.Label(
            config_card,
            text="These are placeholders for sliders, knobs, and preset controls.",
            style="CardBody.TLabel",
        ).pack(anchor="w", padx=14, pady=(0, 10))

        scale_box = ttk.Combobox(
            config_card,
            textvariable=self.dropdown_var,
            values=["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"],
            state="readonly",
        )
        scale_box.pack(fill="x", padx=14, pady=(10, 12))
        scale_box.bind("<<ComboboxSelected>>", self._apply_settings)

        entry = ttk.Entry(config_card, textvariable=self.text_box_var)
        entry.pack(fill="x", padx=14, pady=(0, 10))
        entry.bind("<Return>", self._apply_settings)

        ttk.Button(
            config_card,
            text="Apply Settings",
            style="Primary.TButton",
            command=self._apply_settings,
        ).pack(fill="x", padx=14, pady=(0, 14))

        slider_card = tk.Frame(parent, bg="#edf2f7", bd=0, highlightthickness=1, highlightbackground="#cbd2d9")
        slider_card.pack(fill="x", pady=(0, 14))

        self._build_placeholder_slider(slider_card, 35)
        self._build_placeholder_slider(slider_card, 60)
        self._build_placeholder_slider(slider_card, 45)

        status_card = tk.Frame(parent, bg="#e8f1eb", bd=0, highlightthickness=1, highlightbackground="#b7d0be")
        status_card.pack(fill="x")

        ttk.Label(status_card, text="Status", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(14, 6))
        ttk.Label(status_card, textvariable=self.status_var, style="CardBody.TLabel", wraplength=220).pack(anchor="w", padx=14)
        ttk.Label(status_card, textvariable=self.current_key_var, style="CardBody.TLabel", wraplength=220).pack(
            anchor="w",
            padx=14,
            pady=(6, 14),
        )

    def _build_placeholder_slider(self, parent, value):
        row = tk.Frame(parent, bg="#edf2f7")
        row.pack(fill="x", padx=14, pady=(0, 10))

        scale = ttk.Scale(row, from_=0, to=100)
        scale.set(value)
        scale.pack(fill="x")

    def _build_keyboard(self, parent):
        title_row = tk.Frame(parent, bg="#fffaf2")
        title_row.pack(fill="x", pady=(0, 12))

        tk.Label(
            title_row,
            text="Keyboard Mockup",
            bg="#fffaf2",
            fg="#1f2933",
            font=("Georgia", 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_row,
            text="Mapped keys light up when pressed on your keyboard or clicked with the mouse.",
            bg="#fffaf2",
            fg="#52606d",
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        keyboard_frame = tk.Frame(parent, bg="#d9cab3", padx=18, pady=18)
        keyboard_frame.pack(fill="both", expand=True)

        black_row = tk.Frame(keyboard_frame, bg="#d9cab3", height=110)
        black_row.pack(fill="x")

        black_positions = {"W": 1, "E": 2, "T": 4, "Y": 5, "U": 6}
        for key_name, column in black_positions.items():
            spacer = tk.Frame(black_row, bg="#d9cab3", width=18)
            spacer.grid(row=0, column=column * 2, padx=8)
            button = tk.Label(
                black_row,
                text=key_name,
                bg="#1f2933",
                fg="#fffaf2",
                width=6,
                height=5,
                relief="flat",
                font=("Segoe UI", 11, "bold"),
                cursor="hand2",
            )
            button.grid(row=0, column=column * 2 + 1, padx=2)
            self.key_widgets[key_name] = button
            self._bind_mouse_events(button, key_name)

        white_row = tk.Frame(keyboard_frame, bg="#d9cab3")
        white_row.pack(fill="x", pady=(8, 0))

        for key_name in self.WHITE_KEYS:
            button = tk.Label(
                white_row,
                text=key_name,
                bg="#fffaf2",
                fg="#1f2933",
                width=9,
                height=9,
                relief="solid",
                bd=1,
                font=("Segoe UI", 12, "bold"),
                cursor="hand2",
            )
            button.pack(side="left", padx=3)
            self.key_widgets[key_name] = button
            self._bind_mouse_events(button, key_name)

    def _bind_mouse_events(self, widget, key_name):
        widget.bind("<ButtonPress-1>", lambda _event, key=key_name: self._press_key(key))
        widget.bind("<ButtonRelease-1>", lambda _event, key=key_name: self._release_key(key))

    def _apply_settings(self, _event=None):
        self.text_box_input.start_input()
        self.text_box_input.clear()

        for character in self.text_box_var.get():
            self.text_box_input.add_digit(character)

        typed_value = self.text_box_input.parse_value()
        self.text_box_input.stop_input()
        self.key_input.setup_key_map(self.dropdown_var.get(), typed_value)
        self.clear_active_keys()
        self._update_active_notes_label()

    def _press_key(self, key_name):
        self.key_input.on_press(key_name)
        self._set_key_visual(key_name, pressed=True)
        if key_name in self.key_input.key_map:
            self.status_var.set(f"Pressed {key_name}")
        self._update_active_notes_label()

    def _release_key(self, key_name):
        self.key_input.on_release(key_name)
        self._set_key_visual(key_name, pressed=False)
        self.status_var.set(f"Released {key_name}")
        self._update_active_notes_label()

    def _set_key_visual(self, key_name, pressed):
        widget = self.key_widgets.get(key_name)
        if widget is None:
            return

        if key_name in self.BLACK_KEYS:
            widget.configure(bg="#ff9f1c" if pressed else "#1f2933", fg="#1f2933" if pressed else "#fffaf2")
        else:
            widget.configure(bg="#7bd389" if pressed else "#fffaf2", fg="#1f2933")

    def _update_active_notes_label(self):
        current_key = self.key_input.last_pressed_key
        if current_key:
            self.current_key_var.set(f"Current note: {current_key}")
        else:
            self.current_key_var.set("Current note: none")

    def _handle_key_press(self, event):
        key_name = event.keysym.upper()
        if key_name in self.key_input.key_map:
            self._press_key(key_name)

    def _handle_key_release(self, event):
        key_name = event.keysym.upper()
        if key_name in self.key_input.key_map:
            self._release_key(key_name)

    def start_listener(self):
        if self.key_input.listener_running:
            return
        self.key_input.start_listener()
        self.root.bind("<KeyPress>", self._handle_key_press)
        self.root.bind("<KeyRelease>", self._handle_key_release)

    def stop_listener(self):
        if not self.key_input.listener_running:
            return
        self.key_input.stop_listener()
        self.root.unbind("<KeyPress>")
        self.root.unbind("<KeyRelease>")

    def get_active_notes(self):
        return self.key_input.get_active_notes()

    def is_key_active(self, key):
        return self.key_input.is_key_active(key)

    def clear_active_keys(self):
        for key_name in list(self.key_input.active_keys):
            self._set_key_visual(key_name, pressed=False)
        self.key_input.clear_active_keys()
        self._update_active_notes_label()

    def run(self):
        self.root.mainloop()


def main():
    app = SynthMockUI()
    app.run()


if __name__ == "__main__":
    main()
