import math
import cv2
import camera_config
import image_processing as ip
import movement

#processor = ip.ProcessFrames(False)
camera = camera_config.Config()


def keyboard_control():
    cv2.namedWindow("Controller")
    # print("distance", basket_distance*100)
    moving_speed = 15
    throwing_speed = 1100
    while True:
        #count, y, x, center_x, center_y, basket_distance, floor_area = processor.ProcessFrame(camera.pipeline,
                                                                                              #camera.camera_x,
                                                                                              #camera.camera_y)
        #print("distance", basket_distance * 100)
        #move(0, throwing_speed, 0)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("w"):
            print("Moving forward.")
            movement.move_omni(0, moving_speed, 0,0)
        if key == ord("d"):
            print("Moving right.")
            movement.move_omni(moving_speed, 0, 0,0)
        if key == ord("s"):
            print("Moving backwards.")
            movement.move_omni(0, -moving_speed, 0,0)
        if key == ord("a"):
            print("Moving left.")
            movement.move_omni(-moving_speed, 0, 0,0)
        if key == ord("e"):
            print("Spinning right.")
            movement.move_omni(0, 0, moving_speed,0)
        if key == ord("q"):
            print("Spinning left.")
            movement.move_omni(0, 0, -moving_speed,0)
        if key == ord("t"):
            print("Throwing.")
            movement.move_omni(0, 0, 0,throwing_speed)
        if key == ord("c"):
            print("Stopping.")
            movement.stop()
        if key == ord("x"):
            print("Shutting down.")
            movement.stop()
            break


keyboard_control()

cv2.destroyAllWindows()