from DataObjects import Song
from DataObjects import GlobalConfig
import json, os, mido, mido.backends.rtmidi, time, sys
import clockTimer as ct
# Docs: https://docs.python.org/3/library/threading.html#timer-objects
from RPLCD.i2c import CharLCD
import subprocess

currentIdx = 0
outPort = None
inPort = None
lcd = None

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

def exitingProgram(text: str, e: Exception):
    if e != None:
        print("Error: ",e)
    print(text)
    lcd.clear()
    lcd.write_string(text)
    time.sleep(3)
    lcd.clear()
    sys.exit()

if __name__ == "__main__":

    lcd = CharLCD('PCF8574', 0x27)
    # lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1,
    #           cols=20, rows=4, dotsize=8,
    #           charmap='A02',
    #           auto_linebreaks=True,
    #           backlight_enabled=True)
    lcd.clear()
    time.sleep(2)
    lcd.write_string('Welcome to\n\rMIDI controller PCC')
    time.sleep(2)
    # Get the current working directory
    current_directory = os.getcwd() 
    
    # Define the filename for the JSON file
    json_filename = os.path.join(current_directory, "setlist.json")
    
    # Read and parse the JSON file
    with open(json_filename, "r") as json_file:
        data = json.load(json_file)

    allSongs = [Song(song["songname"], song["tempo"], song["programchange"], song["tempoOffset"]) for song in data["songs"]]
    globalconfig = data["globalconfig"]
    config = GlobalConfig(globalconfig['midiChannel'],
                          globalconfig['prevSongMidiNote'],
                          globalconfig['nextSongMidiNote'],
                          globalconfig['resetSongMidiNote'],
                          globalconfig['startStopSongMidiNote'],
                          globalconfig['shutdownPiMidiNote'])
    allMidiControlNotes = [config.nextSongMidiNote,
                           config.prevSongMidiNote,
                           config.resetSongMidiNote,
                           config.shutdownPiMidiNote,
                           config.startStopSongMidiNote]
    # get the spd-sx ports
    try:
        inPort, outPort = ct.getMidiInOutPorts("SPD-SX")

        if inPort == None or outPort == None:
            exitingProgram("No ports found.\n\rExiting script", None)
    except Exception as e:
        exitingProgram("No ports found.\n\rExiting script", e)

    pc = mido.Message(type='program_change',channel=config.midiChannel-1,program=allSongs[currentIdx].programchange-1)
    print("Initial Song: ", f"{allSongs[currentIdx].songname} --> tempo {allSongs[currentIdx].tempo} BPM")
    lcd.clear()
    lcd.write_string(f"Song: {allSongs[currentIdx].songname}\n\rTempo: {allSongs[currentIdx].tempo}")
    time.sleep(5)
    outPort.send(pc)
    clock = None
    # clock = ct.ClockTimer(outPort, tempo=allSongs[currentIdx].tempo + allSongs[currentIdx].tempoOffset)
    # clock.start()
    
    try:          
        while inPort != None:
            print(f"PROCESSING: Raspberry Pi is listening for MIDI messages on {inPort.name}...")
            for msg in inPort:
                print(msg)
                if outPort.closed == True:
                    outPort._open()
                if msg.channel == config.midiChannel - 1:
                    if msg.type == 'note_on' and msg.velocity == 0:
                        if msg.note in allMidiControlNotes: # == config.prevSongMidiNote or msg.note == config.nextSongMidiNote or msg.note == config.resetSongMidiNote or msg.note == config.shutdownPiMidiNote or msg.note == config.startStopSongMidiNote:
                            # start/stop the song(MIDI clock)
                            if msg.note == config.startStopSongMidiNote:                                                            
                                if clock == None:                                    
                                    clock = ct.ClockTimer(outPort, tempo=allSongs[currentIdx].tempo + allSongs[currentIdx].tempoOffset)
                                    clock.start()
                                    print(f"PROCESSING: Raspberry Pi is listening for MIDI messages on {inPort.name}...")
                                else:
                                    clock.stop()
                                    clock = None
                            elif msg.note == config.shutdownPiMidiNote:
                                print('PROCESSING: Shutting down')
                                lcd.clear()
                                lcd.write('Shutting down the Pi...')
                                time.sleep(3)
                                lcd.clear()
                                subprocess.call(['sudo', 'shutdown','-h','now'])
                            else:                            
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
                                    print("PROCESSING: Reseting setlist")
                                    # go to first song in the list
                                    currentIdx = 0
                                
                                pc = mido.Message(type='program_change',channel=config.midiChannel-1,program=allSongs[currentIdx].programchange-1)
                                #print (f"PROCESSING: Changing kit to {allSongs[currentIdx].songname}")
                                outPort.send(pc)
                                print (f"DONE: Changed kit to {allSongs[currentIdx].songname} --> tempo {allSongs[currentIdx].tempo} BPM")
                                lcd.clear()
                                lcd.write(f"Song: {allSongs[currentIdx].songname}\n\rTempo: {allSongs[currentIdx].tempo} BPM")

                            
                            if currentIdx == -1:
                                print("There was an error above.")
                                break
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"\n{e}")
        
