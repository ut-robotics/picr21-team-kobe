import test_drive
from time import sleep
speed = [30,0,30,0]

i = 0
while(i > 30):
    test_drive.moveForward(speed)
    i += 1
    sleep(0.2)