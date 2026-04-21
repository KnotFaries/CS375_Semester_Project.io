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
    a =np.array([4.0,4.0,4.0,4.0])
    b =np.array([4.0,4.0,4.0,4.0])
    wt.amp(a, -20)
    assert b[1] > a [1]
    assert b[2] > a [2]
    assert b[3] > a [3]
    assert b[0] > a [0]
    
def test_create_envelope():
    a =np.array([10.0,10.0,10.0,10.0,10.0,10.0,10.0])
    wt.create_envelope(a, -3, 3, 3)

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

    assert output[1] != 0 
    assert output[3] != 0 
    assert output[2] != 0 

def test_generate_wavetabel():
    pass 