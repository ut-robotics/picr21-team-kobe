#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np
#from numpy.lib.ufunclike import _dispatcher
import Movement as drive
from math import atan2
import pyrealsense2 as rs
import math
#import Blobparams
#import CameraConfig
#import ReadValues
import Image_processing as ip
import serialcomms 

#ser = serialcomms.Connection()


#speed, direction, dist, keypoints = ip.ProcessFrame()

#pipeline, camera_x, camera_y = CameraConfig.init()
#lHue, lSaturation, lValue, hHue, hSaturation, hValue = ReadValues.ReadThreshold("trackbar_defaults.txt")
#lHue1, lSaturation1, lValue1, hHue1, hSaturation1, hValue1 = ReadValues.ReadThreshold("blue_basket.txt")
#lHue2, lSaturation2, lValue2, hHue2, hSaturation2, hValue2 = ReadValues.ReadThreshold("pink_basket.txt")
#kernel = np.ones((5,5),np.uint8)
#detector = Blobparams.CreateDetector()


state = "Find"
while True:
    print(state)
    speed, direction, dist, keypoints = ip.ProcessFrame()

    if keypoints >= 1:
        state = "Driving"

    if state == "Find":
        drive.spinRight([-10,-10,-10,0])
        if keypoints >= 1:
            state = "Driving"
    
    elif state == "Driving":
        
        if keypoints >= 1:
            drive.move(speed, direction)
        elif keypoints <= 0:
            state = "Find"

    elif state == "Find basket":
        drive.orbit()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()
