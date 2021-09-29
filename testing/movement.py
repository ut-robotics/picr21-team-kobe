import math
from serialConnector import SerialConnectorClass

wheelAngle1 = 0
wheelAngle2 = 120
wheelAngle3 = 240

ser = SerialConnectorClass().start()

def calc_wheel_speed(moving_speed, direction, wheel_angle):
    wheel_speed = moving_speed * math.cos(math.radians(direction - wheel_angle))
    return wheel_speed

def omni_move(moving_speed, direction):
    wheel_speeds = [0, 0, 0]
    wheel_speeds[0] = int(calc_wheel_speed(moving_speed, direction, wheelAngle1))
    wheel_speeds[1] = int(calc_wheel_speed(moving_speed, direction, wheelAngle2))
    wheel_speeds[2] = - int(calc_wheel_speed(moving_speed, direction, wheelAngle3))
    return wheel_speeds

def set_speeds(wheel_speeds):
    ser.write_speeds("sd:" + str(wheel_speeds[0]) + ":" + str(wheel_speeds[1]) + ":" + str(wheel_speeds[2]) + "\r\n")

def move_in_direction(moving_speed, direction):
    wheel_speeds = omni_move(moving_speed, direction)
    set_speeds(wheel_speeds)

def turn_left(turn_speed):
    wheel_speeds = [turn_speed, turn_speed, turn_speed]
    set_speeds(wheel_speeds)

def turn_right(turn_speed):
    wheel_speeds = [-turn_speed, -turn_speed, -turn_speed]
    set_speeds(wheel_speeds)

def stop():
    wheel_speeds = [0, 0, 0]
    set_speeds(wheel_speeds)

def shutdown():
    stop()
    ser.close_connection()

def pid(kp, ki, kd, target, position, error_prev, integral_prev, t_prev, t):
    error = target - position
    proportional = kp * error
    integral = integral_prev + ki * error * (t - t_prev)
    derivative = kd * (error - error_prev) / (t - t_prev)
    return int(proportional + integral + derivative), error