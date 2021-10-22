import serialcomms
import math

ser = serialcomms.Connection('/dev/ttyACM0')


def move(movspeed, dir):
    speed = [0,0,0,0]
    speed[0] = int(wheelSpeed(movspeed, dir, 240))
    speed[1] = int(wheelSpeed(movspeed, dir, 120))
    speed[2] = int(wheelSpeed(movspeed, dir, 0))
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

def moveForward(speed):

    #Order: motor1, motor2, motor3, thrower, failsafe
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)


def wheelSpeed(speed, dir, angle):
    wheelLinearVelocity = speed * math.cos(dir - math.radians(angle+30))
    return wheelLinearVelocity

def spinLeft(speed):
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)


def spinRight(speed):
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

def moveBack(speed):
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

def stop():
    speed = [0,0,0,0]
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)


def orbit():
    speed = [-10,0,0,0]
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

