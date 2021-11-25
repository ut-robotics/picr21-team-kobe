#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import Movement as drive
import Image_processing as ip
import CameraConfig
import math
from enum import Enum
import Thrower
import Referee_client as Client
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
        self.debug = False
        self.thrower_speed = 0


cl = Client.Client()
cl.start()

Camera = CameraConfig.Config()

#States for logic
class State(Enum):
    FIND = 0
    DRIVE = 1
    AIM = 2
    THROWING = 3
    STOPPED = 4
    MANUAL = 5
    DEBUG = 6

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

def HandleManual(state_data, gamepad):
    # if gamepad.a == 1:
    #         state_data.state = State.FIND
    #         return
    if gamepad.right_trigger > 0:
        drive.Move2(int(gamepad.x*30),-int(gamepad.y*30),int(gamepad.rx*20), int(abs(gamepad.right_trigger*2000)))
    else:
        drive.Move2(int(gamepad.x*30),-int(gamepad.y*30),int(gamepad.rx*20), 0)
        

def HandleDrive(state_data, gamepad):

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
        front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, 5, 500, 60)
        rotSpd = CalcSpeed(delta_x, Camera.camera_x, minDelta, minSpeed, 300, 50)
        drive.Move2(-0, front_speed, -rotSpd, 0)
        
        if 500 > state_data.ball_y > 315 : # How close ball y should be to switch to next state
            state_data.state = State.AIM
            return
        
    if state_data.keypoint_count <= 0 or None:
        state_data.state = State.FIND
        return
    
    state_data.state = State.DRIVE

def HandleFind(state_data, gamepad):
    drive.Move2(0, 0, 10, 0)
    if state_data.keypoint_count >= 1:
        HandleDrive(state_data, gamepad)
        state_data.state = State.DRIVE
        return
    state_data.state = State.FIND

def HandleStopped(state_data,gamepad):
    drive.Stop()
    state_data.state = State.STOPPED

def HandleAim(state_data, gamepad):
    
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
    front_speed = CalcSpeed(delta_y, Camera.camera_y, 7, 3, 500, 40)
    side_speed = CalcSpeed(delta_x, Camera.camera_x, 7, 6, 200, 30)
    rotSpd = CalcSpeed(rot_delta_x, Camera.camera_x, 7, 3, 200, 50)
    drive.Move2(-side_speed, front_speed, -rotSpd, 0)
    

    
    if basketInFrame and 320 <= state_data.basket_x <= 330 and state_data.ball_y >= 410: # Start throwing if ball y is close to robot and basket is centered to camera x
        drive.Stop()                             #prev center 315 to 325
        state_data.state = State.THROWING
        return
    state_data.state = State.AIM

def HandleThrowing(state_data, gamepad):
    
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
    
    if state_data.keypoint_count >= 1 and not state_data.has_thrown:
    
        basketInFrame = state_data.basket_x is not None

        if not basketInFrame:
            delta_x = Camera.camera_x
        else:
            delta_x = state_data.ball_x - state_data.basket_x
        rot_delta_x = state_data.ball_x - Camera.camera_x/2 #if no ball and throw true basket_x - camera_x
        delta_y = 500 - state_data.ball_y
        thrower_speed = Thrower.ThrowerSpeed(state_data.basket_distance)
        front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, minSpeed, 200, maxSpeed)
        side_speed = CalcSpeed(delta_x, Camera.camera_x, minDelta, 2, 150, maxSpeed)
        rotSpd = CalcSpeed(rot_delta_x, Camera.camera_x, minDelta, 2, 100, maxSpeed)
        drive.Move2(-side_speed, front_speed, -rotSpd, thrower_speed)
        state_data.has_thrown = True
        state_data.state = State.THROWING
        return
    
    elif state_data.has_thrown: 
        basketInFrame = state_data.basket_x is not None
        delta_x = 0

        if basketInFrame:
            delta_x = state_data.basket_x - Camera.camera_x/2
    
            #delta_x = state_data.ball_x - state_data.basket_x
        delta_y = 0#500 - Camera.camera_y
        thrower_speed = Thrower.ThrowerSpeed(state_data.basket_distance)
        #front_speed = CalcSpeed(delta_y, Camera.camera_y, minDelta, 0, 100, 8)
        side_speed = CalcSpeed(delta_x, Camera.camera_x, 0, 0, 75, 20)

        rotSpd = CalcSpeed(delta_x, Camera.camera_x, 0, 0, 50, 20)
        
        print("using speed: ", thrower_speed, "at", state_data.basket_distance)
        #drive.Move2(-0, 8, rotSpd, state_data.thrower_speed)
        drive.Move2(-side_speed, 8, rotSpd, thrower_speed)

        state_data.state = State.THROWING
        if state_data.debug and state_data.after_throw_counter > 59:
            state_data.state = State.DEBUG
        return

    elif state_data.keypoint_count == 0 and not state_data.has_thrown:    
        state_data.state = State.FIND
    #state_data.has_thrown = False
    
def HandleDebug(state_data, gamepad):
    drive.Stop()
    print("distance from basket: ", state_data.basket_distance)
    state_data.thrower_speed = int(input("Enter thrower speed to use:"))
    state_data.state = State.FIND
    
    
data = None

def ListenForRefereeCommands(state_data, Processor):
    try:
        run, target = cl.get_current_referee_command()
        #print("Target:  " + str(target))
        #print("Run: " + str(run))
        
        Processor.SetTarget(target)
        if not run:
            state_data.state = State.STOPPED
            return
        if run and state_data.state == State.STOPPED and not state_data.debug:
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
    State.MANUAL: HandleManual,
    State.DEBUG: HandleDebug
}

def Logic(switcher):
    start_time = time.time()
    counter = 0
    joy = Xbox360.XboxController()
    debug = False
    state_data = RobotStateData()
    try:
        while True:
            # Main code
            #ListenForRefereeCommands(state_data, Processor)
            #Align depth frame if we are in throw state
            count, y, x, center_x, center_y, basket_distance, floorarea = Processor.ProcessFrame(align_frame = state_data.state == State.THROWING)
            state_data.ball_x = x 
            state_data.ball_y = y
            state_data.keypoint_count = count
            state_data.basket_x = center_x
            state_data.debug = debug
            state_data.floor_area = floorarea
            state_data.basket_distance = basket_distance            
            controller = joy.read()

            if controller.ybtn == 1:
                state_data.state = State.MANUAL
                #switcher.get(state_data.state)(state_data, controller)
            if controller.start == 1:
                state_data.state = State.FIND
                
            if controller.stop == 1:
                state_data.state = State.STOPPED

            key = cv2.waitKey(1) & 0xFF
            if key == ord('r'):
                state_data.state = State.FIND
            print(state_data.state)
            switcher.get(state_data.state)(state_data, controller)
            
            if key == ord('q'):
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
