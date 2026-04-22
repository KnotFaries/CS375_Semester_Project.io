from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk

import numpy as np
import sounddevice as sd


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from SoundGenerationClasses import WaveTable as wt
from SoundGenerationClasses.synthictest2 import Envelope, Preset, SAMPLE_RATE


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

    def is_valid(self, minimum=20.0, maximum=20000.0):
        return self.value is not None and minimum <= self.value <= maximum


class KeyInput:
    KEYS_ON_SCREEN = ["A", "W", "S", "E", "D", "F", "T", "G", "Y", "H", "U", "J"]

    def __init__(self):
        self.key_map = {}
        self.active_keys = set()
        self.listener_running = False
        self.last_pressed_key = None

    def setup_key_map(self, scale):
        self.key_map.clear()
        self.active_keys.clear()
        self.last_pressed_key = None

        for index, key_name in enumerate(self.KEYS_ON_SCREEN):
            if index < len(scale):
                self.key_map[key_name] = scale[index]

    def on_press(self, key_name):
        key_name = str(key_name).upper()
        if key_name in self.key_map and key_name not in self.active_keys:
            self.active_keys.add(key_name)
            self.last_pressed_key = key_name
            return self.key_map[key_name]
        return None

    def on_release(self, key_name):
        key_name = str(key_name).upper()
        self.active_keys.discard(key_name)
        if key_name == self.last_pressed_key:
            self.last_pressed_key = sorted(self.active_keys)[-1] if self.active_keys else None

    def start_listener(self):
        self.listener_running = True

    def stop_listener(self):
        self.listener_running = False

    def clear_active_keys(self):
        self.active_keys.clear()
        self.last_pressed_key = None


class SynthAudioEngine:
    def __init__(self):
        self.preset = Preset()
        self.envelope = Envelope()
        self.waveforms = {
            "sine": np.sin,
            "square": self._square_wave,
            "saw": self._saw_wave,
            "triangle": self._triangle_wave,
        }

    def calculate_scale(self, base_freq, scale_type):
        return self.preset.calculate_scale(base_freq, scaletype=scale_type)

    def play_note(self, freq, settings):
        signal = wt.generate_wavetable(freq, settings["duration"], self.waveforms[settings["waveform"]], SAMPLE_RATE)
        signal = wt.create_envelope(signal, settings["gain"], settings["wavetable_attack"], settings["wavetable_release"])
        envelope_settings = self._fit_envelope_to_duration(settings)
        signal = self.envelope.apply(
            signal,
            attack=envelope_settings["env_attack"],
            decay=envelope_settings["env_decay"],
            sustain=envelope_settings["env_sustain"],
            release=envelope_settings["env_release"],
        )
        signal = np.clip(signal, -1.0, 1.0)
        sd.play(signal, SAMPLE_RATE, blocking=False)
        return signal

    @staticmethod
    def _fit_envelope_to_duration(settings):
        duration = max(0.0, float(settings["duration"]))
        attack = max(0.0, float(settings["env_attack"]))
        decay = max(0.0, float(settings["env_decay"]))
        release = max(0.0, float(settings["env_release"]))

        if attack > duration:
            attack = duration

        remaining = max(0.0, duration - attack)
        if decay > remaining:
            decay = remaining

        remaining = max(0.0, duration - attack - decay)
        if release > remaining:
            release = remaining

        return {
            "env_attack": attack,
            "env_decay": decay,
            "env_sustain": float(settings["env_sustain"]),
            "env_release": release,
        }

    @staticmethod
    def _square_wave(phase):
        return np.sign(np.sin(phase))

    @staticmethod
    def _saw_wave(phase):
        cycle_position = phase / (2 * np.pi)
        return 2 * (cycle_position - np.floor(0.5 + cycle_position))

    @staticmethod
    def _triangle_wave(phase):
        return 2 * np.arcsin(np.sin(phase)) / np.pi


class SynthMockUI:
    WHITE_KEYS = ["A", "S", "D", "F", "G", "H", "J"]
    BLACK_KEYS = ["W", "E", "T", "Y", "U"]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CS375 Synthesizer UI Mockup")
        self.root.geometry("1120x760")
        self.root.configure(bg="#f2efe8")
        self.root.minsize(980, 700)

        self.audio_engine = SynthAudioEngine()
        self.key_input = KeyInput()
        self.text_box_input = NumberInput(initial_value=261.63)

        self.scale_var = tk.StringVar(value="minor")
        self.waveform_var = tk.StringVar(value="saw")
        self.text_box_var = tk.StringVar(value="261.63")
        self.status_var = tk.StringVar(value="")
        self.current_key_var = tk.StringVar(value="Current note: none")

        self.key_widgets = {}
        self.slider_vars = {}

        self._configure_styles()
        self._build_layout()
        self.start_listener()
        self._apply_settings()
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.after(100, self.root.focus_force)

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
            text="The mock UI now matches the current WaveTable and synthictest2 controls.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        content = tk.Frame(outer, bg="#fffaf2")
        content.pack(fill="both", expand=True)

        left_panel = tk.Frame(content, bg="#fffaf2", width=330)
        left_panel.pack(side="left", fill="y", padx=(8, 20), pady=(52, 8))
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(content, bg="#fffaf2")
        right_panel.pack(side="left", fill="both", expand=True, pady=(52, 8))

        self._build_controls(left_panel)
        self._build_keyboard(right_panel)

    def _build_controls(self, parent):
        config_card = tk.Frame(parent, bg="#f8f2e7", bd=0, highlightthickness=1, highlightbackground="#dfd2bd")
        config_card.pack(fill="x", pady=(0, 14))

        ttk.Label(config_card, text="Preset + Mapping", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(14, 4))
        ttk.Label(
            config_card,
            text="Scale type, base frequency, and waveform come from the current sound classes.",
            style="CardBody.TLabel",
            wraplength=280,
        ).pack(anchor="w", padx=14, pady=(0, 10))

        self._build_dropdown(config_card, "Scale Type", self.scale_var, ["chroma", "major", "minor", "penta"])
        self._build_dropdown(config_card, "Waveform", self.waveform_var, ["sine", "square", "saw", "triangle"])

        ttk.Label(config_card, text="Base Frequency (Hz)", style="CardBody.TLabel").pack(anchor="w", padx=14, pady=(2, 4))
        entry = ttk.Entry(config_card, textvariable=self.text_box_var)
        entry.pack(fill="x", padx=14, pady=(0, 10))
        entry.bind("<Return>", self._apply_settings)

        ttk.Button(
            config_card,
            text="Apply Settings",
            style="Primary.TButton",
            command=self._apply_settings,
        ).pack(fill="x", padx=14, pady=(0, 14))

        wavetable_card = tk.Frame(parent, bg="#edf2f7", bd=0, highlightthickness=1, highlightbackground="#cbd2d9")
        wavetable_card.pack(fill="x", pady=(0, 14))

        ttk.Label(wavetable_card, text="WaveTable", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(14, 4))
        ttk.Label(
            wavetable_card,
            text="These sliders mirror WaveTable duration, gain, attack, and release.",
            style="CardBody.TLabel",
            wraplength=280,
        ).pack(anchor="w", padx=14, pady=(0, 10))

        self._build_slider(wavetable_card, "Duration (seconds)", "duration", 1, 5, 1, 0)
        self._build_slider(wavetable_card, "Gain (dB)", "gain", -30, 0, -10, 0)
        self._build_slider(wavetable_card, "Attack (samples)", "wavetable_attack", 0, 5000, 1000, 0)
        self._build_slider(wavetable_card, "Release (samples)", "wavetable_release", 0, 5000, 3000, 0)

        envelope_card = tk.Frame(parent, bg="#f4efe6", bd=0, highlightthickness=1, highlightbackground="#d7c7af")
        envelope_card.pack(fill="x", pady=(0, 14))

        ttk.Label(envelope_card, text="Envelope", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(14, 4))
        ttk.Label(
            envelope_card,
            text="These sliders mirror synthictest2 attack, decay, sustain, and release.",
            style="CardBody.TLabel",
            wraplength=280,
        ).pack(anchor="w", padx=14, pady=(0, 10))

        self._build_slider(envelope_card, "Attack (seconds)", "env_attack", 0.0, 1.0, 0.01, 2)
        self._build_slider(envelope_card, "Decay (seconds)", "env_decay", 0.0, 1.0, 0.10, 2)
        self._build_slider(envelope_card, "Sustain", "env_sustain", 0.0, 1.0, 1.0, 2)
        self._build_slider(envelope_card, "Release (seconds)", "env_release", 0.0, 5.0, 0.25, 2)

        status_card = tk.Frame(parent, bg="#e8f1eb", bd=0, highlightthickness=1, highlightbackground="#b7d0be")
        status_card.pack(fill="x")

        ttk.Label(status_card, text="Status", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(14, 6))
        ttk.Label(status_card, textvariable=self.status_var, style="CardBody.TLabel", wraplength=280).pack(anchor="w", padx=14)
        ttk.Label(status_card, textvariable=self.current_key_var, style="CardBody.TLabel", wraplength=280).pack(
            anchor="w",
            padx=14,
            pady=(6, 14),
        )

    def _build_dropdown(self, parent, label_text, variable, values):
        ttk.Label(parent, text=label_text, style="CardBody.TLabel").pack(anchor="w", padx=14, pady=(8, 4))
        dropdown = ttk.Combobox(parent, textvariable=variable, values=values, state="readonly")
        dropdown.pack(fill="x", padx=14, pady=(0, 10))
        dropdown.bind("<<ComboboxSelected>>", self._apply_settings)

    def _build_slider(self, parent, label_text, key, minimum, maximum, value, decimals):
        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(fill="x", padx=14, pady=(0, 10))

        value_var = tk.DoubleVar(value=value)
        self.slider_vars[key] = value_var

        label_row = tk.Frame(row, bg=parent["bg"])
        label_row.pack(fill="x")

        tk.Label(label_row, text=label_text, bg=parent["bg"], fg="#1f2933", font=("Segoe UI", 10)).pack(side="left")
        value_label = tk.Label(
            label_row,
            text=self._format_slider_value(value, decimals),
            bg=parent["bg"],
            fg="#52606d",
            font=("Segoe UI", 9),
        )
        value_label.pack(side="right")

        slider = ttk.Scale(row, from_=minimum, to=maximum, variable=value_var)
        slider.pack(fill="x", pady=(4, 0))
        slider.bind(
            "<B1-Motion>",
            lambda _event, var=value_var, label=value_label, digits=decimals: label.configure(
                text=self._format_slider_value(var.get(), digits)
            ),
        )
        slider.bind(
            "<ButtonRelease-1>",
            lambda _event, var=value_var, label=value_label, digits=decimals: label.configure(
                text=self._format_slider_value(var.get(), digits)
            ),
        )

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
            text="Mapped keys light up when pressed and trigger the current note settings.",
            bg="#fffaf2",
            fg="#52606d",
            font=("Segoe UI", 10),
            wraplength=700,
            justify="left",
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
                width=7,
                height=5,
                relief="flat",
                font=("Segoe UI", 9, "bold"),
                cursor="hand2",
                justify="center",
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
                width=10,
                height=9,
                relief="solid",
                bd=1,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                justify="center",
            )
            button.pack(side="left", padx=3)
            self.key_widgets[key_name] = button
            self._bind_mouse_events(button, key_name)

    def _bind_mouse_events(self, widget, key_name):
        widget.bind("<ButtonPress-1>", lambda _event, key=key_name: self._handle_mouse_press(key))
        widget.bind("<ButtonRelease-1>", lambda _event, key=key_name: self._release_key(key))

    def _handle_mouse_press(self, key_name):
        self.root.focus_force()
        self._press_key(key_name)

    def _apply_settings(self, _event=None):
        self.text_box_input.start_input()
        self.text_box_input.clear()

        for character in self.text_box_var.get():
            self.text_box_input.add_digit(character)

        typed_value = self.text_box_input.parse_value()
        self.text_box_input.stop_input()

        if typed_value is None or not self.text_box_input.is_valid():
            self.status_var.set("Base frequency must be a number between 20 and 20000 Hz.")
            return

        scale = self.audio_engine.calculate_scale(typed_value, self.scale_var.get())
        self.key_input.setup_key_map(scale)
        self.clear_active_keys()
        self._refresh_keyboard_labels()
        self.status_var.set(
            f"Loaded {self.scale_var.get()} scale from {typed_value:.2f} Hz with {self.waveform_var.get()} waveform."
        )
        self._update_active_notes_label()

    def _press_key(self, key_name):
        if key_name not in self.key_input.key_map:
            self.status_var.set(f"{key_name} is not mapped in the current scale.")
            return

        frequency = self.key_input.on_press(key_name)
        if frequency is None:
            return

        self._set_key_visual(key_name, True)
        self.root.update_idletasks()
        self.root.after(0, lambda freq=frequency, key=key_name: self._play_note_for_key(key, freq))

        self._update_active_notes_label()

    def _play_note_for_key(self, key_name, frequency):
        try:
            self.audio_engine.play_note(frequency, self._get_audio_settings())
            self.status_var.set(f"Pressed {key_name} at {frequency:.2f} Hz.")
        except Exception as error:
            self.status_var.set(f"Audio playback error: {error}")

    def _release_key(self, key_name):
        if key_name not in self.key_input.key_map:
            return

        self.key_input.on_release(key_name)
        self._set_key_visual(key_name, False)
        self.status_var.set(f"Released {key_name}")
        self._update_active_notes_label()

    def _set_key_visual(self, key_name, pressed):
        widget = self.key_widgets.get(key_name)
        if widget is None:
            return

        is_mapped = key_name in self.key_input.key_map
        if key_name in self.BLACK_KEYS:
            default_bg = "#1f2933" if is_mapped else "#5f6c7b"
            default_fg = "#fffaf2" if is_mapped else "#d9e2ec"
            widget.configure(bg="#ff9f1c" if pressed else default_bg, fg="#1f2933" if pressed else default_fg)
        else:
            default_bg = "#fffaf2" if is_mapped else "#e4e7eb"
            widget.configure(bg="#7bd389" if pressed else default_bg, fg="#1f2933")

    def _update_active_notes_label(self):
        current_key = self.key_input.last_pressed_key
        if current_key:
            frequency = self.key_input.key_map.get(current_key)
            if frequency is not None:
                self.current_key_var.set(f"Current note: {current_key} ({frequency:.2f} Hz)")
                return
        self.current_key_var.set("Current note: none")

    def _handle_key_press(self, event):
        key_name = event.keysym.upper()
        if key_name in self.key_widgets:
            self._press_key(key_name)

    def _handle_key_release(self, event):
        key_name = event.keysym.upper()
        if key_name in self.key_widgets:
            self._release_key(key_name)

    def _refresh_keyboard_labels(self):
        for key_name, widget in self.key_widgets.items():
            frequency = self.key_input.key_map.get(key_name)
            if frequency is None:
                widget.configure(text=f"{key_name}\n--")
            else:
                widget.configure(text=f"{key_name}\n{frequency:.2f}")
            self._set_key_visual(key_name, False)

    def _get_audio_settings(self):
        return {
            "duration": max(1, int(round(self.slider_vars["duration"].get()))),
            "gain": int(round(self.slider_vars["gain"].get())),
            "wavetable_attack": int(round(self.slider_vars["wavetable_attack"].get())),
            "wavetable_release": int(round(self.slider_vars["wavetable_release"].get())),
            "env_attack": round(self.slider_vars["env_attack"].get(), 2),
            "env_decay": round(self.slider_vars["env_decay"].get(), 2),
            "env_sustain": round(self.slider_vars["env_sustain"].get(), 2),
            "env_release": round(self.slider_vars["env_release"].get(), 2),
            "waveform": self.waveform_var.get(),
        }

    def _format_slider_value(self, value, decimals):
        if decimals == 0:
            return str(int(round(value)))
        return f"{value:.{decimals}f}"

    def start_listener(self):
        if self.key_input.listener_running:
            return
        self.key_input.start_listener()
        self.root.bind_all("<KeyPress>", self._handle_key_press)
        self.root.bind_all("<KeyRelease>", self._handle_key_release)

    def stop_listener(self):
        if not self.key_input.listener_running:
            return
        self.key_input.stop_listener()
        self.root.unbind_all("<KeyPress>")
        self.root.unbind_all("<KeyRelease>")

    def clear_active_keys(self):
        for key_name in list(self.key_input.active_keys):
            self._set_key_visual(key_name, False)
        self.key_input.clear_active_keys()
        self._update_active_notes_label()

    def _close(self):
        self.stop_listener()
        sd.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    app = SynthMockUI()
    app.run()


if __name__ == "__main__":
    main()
