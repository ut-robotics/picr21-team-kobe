#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import Movement as drive
import Image_processing as ip
import time
import CameraConfig
import math

pipeline, camera_x, camera_y = CameraConfig.init()
state = "Find"
while True:
    print(state)
    keypoints, y, x, basket_center = ip.ProcessFrame(pipeline, camera_x, camera_y)
    #print(y,basket_center)
    # if keypoints >= 1:
    #     state = "Driving"
    #dist = depth_frame.get_distance(x, y)
    speed = math.sqrt((camera_x/2-x)**2 + (camera_y-y)**2)*0.05 #proportional robot speed, maybe try 640 for x? #frame[1]-x, frame[0]-y
    direction = math.atan2(camera_x/2 - x, camera_y - y)


    if state == "Find":
        drive.spinRight([-10,-10,-10,0])
        if keypoints >= 1:
            state = "Driving"
    
    elif state == "Driving":
        
        if keypoints >= 1 and y < 380:
            rotSpd = int((x - 320)/320.0 * -15.0)
            drive.move(speed, direction, rotSpd)
            print("y", y)

        elif y >= 380: # specify better y value that is near robot, represents ball y value in reference with camera y
            #drive.stop()
            state = "basket"
        elif keypoints <= 0:
            state = "Find"

    elif state == "basket":
        print("Here")
        #print("center342", basket_center)
        speed = math.sqrt((camera_x/2-x)**2 + (camera_y-y)**2)*0.1
        if basket_center >= 320:
            drive.stop()
            #state = "Throwing"
        else:
            #rotSpd = int((basket_center - 320)/320.0 * -15.0)

            drive.move(speed, direction, 0)

    elif state == "Throwing":
        for i in range(4):
            #calculate some speed for thrower motor here and send it to serial, figure out some formula, probably polynomial regression for curve fitting
            thrower_speed = 800
            drive.moveForward([0,-10,10,thrower_speed])
            time.sleep(0.3)
        state = "Find"


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
