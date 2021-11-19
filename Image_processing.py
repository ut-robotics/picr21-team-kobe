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

        return len(ball_array), y, x, basket_x_center, basket_y_center, basket_distance, floorarea