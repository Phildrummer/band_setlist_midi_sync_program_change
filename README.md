# MIDI Clock Sync and Progam Change for Band

This application reads data from a json file, that defines the setlist of your band.

The JSON file contains:
-  Song Name
-  Song Tempo
-  Program Change
-  MIDI Note for next song
-  MIDI Note for previous song
-  MIDI Note for setlist reset --> goes to first song in the list
-  Global MIDI Channel
  
The JSON is parsed and the needed arrays are built.

When the song is changed, the program change value is sent to the **Global MIDI Channel** located in the JSON.

Additionally the **Song Tempo** is sent as a **MIDI Clock** to the same **MIDI Global Channel** sychronizing all devices on that channel.
