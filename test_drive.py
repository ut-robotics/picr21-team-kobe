import serialcomms
import math
i = 0
#speed = [-10,-10,-10,100]

def move(movspeed, dir):
    speed = [0,0,0,0]
    speed[0] = int(wheelSpeed(movspeed, dir, 240))
    speed[1] = int(wheelSpeed(movspeed, dir, 120))
    speed[2] = int(wheelSpeed(movspeed, dir, 0))
    print("speed", speed)
    serialcomms.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

def moveForward(speed):

    #order: motor1, motor2, motor3, thrower, failsafe
    serialcomms.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)


def wheelSpeed(speed, dir, angle):
    wheelLinearVelocity = speed * math.cos(dir - math.radians(angle+30))
    #print(wheelLinearVelocity, "velocity")
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


def test():
    speed = [0,0,0,0]
    movspeed=10
    dir=0
    # while True:
    #     speed[0] = int(wheelSpeed(movspeed, dir, 240))
    #     speed[1] = int(wheelSpeed(movspeed, dir, 120))
    #     speed[2] = int(wheelSpeed(movspeed, dir, 0))
    #     print("speed", speed)
    #     serialcomms.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)