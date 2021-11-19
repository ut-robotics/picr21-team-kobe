#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np
from math import atan2, floor
import pyrealsense2 as rs
import math
import Blobparams
import CameraConfig
import ReadValues
import camera
import image_processor
import Color
import color_sampler
##21,36,56,91,179,237 new ball thresh



class ProcessFrames():
    def __init__(self, target, camera):
        
        self.processor = image_processor.ImageProcessor(camera.cam, debug=True)

        self.target = target
        self.lHue, self.lSaturation, self.lValue, self.hHue, self.hSaturation, self.hValue = ReadValues.ReadThreshold("trackbar_defaults.txt")
        #from referee check what the target command is
        self.lHue1, self.lSaturation1, self.lValue1, self.hHue1, self.hSaturation1, self.hValue1 = ReadValues.ReadThreshold("blue_basket.txt")
        self.lHue2, self.lSaturation2, self.lValue2, self.hHue2, self.hSaturation2, self.hValue2 = ReadValues.ReadThreshold("pink_basket.txt")
        self.lHue3, self.lSaturation3, self.lValue3, self.hHue3, self.hSaturation3, self.hValue3 = ReadValues.ReadThreshold("floor.txt")

        self.kernel = np.ones((5,5),np.uint8)
        self.detector = Blobparams.CreateDetector()
        self.frame = None


    def SetTarget(self, target):
        self.target = target

    def ProcessFrame(self, align_frame = False):
        
        processed = self.processor.process_frame(aligned_depth=align_frame)
        ball_array = processed.balls
        x = None
        y = None
        basket = None
        basket_x_center = None
        basket_y_center = None
        basket_distance = None

        if self.target:
            basket = processed.basket_b
        else:
            basket = processed.basket_m

        if basket.exists:
            basket_x_center = basket.x
            basket_y_center = basket.y
            basket_distance = basket.distance


        floorarea = np.count_nonzero(processed.fragmented == int(Color.Color.ORANGE))
        #out_of_field = color_sampler.test(processed.fragmented,3, (int(Color.Color.ORANGE),int(Color.Color.BLACK), int(Color.Color.WHITE), int(Color.Color.ORANGE)))
        
        if floorarea is None:
            floorarea = 0

        if len(ball_array) > 0:
            x = ball_array[0].x
            y = ball_array[0].y
<<<<<<< HEAD

        return len(ball_array), y, x, basket_x_center, basket_y_center, basket_distance, floorarea
=======
        cv2.imshow("test", processed.debug_frame)
        return len(ball_array), y, x, basket_x_center, basket_y_center, basket_distance, floorarea
        
        
    def Threshold(self, pipeline):
        frames = pipeline.wait_for_frames()
        aligned_frames = rs.align(rs.stream.color).process(frames)
        color_frame = aligned_frames.get_color_frame()
        frame = np.asanyarray(color_frame.get_data())
        depth_frame = aligned_frames.get_depth_frame()

        #Ball threshold
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lowerLimits = np.array([self.lHue1, self.lSaturation1, self.lValue1])
        upperLimits = np.array([self.hHue1, self.hSaturation1, self.hValue1])

        thresholded = cv2.inRange(hsv, lowerLimits, upperLimits)
        thresholded = cv2.bitwise_not(thresholded)
        #thresholded = cv2.erode(thresholded,self.kernel, iterations=1)
        #thresholded = cv2.bitwise_not(thresholded)
        outimage = cv2.bitwise_and(frame, frame, mask=thresholded)
        keypoints = self.detector.detect(thresholded)

        if len(keypoints) >= 1:
            for kp in keypoints:
                x = int(kp.pt[0])
                y = int(kp.pt[1])
                #print(kp.size)
                cv2.putText(outimage, str(x) + "," + str(y), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
        # contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # if len(contours) > 0:
        #     contour = max(contours, key= cv2.contourArea)
        #     if cv2.contourArea(contour) > 500:

        #         cv2.drawContours(frame, contour, -1, 255, -1)
        #         print(cv2.contourArea(contour))
        #     if cv2.contourArea(contour) < 1500 or contour is None:
        #         print("go back going over playfield!")
        #         #x1, y1, w, h = cv2.boundingRect(contour)
        #         #cv2.rectangle(frame,(x1,y1),(x1+w,y1+h),(0,255,0),3)

        
        contours, hierarchy = cv2.findContours(thresholded, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) > 0:
            contour = max(contours, key= cv2.contourArea)
            if cv2.contourArea(contour) > 200:

                cv2.drawContours(frame, contour, -1, 255, -1)
                x1, y1, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame,(x1,y1),(x1+w,y1+h),(0,255,0),3)
                basket_x_center = int(x1+(w/2))
                basket_y_center = int(y1+(h/2))
                basket_distance = depth_frame.get_distance(basket_x_center, basket_y_center)
                print(basket_distance*100)
        
        outimage = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        cv2.imshow('Thresholded', thresholded)
        cv2.imshow('Keypoints', outimage)
>>>>>>> d0342489cb1f8dcc5833b1fe47e8f55914d58301
