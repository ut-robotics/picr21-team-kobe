#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np
from numpy.lib.ufunclike import _dispatcher
import test_drive as drive
from math import atan2
import pyrealsense2 as rs

#from realsense_depth import *


pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
pipeline.start(config)


lHue = 0 #lowest value l # 36 61 89 101 255 255
lSaturation = 0
lValue = 0
hHue = 0
hSaturation = 0
hValue = 0 # highest value h


#cap = DepthCamera()

# Thresholds an image and writes values into file to later use again

def updateValue(new_value):
    global lHue
    lHue = new_value

def updateValue1(new_value1):
    global lSaturation
    lSaturation = new_value1
    
def updateValue2(new_value2):
    global lValue
    lValue = new_value2
    
def updateValue3(new_value3):
    global hHue
    hHue = new_value3
    
def updateValue4(new_value4):
    global hSaturation
    hSaturation = new_value4
    
def updateValue5(new_value5):
    global hValue
    hValue = new_value5

def use_default_values():
    pass

try:
    print("here")
    with open("trackbar_defaults.txt", 'r') as reader:
        values = reader.readline().split(",")

        # only read from the file if there are enough items to read
        if len(values) >= 6: 
            lHue = int(values[0])
            lSaturation = int(values[1])
            lValue = int(values[2])
            hHue = int(values[3])
            hSaturation = int(values[4])
            hValue = int(values[5])
        else:
            print("using default values")
            use_default_values()

except IOError:
    pass

cv2.namedWindow("Processed")
cv2.createTrackbar("lHue", "Processed", lHue, 179, updateValue)
cv2.createTrackbar("lSaturation", "Processed", lSaturation, 255, updateValue1)
cv2.createTrackbar("lValue", "Processed", lValue, 255, updateValue2)
cv2.createTrackbar("hHue", "Processed", hHue, 179, updateValue3)
cv2.createTrackbar("hSaturation", "Processed", hSaturation, 255, updateValue4)
cv2.createTrackbar("hValue", "Processed", hValue, 255, updateValue5)

blobparams = cv2.SimpleBlobDetector_Params()
blobparams.minDistBetweenBlobs = 50
blobparams.filterByCircularity = False
blobparams.filterByArea = True
blobparams.minArea = 25
blobparams.maxArea = 100000
blobparams.filterByInertia = False
blobparams.filterByConvexity = False
detector = cv2.SimpleBlobDetector_create(blobparams)

def writevalues():
    print("saving values")
    with open("trackbar_defaults.txt", "w") as writer:
        writer.write(str(lHue) + "," + str(lSaturation) + "," + str(lValue) + "," + str(hHue) + "," + str(hSaturation) + "," + str(hValue))

#cap = cv2.VideoCapture(0)

while True:
    #ret, frame = cap.read()
    #ret,depth, frame = cap.get_frame()

    frames = pipeline.wait_for_frames()
    aligned_frames = rs.align(rs.stream.color).process(frames)
    color_frame = aligned_frames.get_color_frame()
    frame = np.asanyarray(color_frame.get_data())
    depth_frame = aligned_frames.get_depth_frame()
    depth = np.asanyarray(depth_frame.get_data())

    #colorizer = rs.colorizer()
    #colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())
    #cv2.circle(colorized_depth, point, 10, (0, 0, 255))

    #print(dist)


    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lHue = cv2.getTrackbarPos("lHue", "Processed")
    lSaturation = cv2.getTrackbarPos("lSaturation", "Processed")
    lValue = cv2.getTrackbarPos("lValue", "Processed")
    hHue = cv2.getTrackbarPos("hHue", "Processed")
    hSaturation = cv2.getTrackbarPos("hSaturation", "Processed")
    hValue = cv2.getTrackbarPos("hValue", "Processed")

    lowerLimits = np.array([lHue, lSaturation, lValue])
    upperLimits = np.array([hHue, hSaturation, hValue])
    
    # Our operations on the frame come here
    thresholded = cv2.inRange(hsv, lowerLimits, upperLimits)
    thresholded = cv2.bitwise_not(thresholded)
    cv2.imshow('Thresholded', thresholded)

    outimage = cv2.bitwise_and(frame, frame, mask=thresholded)
    keypoints = detector.detect(thresholded)

    if len(keypoints) >= 1:
        for kp in keypoints:
            x = int(kp.pt[0])
            y = int(kp.pt[1])
            #depth = cap.get_frame(depth)
            #dist = depth.get_distance(x, y)
            dist = depth_frame.get_distance(x, y)
            print("size ", kp.size)

            print("dist", dist)

            #cv2.putText(outimage, str(x) + "," + str(y), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
            direction = atan2(340 - kp.pt[0], 480 - kp.pt[1])
            # Check if the detected blob is left or right from the center of the camera's screen
            # drive.move([50,50,50], direction) #Experimental #TODO: Define angle
            #print("x", x, "y" ,y)
            #print(x)
            if dist < 0.1:
                drive.stop()
            elif x <  350 and x > 270:
                drive.move([10,10,10,0], direction)
            elif x > 350 and x < 400:
                drive.spinRight([-5,-5,-5,0])
            elif x < 270 and x > 200:
                drive.spinLeft([5,5,5,0])

            # if x < 320 - 20 or x > 320 + 20:
            #     drive.moveForward([0,5,5,0]) # add speed value with func
            # elif x < 320: #TODO: replace x value with camera resolution x-axis/2
            #     drive.spinLeft([5,5,5,0]) # add speed value with func  
            # elif x > 320:   #TODO: replace x value with camera resolution x-axis/2
            #     # TODO2: also check if ball is further than 10cm if not stop
            #     drive.spinRight([-5,-5,-5,0]) # add speed value with func
    else:
        pass#drive.spinRight([-5,-5,-5,0])


    outimage = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("Original", frame)
    cv2.imshow("Processed", outimage)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("writing values")
        writevalues()
        
        break

cap.release()
writevalues()
cv2.destroyAllWindows()
