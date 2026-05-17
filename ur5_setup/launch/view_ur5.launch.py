import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # Get the package directory
    pkg_ur5_setup = get_package_share_directory('ur5_setup')

    # Declare arguments
    description_package = LaunchConfiguration('description_package', default='ur5_setup')
    description_file = LaunchConfiguration('description_file', default='urdf/ur5.urdf.xacro')

    # Path to the xacro file
    xacro_file = os.path.join(pkg_ur5_setup, 'urdf', 'ur5.urdf.xacro')

    # Robot State Publisher node
    # Use xacro to process the file
    robot_description_content = Command(
        ['xacro ', xacro_file]
    )
    
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[{'robot_description': robot_description_content}]
    )

    # Joint State Publisher GUI node
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    # RViz node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_ur5_setup, 'config', 'view_robot.rviz')]
    )

    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])
