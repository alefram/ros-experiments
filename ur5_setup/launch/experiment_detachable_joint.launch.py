import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, EmitEvent, IncludeLaunchDescription,
                            RegisterEventHandler, TimerAction)
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('ur5_setup')
    camera_sdf = os.path.join(pkg, 'worlds', 'video_camera.sdf')

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg, 'launch', 'sim_ur5.launch.py')),
        launch_arguments={'headless': LaunchConfiguration('headless')}.items(),
    )

    spawn_camera = Node(
        package='ros_gz_sim', executable='create',
        # Looks from (1.7, 1.7, 1.5) towards (0.5, 0.1, 0.45)
        arguments=['-name', 'video_camera', '-file', camera_sdf,
                   '-x', '1.7', '-y', '1.7', '-z', '1.5', '-P', '0.48', '-Y', '-2.21'],
        output='screen',
    )

    camera_bridge = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        arguments=['/video_cam/image@sensor_msgs/msg/Image[gz.msgs.Image'],
        output='screen',
    )

    recorder = Node(
        package='ur5_setup', executable='record_camera.py', output='screen',
        parameters=[{'output': LaunchConfiguration('video'), 'use_sim_time': True}],
    )

    demo = Node(
        package='ur5_setup', executable='detachable_joint_demo.py', output='screen',
    )

    # Stop everything (and flush the video) when the experiment finishes
    stop_on_exit = RegisterEventHandler(OnProcessExit(
        target_action=demo, on_exit=[
            TimerAction(period=2.0, actions=[EmitEvent(event=Shutdown())])]))

    return LaunchDescription([
        DeclareLaunchArgument('headless', default_value='true',
                              description='Run Gazebo server only (no GUI)'),
        DeclareLaunchArgument('video', default_value='/tmp/detachable_joint.mp4',
                              description='Output video file'),
        sim, spawn_camera, camera_bridge, recorder, demo, stop_on_exit,
    ])
