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

#Camera = CameraConfig.Config()

lHue = 0 #lowest value l # 36 61 89 101 255 255
lSaturation = 0
lValue = 0
hHue = 0
hSaturation = 0
hValue = 0 # highest value h
kernel = (5,5)
prev_time_frame = 0.0
cur_time_frame = 0.0

Processor = ip.ProcessFrames(True)
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
    

Processor = ip.ProcessFrames(True)

cv2.namedWindow("Processed")
cv2.createTrackbar("lHue", "Processed", Processor.lHue1, 179, updateValue)
cv2.createTrackbar("lSaturation", "Processed", Processor.lSaturation1, 255, updateValue1)
cv2.createTrackbar("lValue", "Processed", Processor.lValue1, 255, updateValue2)
cv2.createTrackbar("hHue", "Processed", Processor.hHue1, 179, updateValue3)
cv2.createTrackbar("hSaturation", "Processed", Processor.hSaturation1, 255, updateValue4)
cv2.createTrackbar("hValue", "Processed", Processor.hValue1, 255, updateValue5)



#Creates the blobdetector with parameters
detector = Blobparams.CreateDetector()

def writevalues(filename):
    print("saving values")
    with open(filename, "w") as writer:
        writer.write(str(Processor.lHue1) + "," + str(Processor.lSaturation1) + "," + str(Processor.lValue1) + "," + str(Processor.hHue1) + "," + str(Processor.hSaturation1) + "," + str(Processor.hValue1))
        print("values saved successfully.")

while True:
    cur_time_frame = time.time()
    fps = 1/ (cur_time_frame - prev_time_frame)
    prev_time_frame = cur_time_frame
    fps = int(fps)
    #print(fps)
    
    Processor.lHue = cv2.getTrackbarPos("lHue", "Processed")
    Processor.lSaturation1 = cv2.getTrackbarPos("lSaturation", "Processed")
    Processor.lValue1 = cv2.getTrackbarPos("lValue", "Processed")
    Processor.hHue1 = cv2.getTrackbarPos("hHue", "Processed")
    Processor.hSaturation1 = cv2.getTrackbarPos("hSaturation", "Processed")
    Processor.hValue1 = cv2.getTrackbarPos("hValue", "Processed")

    Processor.Threshold(Camera.pipeline)

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
    elif key == ord('f'):
        writevalues("floor.txt")
        break


Camera.StopStreams()

cv2.destroyAllWindows()