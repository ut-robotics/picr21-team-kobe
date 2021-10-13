import test_drive
from time import sleep
speed = [0,-10,10,0]

i = 0
while(i < 80):
    test_drive.moveForward(speed)
    i += 1
    sleep(0.2)
