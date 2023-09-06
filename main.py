from DataObjects import Song
from DataObjects import GlobalConfig
import json
import os
import mido
#import mido.backends.rtmidi
import datetime
import time

currentIdx = 0

def midiNoteListenerCallBack(msg, idx):
    try:
        if msg.channel == config.midiChannel - 1:
            if msg.type == 'note_off':
                if msg.note == config.prevSongMidiNote:
                    # go to previous song in the list
                    if idx == 0: #if the current song is the first one in the list
                        idx = len(allSongs)-1
                    else:
                        idx = idx - 1
                elif msg.note == config.nextSongMidiNote:
                    # go to next song in the list
                    if idx == len(allSongs)-1: # if the current song is the last one in the list
                        idx = 0
                    else:
                        idx = idx + 1
                elif msg.note == config.resetSongMidiNote:
                    # go to first song in the list
                    idx = 0

                pc = mido.Message(type='program_change',channel=config.midiChannel-1,program=allSongs[idx].programchange)
                outPort.send(pc)
                print (f"Changing kit to {allSongs[idx].songname}")
            elif msg.type == 'program_change':
                sendMidiClock(allSongs[idx])
                print(f"Raspberry Pi is listening for MIDI messages on {inPort.name}...")
    except Exception as e:
        print(f"\n{e}")
        idx = -1    
        
    return idx
        
def sendMidiClock(song: Song):
    try:
        # Calculate the time interval (in seconds) between MIDI clock messages based on the tempo
        interval = 60.0 / (song.tempo * 24)  # 24 MIDI clock messages per quarter note
        with outPort:
            print(f"Sending MIDI clock messages on {outPort.name} for Song:",f"{song.songname}",f"Tempo: {song.tempo}","...")
            # Send MIDI clock messages periodically to simulate the tempo
            totalTime = 0
            while True:
                msg = mido.Message('clock')
                outPort.send(msg)
                time.sleep(interval)
                totalTime = totalTime + interval
                if totalTime > 10:
                    print(f"Stopped sending MIDI clock messages on {outPort.name}...")
                    break
    except Exception as e:
        print(f"\n{e}")

if __name__ == "__main__":

    # Get the current working directory
    current_directory = os.getcwd()
    print("Current Working Dir:",current_directory,"\n")
    try:        
        print(mido.get_output_names())
    except Exception as e:
        print(e)
    
    # Define the filename for the JSON file
    json_filename = os.path.join(current_directory, "setlist.json")

    # Read and parse the JSON file
    with open(json_filename, "r") as json_file:
        data = json.load(json_file)

    allSongs = [Song(song["songname"], song["tempo"], song["programchange"]) for song in data["songs"]]
    print(f"Total Count: {len(allSongs)}")
    print("\nSongs:")
    for theSong in allSongs:
        print("Song Name:",theSong.songname,"Song Tempo:",theSong.tempo,"Program Change:",theSong.programchange)
    
    globalconfig = data["globalconfig"]
    config = GlobalConfig(globalconfig['midiChannel'],globalconfig['prevSongMidiNote'],globalconfig['nextSongMidiNote'],globalconfig['resetSongMidiNote'], globalconfig['midiInportName'], globalconfig['midiOutportName'])
    print("\nGlobal Config:")
    print("MIDI Channel:",config.midiChannel,"Previous Song Note:",config.prevSongMidiNote,"Next Song Note:",config.nextSongMidiNote,"Reset Note:",config.resetSongMidiNote,"\n")

    inPort = mido.open_input(name=config.midiInportName)
    outPort = mido.open_output(config.midiOutportName)

    pc = mido.Message(type='program_change',channel=config.midiChannel-1,program=allSongs[currentIdx].programchange)
    outPort.send(pc)

    try:          
        while inPort != None:
            print(f"Raspberry Pi is listening for MIDI messages on {inPort.name}...")
            for msg in inPort:
                if msg.type == 'note_off' or msg.type == 'program_change':
                    if outPort.closed == True:
                        outPort._open()
                    currentIdx = midiNoteListenerCallBack(msg, currentIdx)
                    if currentIdx == -1:
                        print("There was an error above.")
                        break
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"\n{e}")
        
