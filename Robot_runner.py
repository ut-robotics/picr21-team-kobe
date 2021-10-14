#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np
#from numpy.lib.ufunclike import _dispatcher
import Movement as drive
from math import atan2
import pyrealsense2 as rs
import math
import Blobparams
import CameraConfig
import ReadValues

pipeline, camera_x, camera_y = CameraConfig.init()
lHue, lSaturation, lValue, hHue, hSaturation, hValue = ReadValues.ReadThreshold()
kernel = np.ones((5,5),np.uint8)
detector = Blobparams.CreateDetector()


state = "Find"
while True:

    frames = pipeline.wait_for_frames()
    aligned_frames = rs.align(rs.stream.color).process(frames)
    color_frame = aligned_frames.get_color_frame()
    frame = np.asanyarray(color_frame.get_data())
    depth_frame = aligned_frames.get_depth_frame()
    depth = np.asanyarray(depth_frame.get_data())

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lowerLimits = np.array([lHue, lSaturation, lValue])
    upperLimits = np.array([hHue, hSaturation, hValue])
    
    # Our operations on the frame come here
    thresholded = cv2.inRange(hsv, lowerLimits, upperLimits)
    thresholded = cv2.bitwise_not(thresholded)

    #Morphological operations
    thresholded = cv2.erode(thresholded,kernel, iterations=1)
    cv2.imshow('Thresholded', thresholded)

    outimage = cv2.bitwise_and(frame, frame, mask=thresholded)
    keypoints = detector.detect(thresholded)

    # if len(keypoints) >= 1:
    #     for kp in keypoints:
    #         x = int(kp.pt[0])
    #         y = int(kp.pt[1])
    #         dist = depth_frame.get_distance(x, y)
    #         #proportional robot speed
    #         speed = math.sqrt((320-x)**2 + (480-y)**2)*0.2
    #         direction = atan2(320 - x, 480 - y)
            #cv2.putText(outimage, str(x) + "," + str(y), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

            # if dist < 0.4:
            #     drive.stop()
            # drive.move(speed, direction)x
    if state == "Find":
        drive.spinRight([-10,-10,-10,0])
        if len(keypoints) >= 1:
            state = "Driving"
    
    elif state == "Driving":
        
        print("y", camera_y)
        if len(keypoints) >= 1:
            for kp in keypoints:
                x = int(kp.pt[0])
                y = int(kp.pt[1])
                dist = depth_frame.get_distance(x, y)
                speed = math.sqrt((camera_x/2-x)**2 + (camera_y-y)**2)*0.1 #proportional robot speed, maybe try 640 for x? #frame[1]-x, frame[0]-y
                direction = atan2(camera_x/2 - x, camera_y - y)
                print("speed", int(speed)) #frame[1]-x, frame[0]-y
                drive.move(speed, direction)
        elif len(keypoints) <= 0:
            state = "Find"


    outimage = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    #cv2.imshow("Original", frame)
    cv2.imshow("Processed", outimage)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
