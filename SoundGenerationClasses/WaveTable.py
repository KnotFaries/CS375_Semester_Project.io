# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 10:19:48 2026

@author: maiam
"""
import sounddevice as sd
import numpy as np


def attack (signal, fade_length = 1000):
    """

    Parameters
    ----------
    signal : Array
        DESCRIPTION.
    fade_length : int, optional
        DESCRIPTION. The default is 1000.Number of samples that the attack takes place over

    Returns
    -------
    signal : Array
        DESCRIPTION.

    """
    fade_in = (1- np.cos(np.linspace(0, np.pi, fade_length))) *0.5
    signal[:fade_length] = np.multiply(fade_in, signal[:fade_length])
    return signal
    
def release (signal, fade_length = 1000):
    """

    Parameters
    ----------
    signal : Array
        DESCRIPTION.
    fade_length : int, optional
        DESCRIPTION. The default is 1000.Number of samples that the attack takes place over

    Returns
    -------
    signal : Array
        DESCRIPTION.

    """
    fade_in = (1- np.cos(np.linspace(0, np.pi, fade_length))) *0.5
    fade_out = np.flip(fade_in)
    signal[-fade_length:] = np.multiply(fade_out, signal[-fade_length:])
    return signal
    

def amp(output, gain = -20):
    """
    Parameters
    ----------
    output : Array
        DESCRIPTION.
    gain : TYPE, optional
        DESCRIPTION. The default is -20.
    Returns
    -------
    output : array
        Output, but less loud

    """
    gain = -20
    amp = 10 ** (gain/20)
    output *= amp 
    return output

def create_envelope(signal, gain, attack_len, release_leng):
    signal = amp(signal, gain)
    signal = attack(signal, attack_len)
    signal = release(signal, release_leng)
    return signal

def interpolate_linearly(wavetable, index):
    """
    Helper function 
    Parameters
    ----------
    wavetable : array/list
        DESCRIPTION.
    index : float
        DESCRIPTION.

    Returns
    -------
    float, the closest y value from the wave table 

    """
    trunk_index = int(np.floor(index))
    next_index= (trunk_index +1) % wavetable.shape[0]
    
    next_index_weight = index - trunk_index
    trunk_index_wieght = 1- next_index_weight
    
    return trunk_index_wieght * wavetable[trunk_index] + next_index_weight * wavetable[next_index]


def generate_wavetable(frequency, durration, waveform, sample_rate = 44100):
    
    """
    Parameters
    ----------
    frequency : INT
        Frequency in hrzt
    durration : float
        Time in seconds of the tone
    waveform: a method
        a method with x as it's only varible in acycle of 2 pi. Do not add the parethisise 
    sample_rate : INT, 44100 is standard
        DESCRIPTION.
    Returns
    -------
    None.

    """
    
    
    sample_rate = sample_rate
    frequency = frequency
    t = durration
    #waveform is a function
    waveform = waveform
    
    wavetable_length = 64
    wavetable= np.zeros((wavetable_length,))
    
    for n in range(wavetable_length):
        wavetable [n] = waveform( 2* np.pi * n / wavetable_length)
        
        
    output = np.zeros((t*sample_rate,))
    
    
    index = 0 
    index_increment = frequency * wavetable_length/sample_rate
    
    for n in range(output.shape[0]):
        
        output[n]= interpolate_linearly(wavetable, index)
        index += index_increment
        index %= wavetable_length
      
    output = create_envelope(output, -10, 1000, 3000)
    
      
    return output
    
sample_rate = 44100
frequency = 440
durration = 3
waveform = np.sin

c = generate_wavetable(261.63, durration, waveform)
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
sd.play(g)