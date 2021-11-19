#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import stat
import cv2
import Movement as drive
import Image_processing as ip
import CameraConfig
import math
from enum import Enum
import Thrower
import Referee_server as Server
import time
import Xbox360

class RobotStateData():
    def __init__(self) -> None:
        self.ball_x = None
        self.ball_y = None
        self.basket_x = None
        self.image_processor = None
        self.state = State.STOPPED
        self.keypoint_count = None
        self.has_thrown = False
        self.after_throw_counter = 0
        self.floor_area = None
        self.basket_distance = None


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
    MANUAL = 5

#set target value with referee commands True = Blue, !True = Magenta
target = True
#Create image processing object
Processor = ip.ProcessFrames(target, Camera)

def CalcSpeed(delta, maxDelta, minDelta, minSpeed, maxDeltaSpeed, maxSpeed):
    if abs(delta) < minDelta:
        return 0
    deltaDiv = delta/maxDelta
    sign = math.copysign(1, deltaDiv)
    normalizedDelta = math.pow(abs(deltaDiv), 2) * sign
    speed = normalizedDelta * maxDeltaSpeed
    return int(int(speed) if abs(speed) >= minSpeed and abs(speed) <= maxSpeed else maxSpeed * sign if speed > maxSpeed else minSpeed * sign)

def HandleManual(yspd, xspd, rotspd, throw):
    drive.Stop()
    if throw == 1:
        drive.Move2(int(yspd*10),int(xspd*10),int(rotspd*10), 1000)
    else:
        drive.Move2(int(yspd*10),int(xspd*10),int(rotspd*10),0)
    
        

def HandleDrive(state_data):

    if state_data.floor_area is None or state_data.floor_area < 20000:
        
        drive.Move2(0, -10,20,0)
        time.sleep(0.3)
        return State.FIND
    
    if state_data.keypoint_count > 0 and state_data.floor_area > 20000:
        #print(floorarea)
        delta_x = state_data.ball_x - Camera.camera_x/2
        delta_y = 390-state_data.ball_y
        minSpeed = 2
        maxSpeed = 50
        minDelta = 5
        front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, 5, 500, 50)
        rotSpd = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, 300, 40)
        drive.Move2(-0, front_speed, -rotSpd, 0)
        
        if 500 > state_data.ball_y > 315 : # How close ball y should be to switch to next state
            state_data.state = State.AIM
            return
        
    if state_data.keypoint_count <= 0 or None:
        state_data.state = State.FIND
        return
    
    state_data.state = State.DRIVE

def HandleFind(state_data):
    drive.Move2(0, 0, 10, 0)
    if state_data.keypoint_count >= 1:
        HandleDrive(state_data)
        state_data.state = State.DRIVE
        return
    state_data.state = State.FIND

def HandleStopped(state_data):
    drive.Stop()
    state_data.state = State.STOPPED

def HandleAim(state_data):
    
    if state_data.floor_area is None or state_data.floor_area < 15000:
        floorarea = 0
        state_data.state = State.FIND
        return
    
    basketInFrame = state_data.basket_x is not None
    if state_data.ball_x is None :
        state_data.state = State.FIND
        return
    
    if not basketInFrame:
        delta_x = Camera.camera_x
    else:
        delta_x = state_data.ball_x - state_data.basket_x
    
    rot_delta_x = state_data.ball_x - Camera.camera_x/2
    delta_y = 450 - state_data.ball_y
    front_speed = CalcSpeed(delta_y, Camera.camera_y, 7, 3, 500, 30)
    side_speed = CalcSpeed(delta_x, Camera.camera_x, 7, 3, 200, 40)
    rotSpd = CalcSpeed(rot_delta_x, Camera.camera_x, 7, 3, 200, 40)
    drive.Move2(-side_speed, front_speed, -rotSpd, 0)
    
    if basketInFrame and 320 <= state_data.basket_x <= 335 and state_data.ball_y >= 410: # Start throwing if ball y is close to robot and basket is centered to camera x
        drive.Stop()                             #prev center 315 to 325
        state_data.state = State.THROWING
        return
    state_data.state = State.AIM

def HandleThrowing(state_data):
    
    minSpeed = 15
    maxSpeed = 30
    minDelta = 6
    
    if state_data.has_thrown:
        state_data.after_throw_counter += 1

    if state_data.after_throw_counter > 60:
        state_data.after_throw_counter = 0
        state_data.state = State.FIND
        state_data.has_thrown = False
        return
    
    if state_data.keypoint_count >= 1:
    
        basketInFrame = state_data.basket_x is not None

        if not basketInFrame:
            delta_x = Camera.camera_x
        else:
            delta_x = state_data.ball_x - state_data.basket_x
        rot_delta_x = state_data.ball_x - Camera.camera_x/2 #if no ball and throw true basket_x - camera_x
        delta_y = 500 - state_data.ball_y
        thrower_speed = Thrower.ThrowerSpeed(state_data.basket_distance)
        front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, minSpeed, 200, maxSpeed)
        #side_speed = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, 150, maxSpeed)
        rotSpd = CalcSpeed(rot_delta_x, Camera.camera_x, minDelta, 2, 100, maxSpeed)
        drive.Move2(-0, front_speed, -rotSpd, thrower_speed)
        state_data.has_thrown = True
        state_data.state = State.THROWING
        return
    
    # elif state_data.keypoint_count == 0 and state_data.has_thrown: 
    #     basketInFrame = state_data.basket_x is not None

    #     if not basketInFrame:
    #         delta_x = Camera.camera_x
    #     else:
    #         rot_delta_x = state_data.basket_x - Camera.camera_x
    #     #rot_delta_x = state_data.basket_x - Camera.camera_x
    
    #         #delta_x = state_data.ball_x - state_data.basket_x
    #     delta_y = 0#500 - Camera.camera_y
    #     thrower_speed = Thrower.ThrowerSpeed(state_data.basket_distance)
    #     front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, minSpeed, 200, maxSpeed)
    #     rotSpd = CalcSpeed(rot_delta_x, Camera.camera_x, minDelta, 2, 100, maxSpeed)
    #     drive.Move2(-0, 15, -rotSpd, thrower_speed)
    #     state_data.state = State.THROWING
    #     return
    
    elif state_data.keypoint_count == 0 and not state_data.has_thrown:    
        state_data.state = State.FIND
    #state_data.has_thrown = False
data = None

def ListenForRefereeCommands(state_data, Processor):
    try:
        run, target = srv.get_current_referee_command()
        #print("Target:  " + str(target))
        #print("Run: " + str(run))
        
        Processor.SetTarget(target)
        if not run:
            state_data.state = State.STOPPED
            return
        if run and state_data.state == State.STOPPED:
            print(state_data.state)
            state_data.state = State.FIND
            return
    except:
        print("Server client communication failed.")

switcher = {
    State.FIND: HandleFind,
    State.DRIVE: HandleDrive,
    State.AIM: HandleAim,
    State.THROWING: HandleThrowing,
    State.STOPPED: HandleStopped,
    State.MANUAL: HandleManual
}

def Logic(switcher):
    start_time = time.time()
    counter = 0
    joy = Xbox360.XboxController()

    state_data = RobotStateData()
    try:
        while True:
            # Main code
            ListenForRefereeCommands(state_data, Processor)
            #Align depth frame if we are in throw state
            count, y, x, center_x, center_y, basket_distance, floorarea = Processor.ProcessFrame(align_frame = state_data.state == State.THROWING)
            state_data.ball_x = x 
            state_data.ball_y = y
            state_data.keypoint_count = count
            state_data.basket_x = center_x
            state_data.floor_area = floorarea
            state_data.basket_distance = basket_distance

            #print("ball x: ", x, "basket x: ", center_x, "ball y: ", y)
            switcher.get(state_data.state)(state_data)
            #left x left y right x
            lx,ly,rx,abtn,ybtn,start,stop = joy.read()
            print(lx,ly,rx,abtn,ybtn,start,stop)
            if ybtn == 1:
                state_data.state = State.MANUAL
                switcher.get(state_data.state)(lx,ly,rx,abtn)
            elif start == 1:
                state_data.state = State.FIND
                switcher.get(state_data.state)(state_data)
            elif stop == 1:
                state_data.state = State.STOPPED
                switcher.get(state_data.state)(state_data)
            
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
