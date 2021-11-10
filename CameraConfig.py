import pyrealsense2 as rs

class Config():
    def __init__(self):
        self.camera_x = 640
        self.camera_y = 480
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, self.camera_x, self.camera_y, rs.format.bgr8, 60)
        self.config.enable_stream(rs.stream.depth, self.camera_x, self.camera_y, rs.format.z16, 60)
        self.profile = self.pipeline.start(self.config)
        self.color_sensor = self.profile.get_device().query_sensors()[1]
        self.color_sensor.set_option(rs.option.enable_auto_exposure, False)
        self.color_sensor.set_option(rs.option.enable_auto_white_balance, False)
        self.color_sensor.set_option(rs.option.white_balance, 3500)
        self.color_sensor.set_option(rs.option.exposure, 50)
        #return self.pipeline, self.camera_x, self.camera_y

    def StopStreams(self):
        self.config.disable_all_streams(self)