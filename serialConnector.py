import serial
from threading import Thread

class SerialConnectorClass:

    def __init__(self):
        # self.port = '/dev/ttyACM1'
        # self.port = '/dev/ttyACM0'
        self.port = 'COM3'
        self.rate = 115200
        print("Opening connection to port " + self.port + ".")
        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.rate,
            bytesize=serial.EIGHTBITS
        )

    def start(self):
        #Thread(target=self.write_speeds, args=()).start()
        return self

    def close_connection(self):
        print("Closing serial port " + self.port + ".")
        self.ser.close()

    def write_speeds(self, speedstr):
        print("Writing " + speedstr + "to port " + self.port)
        self.ser.write(speedstr.encode('utf-8'))

