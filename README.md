# MIDI Clock Sync and Progam Change for Band

This application is meant for a Raspberry Pi.
I personally have a Roland SPD-SX. I use samples on this device, but I only use about 10 or so. Some songs require the same samples i.e. a shaker, but these songs have a different tempos. I do not want to make a copy of the so called "KIT" in the SPD-SX just to have the shaker in all of the copies. What if I have to make a change to all of the kits? 🤷‍♂️
I do, however, need kits to store things like these samples and some MIDI note numbers for specific pads. I have the handful of kits setup, now all I need is to send a Program Change to the device(SPD-SX) to change the kit depending on the song and send a MIDI clock tempo. This is where this Python project comse into play.

I have setup 3 pads on my SPD-SX that can send specific MIDI on-notes. These will advanced the song, go the previous song, or reset the list, meaning go to the first song in the list. If I, for example, advance the song, the next song object in the list contains the song name, program change for possible kit change on the device(SPD-SX) and a tempo in BMP(beats per minute). The program change is sent to the device(SPD-SX) to change the kit and then a MIDI clock in the specified tempo is sent to the device(SPD-SX). Now I have the correct kit and tempo and can start to play. I can change the song at anytime.

The idea is to have a band's setlist as a json.
The program reads data from a json file, that defines the setlist of your band.

# JSON Setup

-  List of Songs with this structure
   -  Song Name
   -  Song Tempo
   -  Program Change
-  Global Settings
   -  MIDI Note from device for next song
   -  MIDI Note from device for previous song
   -  MIDI Note from device for setlist reset --> goes to first song in the list
   -  Global MIDI Channel
   -  MIDI Inport Name
   -  MIDI Outport Name

# Program Steps

1. The JSON is parsed and the needed arrays are built.
2. The first song is chosen
3. The Inport and Outport with the specified names in the JSON file are initialized
4. The program change number is sent to the device's MIDI channel defined in the JSON file
5. A MIDI clock with the song's tempo is sent to the device MIDI channel defined in the JSON file
6. Ready to play

When the song is changed, steps 4 and 5 are performed

# Possible Enhancements

1. LCD or touch screen reading the song's name and its tempo to validate the tempo on the Raspberry Pi and the connected device.

