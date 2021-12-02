#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import numpy as np
import image_processor
import Color

class ProcessFrames():
    def __init__(self, camera, target=False):
        
        self.processor = image_processor.ImageProcessor(camera.cam, debug=True)
        self.target = target

    def set_target(self, target):
        self.target = target

    def process_frame(self, align_frame = False):
        
        processed = self.processor.process_frame(aligned_depth=align_frame)
        ball_array = processed.balls
        x = None
        y = None
        basket = None
        basket_x_center = None
        basket_y_center = None
        basket_distance = None
        out_of_field = False

        out_of_field = processed.out_of_field

        if self.target:
            basket = processed.basket_b
        else:
            basket = processed.basket_m

        if basket.exists:
            basket_x_center = basket.x
            basket_y_center = basket.y
            basket_distance = basket.distance


        floorarea = np.count_nonzero(processed.fragmented == int(Color.Color.ORANGE))
        
        if floorarea is None:
            floorarea = 0

        if len(ball_array) > 0:
            x = ball_array[0].x
            y = ball_array[0].y

        cv2.imshow("Debug", processed.debug_frame)

        return len(ball_array), y, x, basket_x_center, basket_y_center, basket_distance, floorarea, out_of_field
