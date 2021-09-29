import time
import serial
import struct

ser=serial.Serial('COM3', 115200, timeout=2)

# disable_failsafe = 0
# speed1 = 654
# speed2 = 600
# speed3 = 1000
# thrower_speed = 3700

data_size = struct.calcsize('<hhhH')
def WriteCommand(speed1, speed2, speed3, thrower_speed, disable_failsafe):
    try:
        data = struct.pack('<hhhHBH', speed1, speed2, speed3, thrower_speed, disable_failsafe, 0xAAAA)
        ser.write(data)

        received_data = ser.read(data_size)
        data = struct.unpack('<hhhH', received_data)
        #actual_speed1, actual_speed2, actual_speed_3, feedback_delimiter = data
        print(data)
        time.sleep(0.05)
        ser.flush()
    except:
        print("error occured couldnt write to serial")
        ser.close()
