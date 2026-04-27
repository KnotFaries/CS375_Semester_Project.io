import numpy as np
import sounddevice as sd
from pynput import keyboard
import soundfile as sf

SAMPLE_RATE = 44100

class Oscillator:
    def __init__(self, waveform="saw"):
        self.waveform = waveform

    def generate(self, freq, duration, amp=0.5):
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

        if self.waveform == "sine":
            return amp * np.sin(2 * np.pi * freq * t)
        elif self.waveform == "square":
            return amp * np.sign(np.sin(2 * np.pi * freq * t))
        elif self.waveform == "saw":
            return amp * (2 * (t * freq - np.floor(0.5 + t * freq)))
        elif self.waveform == "triangle":
            return amp * (2 * np.arcsin(np.sin(2 * np.pi * freq * t)) / np.pi)        

class Envelope:
    def apply(self, signal, attack=0.01, decay=0.1, sustain=1.0, release=5.0):
        length = len(signal)

        a = int(attack * SAMPLE_RATE)
        d = int(decay * SAMPLE_RATE)
        r = int(release * SAMPLE_RATE)
        s = length - (a + d + r)
        env = np.zeros(length)

        if a > 0: env[:a] = np.linspace(0, 1, a)
        if d > 0: env[a:a+d] = np.linspace(1, sustain, d)
        if s > 0: env[a+d:a+d+s] = sustain
        if r > 0: env[-r:] = np.linspace(sustain, 0, r)
        return signal * env
    
class Preset:
    def calculate_scale(self, base_freq, scaletype="minor"):
        intervals = {
            "chroma": list(range(12)),
            "major": [0,2,4,5,7,9,11,12],
            "minor": [0,2,3,5,7,8,10,12],
            "penta": [0,2,4,7,9,12]}

        steps = intervals.get(scaletype, intervals[scaletype])
        return [base_freq * (2 ** (n/12)) for n in steps]
    
class Synth:
    def __init__(self, recorder=None):
        self.osc1 = Oscillator("sine")
        self.osc2 = Oscillator("saw")
        self.osc3 = Oscillator("square")
        self.env = Envelope()
        self.recorder = recorder

    def play_note(self, freq, duration=1.0):
        sine = self.osc1.generate(freq, duration, 0.4)
        saw = self.osc2.generate(freq*1.01, duration, 0.3)
        square = self.osc3.generate(freq*0.99, duration, 0.3)
        
        signal = saw

        sd.play(signal, SAMPLE_RATE)

        if self.recorder:
            self.recorder.add(signal) 

        return signal

class KeyInput:
    def __init__(self, synth, scale):
        self.synth = synth
        self.key_map = {}
        self.active_keys = set()

        keys = list("asdfghjklqwertyuiop")
        for i, key in enumerate(keys[:len(scale)]):
            self.key_map[key] = scale[i]

    def on_press(self, key):
        print(f" {str(key)}")

        if key == keyboard.Key.esc:
            print("Exiting!")
            return False

        try:
            k = key.char

            if k == "r":
                print("Recording save triggered")
                self.synth.recorder.save("my_recording.wav")
                return

            if k in self.key_map and k not in self.active_keys:
                self.active_keys.add(k)
                self.synth.play_note(self.key_map[k])
        except: pass

    def on_release(self, key):
        try:
            k = key.char
            if k in self.active_keys:
                self.active_keys.remove(k)
        except: pass

    def start(self):
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        ) as listener:
            listener.join()


class Recorder:
    def __init__(self):
        self.buffer = []

    def add(self, signal):
        self.buffer.append(signal.copy())

    def save(self, filename="output.wav"):
        if not self.buffer:
            print("Nothing recorded!")
            return

        audio = np.concatenate(self.buffer)
        sf.write(filename, audio, SAMPLE_RATE)
        print(f"Saved recording to {filename}")


if __name__ == "__main__":
    base_freq = 261.63  # C4

    preset = Preset()
    scale = preset.calculate_scale(base_freq, scaletype="minor")

    recorder = Recorder()

    synth = Synth(recorder=recorder)
    env1 = Envelope()
    keys = KeyInput(synth, scale)

    print("Press keys (QWERTY...) to play notes")
    print("Press 'r' to save recording")
    keys.start()
