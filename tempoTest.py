import clockTimer as CT


if __name__ == "__main__":
# get the ports
    spdSxInPort, spdSxOutPort = CT.getMidiInOutPorts("SPD-SX")
    for bpm in range(50, 201, 1):
        CT.sendMidiClock(spdSxOutPort, bpm)
    