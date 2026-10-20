FROM ros:jazzy-ros-base

# Instalar herramientas básicas y dependencias de simulación para Jazzy
RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    ros-jazzy-ur-description \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-gz-ros2-control \
    ros-jazzy-controller-manager \
    ros-jazzy-control-msgs \
    ros-jazzy-joint-trajectory-controller \
    ros-jazzy-joint-state-broadcaster \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-xacro \
    ros-jazzy-cv-bridge \
    python3-opencv \
    ros-jazzy-rviz2 \
    ros-jazzy-joint-state-publisher-gui \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Configurar el workspace
WORKDIR /ros2_ws
RUN mkdir src

# Source del entrypoint de ROS
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
