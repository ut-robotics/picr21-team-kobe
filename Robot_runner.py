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
import Color

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
        self.prev_xspeed = 0
        self.prev_yspeed = 0
        self.prev_rotspeed = 0
        self.out_of_field = False
        #self.has_rotated = True
        self.after_rotation_counter = 0


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
Processor = ip.ProcessFrames(Camera, target)

def calc_speed(delta, maxDelta, minDelta, minSpeed, maxDeltaSpeed, maxSpeed):
    if abs(delta) < minDelta:
        return 0
    deltaDiv = delta/maxDelta
    sign = math.copysign(1, deltaDiv)
    normalizedDelta = math.pow(abs(deltaDiv), 2) * sign
    speed = normalizedDelta * maxDeltaSpeed
    return int(int(speed) if abs(speed) >= minSpeed and abs(speed) <= maxSpeed else maxSpeed * sign if speed > maxSpeed else minSpeed * sign)

def handle_manual(state_data, gamepad):
    # if gamepad.a == 1:
    #         state_data.state = State.FIND
    #         return
    if gamepad.right_trigger > 0:
        drive.move_omni(int(gamepad.x*30),-int(gamepad.y*30),int(gamepad.rx*20), int(abs(gamepad.right_trigger*2000)))
    else:
        drive.move_omni(int(gamepad.x*30),-int(gamepad.y*30),int(gamepad.rx*20), 0)
        

def handle_drive(state_data, gamepad):

    max_acceleration = 4
    if state_data.out_of_field:
        drive.move_omni(0, 0, 20, 0)
        time.sleep(0.3)
        state_data.out_of_field = False
        state_data.state = State.FIND
        return
    # meters
    if state_data.basket_distance is not None:
        if state_data.basket_distance < 0.5:
            drive.move_omni(0, 0, 20, 0)
            time.sleep(0.3)
            state_data.state = State.FIND
            return

    if not state_data.floor_area or state_data.floor_area < 20000:
        
        drive.move_omni(0, -10,20,0)
        time.sleep(0.3)
        state_data.state = State.FIND
        return
    
    if state_data.keypoint_count > 0 and state_data.floor_area > 20000:
        #print(floorarea)
        delta_x = state_data.ball_x - Camera.camera_x/2
        delta_y = (Camera.camera_y - 110) - state_data.ball_y
        minSpeed = 2
        maxSpeed = 50
        minDelta = 5
        front_speed = calc_speed(delta_y, Camera.camera_y, minDelta, 5, 500, 60)
        rot_spd = calc_speed(delta_x, Camera.camera_x, minDelta, minSpeed, 150, 40)

        front_delta = front_speed - state_data.prev_yspeed
        if abs(front_delta) > max_acceleration and front_delta > 0:
            
            sign = math.copysign(1, front_delta)
            front_speed = int(state_data.prev_yspeed + max_acceleration * sign)


        state_data.prev_xspeed = 0
        state_data.prev_yspeed = front_speed
        state_data.prev_rotspeed = -rot_spd

        drive.move_omni(-0, front_speed, -rot_spd, 0)
        
        if Camera.camera_y + 20 > state_data.ball_y > Camera.camera_y - 160 : # How close ball y should be to switch to next state
            state_data.state = State.AIM
            return
        
    if state_data.keypoint_count <= 0 or None:
        state_data.state = State.FIND
        return
    
    state_data.state = State.DRIVE

def handle_find(state_data, gamepad):

    drive.move_omni(0, 0, 7, 0)
    if state_data.keypoint_count >= 1:
        handle_drive(state_data, gamepad)
        state_data.state = State.DRIVE
        return
        
    state_data.state = State.FIND

def handle_stopped(state_data,gamepad):
    drive.stop()
    state_data.state = State.STOPPED

def handle_aim(state_data, gamepad):
    
    if state_data.floor_area is None or state_data.floor_area < 20000:
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
    delta_y = (Camera.camera_y - 30) - state_data.ball_y
    front_speed = calc_speed(delta_y, Camera.camera_y, 5, 3, 500, 40)
    side_speed = calc_speed(delta_x, Camera.camera_x, 5, 6, 200, 30)
    rot_spd = calc_speed(rot_delta_x, Camera.camera_x, 5, 3, 200, 50)
    state_data.prev_yspeed = front_speed
    state_data.prev_rotspeed = rot_spd
    state_data.prev_xspeed = side_speed

    drive.move_omni(-side_speed, front_speed, -rot_spd, 0)
    

    
    if basketInFrame and (Camera.camera_x/2)- 5 <= state_data.basket_x <= (Camera.camera_x/2) + 5 and state_data.ball_y >= 410: # Start throwing if ball y is close to robot and basket is centered to camera x
        drive.stop()                             #prev center 315 to 325
        state_data.state = State.THROWING
        return
    state_data.state = State.AIM

def handle_throwing(state_data, gamepad):
    
    minSpeed = 15
    maxSpeed = 30
    minDelta = 5
    
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
        delta_y = Camera.camera_y + 20 - state_data.ball_y
        thrower_speed = Thrower.thrower_speed(state_data.basket_distance)
        front_speed = calc_speed(delta_y, Camera.camera_y, minDelta, minSpeed, 200, maxSpeed)
        side_speed = calc_speed(delta_x, Camera.camera_x, minDelta, 2, 150, maxSpeed)
        rot_spd = calc_speed(rot_delta_x, Camera.camera_x, minDelta, 2, 100, maxSpeed)
        state_data.prev_yspeed = front_speed
        state_data.prev_rotspeed = rot_spd
        state_data.prev_xspeed = side_speed
        drive.move_omni(-side_speed, front_speed, -rot_spd, thrower_speed)
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
        #front_speed = calc_speed(delta_y, Camera.camera_y, minDelta, 0, 100, 8)
        side_speed = calc_speed(delta_x, Camera.camera_x, 0, 0, 75, 20)

        rot_spd = calc_speed(delta_x, Camera.camera_x, 0, 0, 50, 20)


        state_data.prev_yspeed = 0
        state_data.prev_rotspeed = rot_spd
        state_data.prev_xspeed = side_speed
        
        thrower_speed = Thrower.thrower_speed(state_data.basket_distance)
        drive.move_omni(-side_speed, 8, rot_spd, thrower_speed)

        state_data.state = State.THROWING
        if state_data.debug and state_data.after_throw_counter > 59:
            state_data.state = State.DEBUG
        return

    elif state_data.keypoint_count == 0 and not state_data.has_thrown:    
        state_data.state = State.FIND
    
def handle_debug(state_data, gamepad):
    drive.stop()
    print("distance from basket: ", state_data.basket_distance)
    state_data.thrower_speed = int(input("Enter thrower speed to use:"))
    state_data.state = State.FIND
    
    
data = None

def listen_for_referee_commands(state_data, Processor):
    try:
        run, target = cl.get_current_referee_command()
        #print("Target:  " + str(target))
        #print("Run: " + str(run))
        if target:
            target = True
        else:
            target = False
        Processor.set_target(target)
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
    State.FIND: handle_find,
    State.DRIVE: handle_drive,
    State.AIM: handle_aim,
    State.THROWING: handle_throwing,
    State.STOPPED: handle_stopped,
    State.MANUAL: handle_manual,
    State.DEBUG: handle_debug
}

def logic(switcher):
    start_time = time.time()
    counter = 0
    joy = Xbox360.XboxController()
    debug = False
    state_data = RobotStateData()
    try:
        while True:
            # Main code
            listen_for_referee_commands(state_data, Processor)
            #Align depth frame if we are in throw state
            count, y, x, center_x, center_y, basket_distance, floorarea, out_of_field = Processor.process_frame(align_frame = state_data.state == State.THROWING)
            state_data.ball_x = x 
            state_data.ball_y = y
            state_data.keypoint_count = count
            state_data.basket_x = center_x
            state_data.debug = debug
            state_data.floor_area = floorarea
            state_data.basket_distance = basket_distance
            state_data.out_of_field = out_of_field            
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
            #print(state_data.basket_distance)
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
    except Exception as e:
        print(e)
        raise
    finally:
        Camera.stop_streams()

logic(switcher)
