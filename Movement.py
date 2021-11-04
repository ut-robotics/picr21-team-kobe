import serialcomms
import math

ser = serialcomms.Connection('/dev/ttyACM0')

#Order: motor1, motor2, motor3, thrower, failsafe
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
    speed[0] = int(wheelSpeed(movspeed, dir, 240))+rot
    speed[1] = int(wheelSpeed(movspeed, dir, 120))+rot
    speed[2] = int(wheelSpeed(movspeed, dir, 0))+rot

    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

def wheelSpeed(speed, dir, angle):
    wheelLinearVelocity = speed * math.cos(dir - math.radians(angle+30))
    return wheelLinearVelocity

def spinLeft(speed):
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)


def spinRight(speed):
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

def stop():
    speed = [0,0,0,0]
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)
