#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np

lHue = 0 #lowest value l # 36 61 89 101 255 255
lSaturation = 0
lValue = 0
hHue = 0
hSaturation = 0
hValue = 0 # highest value h
cap = cv2.VideoCapture(1)


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

cv2.namedWindow("Original")
cv2.createTrackbar("lHue", "Original", lHue, 179, updateValue)
cv2.createTrackbar("lSaturation", "Original", lSaturation, 255, updateValue1)
cv2.createTrackbar("lValue", "Original", lValue, 255, updateValue2)
cv2.createTrackbar("hHue", "Original", hHue, 179, updateValue3)
cv2.createTrackbar("hSaturation", "Original", hSaturation, 255, updateValue4)
cv2.createTrackbar("hValue", "Original", hValue, 255, updateValue5)

blobparams = cv2.SimpleBlobDetector_Params()
blobparams.minDistBetweenBlobs = 50
blobparams.filterByCircularity = False
blobparams.filterByArea = True
blobparams.minArea = 200
blobparams.maxArea = 100000
blobparams.filterByInertia = False
blobparams.filterByConvexity = False
detector = cv2.SimpleBlobDetector_create(blobparams)

def writevalues():
    print("saving values")
    with open("trackbar_defaults.txt", "w") as writer:
        writer.write(str(lHue) + "," + str(lSaturation) + "," + str(lValue) + "," + str(hHue) + "," + str(hSaturation) + "," + str(hValue))

while True:
    ret, frame = cap.read()

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lowerLimits = np.array([lHue, lSaturation, lValue])
    upperLimits = np.array([hHue, hSaturation, hValue])
    
    # Our operations on the frame come here
    thresholded = cv2.inRange(hsv, lowerLimits, upperLimits)
    thresholded = cv2.bitwise_not(thresholded)
    outimage = cv2.bitwise_and(frame, frame, mask = thresholded)
    keypoints = detector.detect(thresholded)

    for kp in keypoints:
        x = int(kp.pt[0])
        y = int(kp.pt[1])
        cv2.putText(frame, str(x)+ "," + str(y), (x,y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

    frame = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imshow("Original", frame)
    cv2.imshow("Processed", outimage)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("writing values")
        writevalues()
        
        break


    
    #TODO: use threshold values defined in the code


cap.release()
writevalues()
cv2.destroyAllWindows()