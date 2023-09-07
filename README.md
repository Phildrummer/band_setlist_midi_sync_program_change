# MIDI Clock Sync and Progam Change for Band

This application is meant for a Raspberry Pi.
I personally have a Roland SPD-SX. I use samples on this device, but I only use about 10 or so. Some songs require the same samples i.e. a shaker, but these songs have a different tempos. I do not want to make a copy of the so called "KIT" in the SPD-SX just to have the shaker in all of the copies. What if I have to make a change to of the kits? 🤷‍♂️
I do, however, need kits to store things like these samples and some MIDI note numbers for specific pads. I have the handful of kits setup, now all I need is to send a Program Change to the device to change the kit depending on the song and send a MIDI clock tempo. This is where this project comes in.

I have setup 3 pads on my SPD-SX that can send specific MIDI on-notes. These will advanced the song, go the previous song, or reset the list, meaning go to the first song in the list. If, for example, advance the song, the next song object in the list contains the song name, program change for possible kit change on the SPD-SX and a tempo in BMP(beats per minute). The program change is sent to the SPD-SX to change the kit and then the a MIDI clock in the specified tempo is sent to the SPD-SX. Now I have the correct kit and tempo and can start to play. I can change the song at anytime.

The idea is to have a band's setlist as a json.
The program reads data from a json file, that defines the setlist of your band.

The JSON file contains:
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
  
The JSON is parsed and the needed arrays are built.

When the song is changed, the program change value is sent to the **Global MIDI Channel** located in the JSON.

Additionally the **Song Tempo** is sent as a **MIDI Clock** to the same **MIDI Global Channel** sychronizing all devices on that channel.

