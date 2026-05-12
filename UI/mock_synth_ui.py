from pathlib import Path
import os
import sys
import threading


def _configure_tcl_tk_paths():
    base_paths = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_paths.append(Path(sys._MEIPASS))
    base_paths.append(Path(sys.executable).resolve().parent)
    base_paths.append(Path(sys.base_prefix))

    for base_path in base_paths:
        tcl_library = base_path / "tcl" / "tcl8.6"
        tk_library = base_path / "tcl" / "tk8.6"
        if tcl_library.exists() and tk_library.exists():
            os.environ.setdefault("TCL_LIBRARY", str(tcl_library))
            os.environ.setdefault("TK_LIBRARY", str(tk_library))
            return


_configure_tcl_tk_paths()

import tkinter as tk
from tkinter import filedialog, ttk
import wave

import numpy as np
import sounddevice as sd


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from SoundGenerationClasses.synthictest2 import Preset, SAMPLE_RATE
except ModuleNotFoundError:
    from synthictest2 import Preset, SAMPLE_RATE


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
    KEYS_ON_SCREEN = ["A", "W", "S", "E", "D", "F", "T", "G", "Y", "H", "U", "J", "K"]

    def __init__(self):
        self.key_map = {}
        self.active_keys = set()
        self.listener_running = False
        self.last_pressed_key = None

    def setup_key_map(self, notes):
        self.key_map.clear()
        self.active_keys.clear()
        self.last_pressed_key = None

        for index, note in enumerate(notes):
            if isinstance(note, dict):
                self.key_map[note["key"]] = note["frequency"]
            elif index < len(self.KEYS_ON_SCREEN):
                self.key_map[self.KEYS_ON_SCREEN[index]] = note

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
    TWO_PI = 2 * np.pi
    MIN_TAP_SECONDS = 0.05

    def __init__(self):
        self.preset = Preset()
        self.lock = threading.RLock()
        self.voices = []
        self.stream = None
        self.recording_active = False
        self.recording_chunks = []
        self.recording_has_audio = False
        self.last_stream_status = None

    def calculate_scale(self, base_freq, scale_type):
        return self.preset.calculate_scale(base_freq, scaletype=scale_type)

    def note_on(self, key_name, freq, settings):
        self.start_stream()
        with self.lock:
            self.voices.append(self._create_voice(key_name, freq, settings))

    def note_off(self, key_name):
        with self.lock:
            for voice in self.voices:
                if voice["key_name"] == key_name and voice["stage"] != "release":
                    self._begin_release(voice)

    def clear_voices(self):
        with self.lock:
            self.voices.clear()

    def start_recording(self):
        self.start_stream()
        with self.lock:
            self.recording_chunks = []
            self.recording_has_audio = False
            self.recording_active = True

    def stop_recording(self):
        with self.lock:
            self.recording_active = False
            return self.get_recording_signal()

    def get_recording_signal(self):
        if not self.recording_chunks:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(self.recording_chunks).astype(np.float32, copy=False)

    def close(self):
        with self.lock:
            self.voices.clear()
            self.recording_active = False
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def start_stream(self):
        if self.stream is not None and self.stream.active:
            return

        if self.stream is not None:
            self.stream.close()
            self.stream = None

        stream = sd.OutputStream(
            channels=1,
            samplerate=SAMPLE_RATE,
            dtype="float32",
            blocksize=512,
            callback=self._audio_callback,
        )
        try:
            stream.start()
        except Exception:
            stream.close()
            raise
        self.stream = stream

    def _audio_callback(self, outdata, frames, _time_info, status):
        if status:
            self.last_stream_status = str(status)

        with self.lock:
            mixed = np.zeros(frames, dtype=np.float32)
            live_voices = []

            for voice in self.voices:
                mixed += self._render_voice(voice, frames)
                if not voice["finished"]:
                    live_voices.append(voice)

            self.voices = live_voices
            output = np.tanh(mixed).astype(np.float32)

            if self.recording_active:
                self.recording_chunks.append(output.copy())
                if np.any(np.abs(output) > 0.0001):
                    self.recording_has_audio = True

        outdata[:, 0] = output

    def _create_voice(self, key_name, freq, settings):
        attack_samples = int(max(0.0, float(settings["env_attack"])) * SAMPLE_RATE)
        decay_samples = int(max(0.0, float(settings["env_decay"])) * SAMPLE_RATE)
        release_samples = int(max(0.0, float(settings["env_release"])) * SAMPLE_RATE)
        sustain = min(1.0, max(0.0, float(settings["env_sustain"])))
        gain_amp = 10 ** (float(settings["gain"]) / 20)

        return {
            "key_name": key_name,
            "frequency": float(freq),
            "waveform": settings["waveform"],
            "phase": 0.0,
            "phase_increment": self.TWO_PI * float(freq) / SAMPLE_RATE,
            "gain_amp": gain_amp,
            "attack_samples": attack_samples,
            "decay_samples": decay_samples,
            "sustain": sustain,
            "release_samples": release_samples,
            "stage": "attack",
            "stage_position": 0,
            "age_samples": 0,
            "min_tap_samples": int(self.MIN_TAP_SECONDS * SAMPLE_RATE),
            "release_requested": False,
            "level": 0.0,
            "release_start_level": 0.0,
            "finished": False,
        }

    def _render_voice(self, voice, frames):
        phases = (voice["phase"] + voice["phase_increment"] * np.arange(frames)) % self.TWO_PI
        voice["phase"] = (voice["phase"] + voice["phase_increment"] * frames) % self.TWO_PI

        oscillator = self._render_waveform(voice["waveform"], phases)
        envelope = np.empty(frames, dtype=np.float32)
        for index in range(frames):
            envelope[index] = self._advance_envelope(voice)

        return (oscillator * envelope * voice["gain_amp"]).astype(np.float32)

    def _advance_envelope(self, voice):
        if not voice["finished"]:
            voice["age_samples"] += 1
            if (
                voice["release_requested"]
                and voice["age_samples"] >= voice["min_tap_samples"]
                and voice["stage"] != "release"
            ):
                self._begin_release(voice, force=True)

        while True:
            stage = voice["stage"]

            if voice["finished"]:
                return 0.0

            if stage == "attack":
                if voice["attack_samples"] <= 0:
                    voice["level"] = 1.0
                    voice["stage"] = "decay"
                    voice["stage_position"] = 0
                    continue

                voice["stage_position"] += 1
                voice["level"] = min(1.0, voice["stage_position"] / voice["attack_samples"])
                if voice["stage_position"] >= voice["attack_samples"]:
                    voice["stage"] = "decay"
                    voice["stage_position"] = 0
                return voice["level"]

            if stage == "decay":
                if voice["decay_samples"] <= 0:
                    voice["level"] = voice["sustain"]
                    voice["stage"] = "sustain"
                    voice["stage_position"] = 0
                    continue

                voice["stage_position"] += 1
                progress = min(1.0, voice["stage_position"] / voice["decay_samples"])
                voice["level"] = 1.0 + (voice["sustain"] - 1.0) * progress
                if voice["stage_position"] >= voice["decay_samples"]:
                    voice["stage"] = "sustain"
                    voice["stage_position"] = 0
                return voice["level"]

            if stage == "sustain":
                voice["level"] = voice["sustain"]
                return voice["level"]

            if stage == "release":
                if voice["release_samples"] <= 0:
                    voice["level"] = 0.0
                    voice["finished"] = True
                    return 0.0

                voice["stage_position"] += 1
                progress = min(1.0, voice["stage_position"] / voice["release_samples"])
                voice["level"] = voice["release_start_level"] * (1.0 - progress)
                if voice["stage_position"] >= voice["release_samples"]:
                    voice["level"] = 0.0
                    voice["finished"] = True
                return max(0.0, voice["level"])

            voice["finished"] = True
            return 0.0

    def _begin_release(self, voice, force=False):
        if voice["stage"] == "release" or voice["finished"]:
            return
        if not force and voice["age_samples"] < voice["min_tap_samples"]:
            voice["release_requested"] = True
            return

        voice["stage"] = "release"
        voice["stage_position"] = 0
        voice["release_start_level"] = voice["level"]
        voice["release_requested"] = False

    @staticmethod
    def _render_waveform(waveform, phase):
        if waveform == "square":
            return np.where(np.sin(phase) >= 0, 1.0, -1.0)
        if waveform == "saw":
            cycle_position = phase / (2 * np.pi)
            return 2 * (cycle_position - np.floor(0.5 + cycle_position))
        if waveform == "triangle":
            return 2 * np.arcsin(np.sin(phase)) / np.pi
        return np.sin(phase)


class SynthMockUI:
    BASE_BG = "#1f2933"
    PANEL_BG = "#263545"
    CARD_BG = "#2f3d4d"
    CARD_ALT_BG = "#34475a"
    TEXT_COLOR = "#e6edf3"
    MUTED_TEXT = "#b7c4d1"
    ACCENT = "#7c93b2"
    WHITE_KEY = "#f5f7fa"
    WHITE_KEY_DISABLED = "#d8dee6"
    BLACK_KEY = "#3f4a58"
    BLACK_KEY_DISABLED = "#596474"
    KEY_ACTIVE = "#84a9d6"
    DARK_TEXT = "#111827"

    WHITE_KEYS = ["A", "S", "D", "F", "G", "H", "J", "K"]
    BLACK_KEYS = ["W", "E", "T", "Y", "U"]
    KEY_ORDER = ["A", "W", "S", "E", "D", "F", "T", "G", "Y", "H", "U", "J", "K"]
    KEY_FOR_SEMITONE = {
        0: "A",
        1: "W",
        2: "S",
        3: "E",
        4: "D",
        5: "F",
        6: "T",
        7: "G",
        8: "Y",
        9: "H",
        10: "U",
        11: "J",
        12: "K",
    }
    KEY_SOLFEGE = {
        "A": "Do",
        "W": "Ra",
        "S": "Re",
        "E": "Me",
        "D": "Mi",
        "F": "Fa",
        "T": "Se",
        "G": "Sol",
        "Y": "Le",
        "H": "La",
        "U": "Te",
        "J": "Ti",
        "K": "Do",
    }
    SCALE_DEGREES = {
        "chroma": [
            (0, "Do"),
            (1, "Ra"),
            (2, "Re"),
            (3, "Me"),
            (4, "Mi"),
            (5, "Fa"),
            (6, "Se"),
            (7, "Sol"),
            (8, "Le"),
            (9, "La"),
            (10, "Te"),
            (11, "Ti"),
            (12, "Do"),
        ],
        "major": [(0, "Do"), (2, "Re"), (4, "Mi"), (5, "Fa"), (7, "Sol"), (9, "La"), (11, "Ti"), (12, "Do")],
        "minor": [(0, "Do"), (2, "Re"), (3, "Me"), (5, "Fa"), (7, "Sol"), (8, "Le"), (10, "Te"), (12, "Do")],
        "penta": [(0, "Do"), (2, "Re"), (4, "Mi"), (7, "Sol"), (9, "La"), (12, "Do")],
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CS375 Synthesizer UI Mockup")
        self.root.geometry("1220x760")
        self.root.configure(bg=self.BASE_BG)
        self.root.minsize(1080, 700)

        self.audio_engine = SynthAudioEngine()
        self.key_input = KeyInput()
        self.text_box_input = NumberInput(initial_value=261.63)

        self.scale_var = tk.StringVar(value="minor")
        self.waveform_var = tk.StringVar(value="saw")
        self.text_box_var = tk.StringVar(value="261.63")
        self.status_var = tk.StringVar(value="")
        self.current_key_var = tk.StringVar(value="Current note: none")

        self.key_widgets = {}
        self.key_note_labels = {}
        self.slider_vars = {}
        self.last_rendered_signal = None
        self.last_rendered_frequency = None
        self.recording_var = tk.StringVar(value="Recording: idle")
        self.recording_active = False
        self.recording_start_time = None
        self.recorded_signal = np.zeros(0, dtype=np.float32)
        self.recording_has_audio = False
        self.controls_canvas = None
        self.controls_inner = None
        self.controls_window = None

        self._configure_styles()
        self._build_layout()
        self.start_listener()
        self._apply_settings()
        self.root.protocol("WM_DELETE_WINDOW", self._close)
        self.root.after(100, self.root.focus_force)

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Card.TFrame", background=self.BASE_BG)
        style.configure("Header.TLabel", font=("Georgia", 22, "bold"), background=self.BASE_BG, foreground=self.TEXT_COLOR)
        style.configure("Sub.TLabel", font=("Segoe UI", 10), background=self.BASE_BG, foreground=self.MUTED_TEXT)
        style.configure("CardTitle.TLabel", font=("Segoe UI", 11, "bold"), background=self.CARD_BG, foreground=self.TEXT_COLOR)
        style.configure("CardBody.TLabel", font=("Segoe UI", 10), background=self.CARD_BG, foreground=self.MUTED_TEXT)
        style.configure("CardTitleAlt.TLabel", font=("Segoe UI", 11, "bold"), background=self.CARD_ALT_BG, foreground=self.TEXT_COLOR)
        style.configure("CardBodyAlt.TLabel", font=("Segoe UI", 10), background=self.CARD_ALT_BG, foreground=self.MUTED_TEXT)
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background=self.CARD_BG, foreground=self.TEXT_COLOR)
        style.configure(
            "TCombobox",
            fieldbackground=self.WHITE_KEY,
            background=self.WHITE_KEY,
            foreground=self.DARK_TEXT,
            arrowcolor=self.DARK_TEXT,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", self.WHITE_KEY), ("focus", self.WHITE_KEY)],
            foreground=[("readonly", self.DARK_TEXT), ("focus", self.DARK_TEXT)],
            selectbackground=[("readonly", self.WHITE_KEY), ("focus", self.WHITE_KEY)],
            selectforeground=[("readonly", self.DARK_TEXT), ("focus", self.DARK_TEXT)],
        )
        style.configure("TEntry", fieldbackground=self.BASE_BG, foreground=self.TEXT_COLOR, insertcolor=self.TEXT_COLOR)
        style.map(
            "TEntry",
            fieldbackground=[("focus", self.BASE_BG)],
            foreground=[("focus", self.TEXT_COLOR)],
            selectbackground=[("focus", self.ACCENT)],
            selectforeground=[("focus", self.DARK_TEXT)],
        )
        style.configure("TScrollbar", background=self.CARD_BG, troughcolor=self.PANEL_BG, arrowcolor=self.TEXT_COLOR)
        self.root.option_add("*TCombobox*Listbox.background", self.WHITE_KEY)
        self.root.option_add("*TCombobox*Listbox.foreground", self.DARK_TEXT)
        self.root.option_add("*TCombobox*Listbox.selectBackground", self.ACCENT)
        self.root.option_add("*TCombobox*Listbox.selectForeground", self.DARK_TEXT)

    def _build_layout(self):
        outer = ttk.Frame(self.root, padding=20, style="Card.TFrame")
        outer.pack(fill="both", expand=True, padx=18, pady=18)

        header = tk.Frame(self.root, bg=self.BASE_BG)
        header.place(x=32, y=22)

        ttk.Label(header, text="Synthesizer UI!! :D", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="WORKING UI",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        content = tk.Frame(outer, bg=self.BASE_BG)
        content.pack(fill="both", expand=True)

        left_panel = tk.Frame(content, bg=self.PANEL_BG, width=330)
        left_panel.pack(side="left", fill="y", padx=(8, 20), pady=(52, 8))
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(content, bg=self.BASE_BG)
        right_panel.pack(side="left", fill="both", expand=True, pady=(52, 8))

        self._build_scrollable_controls(left_panel)
        self._build_keyboard(right_panel)

    def _build_scrollable_controls(self, parent):
        canvas_holder = tk.Frame(parent, bg=self.PANEL_BG)
        canvas_holder.pack(fill="both", expand=True)

        self.controls_canvas = tk.Canvas(
            canvas_holder,
            bg=self.PANEL_BG,
            highlightthickness=0,
            bd=0,
        )
        scrollbar = ttk.Scrollbar(canvas_holder, orient="vertical", command=self.controls_canvas.yview)
        self.controls_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.controls_canvas.pack(side="left", fill="both", expand=True)

        self.controls_inner = tk.Frame(self.controls_canvas, bg=self.PANEL_BG)
        self.controls_window = self.controls_canvas.create_window((0, 0), window=self.controls_inner, anchor="nw")

        self.controls_inner.bind("<Configure>", self._update_controls_scrollregion)
        self.controls_canvas.bind("<Configure>", self._resize_controls_window)

        self._build_controls(self.controls_inner)
        self._bind_controls_mousewheel(self.controls_canvas)
        self._bind_controls_mousewheel(self.controls_inner)

    def _update_controls_scrollregion(self, _event=None):
        if self.controls_canvas is not None:
            self.controls_canvas.configure(scrollregion=self.controls_canvas.bbox("all"))

    def _resize_controls_window(self, event):
        if self.controls_canvas is not None and self.controls_window is not None:
            self.controls_canvas.itemconfigure(self.controls_window, width=event.width)

    def _bind_controls_mousewheel(self, widget):
        widget.bind("<Enter>", self._enable_controls_mousewheel)
        widget.bind("<Leave>", self._disable_controls_mousewheel)

    def _enable_controls_mousewheel(self, _event=None):
        self.root.bind_all("<MouseWheel>", self._scroll_controls_mousewheel)

    def _disable_controls_mousewheel(self, _event=None):
        self.root.unbind_all("<MouseWheel>")

    def _scroll_controls_mousewheel(self, event):
        if self.controls_canvas is None:
            return
        scroll_units = -1 * int(event.delta / 120) if event.delta else 0
        if scroll_units != 0:
            self.controls_canvas.yview_scroll(scroll_units, "units")

    def _build_controls(self, parent):
        config_card = tk.Frame(parent, bg=self.CARD_BG, bd=0, highlightthickness=1, highlightbackground=self.ACCENT)
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

        wavetable_card = tk.Frame(parent, bg=self.CARD_ALT_BG, bd=0, highlightthickness=1, highlightbackground=self.ACCENT)
        wavetable_card.pack(fill="x", pady=(0, 14))

        ttk.Label(wavetable_card, text="WaveTable", style="CardTitleAlt.TLabel").pack(anchor="w", padx=14, pady=(14, 4))
        ttk.Label(
            wavetable_card,
            text="Gain affects live volume; duration and sample fades are legacy wavetable controls.",
            style="CardBodyAlt.TLabel",
            wraplength=280,
        ).pack(anchor="w", padx=14, pady=(0, 10))

        self._build_slider(wavetable_card, "Duration (seconds)", "duration", 1, 5, 1, 0)
        self._build_slider(wavetable_card, "Gain (dB)", "gain", -30, 0, -10, 0)
        self._build_slider(wavetable_card, "Attack (samples)", "wavetable_attack", 0, 5000, 1000, 0)
        self._build_slider(wavetable_card, "Release (samples)", "wavetable_release", 0, 5000, 3000, 0)

        envelope_card = tk.Frame(parent, bg=self.CARD_BG, bd=0, highlightthickness=1, highlightbackground=self.ACCENT)
        envelope_card.pack(fill="x", pady=(0, 14))

        ttk.Label(envelope_card, text="Envelope", style="CardTitle.TLabel").pack(anchor="w", padx=14, pady=(14, 4))
        ttk.Label(
            envelope_card,
            text="These sliders mirror attack, decay, sustain, and release.",
            style="CardBody.TLabel",
            wraplength=280,
        ).pack(anchor="w", padx=14, pady=(0, 10))

        self._build_slider(envelope_card, "Attack (seconds)", "env_attack", 0.0, 1.0, 0.01, 2)
        self._build_slider(envelope_card, "Decay (seconds)", "env_decay", 0.0, 1.0, 0.10, 2)
        self._build_slider(envelope_card, "Sustain", "env_sustain", 0.0, 1.0, 1.0, 2)
        self._build_slider(envelope_card, "Release (seconds)", "env_release", 0.0, 5.0, 0.25, 2)

        status_card = tk.Frame(parent, bg=self.CARD_ALT_BG, bd=0, highlightthickness=1, highlightbackground=self.ACCENT)
        status_card.pack(fill="x")

        ttk.Label(status_card, text="Status", style="CardTitleAlt.TLabel").pack(anchor="w", padx=14, pady=(14, 6))
        ttk.Label(status_card, textvariable=self.status_var, style="CardBodyAlt.TLabel", wraplength=280).pack(anchor="w", padx=14)
        ttk.Label(status_card, textvariable=self.current_key_var, style="CardBodyAlt.TLabel", wraplength=280).pack(
            anchor="w",
            padx=14,
            pady=(6, 4),
        )
        ttk.Label(status_card, textvariable=self.recording_var, style="CardBodyAlt.TLabel", wraplength=280).pack(
            anchor="w",
            padx=14,
            pady=(0, 10),
        )
        ttk.Button(
            status_card,
            text="Start Recording",
            style="Primary.TButton",
            command=self._start_recording,
        ).pack(fill="x", padx=14, pady=(0, 8))
        ttk.Button(
            status_card,
            text="Stop Recording",
            style="Primary.TButton",
            command=self._stop_recording,
        ).pack(fill="x", padx=14, pady=(0, 8))
        ttk.Button(
            status_card,
            text="Save Recording",
            style="Primary.TButton",
            command=self._save_recording,
        ).pack(fill="x", padx=14, pady=(0, 14))

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

        tk.Label(label_row, text=label_text, bg=parent["bg"], fg=self.TEXT_COLOR, font=("Segoe UI", 10)).pack(side="left")
        value_label = tk.Label(
            label_row,
            text=self._format_slider_value(value, decimals),
            bg=parent["bg"],
            fg=self.MUTED_TEXT,
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
        title_row = tk.Frame(parent, bg=self.BASE_BG)
        title_row.pack(fill="x", pady=(0, 12))

        tk.Label(
            title_row,
            text="Keyboard Mockup",
            bg=self.BASE_BG,
            fg=self.TEXT_COLOR,
            font=("Georgia", 16, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_row,
            text="Mapped keys light up when pressed and trigger the current note settings.",
            bg=self.BASE_BG,
            fg=self.MUTED_TEXT,
            font=("Segoe UI", 10),
            wraplength=700,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        keyboard_frame = tk.Frame(parent, bg=self.BASE_BG, padx=18, pady=18, highlightthickness=1, highlightbackground=self.ACCENT)
        keyboard_frame.pack(fill="both", expand=True)

        black_row = tk.Frame(keyboard_frame, bg=self.BASE_BG, height=110)
        black_row.pack(fill="x")

        for column in range(15):
            black_row.columnconfigure(column, weight=1, uniform="black-keyboard")

        black_positions = {"W": 1, "E": 3, "T": 7, "Y": 9, "U": 11}
        for key_name, column in black_positions.items():
            button = tk.Label(
                black_row,
                text=self._format_key_label(key_name),
                bg=self.BLACK_KEY,
                fg=self.TEXT_COLOR,
                width=8,
                height=6,
                relief="flat",
                font=("Segoe UI", 8, "bold"),
                cursor="hand2",
                justify="center",
            )
            button.grid(row=0, column=column, padx=2, sticky="nsew")
            self.key_widgets[key_name] = button
            self._bind_mouse_events(button, key_name)

        white_row = tk.Frame(keyboard_frame, bg=self.BASE_BG)
        white_row.pack(fill="x", pady=(8, 0))

        for column, key_name in enumerate(self.WHITE_KEYS):
            white_row.columnconfigure(column, weight=1, uniform="white-keyboard")
            button = tk.Label(
                white_row,
                text=self._format_key_label(key_name),
                bg=self.WHITE_KEY,
                fg=self.DARK_TEXT,
                width=8,
                height=9,
                relief="solid",
                bd=1,
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                justify="center",
            )
            button.grid(row=0, column=column, padx=3, sticky="nsew")
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

        scale_type = self.scale_var.get()
        note_entries = self._build_note_entries(typed_value, scale_type)
        self.key_note_labels = {note["key"]: note["solfege"] for note in note_entries}
        self.key_input.setup_key_map(note_entries)
        self.clear_active_keys()
        self._refresh_keyboard_labels()
        self.status_var.set(
            f"Loaded {scale_type} scale from {typed_value:.2f} Hz with {self.waveform_var.get()} waveform."
        )
        self._update_active_notes_label()

    def _build_note_entries(self, base_frequency, scale_type):
        degrees = self.SCALE_DEGREES.get(scale_type, self.SCALE_DEGREES["chroma"])
        repeating_degrees = degrees[:-1] if degrees and degrees[-1][0] == 12 else degrees

        note_entries = []
        for index, key_name in enumerate(self.KEY_ORDER):
            octave_offset, scale_index = divmod(index, len(repeating_degrees))
            semitone, solfege = repeating_degrees[scale_index]
            total_semitones = semitone + (12 * octave_offset)
            frequency = base_frequency * (2 ** (total_semitones / 12))
            note_entries.append(
                {
                    "key": key_name,
                    "solfege": solfege,
                    "frequency": frequency,
                }
            )
        return note_entries

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
            self.audio_engine.note_on(key_name, frequency, self._get_audio_settings())
            self.last_rendered_signal = None
            self.last_rendered_frequency = frequency
            solfege = self.key_note_labels.get(key_name, self.KEY_SOLFEGE.get(key_name, key_name))
            self.status_var.set(f"Pressed {key_name} ({solfege}) at {frequency:.2f} Hz.")
        except Exception as error:
            self.status_var.set(f"Audio playback error: {error}")

    def _release_key(self, key_name):
        if key_name not in self.key_input.key_map:
            return

        self.key_input.on_release(key_name)
        self.audio_engine.note_off(key_name)
        self._set_key_visual(key_name, False)
        self.status_var.set(f"Released {key_name}")
        self._update_active_notes_label()

    def _set_key_visual(self, key_name, pressed):
        widget = self.key_widgets.get(key_name)
        if widget is None:
            return

        is_mapped = key_name in self.key_input.key_map
        if key_name in self.BLACK_KEYS:
            default_bg = self.BLACK_KEY if is_mapped else self.BLACK_KEY_DISABLED
            default_fg = self.TEXT_COLOR if is_mapped else self.MUTED_TEXT
            widget.configure(bg=self.KEY_ACTIVE if pressed else default_bg, fg=self.DARK_TEXT if pressed else default_fg)
        else:
            default_bg = self.WHITE_KEY if is_mapped else self.WHITE_KEY_DISABLED
            widget.configure(bg=self.KEY_ACTIVE if pressed else default_bg, fg=self.DARK_TEXT)

    def _update_active_notes_label(self):
        current_key = self.key_input.last_pressed_key
        if current_key:
            frequency = self.key_input.key_map.get(current_key)
            if frequency is not None:
                solfege = self.key_note_labels.get(current_key, self.KEY_SOLFEGE.get(current_key, current_key))
                self.current_key_var.set(f"Current note: {current_key} {solfege} ({frequency:.2f} Hz)")
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
        for key_name in self.KEY_ORDER:
            widget = self.key_widgets.get(key_name)
            if widget is None:
                continue

            frequency = self.key_input.key_map.get(key_name)
            widget.configure(text=self._format_key_label(key_name, frequency))
            self._set_key_visual(key_name, False)

    def _format_key_label(self, key_name, frequency=None):
        solfege = self.key_note_labels.get(key_name, self.KEY_SOLFEGE.get(key_name, key_name))
        frequency_text = "-- Hz" if frequency is None else f"{frequency:.2f} Hz"
        return f"{key_name}\n{solfege}\n{frequency_text}"

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

    def _start_recording(self):
        if self.recording_active:
            self.status_var.set("Recording is already running.")
            return

        try:
            self.audio_engine.start_recording()
        except Exception as error:
            self.status_var.set(f"Recording error: {error}")
            return

        self.recording_active = True
        self.recording_start_time = None
        self.recorded_signal = np.zeros(0, dtype=np.float32)
        self.recording_has_audio = False
        self.recording_var.set("Recording: active")
        self.status_var.set("Recording started.")

    def _stop_recording(self):
        if not self.recording_active:
            if self.recording_has_audio:
                self.status_var.set("Recording is already stopped.")
            else:
                self.status_var.set("Start recording before stopping.")
            return

        self.recorded_signal = self.audio_engine.stop_recording()
        self.recording_has_audio = self.audio_engine.recording_has_audio and self.recorded_signal.size > 0
        self.recording_active = False
        self.recording_start_time = None

        if self.recording_has_audio:
            self.recording_var.set("Recording: stopped and ready to save")
            self.status_var.set("Recording stopped. You can now save the WAV file.")
        else:
            self.recording_var.set("Recording: stopped with no notes")
            self.status_var.set("Recording stopped, but no notes were captured.")

    def _save_recording(self):
        if self.recording_active:
            self._stop_recording()

        if not self.recording_has_audio or self.recorded_signal.size == 0:
            self.status_var.set("Record at least one note before saving.")
            return

        default_name = "mockui_recording.wav"
        if self.last_rendered_frequency is not None:
            default_name = f"mockui_recording_{self.last_rendered_frequency:.2f}Hz.wav"

        target_path = filedialog.asksaveasfilename(
            title="Save Synth Output",
            defaultextension=".wav",
            initialfile=default_name,
            filetypes=[("WAV audio", "*.wav")],
        )

        if not target_path:
            self.status_var.set("Save cancelled.")
            return

        try:
            self._write_wav_file(target_path, self.recorded_signal)
            self.status_var.set(f"Saved audio to {Path(target_path).name}.")
        except Exception as error:
            self.status_var.set(f"Save error: {error}")

    def _write_wav_file(self, target_path, signal):
        audio = np.asarray(signal, dtype=np.float32)
        peak = np.max(np.abs(audio)) if audio.size > 0 else 0.0
        if peak > 1.0:
            audio = audio / peak
        audio = np.clip(audio, -1.0, 1.0)
        pcm_audio = np.int16(audio * 32767)
        with wave.open(target_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(pcm_audio.tobytes())

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
        self.audio_engine.clear_voices()
        self._update_active_notes_label()

    def _close(self):
        self.stop_listener()
        self.audio_engine.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    app = SynthMockUI()
    app.run()


if __name__ == "__main__":
    main()
