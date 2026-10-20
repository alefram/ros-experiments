import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Package directories
    pkg_ur5_setup = get_package_share_directory('ur5_setup')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # Paths
    world_file = os.path.join(pkg_ur5_setup, 'worlds', 'ur5_scene.world')
    ur5_xacro_file = os.path.join(pkg_ur5_setup, 'urdf', 'ur5.urdf.xacro')
    cube_urdf_file = os.path.join(pkg_ur5_setup, 'urdf', 'cube.urdf')
    controllers_file = os.path.join(pkg_ur5_setup, 'config', 'ur_controllers.yaml')

    # Robot Description
    robot_description_content = ParameterValue(
        Command(['xacro ', ur5_xacro_file, ' sim_ignition:=true']), value_type=str)
    robot_description = {'robot_description': robot_description_content}

    # Gazebo Sim (headless:=true runs only the server, without the GUI)
    headless = LaunchConfiguration('headless')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': PythonExpression([
                "('-r -s --headless-rendering ' if '", headless, "' == 'true' else '-r ') + '", world_file, "'",
            ]),
        }.items(),
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
        parameters=[robot_description, {'use_sim_time': True}],
    )

    # Controllers
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--param-file", controllers_file,
                   "--controller-manager-timeout", "120", "--switch-timeout", "60"],
        parameters=[{'use_sim_time': True}],
    )

    ur_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["ur_joint_trajectory_controller", "--param-file", controllers_file,
                   "--controller-manager-timeout", "120", "--switch-timeout", "60"],
        parameters=[{'use_sim_time': True}],
    )

    # Bridge for Clock and Detachable Joint (suction gripper)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/ur5/detachable_joint/attach@std_msgs/msg/Empty]gz.msgs.Empty',
            '/ur5/detachable_joint/detach@std_msgs/msg/Empty]gz.msgs.Empty',
            '/ur5/detachable_joint/state@std_msgs/msg/Int32[gz.msgs.Int32',
        ],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('headless', default_value='false',
                              description='Run Gazebo server only (no GUI)'),
        gazebo,
        spawn_ur5,
        spawn_cube,
        robot_state_publisher,
        bridge,
        joint_state_broadcaster_spawner,
        ur_controller_spawner,
    ])
