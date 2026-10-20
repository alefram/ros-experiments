#!/usr/bin/env python3
"""Write the frames of a sensor_msgs/Image topic to a video file (one frame per image)."""
import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class Recorder(Node):
    def __init__(self):
        super().__init__('record_camera')
        self.declare_parameter('topic', '/video_cam/image')
        self.declare_parameter('output', '/tmp/experiment.mp4')
        self.declare_parameter('fps', 30.0)
        self.bridge = CvBridge()
        self.writer = None
        self.frames = 0
        self.create_subscription(
            Image, self.get_parameter('topic').value, self.on_image, 10)

    def on_image(self, msg):
        frame = cv2.cvtColor(self.bridge.imgmsg_to_cv2(msg, 'rgb8'), cv2.COLOR_RGB2BGR)
        if self.writer is None:
            h, w = frame.shape[:2]
            self.writer = cv2.VideoWriter(
                self.get_parameter('output').value, cv2.VideoWriter_fourcc(*'mp4v'),
                self.get_parameter('fps').value, (w, h))
        self.writer.write(frame)
        self.frames += 1

    def close(self):
        if self.writer is not None:
            self.writer.release()
        self.get_logger().info(f'Saved {self.frames} frames')


def main():
    rclpy.init()
    node = Recorder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
