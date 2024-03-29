import json

# Define a custom class
class Song:
    def __init__(self, songname, tempo, programchange, tempoOffset):
        self.songname = songname
        self.tempo = tempo
        self.programchange = programchange
        self.tempoOffset = tempoOffset

    def to_dict(self):
        return {
            "songname": self.songname,
            "tempo": self.tempo,
            "programchange": self.programchange
        }

    # Define a class method to create an instance from a JSON dictionary
    @classmethod
    def from_json(cls, json_data):
        return cls(json_data["songname"], json_data["tempo"], json_data["programchange"])

# Define a custom class
class GlobalConfig:
    def __init__(self, midiChannel, prevSongMidiNote, nextSongMidiNote, resetSongMidiNote, startStopSongMidiNote, shutdownPiMidiNote):
        self.midiChannel = midiChannel
        self.prevSongMidiNote = prevSongMidiNote
        self.nextSongMidiNote = nextSongMidiNote
        self.resetSongMidiNote = resetSongMidiNote
        self.startStopSongMidiNote = startStopSongMidiNote
        self.shutdownPiMidiNote = shutdownPiMidiNote

    # Define a method to convert the instance to a JSON-serializable dictionary
    def to_json(self):
        return {
            "midiChannel": self.midiChannel,
            "prevSongMidiNote": self.prevSongMidiNote,
            "nextSongMidiNote": self.nextSongMidiNote,
            "resetSongMidiNote": self.resetSongMidiNote,
            "startStopSongMidiNote": self.startStopSongMidiNote,
            "shutdownPiMidiNote": self.shutdownPiMidiNote
        }

    # Define a class method to create an instance from a JSON dictionary
    @classmethod
    def from_json(cls, json_data):
        return cls(json_data["midiChannel"], json_data["prevSongMidiNote"], json_data["nextSongMidiNote"], json_data["resetSongMidiNote"])