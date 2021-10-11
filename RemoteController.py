import serialcomms
import math
import cv2

wheelAngle1 = 240
wheelAngle2 = 120
wheelAngle3 = 0

def stop():
    send_speeds([0, 0, 0, 0])

def move(moving_speed, thrower_speed, direction):
    speeds = get_speeds(moving_speed, thrower_speed, direction)
    send_speeds(speeds)

def get_speeds(moving_speed, thrower_speed, direction):
    speeds = [0, 0, 0, 0]
    speeds[0] = int(calc_wheel_speed(moving_speed, direction, wheelAngle1))
    speeds[1] = int(calc_wheel_speed(moving_speed, direction, wheelAngle2))
    speeds[2] = - int(calc_wheel_speed(moving_speed, direction, wheelAngle3))
    speeds[3] = thrower_speed
    return speeds

def send_speeds(speeds):
    print("Sending: " + str(speeds))
    #order: motor1, motor2, motor3, thrower, failsafe
    serialcomms.WriteCommand(speeds[0], speeds[1], speeds[2], speeds[3], 0)

def calc_wheel_speed(moving_speed, direction, wheel_angle):
    wheel_speed = moving_speed * math.cos(math.radians(direction - wheel_angle))
    return wheel_speed

def spinRight(speed):
    send_speeds([-5, -5, -5, 0])

def spinLeft(speed):
    send_speeds([5, 5, 5, 0])

def keyBoardControl():
    cv2.namedWindow("Controller")
    while(True):
        key = cv2.waitKey(1) & 0xFF
        if key == ord("w"):
            print("Moving forward.")
            move(5, 0, 90)
        if key == ord("d"):
            print("Moving right.")
            move(5, 0, 180)
        if key == ord("s"):
            print("Moving backwards.")
            move(5, 0, 270)
        if key == ord("a"):
            print("Moving left.")
            move(5, 0, 0)
        if key == ord("e"):
            print("Spinning right.")
            spinRight(5)
        if key == ord("q"):
            print("Spinning left.")
            spinLeft(5)
        if key == ord("t"):
            print("Throwing.")
            move(0, 5, 0)
        if key == ord("c"):
            print("Stopping.")
            stop()
        if key == ord("x"):
            print("Shutting down.")
            stop()
            break

keyBoardControl()

cv2.destroyAllWindows()