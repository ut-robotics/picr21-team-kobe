import time
import serial
import struct

ser=serial.Serial('/dev/ttyACM0', 115200, timeout=2)
data_size = struct.calcsize('<hhhH')

def WriteCommand(speed1, speed2, speed3, thrower_speed, disable_failsafe):
    try:
        data = struct.pack('<hhhHBH', speed1, speed2, speed3, thrower_speed, disable_failsafe, 0xAAAA)
        ser.write(data)

        received_data = ser.read(data_size)
        data = struct.unpack('<hhhH', received_data)
        #actual_speed1, actual_speed2, actual_speed_3, feedback_delimiter = data
    except:
        print("error occured couldnt write to serial")
        ser.close()
