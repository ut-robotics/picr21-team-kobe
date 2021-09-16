import serial
from threading import Thread

class SerialConnectorClass:

    def __init__(self):
        # port = '/dev/ttyACM1'
        # port = '/dev/ttyACM0'
        self.port = 'COM3'
        self.rate = 115200
        print("Opening connection to port " + self.port + ".")
        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.rate,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE
        )

    def start(self):
        #Thread(target=self.write_speeds, args=()).start()
        return self

    def write_speeds(self, speedstr):
        print("writing " + speedstr + "to port " + self.port)
        self.ser.write(speedstr.encode('utf-8'))

