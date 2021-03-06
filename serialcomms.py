import serial
import struct
import serial.tools.list_ports

data_size = struct.calcsize('<hhhH')
ports = serial.tools.list_ports.comports()
print([port.name for port in ports])


class Connection:
    def __init__(self, port):
        self.ser = serial.Serial(port, baudrate=115200, timeout=2)
        self.port = port
        init_data = struct.pack('<hhhHH', 0, 0, 0, 0, 0xBBBB)
        self.ser.write(init_data)

    def write_command(self, speed1, speed2, speed3, thrower_speed, disable_failsafe):
        try:
            data = struct.pack('<hhhHH', speed1, speed2, speed3, thrower_speed, 0xAAAA)
            self.ser.write(data)
        except Exception as e:
            print(e)
            self.ser.close()
            print([port.name for port in ports])

            # print("serial is none", self.ser is None

            raise
