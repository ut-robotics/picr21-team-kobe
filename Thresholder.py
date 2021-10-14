#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import Blobparams
import pyrealsense2 as rs
import CameraConfig
import ReadValues

pipeline, camera_x, camera_y = CameraConfig.init()

lHue = 0 #lowest value l # 36 61 89 101 255 255
lSaturation = 0
lValue = 0
hHue = 0
hSaturation = 0
hValue = 0 # highest value h


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

# try:
#     with open("trackbar_defaults.txt", 'r') as reader:
#         values = reader.readline().split(",")

#         # only read from the file if there are enough items to read
#         if len(values) >= 6: 
#             lHue = int(values[0])
#             lSaturation = int(values[1])
#             lValue = int(values[2])
#             hHue = int(values[3])
#             hSaturation = int(values[4])
#             hValue = int(values[5])
# except Exception as e:
#     print(e)
lHue, lSaturation, lValue, hHue, hSaturation, hValue = ReadValues.ReadThreshold()


cv2.namedWindow("Processed")
cv2.createTrackbar("lHue", "Processed", lHue, 179, updateValue)
cv2.createTrackbar("lSaturation", "Processed", lSaturation, 255, updateValue1)
cv2.createTrackbar("lValue", "Processed", lValue, 255, updateValue2)
cv2.createTrackbar("hHue", "Processed", hHue, 179, updateValue3)
cv2.createTrackbar("hSaturation", "Processed", hSaturation, 255, updateValue4)
cv2.createTrackbar("hValue", "Processed", hValue, 255, updateValue5)

#Creates the blobdetector with parameters
detector = Blobparams.CreateDetector()

def writevalues():
    print("saving values")
    with open("trackbar_defaults.txt", "w") as writer:
        writer.write(str(lHue) + "," + str(lSaturation) + "," + str(lValue) + "," + str(hHue) + "," + str(hSaturation) + "," + str(hValue))
        print("values saved successfully.")

while True:

    frames = pipeline.wait_for_frames()
    aligned_frames = rs.align(rs.stream.color).process(frames)
    color_frame = aligned_frames.get_color_frame()
    frame = np.asanyarray(color_frame.get_data())

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
            cv2.putText(outimage, str(x) + "," + str(y), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

    outimage = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("Original", frame)
    cv2.imshow("Processed", outimage)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        writevalues()
        break

writevalues()
cv2.destroyAllWindows()