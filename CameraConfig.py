import camera
import time

class Config():
    def __init__(self):
        print('opening camera')
        self.camera_x = 640
        self.camera_y = 480
        self.cam = camera.RealsenseCamera(  rgb_height=self.camera_y, 
                                            rgb_width=self.camera_x,
                                            rgb_framerate=60,
                                            depth_height=self.camera_y,
                                            depth_width=self.camera_x)
        self.cam.open()
        #return self.pipeline, self.camera_x, self.camera_y

    def StopStreams(self):
        self.cam.close()