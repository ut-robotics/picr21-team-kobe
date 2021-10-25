#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np
from math import atan2
import pyrealsense2 as rs
import math
import Blobparams
import CameraConfig
import ReadValues

#pipeline, camera_x, camera_y = CameraConfig.init()
lHue, lSaturation, lValue, hHue, hSaturation, hValue = ReadValues.ReadThreshold("trackbar_defaults.txt")
lHue1, lSaturation1, lValue1, hHue1, hSaturation1, hValue1 = ReadValues.ReadThreshold("blue_basket.txt")
#lHue2, lSaturation2, lValue2, hHue2, hSaturation2, hValue2 = ReadValues.ReadThreshold("pink_basket.txt")
kernel = np.ones((5,5),np.uint8)
detector = Blobparams.CreateDetector()


def ProcessFrame(pipeline, camera_x, camera_y):
    speed = 0
    direction = 0
    dist = 0
    keypointnr = 0
    y = 0
    x = 0
    basket_center = 0

    frames = pipeline.wait_for_frames()
    aligned_frames = rs.align(rs.stream.color).process(frames)
    color_frame = aligned_frames.get_color_frame()
    frame = np.asanyarray(color_frame.get_data())
    depth_frame = aligned_frames.get_depth_frame()
    depth = np.asanyarray(depth_frame.get_data())

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lowerLimits = np.array([lHue, lSaturation, lValue])
    upperLimits = np.array([hHue, hSaturation, hValue])


    lowerLimits1 = np.array([lHue1, lSaturation1, lValue1])
    upperLimits1 = np.array([hHue1, hSaturation1, hValue1])
    
    # Our operations on the frame come here
    thresholded = cv2.inRange(hsv, lowerLimits, upperLimits)
    thresholded = cv2.bitwise_not(thresholded)

    thresholded1 = cv2.inRange(hsv, lowerLimits1, upperLimits1)
    print(lowerLimits1, upperLimits1)
    

    contours, hierarchy = cv2.findContours(thresholded1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    



    #thresholded1 = cv2.bitwise_not(thresholded1)

    if len(contours) > 0:
        print(contours)
        contours = max(contours, key= cv2.contourArea)
        cv2.drawContours(frame, [contours], -1, (0,255,255), 3)

        M = cv2.moments(contours)
        print(M)
        if M["m00"] > 0:
            basket_center = int(M["m10"] / M["m00"])
        print("center", basket_center)
        


    #Morphological operations
    thresholded = cv2.erode(thresholded,kernel, iterations=1)
    cv2.imshow('Thresholded', frame)

    #outimage = cv2.bitwise_and(frame, frame, mask=thresholded)
    keypoints = detector.detect(thresholded)
    keypoints = sorted(keypoints, key=lambda kp:kp.size, reverse=True)
    keypointnr = len(keypoints)
    if len(keypoints) >= 1:
        for kp in keypoints:
            x = int(kp.pt[0])
            y = int(kp.pt[1])
            dist = depth_frame.get_distance(x, y)
            speed = math.sqrt((camera_x/2-x)**2 + (camera_y-y)**2)*0.05 #proportional robot speed, maybe try 640 for x? #frame[1]-x, frame[0]-y
            direction = atan2(camera_x/2 - x, camera_y - y)
            #return speed, direction, dist, len(keypoints), y, basket_center
    return keypointnr, y, x, basket_center
