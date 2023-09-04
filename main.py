from DataObjects import Song
from DataObjects import GlobalConfig
import json
import os

if __name__ == "__main__":

    # Get the current working directory
    current_directory = os.getcwd()
    
    # Define the filename for the JSON file
    json_filename = os.path.join(current_directory, "setlist.json")

    # Read and parse the JSON file
    with open(json_filename, "r") as json_file:
        data = json.load(json_file)

    print("Songs:")
    for song in data["songs"]:
        print(f"Song Name: {song['songname']}, Tempo: {song['tempo']}, Program Change: {song['programchange']}")

    print("\nGlobal Config:")
    globalconfig = data["globalconfig"]
    print(f"Midi Channel: {globalconfig['midiChannel']}, Prev Song MIDI NOTE: {globalconfig['prevSongMidiNote']}, Next Song MIDI NOTE: {globalconfig['nextSongMidiNote']}, Reset MIDI NOTE: {globalconfig['resetSongMidiNote']}")

