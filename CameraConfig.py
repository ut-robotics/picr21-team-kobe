import pyrealsense2 as rs


def init():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    profile = pipeline.start(config)
    color_sensor = profile.get_device().query_sensors()[1]
    color_sensor.set_option(rs.option.enable_auto_exposure, False)
    color_sensor.set_option(rs.option.enable_auto_white_balance, False)
    color_sensor.set_option(rs.option.white_balance, 3500)
    color_sensor.set_option(rs.option.exposure, 50)
    return pipeline