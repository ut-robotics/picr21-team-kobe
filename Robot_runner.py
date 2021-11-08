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
state = State.FIND
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
    sign = math.copysign(1, delta/maxDelta)
    normalizedDelta = math.pow(abs(delta/maxDelta), 2) * sign
    speed = normalizedDelta * maxSpeed
    sign = math.copysign(1, speed)
    return int(int(speed) if abs(speed) >= minSpeed and abs(speed) <= maxSpeed else maxSpeed * sign if speed > maxSpeed else minSpeed * sign)

def HandleFind(data):
    drive.Move2(0, 0, 10, 0)
    if data["count"] >= 1:
        return State.DRIVE
    return State.FIND

def HandleDrive(data):
    if data["count"] >= 1:
        delta_x = data["x"] - camera_x/2
        delta_y = data["y"] - 400
        print(data)
        print(delta_y)
        minSpeed = 2
        maxSpeed = 50
        minDelta = 5
        front_speed = CalcSpeed(delta_y, camera_y, minDelta, 8, 200)#3 + (480-y)/ 540.0 * 30
        side_speed = CalcSpeed(delta_x, camera_x, minDelta, minSpeed, maxSpeed)#(x - data["basket_x"])/480.0 * 15 
        rotSpd = CalcSpeed(delta_x, camera_x, minDelta, minSpeed, 100)#int((x - 480)/480.0 * 25)
        print(front_speed)
        drive.Move2(-0, -front_speed, -rotSpd, 0)
    if data["y"] >= 420: # specify better y value that is near robot, represents ball y value in reference with camera y
        return State.AIM
    if data["count"] <= 0:
        return State.FIND

    return State.DRIVE

def HandleAim(data):
    if 470 <= data["basket_x"] <= 490 and data["y"] >= 480:
        #front_speed = (420-y)/ 480.0 * 30
        #side_speed = (x - basket_x_center)/320.0 * 50
        time.sleep(0.1)
        drive.Stop()
        state = State.THROWING
    delta_x = data["basket_x"] - data["x"]
    delta_y = data["basket_y"] - data["y"]
    front_speed = CalcSpeed(delta_y, camera_y, minDelta, minSpeed, maxSpeed)#3 + (480-y)/ 540.0 * 30
    side_speed = CalcSpeed(delta_x, camera_x, minDelta, minSpeed, maxSpeed)#(x - data["basket_x"])/480.0 * 15 
    rotSpd = CalcSpeed(delta_x, camera_x, minDelta, minSpeed, maxSpeed)#int((x - 480)/480.0 * 25)
    #print("side_speed ", side_speed, "front speed", front_speed, "rotspeed", rotSpd, "kp", data["count"], "x", x, "y",y)
    if data["count"] < 1:
        #ball is lost, probably near the the mouth of the thrower so move forward
        drive.Move2(-0  , front_speed, -0, 0)              
    drive.Move2(-side_speed  , front_speed, -rotSpd, 0)
    return State.DRIVE

i = 0
def HandleThrowing(data):
    global i
    time.sleep(0.1)
    if i >= 3:
        i = 0
        return State.FIND
    if data["count"] >= 1:
        delta_x = data["basket_x"] - data["x"]
        delta_y = data["basket_y"] - data["y"]
        # side_speed = (x - basket_x_center)/480.0 * 15
        thrower_speed = Thrower.ThrowerSpeed(data["basket_distance"])
        # rotSpd = int((x - 480)/480.0 * 20)
        front_speed = CalcSpeed(delta_y, camera_y, minDelta, minSpeed, maxSpeed)#3 + (480-y)/ 540.0 * 30
        side_speed = CalcSpeed(delta_x, camera_x, minDelta, maxSpeed)#(x - basket_x_center)/480.0 * 15 
        rotSpd = CalcSpeed(delta_x, camera_x, minDelta, minSpeed, maxSpeed)#int((x - 480)/480.0 * 25)
        drive.Move2(-side_speed, front_speed, -rotSpd, thrower_speed)
    if data["count"] <= 0:
        thrower_speed = Thrower.ThrowerSpeed(data["basket_distance"])
        drive.Move2(-side_speed, front_speed, -rotSpd, thrower_speed)
        i += 1
    return State.THROWINGs
data = None


switcher = {
    State.FIND: HandleFind,
    State.DRIVE: HandleDrive,
    State.AIM: HandleAim,
    State.THROWING: HandleThrowing
}


while True:
    data = Processor.ProcessFrame(pipeline,camera_x, camera_y)
    #print(state)
    #keypointcount, y, x, basket_x_center, basket_y_center, distance = ip.ProcessFrame(pipeline, camera_x, camera_y)
    #keypointcount, y, x, basket_x_center, basket_y_center, distance = Processor.ProcessFrame(pipeline, camera_x, camera_y)
    #side_speed = (x - data["basket_x"])/float(camera_x) * 5.0

    print(state)

    state = switcher.get(state)(data)
    # match state:
    #     case State.FIND:

    #     case State.DRIVE:

    #     case State.AIM:

    #     case State.THROWING:
    #     case _:
    #         state = State.FIND

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
