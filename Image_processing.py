#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ctypes.wintypes import tagRECT
import cv2
import numpy as np
from math import atan2
import pyrealsense2 as rs
import math
import Blobparams
import CameraConfig
import ReadValues


class ProcessFrames():
    def __init__(self, target):

        self.target = target
        self.lHue, self.lSaturation, self.lValue, self.hHue, self.hSaturation, self.hValue = ReadValues.ReadThreshold("trackbar_defaults.txt")
        #from referee check what the target command is
        if self.target:
            self.lHue1, self.lSaturation1, self.lValue1, self.hHue1, self.hSaturation1, self.hValue1 = ReadValues.ReadThreshold("blue_basket.txt")
        else:
            self.lHue2, self.lSaturation2, self.lValue2, self.hHue2, self.hSaturation2, self.hValue2 = ReadValues.ReadThreshold("pink_basket.txt")

        self.kernel = np.ones((5,5),np.uint8)
        self.detector = Blobparams.CreateDetector()
        #self.basket_x_center = 0
        #self.basket_y_center = 0

    def ProcessFrame(self, pipeline, camera_x, camera_y):
        basket_x_center = 0
        basket_y_center = 0
        x = 0
        y = 0
        basket_distance = 0
        keypointcount = 0
        frames = pipeline.wait_for_frames()
        aligned_frames = rs.align(rs.stream.color).process(frames)
        color_frame = aligned_frames.get_color_frame()
        frame = np.asanyarray(color_frame.get_data())
        depth_frame = aligned_frames.get_depth_frame()
        #depth = np.asanyarray(depth_frame.get_data())

        #Ball threshold
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lowerLimits = np.array([self.lHue, self.lSaturation, self.lValue])
        upperLimits = np.array([self.hHue, self.hSaturation, self.hValue])

        thresholded = cv2.inRange(hsv, lowerLimits, upperLimits)
        thresholded = cv2.bitwise_not(thresholded)
        thresholded = cv2.erode(thresholded,self.kernel, iterations=1)
        #blue basket
        if self.target == True:
            basketlowerLimits = np.array([self.lHue1, self.lSaturation1, self.lValue1])
            basketupperLimits = np.array([self.hHue1, self.hSaturation1, self.hValue1])

            basketthresholded = cv2.inRange(hsv, basketlowerLimits, basketupperLimits)
            basketthresholded = cv2.erode(basketthresholded, self.kernel, iterations=2)
            contours, hierarchy = cv2.findContours(basketthresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        #magenta basket
        if self.target != True:
            basketlowerLimits = np.array([self.lHue2, self.lSaturation2, self.lValue2])
            basketupperLimits = np.array([self.hHue2, self.hSaturation2, self.hValue2])

            basketthresholded = cv2.inRange(hsv, basketlowerLimits, basketupperLimits)
            basketthresholded = cv2.erode(basketthresholded, self.kernel, iterations=2)
            contours, hierarchy = cv2.findContours(basketthresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        
        if len(contours) > 0:
            contours = max(contours, key= cv2.contourArea)
            cv2.drawContours(frame, [contours], -1, (0,255,255), 3)

            M = cv2.moments(contours)
            if M["m00"] > 0:
                basket_x_center = int(M["m10"] / M["m00"])
                basket_y_center = int(M["m01"] / M["m00"])
                basket_distance = depth_frame.get_distance(basket_x_center, basket_y_center)
            


        cv2.imshow('Thresholded', frame)
        cv2.imshow('test', thresholded)

        #outimage = cv2.bitwise_and(frame, frame, mask=thresholded)
        keypoints = self.detector.detect(thresholded)
        keypoints = sorted(keypoints, key=lambda kp:kp.size, reverse=False)
        if len(keypoints) >= 1:
            x = keypoints[-1].pt[0]
            y = keypoints[-1].pt[1]

            #x = int(keypoints[0])
            #y = int(keypoints[1])

        keypointcount = len(keypoints)

            # for kp in keypoints:
            #     x = int(kp.pt[0])
            #     y = int(kp.pt[1])
        return {"count" : keypointcount, "y" : y, "x": x, "basket_x" : basket_x_center, "basket_y" : basket_y_center, "basket_distance" : basket_distance}
