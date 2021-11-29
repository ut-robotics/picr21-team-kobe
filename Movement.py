import serialcomms
import math

ser = serialcomms.Connection('/dev/ttyACM0')

#Order: motor1, motor2, motor3, thrower, failsafe
def move_omni(xspd, yspd, rotspd, thrower):
    
    speed = [0,0,0,0]

    movspeed = math.sqrt((xspd)**2 + (yspd)**2)
    #print("movspeed", movspeed)
    dir = math.atan2(xspd, yspd)

    speed[0] = int(wheel_speed(movspeed, dir, 240))+rotspd
    speed[1] = int(wheel_speed(movspeed, dir, 120))+rotspd
    speed[2] = int(wheel_speed(movspeed, dir, 0))+rotspd
    speed[3] = int(thrower)


    ser.write_command(speed[0], speed[1], speed[2], speed[3], 0)

def wheel_speed(speed, dir, angle):
    wheelLinearVelocity = speed * math.cos(dir - math.radians(angle+30))
    return wheelLinearVelocity

def spin_left(speed):
    ser.write_command(speed[0], speed[1], speed[2], speed[3], 0)


def spin_right(speed):
    ser.write_command(speed[0], speed[1], speed[2], speed[3], 0)

def stop():
    speed = [0,0,0,0]
    ser.write_command(speed[0], speed[1], speed[2], speed[3], 0)
