import serialcomms
import math
import cv2
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import CameraConfig
import Image_processing as ip

pipeline, camera_x, camera_y = CameraConfig.init()
#Distance from basket
X = [0,122,163,198, 233, 328, 450]
#Used thrower speed
Y = [0,600,800,900, 1000, 1200, 1500]

predicted_function = interp1d(X,Y, kind="linear")
#predict what speed to use from current distance from basket
#print(predicted_speed)
#plt.plot(X,Y)
#plt.show()

wheelAngle1 = 240
wheelAngle2 = 120
wheelAngle3 = 0

ser = serialcomms.Connection('/dev/ttyACM0')


def stop():
    send_speeds([0, 0, 0, 0])

def move(moving_speed, thrower_speed, direction):
    speeds = get_speeds(moving_speed, thrower_speed, direction)
    send_speeds(speeds)

def get_speeds(moving_speed, thrower_speed, direction):
    speeds = [0, 0, 0, 0]
    speeds[0] = int(calc_wheel_speed(moving_speed, direction, wheelAngle1))
    speeds[1] = int(calc_wheel_speed(moving_speed, direction, wheelAngle2))
    speeds[2] = int(calc_wheel_speed(moving_speed, direction, wheelAngle3))
    speeds[3] = thrower_speed
    return speeds

def send_speeds(speeds):
    print("Sending: " + str(speeds))
    #order: motor1, motor2, motor3, thrower, failsafe
    ser.WriteCommand(speeds[0], speeds[1], speeds[2], speeds[3], 0)

def calc_wheel_speed(moving_speed, direction, wheel_angle):
    wheel_speed = moving_speed * math.cos(math.radians(direction - wheel_angle))
    return wheel_speed

def spinRight(speed):
    send_speeds([-30, -30, -30, 0])

def spinLeft(speed):
    send_speeds([15, 15, 15, 0])

def keyBoardControl():
    cv2.namedWindow("Controller")
    movingSpeed = 15
    throwingSpeed = 900
    while(True):
        keypoints, y, x, basket_x_center, basket_y_center, distance = ip.ProcessFrame(pipeline, camera_x, camera_y)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("w"):
            print("Moving forward.")
            move(movingSpeed, 0,330)
        if key == ord("d"):
            print("Moving right.")
            move(movingSpeed, 0, 240)
        if key == ord("s"):
            print("Moving backwards.")
            move(movingSpeed, 0, 150)
        if key == ord("a"):
            print("Moving left.")
            move(movingSpeed, 0, 60)
        if key == ord("e"):
            print("Spinning right.")
            spinRight(movingSpeed)
        if key == ord("q"):
            print("Spinning left.")
            spinLeft(movingSpeed)
        if key == ord("t"):
            #print("Throwing.")
            #print("distance ---->", distance)
            predicted_speed = int(predicted_function(distance*100))
            print("predicted speed", predicted_speed)
            move(0, predicted_speed, 0)
        if key == ord("c"):
            send_speeds([-22,-11, 11, 0]) #25, -10, 15, 0   
            print("Stopping.")
            #stop()
        if key == ord("x"):
            print("Shutting down.")
            stop()
            break

keyBoardControl()

cv2.destroyAllWindows()