import cv2
from movement import *

cv2.namedWindow("Controller")

while(True):
    key = cv2.waitKey(1) & 0xFF

    if key == ord("w"):
        move_in_direction(10, 90)
    if key == ord("d"):
        move_in_direction(10, 180)
    if key == ord("s"):
        move_in_direction(10, 270)
    if key == ord("a"):
        move_in_direction(10, 0)
    if key == ord("e"):
        turn_right(10)
    if key == ord("q"):
        turn_left(-10)
    if key == ord("c"):
        stop()
        break