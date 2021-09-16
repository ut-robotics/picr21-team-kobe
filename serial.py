import serial
from threading import Thread

def __init__(self):
    # port = '/dev/ttyACM1'
    port = '/dev/ttyACM0'
    rate = 115200
    self.ser = serial.Serial(
        port=port,
        baudrate=rate,
        bytesize=serial.EIGHTBITS,
        stopbits=serial.STOPBITS_ONE
    )
    print("Connection to serial port established.")

def start(self):
    Thread(target=self.write_speeds, args=()).start()
    return self

def write_speeds(self, speedstr):
    self.ser.write(speedstr.encode('utf-8'))

