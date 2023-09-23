from DataObjects import Song
from DataObjects import GlobalConfig
import json, os, mido, mido.backends.rtmidi, time, sys
import clockTimer as ct
# Docs: https://docs.python.org/3/library/threading.html#timer-objects
import smbus
import time

# Define I2C bus and LCD address
bus = smbus.SMBus(1)  # 1 indicates /dev/i2c-1

# Define LCD address
lcd_addr = 0x3F  # Use 'i2cdetect -y 1' to find the correct address

# LCD constants
LCD_WIDTH = 20
LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94  # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4  # LCD RAM address for the 4th line

def lcd_init():
    # Initialize the LCD
    bus.write_byte(lcd_addr, 0x38)  # 2-line display, 5x8 character font
    bus.write_byte(lcd_addr, 0x0C)  # Display on, cursor off, blink off
    bus.write_byte(lcd_addr, 0x01)  # Clear display

def lcd_text(message, line):
    # Send text to the LCD
    if line == 1:
        address = LCD_LINE_1
    elif line == 2:
        address = LCD_LINE_2
    elif line == 3:
        address = LCD_LINE_3
    elif line == 4:
        address = LCD_LINE_4
    else:
        return

    message = message.ljust(LCD_WIDTH)
    bus.write_byte(lcd_addr, address)
    for char in message:
        bus.write_byte_data(lcd_addr, 0x40, ord(char))

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

    lcd_init()
    lcd_text("Hello, World!", 1)
    lcd_text("Hello, World!", 2)
    lcd_text("Hello, World!", 3)
    lcd_text("Hello, World!", 4)
    # Get the current working directory
    current_directory = os.getcwd() 
    
    # Define the filename for the JSON file
    json_filename = os.path.join(current_directory, "setlist.json")
    
    # Read and parse the JSON file
    with open(json_filename, "r") as json_file:
        data = json.load(json_file)

    allSongs = [Song(song["songname"], song["tempo"], song["programchange"], song["tempoOffset"]) for song in data["songs"]]
    globalconfig = data["globalconfig"]
    config = GlobalConfig(globalconfig['midiChannel'],globalconfig['prevSongMidiNote'],globalconfig['nextSongMidiNote'],globalconfig['resetSongMidiNote'])
    # get the spd-sx ports
    try:
        inPort, outPort = ct.getMidiInOutPorts("SPD-SX")

        if inPort == None or outPort == None:
            print("No ports found. Exiting script")
            sys.exit()
    except Exception as e:
        print(f"{e}","\nNo ports found. Exiting script")
        sys.exit()

    pc = mido.Message(type='program_change',channel=config.midiChannel-1,program=allSongs[currentIdx].programchange-1)
    print("Initial Song: ", f"{allSongs[currentIdx].songname} --> tempo {allSongs[currentIdx].tempo} BPM")
    outPort.send(pc)
    clock = None
    clock = ct.ClockTimer(outPort, tempo=allSongs[currentIdx].tempo + allSongs[currentIdx].tempoOffset)
    clock.start()
    
    try:          
        while inPort != None:
            print(f"PROCESSING: Raspberry Pi is listening for MIDI messages on {inPort.name}...")
            for msg in inPort:
                print(msg)
                if outPort.closed == True:
                    outPort._open()
                if msg.channel == config.midiChannel - 1:
                    if msg.type == 'note_on' and msg.velocity == 0:
                        if msg.note == config.prevSongMidiNote or msg.note == config.nextSongMidiNote or msg.note == config.resetSongMidiNote:
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
                            if clock != None:
                                clock.stop()
                            clock = ct.ClockTimer(outPort, tempo=allSongs[currentIdx].tempo + allSongs[currentIdx].tempoOffset)
                            clock.start()
                            print(f"PROCESSING: Raspberry Pi is listening for MIDI messages on {inPort.name}...")
                            if currentIdx == -1:
                                print("There was an error above.")
                                break
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"\n{e}")
        
