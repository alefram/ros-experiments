import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Package directories
    pkg_ur5_setup = get_package_share_directory('ur5_setup')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Paths
    world_file = os.path.join(pkg_ur5_setup, 'worlds', 'ur5_scene.world')
    ur5_xacro_file = os.path.join(pkg_ur5_setup, 'urdf', 'ur5.urdf.xacro')
    cube_urdf_file = os.path.join(pkg_ur5_setup, 'urdf', 'cube.urdf')

    # Robot Description
    robot_description_content = Command(['xacro ', ur5_xacro_file, ' sim_ignition:=true'])
    robot_description = {'robot_description': robot_description_content}

    # Gazebo Sim
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )

    # Spawn Robot UR5 (at Z=0.5, on top of chair_1)
    spawn_ur5 = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'ur5',
            '-topic', 'robot_description',
            '-x', '0.0', '-y', '0.0', '-z', '0.5'
        ],
        output='screen',
    )

    # Spawn Cube (at X=0.8, Z=0.5, on top of chair_2)
    spawn_cube = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'blue_cube',
            '-file', cube_urdf_file,
            '-x', '0.8', '-y', '0.0', '-z', '0.5'
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
        arguments=["joint_state_broadcaster"],
    )

    ur_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["ur_joint_trajectory_controller"],
    )

    # Bridge for Clock and Detachable Joint
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/model/ur5/detachable_joint@std_msgs/msg/Bool[gz.msgs.Boolean',
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_ur5,
        spawn_cube,
        robot_state_publisher,
        bridge,
        joint_state_broadcaster_spawner,
        ur_controller_spawner,
    ])
