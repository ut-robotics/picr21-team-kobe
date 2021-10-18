import time
import serial
import struct
import serial.tools.list_ports

data_size = struct.calcsize('<hhhH')

ports = serial.tools.list_ports.comports()

print([port.name for port in ports])


#ser=serial.Serial(port='/dev/ttyACM0', baudrate = 115200, timeout = 2)
def WriteCommand(speed1, speed2, speed3, thrower_speed, disable_failsafe):
    try:
        
        data = struct.pack('<hhhHBH', speed1, speed2, speed3, thrower_speed, disable_failsafe, 0xAAAA)
        ser.write(data)

        received_data = ser.read(data_size)
        data = struct.unpack('<hhhH', received_data)
        print(data)
    except Exception as e:
        print(e)
        
