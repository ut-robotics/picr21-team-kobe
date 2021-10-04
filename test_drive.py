import serialcomms
import math
i = 0
#speed = [-10,-10,-10,100]

def move(movspeed, dir):
    speed = [0,0,0,0]
    speed[0] = wheelSpeed(movspeed[0], dir, 0)
    speed[1] = wheelSpeed(movspeed[1], dir, 120)
    speed[2] = wheelSpeed(movspeed[2], dir, 240)
    serialcomms.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

def moveForward(speed):

    #order: motor1, motor2, motor3, thrower, failsafe
    serialcomms.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)


def wheelSpeed(speed, dir, angle):
    wheelLinearVelocity = speed * math.cos(dir - math.radians(angle))
    return wheelLinearVelocity

def spinLeft(speed):
    serialcomms.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)


def spinRight(speed):
    serialcomms.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

def moveBack(speed):
    serialcomms.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

def stop():
    speed = [0,0,0,0]
    serialcomms.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)
    
