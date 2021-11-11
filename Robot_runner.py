#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from threading import Thread

import cv2
import Movement as drive
import Image_processing as ip
import CameraConfig
import math
from enum import Enum
import Thrower
import Referee_server as Server

srv = Server.Server()
srv.start()

Camera = CameraConfig.Config()

#States for logic
class State(Enum):
    FIND = 0
    DRIVE = 1
    AIM = 2
    THROWING = 3
    STOPPED = 4

#Use this to set the first state
state = State.AIM
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

def HandleFind(count, y, x, center_x, center_y, basket_distance):
    drive.Move2(0, 0, 10, 0)
    if count >= 1:
        return State.DRIVE
    return State.FIND

def HandleDrive(count, y, x, center_x, center_y, basket_distance):
    if count >= 1:
        delta_x = x - Camera.camera_x/2
        delta_y = y - 410
        print(data)
        print(delta_y)
        minSpeed = 2
        maxSpeed = 50
        minDelta = 5
        front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, 8, 200)#3 + (480-y)/ 540.0 * 30
        #side_speed = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, maxSpeed)#(x - data["basket_x"])/480.0 * 15 
        rotSpd = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, 100)#int((x - 480)/480.0 * 25)
        print(y)
        drive.Move2(-0, -front_speed, -rotSpd, 0)
    if Processor.y >= 420: # specify better y value that is near robot, represents ball y value in reference with camera y
        return State.AIM
    if Processor.keypointcount <= 0:
        return State.FIND

    return State.DRIVE

def HandleAim(count, y, x, center_x, center_y, basket_distance):
    
    if 314 <= center_x <= 326 and y >= 440:
        drive.Stop()
        return State.THROWING
    delta_x = x - center_x# - Processor.x#data["basket_x"] - data["x"]
    delta_y = 420 - y#Processor.basket_y_center - Processor.y#data["basket_y"] - 440
    minSpeed = 5
    maxSpeed = 20
    minDelta = 5
    front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, minSpeed, maxSpeed)#3 + (480-y)/ 540.0 * 30
    side_speed = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, maxSpeed)#(x - data["basket_x"])/480.0 * 15
    rotSpd = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, maxSpeed)#int((x - 480)/480.0 * 25)
    print(x)   
    drive.Move2(-side_speed, front_speed, -rotSpd, 0)
    return State.AIM
    return State.THROWING

def HandleStopped(count, y, x, center_x, center_y, basket_distance):
    drive.stop()
    return State.STOPPED

i = 0
def HandleThrowing(count, y, x, center_x, center_y, basket_distance):
    global i
    if i >= 3:
        i = 0
        return State.FIND
    if Processor.keypointcount >= 1:#data["count"] >= 1:
        delta_x = Processor.basket_x_center - Processor.x#data["basket_x"] - data["x"]
        delta_y = Processor.basket_y_center - 500#data["basket_y"] - 500
        
        minSpeed = 10
        maxSpeed = 30
        minDelta = 5
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

def ListenForRefereeCommands():
    global Processor, state
    try:
        run, target = srv.get_current_referee_command()
        print("Target:  " + str(target))
        print("Run: " + str(run))
        Processor = ip.ProcessFrames(target)
        if not run:
            state = State.STOPPED
        if run and state == State.STOPPED:
            state = State.FIND
    except:
        print("Server client communication failed.")

switcher = {
    State.FIND: HandleFind,
    State.DRIVE: HandleDrive,
    State.AIM: HandleAim,
    State.THROWING: HandleThrowing,
    State.STOPPED: HandleStopped
}

def Logic(switcher):
    global state
    try:
        while True:
            ListenForRefereeCommands()
            print(state)
            count, y, x, center_x, center_y, basket_distance = Processor.ProcessFrame(Camera.pipeline,Camera.camera_x, Camera.camera_y)
            state = switcher.get(state)(count, y, x, center_x, center_y, basket_distance)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    except KeyboardInterrupt:
        Camera.StopStreams()

Thread(target=Logic(switcher)).start()
