# Test Plan
## Unit Test
## UI 
## Recording
## Wave Table
The following are the function in test_Wavetable.py followed by a descriptions. 
- test_attack
    - test that the first 2 values of an out put array are smaller than the first two values of an input array
- test_release
    - test that the last 2 values of an out put array are smaller than the last two values of an input array
- test_amp
    - test that the entierty of an output array is smaller tahn the last two values of an input array
- test_create_envelope():
    - test that the first 2 values of an out put array are smaller than the first two values of an input array
    - test that the last 2 values of an out put array are smaller than the last two values of an input array
    - test that the entierty of an output array is smaller tahn the last two values of an input array
- test_interpolate_linearly():
    - Given a blank array and a filled wavetable, each value of an array should exist
- test_generate_wavetabel():
    - Given frequency, durration, and waveform, the out put shoul have some values in all parts of an array
## Integration Test
- 
## User Acceptance Testing
The following test are to test for musical acurracy:
### C major Pitch testing 
Go to the drop down menues on the left. Select 'major' as the scale and 'c' as Do. Using any tuning app, run through a c major scale and check if all notes are in tune. 
### C minor Pitch testing 
Go to the drop down menues on the left. Select 'minor' as the scale and 'c' as Do. Using any tuning app, run through a c major scale and check if all notes are in tune. Using any tuning app, run through a c minor scale and check if all notes are in tune. change scale to D major

### Test ability to play simple piece 
Play the following in any major key: 

Mi Mi Fa So So Fa Mi Re Do Do Re Mi Mi Re Re 
Mi Mi Fa So So Fa Mi Re Do Do Re Mi Re Do Do

- Ode to joy, Ludwig van Bethoven 


## Recording Test
- Test add() play notes on synthesiser and use save() to check that the recording is picking up sound
