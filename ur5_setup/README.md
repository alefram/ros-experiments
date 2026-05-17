# ur5_setup

Paquete de configuración para UR5 en ROS 2 Humble.

## Requisitos

Asegúrate de tener instalados los paquetes oficiales de UR y MoveIt 2:

```bash
sudo apt update
sudo apt install ros-humble-ur-description ros-humble-ur-moveit-config ros-humble-joint-state-publisher-gui ros-humble-xacro
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

## Estructura
- `urdf/`: Contiene el archivo Xacro que instancia el robot UR5.
- `launch/`: Archivos de lanzamiento para visualización y simulación.
- `config/`: Configuraciones de RViz y parámetros de controladores.
