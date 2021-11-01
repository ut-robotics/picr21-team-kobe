import serialcomms
import math

ser = serialcomms.Connection('/dev/ttyACM0')


def move2(xspd, yspd, rotspd, thrower):

    speed = [0,0,0,0]

    movspeed = math.sqrt((xspd)**2 + (yspd)**2)
    print("movspeed", movspeed)
    dir = math.atan2(xspd, yspd)

    speed[0] = int(wheelSpeed(movspeed, dir, 240))+rotspd
    speed[1] = int(wheelSpeed(movspeed, dir, 120))+rotspd
    speed[2] = int(wheelSpeed(movspeed, dir, 0))+rotspd
    speed[3] = int(thrower)


    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)


def move(movspeed, dir, rot, side_speed):
    speed = [0,0,0,0]
    final = [0,0,0,0]

    speed[0] = int(wheelSpeed(movspeed, dir, 240))+rot
    speed[1] = int(wheelSpeed(movspeed, dir, 120))+rot
    speed[2] = int(wheelSpeed(movspeed, dir, 0))+rot

    # speed0 = int(wheelSpeed(movspeed, dir, 240))
    # speed1 = int(wheelSpeed(movspeed, dir, 120))
    # speed2 = int(wheelSpeed(movspeed, dir, 0))

    # rotation0 = int(wheelSpeed(rot, dir, 240))
    # rotation1 = int(wheelSpeed(rot, dir, 120))
    # rotation2 = int(wheelSpeed(rot, dir, 0))

    # side0 = int(wheelSpeed(side_speed, dir, 240))
    # side1 = int(wheelSpeed(side_speed, dir, 120))
    # side2 = int(wheelSpeed(side_speed, dir, 0))

    
    # final[0] = speed0 + side0 + rotation0
    # final[1] = speed1 + side1 + rotation1
    # final[2] = speed2 + side2 + rotation2

    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)
    #ser.WriteCommand(final[0], final[1], final[2], final[3], 0)

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


def orbit(speed):
    #speed = [-10,0,0,0]
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)