#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import Movement as drive
import Image_processing as ip
import time
import CameraConfig
import math
import numpy
#from scipy.interpolate import interp1d
from enum import Enum
import Thrower

Camera = CameraConfig.Config()

#States for logic
class State(Enum):
    FIND = 0
    DRIVE = 1
    AIM = 2
    THROWING = 3

#Use this to set the first state
state = State.FIND
#set target value with referee commands
target = True
#Create image processing object
Processor = ip.ProcessFrames(target)

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
    if Processor.keypointcount >= 1:
        return State.DRIVE
    return State.FIND

def HandleDrive(data):
    if Processor.keypointcount >= 1:
        delta_x = Processor.x - Camera.camera_x/2
        delta_y = Processor.y - 400
        print(data)
        print(delta_y)
        minSpeed = 2
        maxSpeed = 50
        minDelta = 5
        front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, 8, 200)#3 + (480-y)/ 540.0 * 30
        #side_speed = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, maxSpeed)#(x - data["basket_x"])/480.0 * 15 
        rotSpd = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, 100)#int((x - 480)/480.0 * 25)
        print(front_speed)
        drive.Move2(-0, -front_speed, -rotSpd, 0)
    if Processor.y >= 420: # specify better y value that is near robot, represents ball y value in reference with camera y
        return State.AIM
    if Processor.keypointcount <= 0:
        return State.FIND

    return State.DRIVE

def HandleAim(data):
    if 314 <= Processor.basket_x_center <= 326 and Processor.y >= 440:
        drive.Stop()
        return State.THROWING
    delta_x = Processor.basket_x_center - Processor.x#data["basket_x"] - data["x"]
    delta_y = Processor.basket_y_center - 440#data["basket_y"] - 440
    minSpeed = 2
    maxSpeed = 20
    minDelta = 5
    front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, minSpeed, maxSpeed)#3 + (480-y)/ 540.0 * 30
    side_speed = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, maxSpeed)#(x - data["basket_x"])/480.0 * 15 
    rotSpd = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, 100)#int((x - 480)/480.0 * 25)          
    drive.Move2(-side_speed, -front_speed, -rotSpd, 0)
    return State.AIM

i = 0
def HandleThrowing(data):
    global i
    #time.sleep(0.1)
    if i >= 3:
        i = 0
        return State.FIND
    if Processor.keypointcount >= 1:#data["count"] >= 1:
        delta_x = Processor.basket_x_center - Processor.x#data["basket_x"] - data["x"]
        delta_y = Processor.basket_y_center - 500#data["basket_y"] - 500
        minSpeed = 10
        maxSpeed = 30
        minDelta = 3
        thrower_speed = Thrower.ThrowerSpeed(Processor.basket_distance)
        # rotSpd = int((x - 480)/480.0 * 20)
        front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, minSpeed, maxSpeed)#3 + (480-y)/ 540.0 * 30
        side_speed = CalcSpeed(delta_x, Camera.camera_x, minDelta, maxSpeed)#(x - basket_x_center)/480.0 * 15 
        rotSpd = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, maxSpeed)#int((x - 480)/480.0 * 25)
        drive.Move2(-side_speed, -front_speed, -rotSpd, thrower_speed)
    if Processor.keypointcount <= 0:#data["count"] <= 0:
        thrower_speed = Thrower.ThrowerSpeed(Processor.basket_distance)
        drive.Move2(-side_speed, -front_speed, -rotSpd, thrower_speed)
        i += 1
    return State.THROWING
data = None


switcher = {
    State.FIND: HandleFind,
    State.DRIVE: HandleDrive,
    State.AIM: HandleAim,
    State.THROWING: HandleThrowing
}

def Logic():
    try:
        while True:
            data = Processor.ProcessFrame(Camera.pipeline,Camera.camera_x, Camera.camera_y)
            print(state)

            state = switcher.get(state)(data)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        #cv2.destroyAllWindows()
    except KeyboardInterrupt:
        Camera.StopStreams()

        
