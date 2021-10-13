import numpy as np
import cv2
import pyrealsense2 as rs

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
pipeline.start(config)

point = [320, 240]

while (True):
    frames = pipeline.wait_for_frames()
    aligned_frames = rs.align(rs.stream.color).process(frames)
    color_frame = aligned_frames.get_color_frame()
    color = np.asanyarray(color_frame.get_data())
    depth_frame = aligned_frames.get_depth_frame()
    depth = np.asanyarray(depth_frame.get_data())

    colorizer = rs.colorizer()
    colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())
    cv2.circle(colorized_depth, point, 10, (0, 0, 255))

    dist = depth_frame.get_distance(point[0], point[1])
    print(dist)

    cv2.imshow("Color", color)
    cv2.imshow("Depth", colorized_depth)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        pipeline.stop()
        break

cv2.destroyAllWindows()

