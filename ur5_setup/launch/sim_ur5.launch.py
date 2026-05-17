import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Package directories
    pkg_ur5_setup = get_package_share_directory('ur5_setup')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Path to the xacro file
    xacro_file = os.path.join(pkg_ur5_setup, 'urdf', 'ur5.urdf.xacro')

    # Robot Description
    robot_description_content = Command(['xacro ', xacro_file, ' sim_ignition:=true'])
    robot_description = {'robot_description': robot_description_content}

    # Gazebo Sim
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # Spawn Robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'ur5',
            '-topic', 'robot_description',
            '-z', '0.0'
        ],
        output='screen',
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[robot_description],
    )

    # Controllers
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
    )

    ur_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["ur_joint_trajectory_controller", "--controller-manager", "/controller_manager"],
    )

    # Bridge for Clock and Robot Description (if needed)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_robot,
        robot_state_publisher,
        bridge,
        joint_state_broadcaster_spawner,
        ur_controller_spawner,
    ])
