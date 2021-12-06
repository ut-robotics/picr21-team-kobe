#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import movement as drive
import image_processing as ip
import camera_config
import math
from enum import Enum
import Thrower
import referee_client as client
import time
import Xbox360
import color


class RobotStateData:

    def __init__(self) -> None:
        self.ball_x = None
        self.ball_y = None
        self.basket_x = None
        self.image_processor = None
        self.state = State.FIND
        self.keypoint_count = None
        self.has_thrown = False
        self.after_throw_counter = 0
        self.floor_area = None
        self.basket_distance = None
        self.debug = False
        self.thrower_speed = 0
        self.prev_x_speed = 0
        self.prev_y_speed = 0
        self.prev_rot_speed = 0
        self.out_of_field = False
        # self.has_rotated = True
        self.after_rotation_counter = 0
        self.basket_size = 0


cl = client.Client()
cl.start()

camera = camera_config.Config()
# set target value with referee commands True = Blue, !True = Magenta
target = False
# Create image processing object
processor = ip.ProcessFrames(camera, target)


# States for logic
class State(Enum):
    FIND = 0
    DRIVE = 1
    AIM = 2
    THROWING = 3
    STOPPED = 4
    MANUAL = 5
    DEBUG = 6


def calc_speed(delta, max_delta, min_delta, min_speed, max_delta_speed, max_speed):
    if abs(delta) < min_delta:
        return 0
    delta_div = delta / max_delta
    sign = math.copysign(1, delta_div)
    normalized_delta = math.pow(abs(delta_div), 2) * sign
    speed = normalized_delta * max_delta_speed
    return int(int(speed) if abs(speed) >= min_speed and abs(
        speed) <= max_speed else max_speed * sign if speed > max_speed else min_speed * sign)


def handle_manual(state_data, gamepad):
    # if gamepad.a == 1:
    #         state_data.state = State.FIND
    #         return
    # print("speed: ", state_data.thrower_speed, "dist: ", state_data.basket_distance)
    if gamepad.a > 0:
        state_data.thrower_speed += 10
    if gamepad.b > 0:
        state_data.thrower_speed -= 10
    # drive.move_omni(0,0,0, state_data.thrower_speed)
    # drive.move_omni(int(gamepad.x*30),-int(gamepad.y*30),int(gamepad.rx*20), 0)


def handle_drive(state_data, gamepad):
    max_acceleration = 4
    print(state_data.basket_size)
    if state_data.basket_size is not None:
        if state_data.basket_size > 28000:
            drive.move_omni(0, 0, 20, 0)
            time.sleep(0.3)
            state_data.state = State.FIND
            return

    if state_data.out_of_field:
        drive.move_omni(0, 0, 20, 0)
        time.sleep(0.3)
        state_data.out_of_field = False
        state_data.state = State.FIND
        return

    if not state_data.floor_area or state_data.floor_area < 20000:
        drive.move_omni(0, -10, 20, 0)
        time.sleep(0.3)
        state_data.state = State.FIND
        return

    if state_data.keypoint_count > 0 and state_data.floor_area > 20000:
        # print(floor_area)
        delta_x = state_data.ball_x - camera.camera_x / 2
        delta_y = (camera.camera_y - 110) - state_data.ball_y
        min_speed = 2
        max_speed = 50
        min_delta = 5
        front_speed = calc_speed(delta_y, camera.camera_y, min_delta, 5, 500, 60)
        rot_spd = calc_speed(delta_x, camera.camera_x, min_delta, min_speed, 150, 40)

        front_delta = front_speed - state_data.prev_y_speed
        if abs(front_delta) > max_acceleration and front_delta > 0:
            sign = math.copysign(1, front_delta)
            front_speed = int(state_data.prev_y_speed + max_acceleration * sign)

        state_data.prev_x_speed = 0
        state_data.prev_y_speed = front_speed
        state_data.prev_rot_speed = -rot_spd

        drive.move_omni(-0, front_speed, -rot_spd, 0)

        if camera.camera_y + 20 > state_data.ball_y > camera.camera_y - 160:  # How close ball y should be to switch to next state
            state_data.state = State.AIM
            return

    if state_data.keypoint_count <= 0 or None:
        state_data.state = State.FIND
        return

    state_data.state = State.DRIVE


def handle_find(state_data, gamepad):
    drive.move_omni(0, 0, 8, 0)
    if state_data.keypoint_count >= 1:
        handle_drive(state_data, gamepad)
        state_data.state = State.DRIVE
        return

    state_data.state = State.FIND


def handle_stopped(state_data, gamepad):
    drive.stop()
    state_data.state = State.STOPPED


def handle_aim(state_data, gamepad):
    # # meters
    # if state_data.basket_distance is not None:
    #     if state_data.basket_distance < 0.3:
    #         drive.move_omni(0, 0, 20, 0)
    #         time.sleep(0.3)
    #         state_data.state = State.FIND
    #         return

    if state_data.floor_area is None or state_data.floor_area < 20000:
        state_data.state = State.FIND
        return

    basket_in_frame = state_data.basket_x is not None
    if state_data.ball_x is None:
        state_data.state = State.FIND
        return

    if not basket_in_frame:
        delta_x = camera.camera_x
    else:
        delta_x = state_data.ball_x - state_data.basket_x

    rot_delta_x = state_data.ball_x - camera.camera_x / 2
    delta_y = (camera.camera_y - 30) - state_data.ball_y
    front_speed = calc_speed(delta_y, camera.camera_y, 5, 3, 500, 40)
    side_speed = calc_speed(delta_x, camera.camera_x, 5, 6, 200, 30)
    rot_speed = calc_speed(rot_delta_x, camera.camera_x, 5, 3, 200, 50)
    state_data.prev_y_speed = front_speed
    state_data.prev_rot_speed = rot_speed
    state_data.prev_x_speed = side_speed

    drive.move_omni(-side_speed, front_speed, -rot_speed, 0)

    if basket_in_frame and (camera.camera_x / 2) - 10 <= state_data.basket_x <= (
            camera.camera_x / 2) + 10 and state_data.ball_y >= 410:  # Start throwing if ball y is close to robot and basket is centered to camera x
        drive.stop()  # prev center 315 to 325
        state_data.state = State.THROWING
        return
    state_data.state = State.AIM


def handle_throwing(state_data, gamepad):
    min_speed = 15
    max_speed = 30
    min_delta = 5

    if state_data.has_thrown:
        state_data.after_throw_counter += 1

    if state_data.after_throw_counter > 60:
        state_data.after_throw_counter = 0
        state_data.state = State.FIND
        state_data.has_thrown = False
        return

    if state_data.keypoint_count >= 1 and not state_data.has_thrown:

        basket_in_frame = state_data.basket_x is not None

        if not basket_in_frame:
            delta_x = camera.camera_x
        else:
            delta_x = state_data.ball_x - state_data.basket_x
        rot_delta_x = state_data.ball_x - camera.camera_x / 2  # if no ball and throw true basket_x - camera_x
        delta_y = camera.camera_y + 20 - state_data.ball_y
        thrower_speed = Thrower.thrower_speed(state_data.basket_distance)
        front_speed = calc_speed(delta_y, camera.camera_y, min_delta, min_speed, 200, max_speed)
        side_speed = calc_speed(delta_x, camera.camera_x, min_delta, 2, 150, max_speed)
        rot_speed = calc_speed(rot_delta_x, camera.camera_x, min_delta, 2, 100, max_speed)
        state_data.prev_y_speed = front_speed
        state_data.prev_rot_speed = rot_speed
        state_data.prev_x_speed = side_speed
        drive.move_omni(-side_speed, front_speed, -rot_speed, thrower_speed)
        state_data.has_thrown = True
        state_data.state = State.THROWING
        return

    elif state_data.has_thrown:
        basket_in_frame = state_data.basket_x is not None
        delta_x = 0

        if basket_in_frame:
            delta_x = state_data.basket_x - camera.camera_x / 2

            # delta_x = state_data.ball_x - state_data.basket_x
        delta_y = 0  # 500 - Camera.camera_y
        # front_speed = calc_speed(delta_y, Camera.camera_y, min_delta, 0, 100, 8)
        side_speed = calc_speed(delta_x, camera.camera_x, 0, 0, 75, 20)

        rot_speed = calc_speed(delta_x, camera.camera_x, 0, 0, 50, 20)

        state_data.prev_y_speed = 0
        state_data.prev_rot_speed = rot_speed
        state_data.prev_x_speed = side_speed

        thrower_speed = Thrower.thrower_speed(state_data.basket_distance)

        drive.move_omni(-side_speed, 8, rot_speed, thrower_speed)
        # print("throwing at ", state_data.thrower_speed, "from ", state_data.basket_distance, "away")

        state_data.state = State.THROWING
        if state_data.debug and state_data.after_throw_counter > 59:
            state_data.state = State.DEBUG
        return

    elif state_data.keypoint_count == 0 and not state_data.has_thrown:
        state_data.state = State.FIND


def handle_debug(state_data, gamepad):
    drive.stop()
    # print("distance from basket: ", state_data.basket_distance)
    state_data.thrower_speed = int(input("Enter thrower speed to use:"))
    state_data.state = State.FIND


data = None


def listen_for_referee_commands(state_data, processor):
    try:
        run, target = cl.get_current_referee_command()
        print("Target:  " + str(target))
        print("Run: " + str(run))
        if target:
            target = True
        else:
            target = False
        processor.set_target(target)
        if not run:
            state_data.state = State.STOPPED
            return
        if run and state_data.state == State.STOPPED:
            print(state_data.state)
            state_data.state = State.FIND
            return
    except:
        print("Server client communication failed.")


switcher = {
    State.FIND: handle_find,
    State.DRIVE: handle_drive,
    State.AIM: handle_aim,
    State.THROWING: handle_throwing,
    State.STOPPED: handle_stopped,
    State.MANUAL: handle_manual,
    State.DEBUG: handle_debug
}


def logic(switcher):
    start_time = time.time()
    counter = 0
    joy = Xbox360.XboxController()
    debug = False
    state_data = RobotStateData()
    try:
        while True:
            # Main code
            listen_for_referee_commands(state_data, processor)
            # Align depth frame if we are in throw state
            count, y, x, center_x, center_y, basket_distance, floor_area, out_of_field, basket_size = processor.process_frame(
                align_frame=state_data.state == State.THROWING)
            state_data.ball_x = x
            state_data.ball_y = y
            state_data.keypoint_count = count
            state_data.basket_x = center_x
            state_data.debug = debug
            state_data.floor_area = floor_area
            state_data.basket_distance = basket_distance
            state_data.out_of_field = out_of_field
            state_data.basket_size = basket_size
            controller = joy.read()

            if controller.ybtn == 1:
                state_data.state = State.MANUAL
                # switcher.get(state_data.state)(state_data, controller)
            if controller.start == 1:
                state_data.state = State.FIND

            if controller.stop == 1:
                state_data.state = State.STOPPED

            key = cv2.waitKey(1) & 0xFF
            if key == ord('r'):
                state_data.state = State.FIND
            # print(state_data.state)
            switcher.get(state_data.state)(state_data, controller)

            if key == ord('q'):
                break

            # FPS stuff
            counter += 1
            if (time.time() - start_time) > 1:  # Frame rate per 1 second
                print("FPS -->", counter / (time.time() - start_time))
                counter = 0
                start_time = time.time()

        cv2.destroyAllWindows()
    except Exception as e:
        print(e)
        raise
    finally:
        camera.stop_streams()


logic(switcher)
