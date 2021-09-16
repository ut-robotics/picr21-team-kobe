from serialConnector import SerialConnectorClass
import time

ser = SerialConnectorClass().start()

while(True):
    try:
        time.sleep(1)
        print("testing motor 1")
        ser.write_speeds("sd:10:00:00\r\n")

        time.sleep(2)
        print("testing motor 2")
        ser.write_speeds("sd:00:10:00\r\n")

        time.sleep(2)
        print("testing motor 3")
        ser.write_speeds("sd:00:00:10\r\n")

        time.sleep(2)
        print("testing all motors")
        ser.write_speeds("sd:10:10:10\r\n")

        time.sleep(2)
        print("Stopping motors")
        ser.write_speeds("sd:00:00:00\r\n")
        time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping motor test")
        ser.write_speeds("sd:00:00:00\r\n")
        ser.close()
        break