#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import movement as drive
import image_processor as ip
import camera_config
import math
from enum import Enum
import thrower
import referee_client as client
import time
import xbox360
from color import Color

data = None
cl = client.Client()
cl.start()
camera = camera_config.Config()
# set target color with referee commands
target = Color.MAGENTA
# Create image processing object
processor = ip.ProcessFrames(camera, target)


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
        self.thrower_speed = 1000
        self.prev_x_speed = 0
        self.prev_y_speed = 0
        self.prev_rot_speed = 0
        self.out_of_field = False
        self.has_rotated = True
        self.after_rotation_counter = 0
        self.basket_size = 0
        self.min_valid_frames = 5
        self.valid_aim_frames = 0
        self.last_attacking_basket_x = None
        self.opponent_basket_x = None
        self.patrol_counter = 0
        self.opponent_basket_bottom_y = None
        self.basket_bottom_y = None
        self.own_basket = True
        self.avoid_collision = False
        self.turn_direction = 1
        self.left_metric = None
        self.right_metric = None


# States for logic
class State(Enum):
    FIND = 0
    DRIVE = 1
    AIM = 2
    THROWING = 3
    STOPPED = 4
    MANUAL = 5
    DEBUG = 6
    PATROL = 7


def calc_speed(delta, max_delta, min_delta, min_speed, max_delta_speed, max_speed):
    if abs(delta) < min_delta:
        return 0
    delta_div = delta / max_delta
    sign = math.copysign(1, delta_div)
    normalized_delta = math.pow(abs(delta_div), 2) * sign
    speed = normalized_delta * max_delta_speed
    return int(int(speed) if abs(speed) >= min_speed and abs(
        speed) <= max_speed else max_speed * sign if abs(speed) > max_speed else min_speed * sign)


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


def handle_patrol(state_data, gamepad):
    if state_data.keypoint_count > 0:
        state_data.state = State.DRIVE
        return

    if state_data.patrol_counter > 300:
        state_data.patrol_counter = 0
        state_data.state = State.FIND  

    #print(state_data.own_basket)
    if state_data.own_basket:
        basket_in_frame = state_data.basket_x is not None
        #print("here", basket_in_frame)
        # if not basket_in_frame:
        #     state_data.own_basket = False
        if basket_in_frame and state_data.basket_bottom_y < camera.camera_y*0.3:
            #rot_delta_x = camera.camera_x/2
            delta_x = state_data.basket_x - camera.camera_x / 2

            rot_spd = calc_speed(delta_x, camera.camera_x/2, 5, 3, 100, 30)  #* turn_direction

            if state_data.left_metric > 0.6 and state_data.right_metric > 0.6:
                drive.move_omni(0,40, -rot_spd, 0)
            if state_data.left_metric < 0.6:
                drive.move_omni(-state_data.left_metric * 70, 40, -rot_spd, 0)
            if state_data.right_metric < 0.6:
                drive.move_omni(state_data.left_metric * 70, 40, -rot_spd, 0)

        elif not basket_in_frame:
            drive.move_omni(0,0,20,0)
        elif state_data.basket_bottom_y <= camera.camera_y * 0.41:
            state_data.own_basket = False
            state_data.basket_bottom_y = None
            state_data.state = State.FIND

    if not state_data.own_basket:
        #print('here2')
        basket_in_frame = state_data.opponent_basket_x is not None
        # if not basket_in_frame:
        #     state_data.own_basket = True
        #print(state_data.opponent_basket_bottom_y, state_data.own_basket)
        if basket_in_frame and state_data.opponent_basket_bottom_y < camera.camera_y*0.3:
            #rot_delta_x = camera.camera_x/2
            delta_x = state_data.opponent_basket_x - camera.camera_x / 2

            rot_spd = calc_speed(delta_x, camera.camera_x/2, 5, 3, 100, 20)  #* turn_direction
            #print(state_data.left_metric, state_data.right_metric)

            if state_data.left_metric > 0.6 and state_data.right_metric > 0.6:
                drive.move_omni(0, 40, -rot_spd, 0)
            if state_data.left_metric < 0.6:
                drive.move_omni(-state_data.left_metric * 70, 40, -rot_spd, 0)
            if state_data.right_metric < 0.6:
                drive.move_omni(state_data.left_metric * 70, 40, -rot_spd, 0)

        elif not basket_in_frame:
            drive.move_omni(0,0,20,0)
        elif state_data.opponent_basket_bottom_y <= camera.camera_y * 0.4:
            state_data.state = State.FIND
            state_data.opponent_basket_bottom_y = None
            state_data.own_basket = True
            return

    if state_data.keypoint_count == 0:
        state_data.patrol_counter += 1
    state_data.State = State.PATROL


def handle_drive(state_data, gamepad):
    max_acceleration = 4
    if state_data.basket_bottom_y is not None and state_data.opponent_basket_bottom_y:
        if state_data.basket_bottom_y > camera.camera_y * 0.5 or state_data.opponent_basket_bottom_y > camera.camera_y * 0.5:
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

    if state_data.floor_area is None or state_data.floor_area < 20000:
        drive.move_omni(0, 0, 20, 0)
        time.sleep(0.3)
        state_data.state = State.FIND
        return

    if state_data.keypoint_count > 0 and state_data.floor_area > 20000: #and state_data.avoid_collision is False:
        delta_x = state_data.ball_x - camera.camera_x / 2
        delta_y = (camera.camera_y * 0.77) - state_data.ball_y
        min_speed = 2
        min_delta = 5
        front_speed = calc_speed(delta_y, camera.camera_y, min_delta, 5, 400, 50)
        rot_spd = calc_speed(delta_x, camera.camera_x, min_delta, min_speed, 100, 30)

        front_delta = front_speed - state_data.prev_y_speed
        if abs(front_delta) > max_acceleration and front_delta > 0:
            sign = math.copysign(1, front_delta)
            front_speed = int(state_data.prev_y_speed + max_acceleration * sign)

        state_data.prev_x_speed = 0
        state_data.prev_y_speed = front_speed
        state_data.prev_rot_speed = -rot_spd

        #print(state_data.right_metric)
        if state_data.left_metric > 0.6 and state_data.right_metric > 0.6:
            drive.move_omni(0,front_speed, -rot_spd, 0)

        if state_data.left_metric < 0.6:
            drive.move_omni(-state_data.left_metric * 70, front_speed, -rot_spd, 0)
        if state_data.right_metric < 0.6:
            drive.move_omni(state_data.left_metric * 70, front_speed, -rot_spd, 0)

        if camera.camera_y > state_data.ball_y > camera.camera_y * 0.66:  # How close ball y should be to switch to next state
            state_data.state = State.AIM
            return

    if state_data.keypoint_count <= 0 or None:
        state_data.state = State.FIND
        return

    state_data.state = State.DRIVE


def handle_find(state_data, gamepad):
    rot_speed = 5

    if state_data.patrol_counter > 300 and state_data.keypoint_count == 0:
        state_data.patrol_counter = 0
        state_data.state = State.PATROL
        return

    if state_data.after_rotation_counter > 20 and state_data.has_rotated:
        state_data.after_rotation_counter = 0
        state_data.has_rotated = not state_data.has_rotated
    elif state_data.after_rotation_counter > 30:
        state_data.after_rotation_counter = 0
        state_data.has_rotated = not state_data.has_rotated

    if state_data.has_rotated:
        rot_speed = 20
    state_data.after_rotation_counter += 1
    state_data.patrol_counter += 1

    drive.move_omni(0, 0, rot_speed, 0)
    if state_data.keypoint_count >= 1:
        handle_drive(state_data, gamepad)
        state_data.state = State.DRIVE
        state_data.has_rotated = False
        state_data.after_rotation_counter = 0
        return

    state_data.state = State.FIND


def handle_stopped(state_data, gamepad):
    #print(state_data.left_metric, "left")
    #print(state_data.right_metric, "right")
    drive.stop()
    state_data.state = State.STOPPED


def handle_aim(state_data, gamepad):

    #print("attacking basket {} opponent_basket {} turn direction {}".format(state_data.last_attacking_basket_x, state_data.opponent_basket_x, state_data.turn_direction))

    if state_data.floor_area is None or state_data.floor_area < 20000:
        state_data.state = State.FIND
        return

    basket_in_frame = state_data.basket_x is not None
    if state_data.ball_x is None:
        state_data.state = State.FIND
        return

    if not basket_in_frame:
        delta_x = camera.camera_x * state_data.turn_direction

    else:
        delta_x = state_data.ball_x - state_data.basket_x
    rot_delta_x = state_data.ball_x - camera.camera_x/2

    delta_y = (camera.camera_y * 0.758) - state_data.ball_y
    front_speed = calc_speed(delta_y, camera.camera_y, 5, 3, 500, 50)
    side_speed = calc_speed(delta_x, camera.camera_x, 5, 4, 100, 30) # * state_data.turn_direction
    rot_spd = calc_speed(rot_delta_x, camera.camera_x/2, 5, 3, 100, 40) # * state_data.turn_direction
    state_data.prev_yspeed = front_speed
    state_data.prev_rotspeed = rot_spd
    state_data.prev_xspeed = side_speed
    drive.move_omni(-side_speed, front_speed, -rot_spd, 0)

                                #415                                                    433
    if basket_in_frame and camera.camera_x * 0.489 <= state_data.basket_x <= camera.camera_x * 0.51 and state_data.ball_y >= camera.camera_y * 0.655: # Start throwing if ball y is close to robot and basket is centered to camera x
        if state_data.basket_distance > 0:
            min_throw_error = 4 #1.5
            max_throw_distance = 5.25
            basket_error_x = state_data.ball_x - state_data.basket_x  # state_data.basket_x - camera.camera_x
            throw_error = max_throw_distance / state_data.basket_distance * min_throw_error
            # is_basket_too_far = state_data.basket_distance > 2
            is_basket_too_close = state_data.basket_distance < 0.5

            if throw_error < min_throw_error:
                throw_error = min_throw_error

            is_basket_error_x_small_enough = abs(basket_error_x) < throw_error
            if is_basket_error_x_small_enough and not is_basket_too_close:  # and not is_basket_too_far:
                state_data.valid_aim_frames += 1
                if state_data.valid_aim_frames > state_data.min_valid_frames:
                    state_data.state = State.THROWING
                    state_data.valid_aim_frames = 0
            return
    state_data.state = State.AIM


def handle_throwing(state_data, controller):
    min_speed = 15
    max_speed = 30
    # min_delta = 5

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
        rot_delta_x = state_data.ball_x - camera.camera_x/2  # if no ball and throw true basket_x - camera_x
        delta_y = camera.camera_y - state_data.ball_y
        thrower_speed = thrower.thrower_speed(state_data.basket_distance)
        #thrower_speed = state_data.thrower_speed
        front_speed = calc_speed(delta_y, camera.camera_y, 5, min_speed, 200, max_speed)
        side_speed = calc_speed(delta_x, camera.camera_x, 0, 2, 150, max_speed)
        rot_spd = calc_speed(rot_delta_x, camera.camera_x, 0, 2, 100, max_speed)
        state_data.prev_yspeed = front_speed
        state_data.prev_rotspeed = rot_spd
        state_data.prev_xspeed = side_speed
        drive.move_omni(-side_speed, front_speed, -rot_spd, thrower_speed)
        #drive.move_omni(-0, 0, -0, 2600)
        state_data.has_thrown = True
        state_data.state = State.THROWING
        return

    elif state_data.has_thrown:
        basket_in_frame = state_data.basket_x is not None
        delta_x = 0
        rot_delta_x = 0

        if basket_in_frame:
            delta_x = state_data.basket_x - camera.camera_x / 2

        # ball_in_frame = state_data.ball_x is not None
        # if ball_in_frame and basket_in_frame:
        #    rot_delta_x = state_data.basket_x - state_data.ball_x
        if basket_in_frame:
            rot_delta_x = state_data.basket_x - camera.camera_x / 2

        # delta_x = state_data.ball_x - state_data.basket_x
        # delta_y = 0  # 500 - camera.camera_y
        # front_speed = calc_speed(delta_y, camera.camera_y, min_delta, 0, 100, 8)
        side_speed = calc_speed(delta_x, camera.camera_x, 0, 0, 75, 20)

        rot_speed = calc_speed(rot_delta_x, camera.camera_x/2, 0, 0, 200, 20)

        state_data.prev_y_speed = 0
        state_data.prev_rot_speed = rot_speed
        state_data.prev_x_speed = side_speed

        #thrower_speed = state_data.thrower_speed
        thrower_speed = thrower.thrower_speed(state_data.basket_distance)

        drive.move_omni(-side_speed, 8, -rot_speed, thrower_speed)
        #drive.move_omni(-0, 0, -0, thrower_speed)

        state_data.state = State.THROWING
        if state_data.debug and state_data.after_throw_counter > 50:
            state_data.state = State.DEBUG
            state_data.after_throw_counter = 0
        return

    elif state_data.keypoint_count == 0 and not state_data.has_thrown:
        state_data.state = State.FIND


def handle_debug(state_data, gamepad):
    drive.stop()
    state_data.thrower_speed = int(input("Enter thrower speed to use:"))
    state_data.state = State.FIND


def listen_for_referee_commands(state_data, processor):
    try:
        run, target = cl.get_current_referee_command()
        print("Target:  " + str(target))
        print("Run: " + str(run))
        if target:
            target = Color.BLUE
        else:
            target = Color.MAGENTA
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
    State.DEBUG: handle_debug,
    State.PATROL: handle_patrol
}


def logic(switcher):
    start_time = time.time()
    counter = 0
    joy = xbox360.XboxController()
    debug = False
    state_data = RobotStateData()
    try:
        while True:
            # Main code
            # Comment this line out if you are not using a referee server to send commands
            listen_for_referee_commands(state_data, processor)
            #state_data.state = State.AIM
            # Align depth frame if we are in throw state
            count, y, x, center_x, center_y, basket_distance, floor_area, out_of_field, basket_size, opponent_basket_x, opponent_basket_bottom_y, basket_bottom_y, avoid_collision, left_metric, right_metric = processor.process_frame(
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
            state_data.basket_bottom_y = basket_bottom_y
            state_data.avoid_collision = avoid_collision
            state_data.left_metric = left_metric
            state_data.right_metric = right_metric

            if opponent_basket_x is not None:
                state_data.opponent_basket_x = opponent_basket_x
                state_data.opponent_basket_bottom_y = opponent_basket_bottom_y
            if center_x is not None:
                state_data.last_attacking_basket_x = center_x

            if state_data.state != State.AIM:
                if state_data.last_attacking_basket_x is not None and state_data.last_attacking_basket_x < camera.camera_x/2:
                    state_data.turn_direction = 1
                else:
                    state_data.turn_direction = -1

                if state_data.opponent_basket_x is not None and state_data.opponent_basket_x > camera.camera_x/2:
                    state_data.turn_direction *= -1  # reverse direction

            controller = joy.read()

            if controller.y_btn == 1:
                state_data.state = State.MANUAL

            if controller.start == 1:
                state_data.state = State.FIND

            if controller.stop == 1:
                state_data.state = State.STOPPED

            key = cv2.waitKey(1) & 0xFF
            if key == ord('r'):
                state_data.state = State.FIND
            #print(state_data.state)
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
