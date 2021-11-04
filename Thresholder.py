#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import Blobparams
import pyrealsense2 as rs
import CameraConfig
import ReadValues
import time
import Image_processing as ip

pipeline, camera_x, camera_y = CameraConfig.init()

lHue = 0 #lowest value l # 36 61 89 101 255 255
lSaturation = 0
lValue = 0
hHue = 0
hSaturation = 0
hValue = 0 # highest value h
kernel = (5,5)
prev_time_frame = 0.0
cur_time_frame = 0.0


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
lHue, lSaturation, lValue, hHue, hSaturation, hValue = ReadValues.ReadThreshold("blue_basket.txt")
lHue1, lSaturation1, lValue1, hHue1, hSaturation1, hValue1 = ReadValues.ReadThreshold("trackbar_defaults.txt")


cv2.namedWindow("Processed")
cv2.createTrackbar("lHue", "Processed", lHue1, 179, updateValue)
cv2.createTrackbar("lSaturation", "Processed", lSaturation1, 255, updateValue1)
cv2.createTrackbar("lValue", "Processed", lValue1, 255, updateValue2)
cv2.createTrackbar("hHue", "Processed", hHue1, 179, updateValue3)
cv2.createTrackbar("hSaturation", "Processed", hSaturation1, 255, updateValue4)
cv2.createTrackbar("hValue", "Processed", hValue1, 255, updateValue5)



#Creates the blobdetector with parameters
detector = Blobparams.CreateDetector()

def writevalues(filename):
    print("saving values")
    with open(filename, "w") as writer:
        writer.write(str(lHue) + "," + str(lSaturation) + "," + str(lValue) + "," + str(hHue) + "," + str(hSaturation) + "," + str(hValue))
        print("values saved successfully.")

while True:
    keypoints, y, x, basket_x_center, basket_y_center, distance = ip.ProcessFrame(pipeline, camera_x, camera_y)
    cur_time_frame = time.time()
    fps = 1/ (cur_time_frame - prev_time_frame)
    prev_time_frame = cur_time_frame
    fps = str(int(fps))
    print(fps)

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


    lowerLimits1 = np.array([lHue1, lSaturation1, lValue1])
    upperLimits1 = np.array([hHue1, hSaturation1, hValue1])
    


    # Our operations on the frame come here
    thresholded = cv2.inRange(hsv, lowerLimits, upperLimits)
    thresholded1 = cv2.inRange(hsv, lowerLimits1, upperLimits1)
    thresholded = cv2.erode(thresholded,kernel, iterations=2)
    

    contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = max(contours, key= cv2.contourArea)

    cv2.imshow('Thresholded1', thresholded)
    thresholded = cv2.bitwise_not(thresholded)

    thresholded1 = cv2.bitwise_not(thresholded1)
    #cv2.imshow('Thresholded', thresholded1)


    outimage = cv2.bitwise_and(frame, frame, mask=thresholded)

    #print(contours)
    if len(contours) > 0:
        cv2.drawContours(frame, [contours], -1, (0,255,255), 3)
        #print(cv2.contourArea(contours))
        M = cv2.moments(contours)
        basket_center = int(M["m10"] / M["m00"])
        print(basket_center)
                

    keypoints = detector.detect(thresholded1)

    if len(keypoints) >= 1:
        for kp in keypoints:
            x = int(kp.pt[0])
            y = int(kp.pt[1])
            cv2.putText(outimage, str(x) + "," + str(y), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

    outimage = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    #thresholded1 = cv2.erode(thresholded1,kernel, iterations=1)
    print("y", y, "x", x)
    #cv2.imshow("Original", frame)
    cv2.imshow("Processed", outimage)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('s'):
        writevalues("blue_basket.txt")
        break
    elif key == ord('d'):
        writevalues("pink_basket.txt")
        break
    elif key == ord('x'):
        writevalues("trackbar_defaults.txt")
        break
        

#writevalues()
cv2.destroyAllWindows()