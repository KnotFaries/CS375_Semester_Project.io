# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 14:43:47 2026

@author: maiam
"""
import WaveTable as wt

print( wt.attack([0,1,2,3,4,5] , 2))

a =[4,4,4,4]
b = wt.attack([4,4,4,4], 2)
c= b[0]
print(c)

def test_attack():
    a =[4,4,4,4]
    b = wt.attack([4,4,4,4],2)
    assert a[0] > b [0]
    assert a[1] == b [1]
    