import camera
import segment
import _pickle as pickle
import numpy as np
import cv2
import color as c
import color_sampler
from color import Color


class Object:
    def __init__(self, x=-1, y=-1, size=-1, distance=-1, exists=False):
        self.x = x
        self.y = y
        self.size = size
        self.distance = distance
        self.exists = exists

    def __str__(self) -> str:
        return "[Object: x={}; y={}; size={}; distance={}; exists={}]".format(
            self.x, self.y, self.size, self.distance, self.exists)

    def __repr__(self) -> str:
        return "[Object: x={}; y={}; size={}; distance={}; exists={}]".format(
            self.x, self.y, self.size, self.distance, self.exists)


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
                 out_of_field=False):
        self.balls = balls
        self.basket_b = basket_b
        self.basket_m = basket_m
        self.color_frame = color_frame
        self.depth_frame = depth_frame
        self.fragmented = fragmented
        self.out_of_field = out_of_field

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
            # the bottom center of the fram to the ball

            size = cv2.contourArea(contour)

            if size < 15: #or self.out_of_field:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            ys = np.arange(y + h, self.camera.rgb_height)
            xs = np.linspace(x + w / 2, self.camera.rgb_width / 2, num=len(ys), dtype=np.uint16)

            colors = self.fragmented[ys, xs]
            out_of_field = color_sampler.check_sequence(colors, 8, self.line_sequence)
            #out_of_field = False
            #print(out_of_field)

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
                cv2.circle(self.debug_frame, (obj_x, obj_y), 10, (0, 255, 0), 2)

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

            obj_x = int(x + (w/2))
            obj_y = int(y + (h/2))
            area_w = 3
            area_h = 3
            depth_image = np.asanyarray(depth_frame.get_data())
            obj_dst = np.average(depth_image[obj_y:obj_y + area_w, obj_x:obj_x + area_h]) * self.camera.depth_scale

            #depth_frame.get_distance(obj_x, obj_y)






            baskets.append(Object(x=obj_x, y=obj_y, size=size, distance=obj_dst, exists=True))

        baskets.sort(key=lambda x: x.size)

        basket = next(iter(baskets), Object(exists=False))

        if self.debug:
            if basket.exists:
                cv2.circle(self.debug_frame, (basket.x, basket.y), 20, debug_color, -1)

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
                                out_of_field=self.out_of_field)


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
        basket = None
        basket_x_center = None
        basket_y_center = None
        basket_distance = None
        out_of_field = False

        out_of_field = processed.out_of_field
        opponent_basket = None
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

        if opponent_basket.exists:
            opponent_basket_x = opponent_basket.x

        floor_area = np.count_nonzero(processed.fragmented == int(Color.ORANGE))

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
                opponent_basket_x)