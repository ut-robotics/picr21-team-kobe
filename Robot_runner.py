#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import Movement as drive
import Image_processing as ip
import time
import CameraConfig
import math
import numpy
from scipy.interpolate import interp1d
from enum import Enum

#States for logic
class State(Enum):
    FIND = 0
    DRIVE = 1
    AIM = 2
    THROWING = 3
#Initialize camera
pipeline, camera_x, camera_y = CameraConfig.init()
#Distance from basket in cm
X = [0,122,163,198, 233, 328, 450, 600]
#Used thrower speed
Y = [700,700,800,900, 1000, 1200, 1600, 2400]
#Function that estimates the speed to use from robot's current distance from the basket
predicted_function = interp1d(X,Y, kind="linear")
#Use this to set the first state
state = State(3)
i=0
#set target value with referee commands
target = False
#Create image processing object
Processor = ip.ProcessFrames(target)

while True:
    #print(state)
    #keypointcount, y, x, basket_x_center, basket_y_center, distance = ip.ProcessFrame(pipeline, camera_x, camera_y)
    keypointcount, y, x, basket_x_center, basket_y_center, distance = Processor.ProcessFrame(pipeline, camera_x, camera_y)
    speed = math.sqrt((camera_x-x)**2 + (camera_y-y)**2)*0.05
    direction = math.atan2(camera_x - x, camera_y - y)
    side_speed = (x - basket_x_center)/320.0 * 5.0

    match state:
        case State(0):
            drive.spinRight([-10,-10,-10,0])
            if keypointcount >= 1:
                state = State.DRIVE

        case State(1):
            if keypointcount >= 1:
                rotSpd = int((x - 480)/480.0 * -15.0)
                drive.move(speed, direction, rotSpd)
            if y >= 420: # specify better y value that is near robot, represents ball y value in reference with camera y
                state = State.AIM
            if keypointcount <= 0:
                state = State.FIND

        case State(2):
            if 470 <= basket_x_center <= 490 and y >= 480:
                #front_speed = (420-y)/ 480.0 * 30
                #side_speed = (x - basket_x_center)/320.0 * 50
                time.sleep(0.1)
                drive.stop()
                state = State.THROWING
            front_speed =3 + (480-y)/ 540.0 * 30
            side_speed = (x - basket_x_center)/480.0 * 15 
            rotSpd = int((x - 480)/480.0 * 25)
            print("side_speed ", side_speed, "front speed", front_speed, "rotspeed", rotSpd, "kp", keypointcount, "x", x, "y",y)
            if keypointcount < 1:
                drive.move2(-side_speed  , front_speed, -0, 0)              
            drive.move2(-side_speed  , front_speed, -rotSpd, 0)

        case State(3):
            time.sleep(0.1)
            if i >= 3:
                i = 0
                state = "Find"
            if keypointcount >= 1:
                side_speed = (x - basket_x_center)/480.0 * 15
                thrower_speed = int(predicted_function(distance*100))
                rotSpd = int((x - 480)/480.0 * 20)
                drive.move2(-0, 15, -0, thrower_speed)

            #print("i", i)
            if keypointcount <= 0:
                thrower_speed = int(predicted_function(distance*100))
                drive.move2(-0, 15, -0, thrower_speed)
                i += 1
            state = State.FIND



    # if state == "Find":
    #     drive.spinRight([-10,-10,-10,0])
    #     if keypointcount >= 1:
    #         state = "Driving"
    
    # elif state == "Driving":
        
    #     if keypointcount >= 1:
    #         rotSpd = int((x - 480)/480.0 * -15.0)
    #         drive.move(speed, direction, rotSpd)
    #         #print("kp", keypointcount)

    #     if y >= 420: # specify better y value that is near robot, represents ball y value in reference with camera y
    #         #drive.stop()
    #         state = "Aim"
    #     if keypointcount <= 0:
    #         state = "Find"
    
    # elif state == "Aim":
    #     if 470 <= basket_x_center <= 490 and y >= 480:
    #         #front_speed = (420-y)/ 480.0 * 30
    #         #side_speed = (x - basket_x_center)/320.0 * 50
    #         time.sleep(0.1)
    #         drive.stop()
    #         state = "Throwing"
    #     #print("y", y, "x", x, "basket", basket_x_center)

    #     front_speed =3 + (480-y)/ 540.0 * 30

    #     side_speed = (x - basket_x_center)/480.0 * 15
        
    #     rotSpd = int((x - 480)/480.0 * 25)
    #     # if front_speed <= 2:
    #     #     front_speed = 10
    #     # if side_speed <= 2:
    #     #     side_speed = 10
    #     print("side_speed ", side_speed, "front speed", front_speed, "rotspeed", rotSpd, "kp", keypointcount, "x", x, "y",y)
    #     if keypointcount < 1:
    #             drive.move2(-side_speed  , front_speed, -0, 0)
            
    #     drive.move2(-side_speed  , front_speed, -rotSpd, 0)

    # elif state == "Throwing":
    #     time.sleep(0.1)
    #     #     #calculate some speed for thrower motor here and send it to serial, figure out some formula, probably polynomial regression for curve fitting
    #     #print("y", y)
    #     if i >= 3:
    #         i = 0
    #         state = "Find"
    #     if keypointcount >= 1:
    #         side_speed = (x - basket_x_center)/480.0 * 15
    #         thrower_speed = int(predicted_function(distance*100))
    #         # if front_speed <= 5:
    #         #     front_speed = 15
    #         # if side_speed <= 5:
    #         #     side_speed = 5
            
    #         rotSpd = int((x - 480)/480.0 * 20)
    #         drive.move2(-0, 15, -0, thrower_speed)

    #     #print("i", i)
    #     if keypointcount <= 0:
    #         #drive.move2(-0, 10, -rotSpd, 0)
    #         thrower_speed = int(predicted_function(distance*100))

    #         drive.move2(-0, 15, -0, thrower_speed)
    #         i += 1
    #     # print("thrower speed ---->", thrower_speed)
    #     #     #drive.moveForward([0,-10,10,thrower_speed])

    #     #state = "Find"


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
