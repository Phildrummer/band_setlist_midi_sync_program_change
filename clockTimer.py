from threading import Timer
from mido.ports import BaseOutput
from mido import Message
import mido

def getMidiInOutPorts(nameToSearch):
    outPutNames = mido.get_output_names()
    # find the spd-sx port name
    for foundName in outPutNames:
        print(f"Port Name: {foundName}")
        if nameToSearch in foundName and "MIDI" not in foundName:
            inPort = mido.open_input(foundName)
            outPort = mido.open_output(foundName)
            return inPort, outPort

class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class ClockTimer:
    timer = None
    _tempo: int

    @classmethod
    def send_clock_pulse(cls, port: BaseOutput):
        port.send(Message('clock'))

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