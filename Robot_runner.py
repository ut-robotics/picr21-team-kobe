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
import Thrower

#States for logic
class State(Enum):
    FIND = 0
    DRIVE = 1
    AIM = 2
    THROWING = 3
#Initialize camera
pipeline, camera_x, camera_y = CameraConfig.init()

#Use this to set the first state
state = State.AIM
i=0
#set target value with referee commands
target = False
#Create image processing object
Processor = ip.ProcessFrames(target)
minSpeed = 10
maxSpeed = 50
minDelta = 10

def CalcSpeed(delta, maxDelta, minDelta, minSpeed, maxSpeed):
    if abs(delta) < minDelta:
        return 0
    normalizedDelta = delta/maxDelta
    speed = normalizedDelta * maxSpeed
    return int(speed) if speed >= minSpeed and speed <= maxSpeed else maxSpeed if speed > maxSpeed else minSpeed

while True:
    #print(state)
    #keypointcount, y, x, basket_x_center, basket_y_center, distance = ip.ProcessFrame(pipeline, camera_x, camera_y)
    keypointcount, y, x, basket_x_center, basket_y_center, distance = Processor.ProcessFrame(pipeline, camera_x, camera_y)
    delta_x = basket_x_center - x
    delta_y = basket_y_center - y
    speed = math.sqrt((camera_x-x)**2 + (camera_y-y)**2)*0.05
    direction = math.atan2(camera_x - x, camera_y - y)
    side_speed = (x - basket_x_center)/320.0 * 5.0

    match state:
        case State.FIND:
            drive.spinRight([-10,-10,-10,0])
            if keypointcount >= 1:
                state = State.DRIVE

        case State.DRIVE:
            if keypointcount >= 1:
                rotSpd = int((x - 480)/480.0 * -15.0)
                drive.move(speed, direction, rotSpd)
            if y >= 420: # specify better y value that is near robot, represents ball y value in reference with camera y
                state = State.AIM
            if keypointcount <= 0:
                state = State.FIND

        case State.AIM:
            if 470 <= basket_x_center <= 490 and y >= 480:
                #front_speed = (420-y)/ 480.0 * 30
                #side_speed = (x - basket_x_center)/320.0 * 50
                time.sleep(0.1)
                drive.stop()
                state = State.THROWING
            front_speed = CalcSpeed(delta_y, camera_y, minDelta, minSpeed, maxSpeed)#3 + (480-y)/ 540.0 * 30
            side_speed = CalcSpeed(delta_x, camera_x, minDelta, maxSpeed)#(x - basket_x_center)/480.0 * 15 
            rotSpd = CalcSpeed(delta_x, camera_x, minDelta, minSpeed, maxSpeed)#int((x - 480)/480.0 * 25)
            print("side_speed ", side_speed, "front speed", front_speed, "rotspeed", rotSpd, "kp", keypointcount, "x", x, "y",y)
            if keypointcount < 1:
                #ball is lost, probably near the the mouth of the thrower so move forward
                drive.move2(-0  , front_speed, -0, 0)              
            drive.move2(-side_speed  , front_speed, -rotSpd, 0)

        case State.THROWING:
            time.sleep(0.1)
            if i >= 3:
                i = 0
                state = State.FIND
            if keypointcount >= 1:
                # side_speed = (x - basket_x_center)/480.0 * 15
                thrower_speed = Thrower.ThrowerSpeed(distance)
                # rotSpd = int((x - 480)/480.0 * 20)
                front_speed = CalcSpeed(delta_y, camera_y, minDelta, minSpeed, maxSpeed)#3 + (480-y)/ 540.0 * 30
                side_speed = CalcSpeed(delta_x, camera_x, minDelta, maxSpeed)#(x - basket_x_center)/480.0 * 15 
                rotSpd = CalcSpeed(delta_x, camera_x, minDelta, minSpeed, maxSpeed)#int((x - 480)/480.0 * 25)
                drive.move2(-side_speed, front_speed, -rotSpd, thrower_speed)
            if keypointcount <= 0:
                thrower_speed = Thrower.ThrowerSpeed(distance)
                drive.move2(-side_speed, front_speed, -rotSpd, thrower_speed)
                i += 1
            state = State.FIND
        case _:
            state = State.FIND

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
