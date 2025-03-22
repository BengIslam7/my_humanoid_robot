import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration

from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription , ExecuteProcess,TimerAction
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution, TextSubstitution

import xacro

def generate_launch_description():

    # Process the URDF file
    pkg_path = os.path.join(get_package_share_directory('diffdrive_arduino'))
    xacro_file = os.path.join(pkg_path, 'description', 'robot.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)

    # Create a robot_state_publisher node
    params = {'robot_description': robot_description_config.toxml()}
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[params]
    )

    controller_params_file = os.path.join(get_package_share_directory('diffdrive_arduino'),'config','my_controllers.yaml')

    twist_mux_params = os.path.join(get_package_share_directory('diffdrive_arduino'),'config','twist_mux.yaml')
    twist_mux = Node(
            package="twist_mux",
            executable="twist_mux",
            parameters=[twist_mux_params, {'use_sim_time': False}],
            remappings=[('/cmd_vel_out','/diff_cont/cmd_vel_unstamped')]
        )


    controller_manager = TimerAction(
        period=6.0,
        actions = [
            Node(
                package="controller_manager",
                executable="ros2_control_node",
                parameters=[params,controller_params_file]
            )
        ]
    )

    joint_state_broadcaster = TimerAction(
        period=8.0,  
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                output='screen',
                arguments=["joint_broad"]
            )
        ]
    )

    diff_drive_controller = TimerAction(
        period=10.0, 
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                output='screen',
                arguments=["diff_cont"]
            )
        ]
    )

    forward_velocity_controller = TimerAction(
        period=14.0, 
        actions=[
            Node(
                package='controller_manager',
                executable='spawner',
                output='screen',
                arguments=["forward_velocity_controller"]
            )
        ]
    )

    control=Node(package='diffdrive_arduino',executable='control_bridge_node',name='control_bridge',output='screen')
    
    # Launch!
    return LaunchDescription([
        controller_manager,
        node_robot_state_publisher,
        diff_drive_controller,
        joint_state_broadcaster,
        twist_mux,
        forward_velocity_controller,
        control
    ])

