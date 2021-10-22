#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import Movement as drive
import Image_processing as ip
import time

state = "Find"
while True:
    print(state)
    speed, direction, dist, keypoints, y, basket_center = ip.ProcessFrame()

    if keypoints >= 1:
        state = "Driving"

    if state == "Find":
        drive.spinRight([-10,-10,-10,0])
        if keypoints >= 1:
            state = "Driving"
    
    elif state == "Driving":
        
        if keypoints >= 1:
            drive.move(speed, direction)

        elif y <= 200: # specify better y value that is near robot, represents ball y value in reference with camera y
            drive.stop()
            state = "Find basket"
        elif keypoints <= 0:
            state = "Find"

    elif state == "Find basket":
        drive.orbit()
        if basket_center < 350 and basket_center > 290:
            drive.stop()
            state = "Throwing"

    elif state == "Throwing":
        for i in range(4):
            #calculate some speed for thrower motor here and send it to serial, figure out some formula, probably polynomial regression for curve fitting
            thrower_speed = 800
            drive.moveForward([0,10,-10,thrower_speed])
            time.sleep(0.3)
        state = "Find"


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
