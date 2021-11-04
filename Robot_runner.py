#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from _typeshed import ReadOnlyBuffer
import cv2
import Movement as drive
import Image_processing as ip
import time
import CameraConfig
import math
import numpy

pipeline, camera_x, camera_y = CameraConfig.init()
state = "Find"
i=0
while True:
    print(state)
    keypoints, y, x, basket_x_center, basket_y_center, distance = ip.ProcessFrame(pipeline, camera_x, camera_y)
    speed = math.sqrt((camera_x/2-x)**2 + (camera_y-y)**2)*0.05
    direction = math.atan2(camera_x/2 - x, camera_y - y)
    side_speed = (x - basket_x_center)/320.0 * 5.0
    #front_speed = (400-y/ 480.0) * 2



    if state == "Find":
        drive.spinRight([-10,-10,-10,0])
        if keypoints >= 1:
            state = "Driving"
    
    elif state == "Driving":
        
        if keypoints >= 1:
            rotSpd = int((x - 320)/320.0 * -15.0)
            drive.move(speed, direction, rotSpd)
            print("kp", keypoints)

        if y >= 400: # specify better y value that is near robot, represents ball y value in reference with camera y
            #drive.stop()
            state = "Find basket"
        if keypoints <= 0:
            state = "Find"
    
    elif state == "Find basket":
        print("y", y, "x", x, "basket", basket_x_center)
        front_speed = (400-y)/ 480.0 * 20
        side_speed = (x - basket_x_center)/320.0 * 20
        
        if 300 <= basket_x_center <= 320:
            
            drive.stop()
            state = "Throwing"
        rotSpd = int((x - 320)/320.0 * 25)
        drive.move2(-side_speed  , front_speed, -rotSpd, 0)

    elif state == "Throwing":
            #calculate some speed for thrower motor here and send it to serial, figure out some formula, probably polynomial regression for curve fitting

        print("i", i)
        if keypoints <= 0:
            i += 1
        if i >= 30:
            i = 0
            state = "Find"
        thrower_speed = 800
            #drive.moveForward([0,-10,10,thrower_speed])
        drive.move2(side_speed, 10, -rotSpd, thrower_speed)

        #state = "Find"


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
