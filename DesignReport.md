# TO DO: 
- UML 
- UI Methods
- Pre and Post condtions 
- Class Diagram 
# Requirments:
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

# Classes and Methods 

## UI
Modules which are about the UI and resolve requriments 

**Key_Input Class(Requriment 11)**
Attributes: 
- key_map
- active_keys

**Methods:**
- Setup for Key Map
    - input:
          - Scale: string
          - Base Frequency: float
    - output:
          - none
    - Preconditons: 
    - Postcondtions (success):
    - Postconditons (fail): 

- On Press (key)
      - input:
          - key
      - output:
          - none
      - Preconditons: 
      - Postcondtions (success):
      - Postconditons (fail): 

- On Release (key)
      - input:
          - key
      - output:
          - none
      - Preconditons: 
      - Postcondtions (success):
      - Postconditons (fail): 

**Number_Input Class (Requriemtn 10)**

## Sound Production 
Moduels which are about the production of noise

**Generate Audio Data classes:**

**Evelopes/Volume/ Class (Requriemnts 4, 9)**

Attributes:
- Fundemtnal: Float
- Aptidue: Float 

**Methods:** 
- Generate Attack 
    - input
        -  Fundemtnal: Float
        - Aptidue: Float 
    - output 
        - Aduio_Data: List
    - Preconditons: 
    - Postcondtions (Success):
    - Postconditons (fail): 

- Generate Decay 
    - input
        -  Fundemtnal: Float
        - Aptidue: Float 
    - output 
        - Aduio_Data: List
    - Preconditons: 
    - Postcondtions (Success):
    - Postconditons (fail): 

- Generate sustain
    - input
        -  Fundemtnal: Float
        - Aptidue: Float 
    - output 
        - Aduio_Data: List
    - Preconditons: 
    - Postcondtions (Success):
    - Postconditons (fail): 

- Generate Relase
    - input
        -  Fundemtnal: Float
        - Aptidue: Float 
    - output 
        - Aduio_Data: List
- Preconditons: 
- Postcondtions (Success):
- Postconditons (fail):

**Overtones Class:(Requriemnts 4, 9)**

Atributes: 
- Fundmental: Float 

Methods: 
- generate_harmonics
    - Input: 
        - Fundemtal: Float
    - Output:
        - Harmonics: List
    - Preconditons: 
    - Postcondtions (Success):
    - Postconditons (fail): 

- generate_overtones
    - Input: 
        - Fundemtal: Float
    - Output:
        - ovetones: List 
    - Preconditons: 
    - Postcondtions (Success):
    - Postconditons (fail): 
    
- fetch_overtones
    - Input: 
        - Instrument: String
    - Output
        - Overtones
    - Preconditons: 
    - Postcondtions (Success):
    - Postconditons (fail): 

Filter Class


**Generate_Preset classes: (Reqirements 3, 6, 7, 8)**

Methods
- Calcuate_Scale
    - Inputs 
        - home_tone: float
        - mode: String (defult = major)
    - Output 
        - frequency_list: list/array
- Preconditons: 
    - home_tone NOT NULL
- Postconitons (success)
    - Outputs a list of frequenices in line withe the modal scale
- Postcondtions(fail)
    - Outputls a list of frequenices not in line with the modal scale
    - dose not output a list
   

## UI and Generation Connections

**Other or Unassigned (Requrments 1, 3,6,7,8,9,10,11)**
**Methods:**
- Assign to Computer_keyboards 
    - input 
        - frequency_list: list/array
    - output 
        - void
    - Preconditons: 
        - frequency_list: NOT NULL
    - Post condtions (success)
        - The computer keys are assigned new numbers in accending order and by designated pattern
    - Post condtions (fail)
        - The computer keys are not assgined new numbers
        - The computer key are assigned number in a non- accending order. 

- Record: 
    - input: 
        - audio_data?
    - output
        - wav file? 
    - Preconditons: 
    - Postcondtions (Success):
    - Postconditons (fail): 
# Relationship Diagram

(![Class Relation chart](ClassRelationship.jpg))
