# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 14:43:47 2026

@author: maiam
"""

import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
#import pytest
import WaveTable as WT

sample_rate = 44100
frequency = 440
durration = 1
waveform = np.sin

c = WT.generate_wavetable(frequency, durration, waveform)
sd.play(c)
plt.plot(c[-6000:])
"""
d = generate_wavetable(293.66, durration, waveform)
e = generate_wavetable(329.63, durration, waveform)
f = generate_wavetable(349.23, durration, waveform)
g = generate_wavetable(392.00, durration, waveform)
a = generate_wavetable(440, durration, waveform)
b = generate_wavetable(493.88, durration, waveform)
c5 = generate_wavetable(523.24, durration, waveform)



sd.play(c)
sd.wait()
sd.play(e)
sd.wait()
sd.play(g)
sd.wait()

sd.play(c)
sd.play(e)
sd.play(g)"""