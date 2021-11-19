import serialcomms
import math

ser = serialcomms.Connection('/dev/ttyACM0')

#Order: motor1, motor2, motor3, thrower, failsafe
def Move2(xspd, yspd, rotspd, thrower):
    
    speed = [0,0,0,0]

    movspeed = math.sqrt((xspd)**2 + (yspd)**2)
    #print("movspeed", movspeed)
    dir = math.atan2(xspd, yspd)

    speed[0] = int(WheelSpeed(movspeed, dir, 240))+rotspd
    speed[1] = int(WheelSpeed(movspeed, dir, 120))+rotspd
    speed[2] = int(WheelSpeed(movspeed, dir, 0))+rotspd
    speed[3] = int(thrower)


    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

def WheelSpeed(speed, dir, angle):
    wheelLinearVelocity = speed * math.cos(dir - math.radians(angle+30))
    return wheelLinearVelocity

def SpinLeft(speed):
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)


def SpinRight(speed):
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)

def Stop():
    speed = [0,0,0,0]
    ser.WriteCommand(speed[0], speed[1], speed[2], speed[3], 0)
