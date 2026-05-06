# WaveTable.py
## Methods
attack (signal, fade_length = 1000)
Signal is an array, fade_length is a number less than the length of signals. 
Creates the attack of the sound. 

Returns an array. 

release (signal, fade_length = 1000):
Signal is an array, fade_length is a number less than the length of signals. 
Creates the reases of the sound

Returns an array. 

amp(output, i_gain = -20)
Signal is an array, i_gain is a negitive integer.
changes the overall ampltuide of the sound

Returns an array. 

create_envelope(signal, gain, attack_len, release_leng)
Signal is an array and gain is a negitive integer. Attack_len and release_leng is a number less than the length of signals. 

interpolate_linearly(wavetable, index)
wavetable is an array. Index is the current index of of the wavetable in the loop. 

Returns a value for to be assigned to the index. 

generate_wavetable(frequency, durration, waveform, sample_rate = 44100)
Frequency is and INT. Duuration is a float. waveform is a method. sample_rate is and Int. 

Returns an array. 