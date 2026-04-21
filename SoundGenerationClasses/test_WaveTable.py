# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 14:43:47 2026

@author: maiam
"""
import WaveTable as wt
import numpy as np



def test_attack():
    a =[4,4,4,4]
    b = wt.attack([4,4,4,4],2)
    assert a[0] > b [0]
    assert a[1] == b [1]
    
    
def test_release():
    a =[4,4,4,4]
    b = wt.release([4,4,4,4],2)
    assert a[3] > b [3]
    assert a[2] == b [2]
    
def test_amp():
    a =[4,4,4,4]
    b = wt.amp([4,4,4,4], -2)
    assert a[3] > b [3]
    assert a[2] == b [2]
    
def test_create_envelope():
    a =[0,0,0,0]
    wt.interpolate_linearly(a, 0)

    pass

def test_interpolate_linearly():
        
    output = np.zeros(4)
    wavetable_length = 7
    wavetable = np.zeros(7)
    index =0
    
    waveform = np.sin
    
    for n in range(wavetable_length):
        wavetable [n] = waveform( 2* np.pi * n / wavetable_length)
    
    
    for n in range(output.shape[0]):
        
        output[n]= wt.interpolate_linearly(wavetable, index)
        index += 1
        index %= wavetable_length
    pass

def test_generate_wavetabel():
    pass 