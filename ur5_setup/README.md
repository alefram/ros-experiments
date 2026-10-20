# ur5_setup

Paquete de configuración para UR5 en ROS 2 Jazzy.

## Requisitos

Asegúrate de tener instalados los paquetes oficiales de UR y Gazebo:

```bash
sudo apt update
sudo apt install ros-jazzy-ur-description ros-jazzy-joint-state-publisher-gui ros-jazzy-xacro ros-jazzy-ros-gz-sim ros-jazzy-gz-ros2-control
```

## Compilación

Desde la raíz de tu workspace (p.e. `~/repos/ros_experiments`):

```bash
colcon build --packages-select ur5_setup
source install/setup.bash
```

## Uso

### Visualizar el robot en RViz

Este comando lanzará `robot_state_publisher`, `joint_state_publisher_gui` y `rviz2`.

```bash
ros2 launch ur5_setup view_ur5.launch.py
```

### Simulación en Gazebo y experimento de detachable joint

```bash
ros2 launch ur5_setup sim_ur5.launch.py                 # simulación (headless:=true sin GUI)
ros2 launch ur5_setup experiment_detachable_joint.launch.py video:=/tmp/demo.mp4
```

## Estructura
- `urdf/`: Contiene el archivo Xacro que instancia el robot UR5.
- `launch/`: Archivos de lanzamiento para visualización y simulación.
- `config/`: Configuraciones de RViz y parámetros de controladores.
