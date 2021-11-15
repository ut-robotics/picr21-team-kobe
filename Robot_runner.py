#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import Movement as drive
import Image_processing as ip
import CameraConfig
import math
from enum import Enum
import Thrower
import Referee_server as Server
import time

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
#set target value with referee commands True = Blue, !True = Magenta
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
    return int(int(speed) if abs(speed) >= minSpeed and abs(speed) <= maxSpeed else maxSpeed * sign if speed > maxSpeed else minSpeed * sign)



def HandleDrive(count, y, x, center_x, center_y, basket_distance):
    if count > 0:
        delta_x = x - Camera.camera_x/2
        delta_y = 390-y
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
        if 500 > y > 315 : # How close ball y should be to switch to next state
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

def HandleStopped(count, y, x, center_x, center_y, basket_distance):
    drive.Stop()
    return State.STOPPED

def HandleAim(count, y, x, center_x, center_y, basket_distance):
    
    basketInFrame = center_x is not None
    if x is None :
        return State.FIND

    if not basketInFrame:
        delta_x = Camera.camera_x
    else:
        delta_x = x - center_x
    rot_delta_x = x - Camera.camera_x/2
    delta_y = 450 - y
    front_speed = CalcSpeed(delta_y, Camera.camera_y, 7, 3, 150, 30)
    side_speed = CalcSpeed(delta_x, Camera.camera_x, 7, 3, 150, 30)
    rotSpd = CalcSpeed(rot_delta_x, Camera.camera_x, 7, 2, 150, 30)
    print("y", y, "x", x, "center", center_x, "side", side_speed, "front", front_speed,"rot", rotSpd)   
    drive.Move2(-side_speed, front_speed, -rotSpd, 0)
    
    if basketInFrame and 315 <= center_x <= 325 and y >= 410: # Start throwing if ball y is close to robot and basket is centered to camera x
       drive.Stop()
       return State.THROWING

    return State.AIM


i = 0
def HandleThrowing(count, y, x, center_x, center_y, basket_distance):
    global i
    if i >= 20:
        i = 0
        return State.FIND
    if count >= 1:
        basketInFrame = center_x is not None

        if not basketInFrame:
            delta_x = Camera.camera_x
        else:
            delta_x = x - center_x
        rot_delta_x = x - Camera.camera_x/2
        delta_y = 500 - y
        
        minSpeed = 10
        maxSpeed = 30
        minDelta = 6
        thrower_speed = Thrower.ThrowerSpeed(basket_distance)
        front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, minSpeed, 150, maxSpeed)
        side_speed = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, 150, maxSpeed)
        rotSpd = CalcSpeed(rot_delta_x, Camera.camera_x, minDelta, 3, 100, maxSpeed)
        drive.Move2(-0, front_speed, -0, thrower_speed)
    if count <= 0:
        thrower_speed = Thrower.ThrowerSpeed(basket_distance)
        drive.Move2(-0, 10, -0, thrower_speed)
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
    start_time = time.time()
    counter = 0
    global state
    try:
        while True:
            
            # Main code
            ListenForRefereeCommands()
            count, y, x, center_x, center_y, basket_distance = Processor.ProcessFrame(Camera.pipeline,Camera.camera_x, Camera.camera_y)
            print(state)
            state = switcher.get(state)(count, y, x, center_x, center_y, basket_distance)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            
            # FPS stuff
            counter += 1
            if(time.time() - start_time) > 1: # Frame rate per 1 second
                print("FPS -->", counter / (time.time() - start_time))
                counter = 0
                start_time = time.time()
                
                
        cv2.destroyAllWindows()
    except KeyboardInterrupt:        
        Camera.StopStreams()
    except Exception as e:
        print(e)
        Camera.StopStreams()
        raise

Logic(switcher)
