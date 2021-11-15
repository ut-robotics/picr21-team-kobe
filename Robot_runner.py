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
state = State.STOPPED
#set target value with referee commands
target = True
#Create image processing object
Processor = ip.ProcessFrames(target)

def CalcSpeed(delta, maxDelta, minDelta, minSpeed, maxDeltaSpeed, maxSpeed):
    if abs(delta) < minDelta:
        return 0
    deltaDiv = delta/maxDelta
    sign = math.copysign(1, deltaDiv)
    normalizedDelta = math.pow(abs(deltaDiv), 2) * sign
    speed = normalizedDelta * maxDeltaSpeed
    #sign = math.copysign(1, speed)
    return int(int(speed) if abs(speed) >= minSpeed and abs(speed) <= maxSpeed else maxSpeed * sign if speed > maxSpeed else minSpeed * sign)



def HandleDrive(count, y, x, center_x, center_y, basket_distance):
    if count > 0:
        delta_x = x - Camera.camera_x/2
        delta_y = 390-y
        #print(data)
        #print(delta_y)
        minSpeed = 2
        maxSpeed = 50
        minDelta = 5
        front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, 5, 350, 40)#3 + (480-y)/ 540.0 * 30
        print(front_speed, delta_y, Camera.camera_y)
        #side_speed = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, maxSpeed)#(x - data["basket_x"])/480.0 * 15 
        rotSpd = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, 150, 20)#int((x - 480)/480.0 * 25)
        print(y,x)
        drive.Move2(-0, front_speed, -rotSpd, 0)
        print(count)
        if 500 > y > 315 : # specify better y value that is near robot, represents ball y value in reference with camera y
            return State.AIM
    if count <= 0 or None:
        return State.FIND

    return State.DRIVE

def HandleFind(count, y, x, center_x, center_y, basket_distance):
    drive.Move2(0, 0, 10, 0)
    if count >= 1:
        HandleDrive(count, y, x, center_x, center_y, basket_distance)
        return State.DRIVE
    return State.FIND

def HandleAim(count, y, x, center_x, center_y, basket_distance):
    
    basketInFrame = center_x is not None
    if x is None :
        return State.FIND

    if not basketInFrame:
        delta_x = Camera.camera_x
    else:
        delta_x = x - center_x
    # if cqreturn State.FIND
    rot_delta_x = x - Camera.camera_x/2
    delta_y = 450 - y
    minSpeed = 5
    maxSpeed = 20
    minDelta = 7
    front_speed = CalcSpeed(delta_y, Camera.camera_y, 7, 2, 150, 30)#3 + (480-y)/ 540.0 * 30
    side_speed = CalcSpeed(delta_x, Camera.camera_x, 7, 2, 150, 30)#(x - data["basket_x"])/480.0 * 15 
    rotSpd = CalcSpeed(rot_delta_x, Camera.camera_x, 7, 2, 150, 30)#int((x - 480)/480.0 * 25)
    print("y", y, "x", x, "center", center_x, "side", side_speed, "front", front_speed,"rot", rotSpd)   
    drive.Move2(-side_speed, front_speed, -rotSpd, 0)
    
    if basketInFrame and 315 <= center_x <= 325 and y >= 410:
       drive.Stop()
       return State.THROWING

    return State.AIM

def HandleStopped(count, y, x, center_x, center_y, basket_distance):
    drive.Stop()
    return State.STOPPED

i = 0
def HandleThrowing(count, y, x, center_x, center_y, basket_distance):
    global i
    if i >= 3:
        i = 0
        return State.FIND
    if count >= 1:#data["count"] >= 1:
        basketInFrame = center_x is not None

        if not basketInFrame:
            delta_x = Camera.camera_x
        else:
            delta_x = x - center_x
        rot_delta_x = x - Camera.camera_x/2
        #delta_x = x - center_x# - Processor.x#data["basket_x"] - data["x"]
        delta_y = 500 - y
        # delta_x = Processor.basket_x_center - Processor.x#data["basket_x"] - data["x"]
        # delta_y = Processor.basket_y_center - 500#data["basket_y"] - 500
        
        minSpeed = 10
        maxSpeed = 30
        minDelta = 6
        thrower_speed = Thrower.ThrowerSpeed(basket_distance)
        # rotSpd = int((x - 480)/480.0 * 20)
        front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, minSpeed, 150, maxSpeed)#3 + (480-y)/ 540.0 * 30
        side_speed = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, 150, maxSpeed)#(x - basket_x_center)/480.0 * 15 
        rotSpd = CalcSpeed(rot_delta_x, Camera.camera_x, minDelta, 3, 100, maxSpeed)#int((x - 480)/480.0 * 25)
        drive.Move2(-0, front_speed, -0, thrower_speed)
    if count <= 0:#data["count"] <= 0:
        thrower_speed = Thrower.ThrowerSpeed(basket_distance)
        drive.Move2(-0, 10, -0, thrower_speed)
        #time.sleep(0.1)
        i += 1
    return State.THROWING
data = None

def ListenForRefereeCommands():
    global Processor, state
    try:
        run, target = srv.get_current_referee_command()
        print("Target:  " + str(target))
        print("Run: " + str(run))
        
        Processor.SetTarget(target)
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

            #state = State.AIM
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    except KeyboardInterrupt:
        #Thread.join()
        
        Camera.StopStreams()
t1 = Thread(target=Logic(switcher))
t1.start()
