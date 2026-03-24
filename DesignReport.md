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

Key_Input Class

Number_Input Class

Display Class

## Tutorial Pages (multpile classes)

## Sound Production 
Moduels which are about the production of noise

**Generate Audio Data classes: (Reqirements 1, 2)**
Methods that generate the audio data

Evelopes/Volume/ Class
Attributes:
- Fundemtnal: Float
- Aptidue: Float 
Methods: 
- Generate Attack 
    - input
        -  Fundemtnal: Float
        - Aptidue: Float 
    - output 
        - Aduio_Data: List
- Generate Decay 
    - input
        -  Fundemtnal: Float
        - Aptidue: Float 
    - output 
        - Aduio_Data: List
- Generate sustain
    - input
        -  Fundemtnal: Float
        - Aptidue: Float 
    - output 
        - Aduio_Data: List
- Generate Relase
    - input
        -  Fundemtnal: Float
        - Aptidue: Float 
    - output 
        - Aduio_Data: List

Overtones Class: 

Atributes: 
- Fundmental: Float 

Methods: 
- generate_harmonics
    - Input: 
        - Fundemtal: Float
    - Output:
        - Harmonics: List 
- generate_overtones
    - Input: 
        - Fundemtal: Float
    - Output:
        - ovetones: List 
- fetch_overtones
    - Input: 
        - Instrument: String
    - Output
        - Overtones


Take a funtmetal, calculate the harmonics, caluate the overtones, lower notes: more harmonics(tighter space?), Higher notes: Less harmonics 


Oscillater class (requirements 3, 4, 5)
Method: 
- Switch to preset 
    - input 
        - key: string
    - out put l
        - list_of_frequencies: list/array
- Generate wave function
    - input: 
        - frequnices: float
    - output: 
        - freqiesces: float



Filter Class


**Generate Preset classes: (Reqirements 1, 2)**
Take Audio data and calcuate them for presets

Methods
- Calcuate_Solfege
    - Inputs 
        - home_tone: float
        - mode: String (defult = major)
    - Output 
        - frequency_list: list/array
- Assign to Computer_keyboards 
    - input 
        - frequency_list: list/array
    - output 
        - void
- Preconditons: 
    - home_tone NOT NULL
    - Caclulate_Solfege outputs 8 unique frequiencies
    - The keyboard has been assigned to diffrent notes. 
- Postconitons (success)
    - Calculate_Solfege out puts a number of frequeineces that is not 8
    - The computer keys are assigned new numbers and accending order 
- Postcondtions(fail)
    - Calculate_Solfege ouptputs a number of frequencies that is not 8 
    - The computer keys are not assgined new numbers
    - The computer key are assigned number in a non- accending order. 


## Others 
Modules which can not be grouped, resolve requrment 
