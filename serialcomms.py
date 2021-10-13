import time
import serial
import struct

data_size = struct.calcsize('<hhhH')

ser=serial.Serial(port='/dev/ttyACM0', baudrate = 115200, timeout = 2)
def WriteCommand(speed1, speed2, speed3, thrower_speed, disable_failsafe):
    try:
        
        data = struct.pack('<hhhHBH', speed1, speed2, speed3, thrower_speed, disable_failsafe, 0xAAAA)
        ser.write(data)

        received_data = ser.read(data_size)
        data = struct.unpack('<hhhH', received_data)
        print(data)
    except Exception as e:
        print(e)
        
