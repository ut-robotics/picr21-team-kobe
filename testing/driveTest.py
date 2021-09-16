import cv2
from movement import *

cv2.namedWindow("Controller")

while(True):
    key = cv2.waitKey(1) & 0xFF

    if key == ord("w"):
        print("Key w was pressed. Moving forward.")
        move_in_direction(10, 90)
    if key == ord("d"):
        print("Key d was pressed. Moving right.")
        move_in_direction(10, 180)
    if key == ord("s"):
        print("Key s was pressed. Moving backwards.")
        move_in_direction(10, 270)
    if key == ord("a"):
        print("Key a was pressed. Moving left.")
        move_in_direction(10, 0)
    if key == ord("e"):
        print("Key e was pressed. Turning right.")
        turn_right(10)
    if key == ord("q"):
        print("Key q was pressed. Turning left.")
        turn_left(10)
    if key == ord("c"):
        print("Key c was pressed. Stopping.")
        stop()
    if key == ord("x"):
        print("Key x was pressed. Shutting down.")
        shutdown()
        break