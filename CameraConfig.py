import pyrealsense2 as rs


def init():
    camera_x = 640
    camera_y = 480
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, camera_x, camera_y, rs.format.bgr8, 60)
    config.enable_stream(rs.stream.depth, camera_x, camera_y, rs.format.z16, 60)
    profile = pipeline.start(config)
    color_sensor = profile.get_device().query_sensors()[1]
    color_sensor.set_option(rs.option.enable_auto_exposure, False)
    color_sensor.set_option(rs.option.enable_auto_white_balance, False)
    color_sensor.set_option(rs.option.white_balance, 3500)
    color_sensor.set_option(rs.option.exposure, 50)
    return pipeline, camera_x, camera_y