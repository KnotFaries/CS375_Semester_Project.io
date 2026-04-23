# Test Plan
## Unit Test
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
- UI to Preset scale mapping integration
    - Launch `UI/mock_synth_ui.py`, select each available scale type, enter a valid base frequency, and click `Apply Settings`.
    - Verify that the on-screen key labels refresh to new note frequencies and that the status message matches the selected scale, base frequency, and waveform.
- MockUI to WaveTable integration
    - In the MockUI, change waveform, duration, gain, wavetable attack, and wavetable release, then press a mapped key.
    - Verify that a note is produced through the speakers/headphones, that changing waveform changes the character of the sound, and that duration/attack/release changes are audible in the generated note.
- MockUI to synthictest2 envelope integration
    - Change the envelope attack, decay, sustain, and release sliders, then play the same note multiple times with different settings.
    - Verify that the envelope shape changes as expected in the real output: slower attack delays the peak, lower sustain reduces held volume, and longer release makes the note fade out longer.
- Full playback stack with real audio device
    - Run the UI on a machine with a working audio output device and play notes using both mouse clicks and keyboard presses.
    - Verify that key highlighting, current-note status text, and audible playback all stay synchronized, and that the UI does not raise playback errors during normal use.
- Boundary integration test for fitted envelope values
    - Set a short note duration and then choose large envelope values so that attack, decay, and release would otherwise exceed the note length.
    - Verify that the note still plays without crashing because the UI audio engine fits the envelope values to the selected duration before calling `synthictest2.Envelope.apply()`.
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
