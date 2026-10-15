#!/usr/bin/env python3
"""Pick & drop experiment with the Gazebo DetachableJoint (suction gripper emulation).

Sequence: move above the cube -> touch it -> ATTACH -> lift -> carry -> DETACH (cube drops).
Waypoints are joint-space solutions (tool pointing down) of the TCP targets listed below,
expressed in the robot base frame (the cube top is at z=0.10 m).
"""
import time

import rclpy
from control_msgs.action import FollowJointTrajectory
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import Empty, Int32
from trajectory_msgs.msg import JointTrajectoryPoint

JOINTS = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
          'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']

HOME = [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]
PRE_GRASP = [-0.137, -0.027, -0.774, -0.770, -1.571, -0.456]   # TCP (0.80, 0.00, 0.25)
GRASP = [-0.137, 0.254, -1.006, -0.819, -1.571, -1.041]        # TCP (0.80, 0.00, 0.118)
LIFT = [-0.137, -0.321, -0.400, -0.850, -1.571, -0.282]        # TCP (0.80, 0.00, 0.35)
CARRY = [0.570, -0.068, -1.124, -0.379, -1.571, -0.615]        # TCP (0.50, 0.45, 0.35)


class DetachableJointDemo(Node):
    def __init__(self):
        super().__init__('detachable_joint_demo')
        self.client = ActionClient(
            self, FollowJointTrajectory,
            '/ur_joint_trajectory_controller/follow_joint_trajectory')
        self.attach_pub = self.create_publisher(Empty, '/ur5/detachable_joint/attach', 10)
        self.detach_pub = self.create_publisher(Empty, '/ur5/detachable_joint/detach', 10)
        self.joint_state = None
        self.create_subscription(Int32, '/ur5/detachable_joint/state', self._on_state, 10)

    def _on_state(self, msg):
        self.get_logger().info(f'detachable joint state: {msg.data}')

    def sleep(self, seconds):
        """Sleep in *simulation* time."""
        end = self.get_clock().now().nanoseconds + int(seconds * 1e9)
        while rclpy.ok() and self.get_clock().now().nanoseconds < end:
            rclpy.spin_once(self, timeout_sec=0.05)

    def move(self, positions, seconds):
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINTS
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start.sec = int(seconds)
        point.time_from_start.nanosec = int((seconds % 1) * 1e9)
        goal.trajectory.points = [point]
        future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        result_future = future.result().get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        return result_future.result().result.error_code

    def run(self):
        self.get_logger().info('Waiting for the trajectory controller...')
        self.client.wait_for_server()
        # Wait for the simulation clock and for the bridge to be connected
        while rclpy.ok() and self.get_clock().now().nanoseconds == 0:
            rclpy.spin_once(self, timeout_sec=0.1)
        self.sleep(1.0)

        # DetachableJoint welds the cube to the cup as soon as the plugin loads, so release it
        # first (the arm has not moved yet). The command is repeated until the bridge is up.
        self.get_logger().info('DETACH (start from a free cube)')
        for _ in range(3):
            self.detach_pub.publish(Empty())
            self.sleep(0.5)
        self.sleep(1.0)

        steps = [
            ('home', HOME, 3.0), ('pre-grasp (above the cube)', PRE_GRASP, 4.0),
            ('grasp (touch the cube)', GRASP, 3.0)]
        for name, q, t in steps:
            self.get_logger().info(f'Moving to {name}')
            self.move(q, t)
        self.sleep(1.0)

        self.get_logger().info('ATTACH (suction on)')
        self.attach_pub.publish(Empty())
        self.sleep(1.0)

        for name, q, t in [('lift', LIFT, 3.0), ('carry', CARRY, 4.0)]:
            self.get_logger().info(f'Moving to {name}')
            self.move(q, t)
        self.sleep(1.0)

        self.get_logger().info('DETACH (suction off) - the cube drops')
        self.detach_pub.publish(Empty())
        self.sleep(3.0)

        self.get_logger().info('Returning home')
        self.move(HOME, 4.0)
        self.sleep(1.0)
        self.get_logger().info('Experiment finished')


def main():
    rclpy.init()
    node = DetachableJointDemo()
    node.set_parameters([rclpy.parameter.Parameter('use_sim_time', value=True)])
    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
