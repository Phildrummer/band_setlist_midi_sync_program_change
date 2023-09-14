from DataObjects import Song
from DataObjects import GlobalConfig
import json, os, mido, mido.backends.rtmidi, time, sys
# Docs: https://docs.python.org/3/library/threading.html#timer-objects
from threading import Timer
from mido.ports import BaseOutput

currentIdx = 0
outPort = None
inPort = None

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class ClockTimer:
    timer = None
    _tempo: int

    @classmethod
    def send_clock_pulse(cls, port: BaseOutput):
        #print("F8")
        port.send(mido.Message('clock'))

    @property
    def interval(self):
        return 60.0 / (self.tempo * 24)  # In seconds

    @property
    def tempo(self):
        return self._tempo

    @tempo.setter
    def tempo(self, value):
        self._tempo = value
        if self.timer:
            self.timer.interval = self.interval

    def __init__(self, out_port, tempo):
        self.tempo = tempo
        self.out_port = out_port
        self.timer = RepeatTimer(
            interval=self.interval,
            function=self.send_clock_pulse,
            args=[self.out_port]
        )

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.cancel()

def sendMidiClock3(song: Song):
    clock = ClockTimer(outPort, tempo=song.tempo)
    clock.start()
    time.sleep(10)
    clock.stop()

def send_clock_pulse(port):
    #print("F8")
    port.send(mido.Message('clock'))

def sendMidiClock2(port, song: Song):
    # Prepare
    interval: float = 60.0 / ((song.tempo) * 24)  # In seconds
    if port == None:
        port = mido.open_output(config.midiOutportName)
    else:
        if port.closed == True:
            port._open()

    timer = RepeatTimer(
        interval=interval, function=send_clock_pulse, args=[port]
    )

    # Launch
    print(f"PROCESSING: Sending MIDI clock messages on {outPort.name} for Song:",f"{song.songname}",f"Tempo: {song.tempo}","...")
    timer.start()
    # run clock for some seconds and then close
    time.sleep(15)
    timer.cancel()
    print(f"DONE: Stopped sending MIDI clock messages on {outPort.name}...")
    

def sendMidiClock(song: Song):
    try:
        # Calculate the time interval (in seconds) between MIDI clock messages based on the tempo
        interval = 60.0 / (song.tempo * 24)  # 24 MIDI clock messages per quarter note
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
    print("Current Working Dir:",current_directory,"\n")

    try:
        print("Output names: ",mido.get_output_names())
    except Exception as e:
        print(e)
        sys.exit()
    
    # Define the filename for the JSON file
    json_filename = os.path.join(current_directory, "setlist.json")

    # Read and parse the JSON file
    with open(json_filename, "r") as json_file:
        data = json.load(json_file)

    allSongs = [Song(song["songname"], song["tempo"], song["programchange"]) for song in data["songs"]]
    print(f"\nTotal Song Count: {len(allSongs)}")
    print("\nSongs:")
    for theSong in allSongs:
        print("Song Name:",theSong.songname,"Song Tempo:",theSong.tempo,"Program Change:",theSong.programchange)
    
    globalconfig = data["globalconfig"]
    config = GlobalConfig(globalconfig['midiChannel'],globalconfig['prevSongMidiNote'],globalconfig['nextSongMidiNote'],globalconfig['resetSongMidiNote'], globalconfig['midiInportName'], globalconfig['midiOutportName'])
    print("\nGlobal Config:")
    print("MIDI Channel:",config.midiChannel,"Previous Song Note:",config.prevSongMidiNote,"Next Song Note:",config.nextSongMidiNote,"Reset Note:",config.resetSongMidiNote,"\n")
    print(mido.get_output_names())

    try:
        inPort = mido.open_input(name=config.midiInportName)
    except Exception as e:
        print(e, "\nexiting script")
        sys.exit()       

    try:
        outPort = mido.open_output(config.midiOutportName)
    except Exception as e:
        print(e, "\nexiting script")
        sys.exit()

    pc = mido.Message(type='program_change',channel=config.midiChannel-1,program=allSongs[currentIdx].programchange-1)
    print("Initial Song: ", pc)
    outPort.send(pc)
    #sendMidiClock(allSongs[currentIdx])
    #sendMidiClock2(outPort, allSongs[currentIdx])
    sendMidiClock3(allSongs[currentIdx])

    
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
                        #sendMidiClock(allSongs[currentIdx])
                        sendMidiClock2(outPort, allSongs[currentIdx])
                        print(f"PROCESSING: Raspberry Pi is listening for MIDI messages on {inPort.name}...")
                        if currentIdx == -1:
                            print("There was an error above.")
                            break
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"\n{e}")
        
