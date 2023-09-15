from DataObjects import Song
from DataObjects import GlobalConfig
import json, os, mido, mido.backends.rtmidi, time, sys
import clockTimer as ct
# Docs: https://docs.python.org/3/library/threading.html#timer-objects


currentIdx = 0
outPort = None
inPort = None

def sendMidiClock3(song: Song):
    #print(f"PROCESSING: Sending MIDI clock messages on {outPort.name} for Song:",f"{song.songname}",f"Tempo: {song.tempo}","...")
    clock = ct(outPort, tempo=song.tempo + 2) #*1.03 - 1.85
    clock.start()
    time.sleep(10)    
    clock.stop()
    #print(f"DONE: Stopped sending MIDI clock messages on {outPort.name}...")
    

def sendMidiClock(song: Song):
    try:
        # Calculate the time interval (in seconds) between MIDI clock messages based on the tempo
        interval = 60.0 / ((song.tempo + song.tempoOffset) * 24)  # 24 MIDI clock messages per quarter note
        with outPort:
            print(f"PROCESSING: Sending MIDI clock messages on {outPort.name} for Song:",f"{song.songname}",f"Tempo: {song.tempo}","...")
            # Send MIDI clock messages periodically to simulate the tempo
            totalTime = 0
            while True:
                msg = mido.Message('clock')
                outPort.send(msg)
                time.sleep(interval)
                totalTime = totalTime + interval
                if totalTime > 15:
                    print(f"DONE: Stopped sending MIDI clock messages on {outPort.name}...")
                    break
    except Exception as e:
        print(f"\n{e}")

if __name__ == "__main__":

    # Get the current working directory
    current_directory = os.getcwd()
    # print("Current Working Dir:",current_directory,"\n")

    # try:
    #     print("Output names: ",mido.get_output_names())
    # except Exception as e:
    #     print(e)
    #     sys.exit()
    
    # Define the filename for the JSON file
    json_filename = os.path.join(current_directory, "setlist.json")

    # Read and parse the JSON file
    with open(json_filename, "r") as json_file:
        data = json.load(json_file)

    allSongs = [Song(song["songname"], song["tempo"], song["programchange"]) for song in data["songs"]]
    #print(f"\nTotal Song Count: {len(allSongs)}")
    #print("\nSongs:")
    #for theSong in allSongs:
        #print("Song Name:",theSong.songname,"Song Tempo:",theSong.tempo,"Program Change:",theSong.programchange)
    
    globalconfig = data["globalconfig"]
    config = GlobalConfig(globalconfig['midiChannel'],globalconfig['prevSongMidiNote'],globalconfig['nextSongMidiNote'],globalconfig['resetSongMidiNote'])
    #print("\nGlobal Config:")
    #print("MIDI Channel:",config.midiChannel,"Previous Song Note:",config.prevSongMidiNote,"Next Song Note:",config.nextSongMidiNote,"Reset Note:",config.resetSongMidiNote,"\n")
    #print(mido.get_output_names())
    # get the in- and outport names
    #outPutNames = mido.get_output_names()
    # find the spd-sx ports

    inPort, outPort = ct.getMidiInOutPorts("SPD-SX")

    if inPort == None or outPort == None:
        print("No ports found. Exiting script")
        sys.exit()
    
    # portName = ""
    # for foundName in outPutNames:
    #     print(f"Port Name: {foundName}")
    #     if "SPD-SX" in foundName and "MIDI" not in foundName:
    #         portName = foundName
    #         break
    # # Check if any matching string was found
    # if portName != "":
    #     print("Found the SPD-SX ports:", portName)
    #     try:
    #         inPort = mido.open_input(portName)
    #     except Exception as e:
    #         print(e, "\nexiting script")
    #         sys.exit()       

    #     try:
    #         outPort = mido.open_output(portName)
    #     except Exception as e:
    #         print(e, "\nexiting script")
    #         sys.exit()

    # else:
    #     print("\nNo SPD-SX found. Exiting script")
    #     sys.exit()

    pc = mido.Message(type='program_change',channel=config.midiChannel-1,program=allSongs[currentIdx].programchange-1)
    print("Initial Song: ", pc)
    outPort.send(pc)
    ct.sendMidiClock(outPort, allSongs[currentIdx].tempo + allSongs[currentIdx].tempoOffset)
    
    try:          
        while inPort != None:
            print(f"PROCESSING: Raspberry Pi is listening for MIDI messages on {inPort.name}...")
            for msg in inPort:
                print(msg)
                if outPort.closed == True:
                    outPort._open()
                if msg.channel == config.midiChannel - 1:
                    if msg.type == 'note_on' and msg.velocity == 0:
                        if msg.note == config.prevSongMidiNote:
                        # go to previous song in the list
                            if currentIdx == 0: #if the current song is the first one in the list
                                currentIdx = len(allSongs)-1
                            else:
                                currentIdx = currentIdx - 1
                        elif msg.note == config.nextSongMidiNote:
                            # go to next song in the list
                            if currentIdx == len(allSongs)-1: # if the current song is the last one in the list
                                currentIdx = 0
                            else:
                                currentIdx = currentIdx + 1
                        elif msg.note == config.resetSongMidiNote:
                            # go to first song in the list
                            currentIdx = 0

                        pc = mido.Message(type='program_change',channel=config.midiChannel-1,program=allSongs[currentIdx].programchange-1)
                        print (f"PROCESSING: Changing kit to {allSongs[currentIdx].songname}")
                        outPort.send(pc)
                        print (f"DONE: Changed kit to {allSongs[currentIdx].songname}")
                        ct.sendMidiClock(outPort, allSongs[currentIdx].tempo + allSongs[currentIdx].tempoOffset)
                        print(f"PROCESSING: Raspberry Pi is listening for MIDI messages on {inPort.name}...")
                        if currentIdx == -1:
                            print("There was an error above.")
                            break
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"\n{e}")
        
