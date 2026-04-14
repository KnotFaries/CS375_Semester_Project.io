# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 14:43:47 2026

@author: maiam
"""
import WaveTable as wt



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
    pass

def test_interpolate_linearly():
    pass

def test_generate_wavetabel():
    pass 