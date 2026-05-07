This is an explainer to prime you on how the various methods work together. Most the sound generation methods are used inside the method generate_wavetable. It takes in the parameters: frequency, durration, waveform, sample_rate.By defualt the sample rate is set to 44100, a common standard for sample rates. 
And example of how using this method would look is: 

```a = generate_wavetable(440, np.sin)```

440 is 440hertzs, or a standard A4. np is short for numpy, so if you don't shorten the library name you woud use 'numpy.sin'. 

The first for loop in the function creates a table of a single period of the the wave form. 

The second loop puts that wave from into a format wich can be played using the library sound divice. In this second loop we find the method interpolate_linearly. 

Interpolate_linearly is a helper function that more or less rounds to the last useable point. Other methods of interploation can be written, such as interpolating to the nearest point or to the average between two neighboring points. To the average person, it won't make much of a sound diffrence. 

After that we use create_envelope. A sounds envelope reffers to the loudness or softeness of a sound, which in live preformances is often refered to as the dynamic. 

Create envelope modifies the output with three methods, amp, attack, and release. Amp is short for amplitude, the overall loundness or softness. This is the diffrence between piano or forte. Attack and relase are two parts of the ASDR modle. Attack is going from scilence to sound, and realese is going from sound to scilence.  

After that, generate_wavetable outputs a numpy array, which sounddivice (often sd in the code) can turn into sound. 