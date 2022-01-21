from concurrent.futures import process
import segment
import _pickle as pickle
import numpy as np
import cv2
import color as c
import color_sampler
from color import Color


class Object:
    def __init__(self, x=-1, y=-1, size=-1, distance=-1, exists=False, bottom_y=-1):
        self.x = x
        self.y = y
        self.size = size
        self.distance = distance
        self.exists = exists
        self.bottom_y = bottom_y

    def __str__(self) -> str:
        return "[Object: x={}; y={}; size={}; distance={}; exists={}; bottom_y={}]".format(
            self.x, self.y, self.size, self.distance, self.exists, self.bottom_y)

    def __repr__(self) -> str:
        return "[Object: x={}; y={}; size={}; distance={}; exists={}; bottom_y{}]".format(
            self.x, self.y, self.size, self.distance, self.exists, self.bottom_y)


# results object of image processing. contains coordinates of objects and frame data used for these results
class ProcessedResults:
    def __init__(self,
                 balls=[],
                 basket_b=Object(exists=False),
                 basket_m=Object(exists=False),
                 color_frame=[],
                 depth_frame=[],
                 fragmented=[],
                 debug_frame=[],
                 out_of_field=False,
                 turn_left=False,
                 turn_right=False):
        self.balls = balls
        self.basket_b = basket_b
        self.basket_m = basket_m
        self.color_frame = color_frame
        self.depth_frame = depth_frame
        self.fragmented = fragmented
        self.out_of_field = out_of_field
        self.turn_left = turn_left
        self.turn_right = turn_right
        # can be used to illustrate things in a separate frame buffer
        self.debug_frame = debug_frame


# Main processor class. processes segmented information
class ImageProcessor:
    def __init__(self, camera, color_config="colors/colors.pkl", debug=True):
        self.camera = camera
        self.color_config = color_config
        with open(self.color_config, 'rb') as conf:
            self.colors_lookup = pickle.load(conf)
            self.set_segmentation_table(self.colors_lookup)

        self.fragmented = np.zeros((self.camera.rgb_height, self.camera.rgb_width), dtype=np.uint8)

        self.t_balls = np.zeros((self.camera.rgb_height, self.camera.rgb_width), dtype=np.uint8)
        self.t_basket_b = np.zeros((self.camera.rgb_height, self.camera.rgb_width), dtype=np.uint8)
        self.t_basket_m = np.zeros((self.camera.rgb_height, self.camera.rgb_width), dtype=np.uint8)

        self.debug = debug
        self.debug_frame = np.zeros((self.camera.rgb_height, self.camera.rgb_width), dtype=np.uint8)
        self.line_sequence = np.array([int(c.Color.ORANGE), int(c.Color.BLACK), int(c.Color.WHITE)], dtype=np.uint8)
        self.out_of_field = False
        self.turn_right = False
        self.turn_left = False

    def set_segmentation_table(self, table):
        segment.set_table(table)

    def start(self):
        self.camera.open()

    def stop(self):
        self.camera.close()

    def analyze_balls(self, t_balls) -> list:
        t_balls = cv2.dilate(t_balls,(20,20),iterations = 1)

        contours, hierarchy = cv2.findContours(t_balls, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        balls = []

        for contour in contours:
            # ball filtering logic goes here. Example includes filtering by size and an example how to get pixels from
            # the bottom center of the frame to the ball
            size = cv2.contourArea(contour)
            #print(size)
            if size < 15: #or self.out_of_field: #15
                continue

            x, y, w, h = cv2.boundingRect(contour)

            ys = np.arange(y + h, self.camera.rgb_height)
            xs = np.linspace(x + w / 2, self.camera.rgb_width / 2, num=len(ys), dtype=np.uint16)

            #obstacle avoidance

            center_x = 424
            center_y = np.arange(150,330)

            left_column_x = 324
            left_column_y = np.arange(150,330)

            left_column_x1 = 224
            left_column_y1 = np.arange(150,330)

            left_column_x2 = 124
            left_column_y2 = np.arange(150,330)

            right_column_x = 524
            right_column_y = np.arange(150,330)

            right_column_x1 = 624
            right_column_y1 = np.arange(150,330)

            right_column_x2 = 724
            right_column_y2 = np.arange(150,330)


            #orange_color_sum = np.count_nonzero(self.fragmented[center_y,center_x] == int(Color.ORANGE))
            orange_color_sum1 = np.count_nonzero(self.fragmented[left_column_y,left_column_x] == int(Color.ORANGE))
            orange_color_sum2 = np.count_nonzero(self.fragmented[left_column_y1,left_column_x1] == int(Color.ORANGE))
            orange_color_sum3 = np.count_nonzero(self.fragmented[left_column_y2,left_column_x2] == int(Color.ORANGE))
            orange_color_sum4 = np.count_nonzero(self.fragmented[right_column_y,right_column_x] == int(Color.ORANGE))
            orange_color_sum5 = np.count_nonzero(self.fragmented[right_column_y1,right_column_x1] == int(Color.ORANGE))
            orange_color_sum6 = np.count_nonzero(self.fragmented[right_column_y2,right_column_x2] == int(Color.ORANGE))

            orange_color_area_left_side = orange_color_sum1 + orange_color_sum2 + orange_color_sum3
            orange_color_area_right_side = orange_color_sum4 + orange_color_sum5 + orange_color_sum6

            if orange_color_area_left_side < 240:
                self.turn_right = True
            if orange_color_area_left_side > 240:
                self.turn_right = False
            if orange_color_area_right_side < 240:
                self.turn_left = True
            if orange_color_area_right_side > 240:
                self.turn_left = False



            # print(orange_color_area_left_side)
            # print(self.turn_right)
            #print(orange_color_sum)

            colors = self.fragmented[ys, xs]
            out_of_field = color_sampler.check_sequence(colors, 8, self.line_sequence)

            if out_of_field:
                self.out_of_field = out_of_field
                continue
            else:
                self.out_of_field = False

            obj_x = int(x + (w / 2))
            obj_y = int(y + (h / 2))
            obj_dst = obj_y

            if self.debug:
                self.debug_frame[ys, xs] = [0, 0, 0]
                #self.debug_frame[200:300, 424] = [0,0,0]
                self.debug_frame[center_y, center_x] = [0,0,0]
                self.debug_frame[left_column_y, left_column_x] = [0,0,0]
                self.debug_frame[left_column_y1, left_column_x1] = [0,0,0]
                self.debug_frame[left_column_y2, left_column_x2] = [0,0,0]
                self.debug_frame[right_column_y, right_column_x] = [0,0,0]
                self.debug_frame[right_column_y1, right_column_x1] = [0,0,0]
                self.debug_frame[right_column_y2, right_column_x2] = [0,0,0]

                #self.debug_frame[100:300, 200:600] = [0,0,0]
                cv2.circle(self.debug_frame, (obj_x, obj_y), 10, (0, 255, 0), 2)
                #cv2.rectangle(self.debug_frame, (100,200), (100,200),(0,255,0), 5)

            balls.append(Object(x=obj_x, y=obj_y, size=size, distance=obj_dst, exists=True))

        balls.sort(key=lambda x: x.distance, reverse=True)

        return balls

    def analyze_baskets(self, t_basket, depth_frame, debug_color = (0, 255, 255)) -> list:
        #t_basket = cv2.dilate(t_basket,(20,20),iterations = 1)
        contours, hierarchy = cv2.findContours(t_basket, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        baskets = []
        for contour in contours:
            # basket filtering logic goes here. Example includes size filtering of the basket
            size = cv2.contourArea(contour)

            if size < 100:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            bottommost = tuple(contour[contour[:,:,1].argmax()][0])
            #bottom = (np.argmax(contour[y+h-1, :]), y+h-1)
            obj_x = int(x + (w/2))
            obj_y = int(y + (h/2))
            area_w = 3
            area_h = 3
            depth_image = np.asanyarray(depth_frame.get_data())

            try:
                obj_dst = np.average(depth_image[obj_y:obj_y + area_w, obj_x:obj_x + area_h]) * self.camera.depth_scale
            except IndexError:
                obj_dst = depth_frame.get_distance(obj_x, obj_y)

            baskets.append(Object(x=obj_x, y=obj_y, size=size, distance=obj_dst, exists=True, bottom_y=bottommost[1]))

        baskets.sort(key=lambda x: x.size)

        basket = next(iter(baskets), Object(exists=False))

        if self.debug:
            if basket.exists:
                cv2.circle(self.debug_frame, (basket.x, basket.y), 20, debug_color, -1)
                #cv2.rectangle(self.debug,(x,y),(x+w, y+h), debug_color, -1)
                #cv2.circle(self.debug, bottommost, 5, (255,0,0), -1)

        return basket

    def get_frame_data(self, aligned_depth=False):
        if self.camera.has_depth_capability():
            return self.camera.get_frames(aligned=aligned_depth)
        else:
            return self.camera.get_color_frame(), np.zeros((self.camera.rgb_height, self.camera.rgb_width),
                                                           dtype=np.uint8)

    def process_frame(self, aligned_depth=False) -> ProcessedResults:
        color_frame, depth_frame = self.get_frame_data(aligned_depth=aligned_depth)

        segment.segment(color_frame, self.fragmented, self.t_balls, self.t_basket_m, self.t_basket_b)
        if self.debug:
            self.debug_frame = np.copy(color_frame)

        balls = self.analyze_balls(self.t_balls)
        basket_b = self.analyze_baskets(self.t_basket_b, depth_frame, debug_color=c.Color.BLUE.color.tolist())
        basket_m = self.analyze_baskets(self.t_basket_m, depth_frame, debug_color=c.Color.MAGENTA.color.tolist())

        return ProcessedResults(balls=balls,
                                basket_b=basket_b,
                                basket_m=basket_m,
                                color_frame=color_frame,
                                depth_frame=depth_frame,
                                fragmented=self.fragmented,
                                debug_frame=self.debug_frame,
                                out_of_field=self.out_of_field,
                                turn_left=self.turn_left,
                                turn_right=self.turn_right)


class ProcessFrames:
    def __init__(self, camera, target=Color.BLUE):
        self.processor = ImageProcessor(camera.cam, debug=True)
        self.target = target

    def set_target(self, target):
        self.target = target

    def process_frame(self, align_frame=False):
        processed = self.processor.process_frame(aligned_depth=align_frame)
        ball_array = processed.balls
        x = None
        y = None
        basket_x_center = None
        basket_y_center = None
        basket_distance = None
        avoid_collision = True
        opponent_basket_bottom_y = None
        basket_bottom_y = None

        out_of_field = processed.out_of_field
        turn_left = processed.turn_left
        turn_right = processed.turn_right
        opponent_basket_x = None

        if self.target == Color.BLUE:
            basket = processed.basket_b
            opponent_basket = processed.basket_m
        else:
            basket = processed.basket_m
            opponent_basket = processed.basket_b

        if basket.exists:
            basket_x_center = basket.x
            basket_y_center = basket.y
            basket_distance = basket.distance
            basket_bottom_y = basket.bottom_y

        if opponent_basket.exists:
            opponent_basket_x = opponent_basket.x
            opponent_basket_bottom_y = opponent_basket.bottom_y

        floor_area = np.count_nonzero(processed.fragmented == int(Color.ORANGE))
        # obstacle_area = np.count_nonzero(processed.fragmented[150:300, 300:600] == int(Color.ORANGE))
        

        
        # if obstacle_area is None:
        #     obstacle_area = 0
            
        # if obstacle_area < 40000:
        #     avoid_collision = True
        # if obstacle_area > 40000:
        #     avoid_collision = False
            
        # print("obstacle area", obstacle_area)
        # print("obstacle ahead", avoid_collision)
        if floor_area is None:
            floor_area = 0

        if len(ball_array) > 0:
            x = ball_array[0].x
            y = ball_array[0].y

        basket_size = basket.size

        cv2.imshow("Debug", processed.debug_frame)

        return (len(ball_array),
                y,
                x,
                basket_x_center,
                basket_y_center,
                basket_distance,
                floor_area,
                out_of_field,
                basket_size,
                opponent_basket_x,
                opponent_basket_bottom_y,
                basket_bottom_y,
                avoid_collision,
                turn_left,
                turn_right)