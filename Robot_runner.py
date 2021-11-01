#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import Movement as drive
import Image_processing as ip
import time
import CameraConfig
import math
import numpy

pipeline, camera_x, camera_y = CameraConfig.init()
state = "Find basket"
while True:
    print(state)
    keypoints, y, x, basket_x_center, basket_y_center = ip.ProcessFrame(pipeline, camera_x, camera_y)
    #print(y,basket_center)
    # if keypoints >= 1:
    #     state = "Driving"dd
    #dist = depth_frame.get_distance(x, y)
    speed = math.sqrt((camera_x/2-x)**2 + (camera_y-y)**2)*0.05 #proportional robot speed, maybe try 640 for x? #frame[1]-x, frame[0]-y
    direction = math.atan2(camera_x/2 - x, camera_y - y)
    side_speed = (x - basket_x_center)/320.0 * 5.0


    if state == "Find":
        drive.spinRight([-10,-10,-10,0])
        if keypoints >= 1:
            state = "Driving"
    
    elif state == "Driving":
        
        if keypoints >= 1:
            rotSpd = int((x - 320)/320.0 * -15.0)
            drive.move(speed, direction, rotSpd, 0)
            print("kp", keypoints)

        if y >= 400: # specify better y value that is near robot, represents ball y value in reference with camera y
            #drive.stop()
            state = "Find basket"
        if keypoints <= 0:
            state = "Find"
    
    elif state == "Find basket":
        print("y", y, "x", x, "basket", basket_x_center)
        
        #print("center342", basket_center)
        speed = math.sqrt((camera_x/2-x)**2 + (camera_y-y)**2)*0.05
        front_speed = (400-y/ 480.0) * 5
        side_speed = (x - basket_x_center)/320.0 * 5
        
        if 300 <= basket_x_center <= 320:
            
            drive.stop()
            state = "Throwing"
        if  basket_x_center <= 320:
            print("rotate left")
            rotSpd = int((basket_x_center - 320)/320.0 * 10.0)
            print('speed', rotSpd)
            #drive.orbit([15, -1,-1, 0])
            #drive.move(front_speed, direction, 0, 0)
            drive.move2(side_speed, front_speed, rotSpd)
        if  basket_x_center >= 320:
            print("rotate right")
            rotSpd = int((basket_x_center - 320)/320.0 * -10.0)
            print('speed', rotSpd)
            #drive.move(-front_speed, direction, 0, 0)
            drive.move2(-side_speed, front_speed, rotSpd)
            #drive.orbit([-10,1,1,0])

    elif state == "Throwing":
        for i in range(6):
            #calculate some speed for thrower motor here and send it to serial, figure out some formula, probably polynomial regression for curve fitting
            thrower_speed = 800
            drive.moveForward([0,-10,10,thrower_speed])
            time.sleep(0.3)
        state = "Find basket"


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
