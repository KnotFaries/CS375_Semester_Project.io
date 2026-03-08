# Requirements: 
## Press Relase: 
Comming from a liberal arts education, we have decided that world is shaped by the art we create, and our art is shaped by our material conditons. Since the 19th century, there has been an increese in the autmotization of music as we strive to not repoduce music, but replicate it. Our goal is to create a tool which encourages free, strange, uniqe and unabashedly human music. 

What we will create is a free synthesizer, that can run on low end computers such as student laptops (AMD Ryzen 5/ Intel I5 cpu and about 8 gigs of ram.) Aspiring artist will have access to all the notes of a standard piano, as well as the free pitch sounds of oscilators.

## Interviews: 
[ Inital Interview with Ash Hawkes](https://drive.google.com/file/d/12T3JomlqMWkhvdudFzyKspx-jlWIuCh7/view?usp=sharing)

Ash is is musical, but not formaly trained. They are looking for a intuitive interface that aligns with how they conceptualize music (As waves and textures) and work with costmoizeable sets of pitches and flowing glisandos. 

## User Stories: 
1. As a musican I want to use the equipment I already own. 
2. As a musican without formal training, I want to be able still make good sounding music. 
3. As a musican I want to be able to hear my work. 
4. As an American musican, I want familar note intervals. 
5. As a musican, I want to play with sound.
6. As somone new to music, I want a shape (wave) based UI 

## Functional Requirements
- US 3: Able to export audio via mp3 file. 
- US 1: play audio through laptop's sound system. 
- US 4: Produce 12 notes of a western chromatic scale in equal temperament
- US 5: Utilizes 2 or 3 oscillators to synthesize multiple frequencies
- US 5: Can amplify the frequencies and convert them to sound
- US 6: Untilize presets:
    - Move between chromatic and pentatonic scale
- US 5: Utilizes filters, LFOs and envelopes for timbral construction
- desktop application 

## Nonfunctional Requirments
- The user interface should allow users to control parameters through intuitive sliders and knobs.
- Export audio player can be accessed through a standard english keyboard 
- US 1 4 5: These features must be optomized for an intel core i5/ ryzen 5 or higher\
- Users should be able to learn basic functionality within 5 minutes without documentation.
- The system should generate and play synthesized audio with latency below 50 ms between user interaction (knob/slider change) and audible output. 
- The application should support standard laptop audio hardware and drivers.
- The desktop application should run on Windows 10 or later
- The synthesizer should not exceed:
    20% CPU usage during normal operation
    500 MB of RAM
- The architecture should allow future support for:
    Additional oscillators
    More musical scales
    MIDI input
    Additional filter types

## Gant Chart
![Picture1](https://github.com/user-attachments/assets/d8641e8b-5fd6-4580-9495-028e9d2b85a2)
