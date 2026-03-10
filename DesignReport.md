# Assignmet
## Requirments:
1) Able to export audio via mp3 file. 
2) play audio through laptop's sound system. 
3) Produce 12 notes of a western chromatic scale in equal temperament
4) Utilizes 2 or 3 oscillators to synthesize multiple frequencies
5) Can amplify the frequencies and convert them to sound
6) Untilize presets major scale in any key
7) Utalize preset of minor scales in any key
8) Utlize preset of major pentatoinic
9) Utilizes filters, LFOs and envelopes for timbral construction
10) The user interface should allow users to control parameters through intuitive sliders and knobs.
11) Export audio player can be accessed through a standard english keyboard 
12) These features must be optomized for an intel core i5/ ryzen 5 or higher\
13) Users should be able to learn basic functionality within 5 minutes without documentation.
14) The system should generate and play synthesized audio with latency below 50 ms between user interaction (knob/slider change) and audible output. 
15) The application should support standard laptop audio hardware and drivers.
16) The desktop application should run on Windows 10 or later
8) The synthesizer should not exceed: 20% CPU usage during normal operation
9) The synthesizer should not exceed 500 MB of RAM
10) The architecture should allow future support for Additional oscillators
11) The architecture should allow future support for More musical scales
12) The architecture should allow future support for MIDI input
13) The architecture should allow future support for Additional filter types

## UI
Modules which are about the UI and resolve requriments 

Class Key Input

## Sound Production 
Moduels which are about the production of noise and resolve requriments 

Audio Input class: 
- Calcuate Solfege, input home_tone, output list of frequencies 
- Assign to Computer_keyboards, input list of frequenices, output void

Oscillater class
- Method: Generate wave function(inputp: frequnices (float) output: freqiesces (float))

Tamber class (Might split later)

## Others 
Modules which can not be grouped, resolve requrment 