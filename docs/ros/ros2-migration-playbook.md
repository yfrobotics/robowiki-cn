# ROS 2 迁移手册

!!! note "引言"
    随着 ROS 1 Noetic 于 2025 年 5 月终止支持，将现有项目从 ROS 1 迁移到 ROS 2 已成为必要任务。本文提供系统性的迁移指南，涵盖 API 变化、构建系统切换、Launch 文件改写、渐进式迁移策略以及常见陷阱，帮助团队平稳过渡到 ROS 2。


## API 变化总览

### 核心 API 对比

| 功能 | ROS 1 (roscpp) | ROS 2 (rclcpp) |
|------|----------------|-----------------|
| 初始化 | `ros::init(argc, argv, "node")` | `rclcpp::init(argc, argv)` |
| 创建节点 | `ros::NodeHandle nh` | `auto node = std::make_shared<rclcpp::Node>("node")` |
| 发布者 | `nh.advertise<Msg>("topic", 10)` | `node->create_publisher<Msg>("topic", 10)` |
| 订阅者 | `nh.subscribe("topic", 10, cb)` | `node->create_subscription<Msg>("topic", 10, cb)` |
| 服务端 | `nh.advertiseService("srv", cb)` | `node->create_service<Srv>("srv", cb)` |
| 客户端 | `nh.serviceClient<Srv>("srv")` | `node->create_client<Srv>("srv")` |
| 定时器 | `nh.createTimer(dur, cb)` | `node->create_wall_timer(dur, cb)` |
| 参数 | `nh.getParam("key", val)` | `node->declare_parameter("key", default)` |
| 日志 | `ROS_INFO("msg")` | `RCLCPP_INFO(node->get_logger(), "msg")` |
| 循环 | `ros::spin()` | `rclcpp::spin(node)` |
| 频率控制 | `ros::Rate rate(10)` | `rclcpp::Rate rate(10)` |


### Python API 对比

| 功能 | ROS 1 (rospy) | ROS 2 (rclpy) |
|------|---------------|----------------|
| 初始化 | `rospy.init_node("node")` | `rclpy.init()` |
| 创建节点 | 隐式（init_node 时创建） | `node = Node("node")` 或继承 `Node` |
| 发布者 | `rospy.Publisher("topic", Msg, queue_size=10)` | `node.create_publisher(Msg, "topic", 10)` |
| 订阅者 | `rospy.Subscriber("topic", Msg, cb)` | `node.create_subscription(Msg, "topic", cb, 10)` |
| 日志 | `rospy.loginfo("msg")` | `node.get_logger().info("msg")` |
| 循环 | `rospy.spin()` | `rclpy.spin(node)` |
| 时间 | `rospy.Time.now()` | `node.get_clock().now()` |
| 休眠 | `rospy.sleep(1.0)` | `time.sleep(1.0)` 或定时器 |


### 代码迁移示例

**ROS 1 节点：**

```python
#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist

def main():
    rospy.init_node('velocity_publisher')
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        msg = Twist()
        msg.linear.x = 0.5
        msg.angular.z = 0.3
        pub.publish(msg)
        rospy.loginfo("发布速度命令")
        rate.sleep()

if __name__ == '__main__':
    main()
```

**迁移后的 ROS 2 节点：**

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class VelocityPublisher(Node):
    def __init__(self):
        super().__init__('velocity_publisher')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10 Hz

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 0.5
        msg.angular.z = 0.3
        self.pub.publish(msg)
        self.get_logger().info("发布速度命令")

def main():
    rclpy.init()
    node = VelocityPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

关键变化：

- ROS 2 推荐使用面向对象的节点类（继承 `Node`）
- 循环逻辑由定时器 (`create_timer`) 代替 `Rate` + `while` 循环
- 必须显式调用 `destroy_node()` 和 `rclpy.shutdown()`


## 构建系统：从 catkin 到 ament

### 构建系统对比

| 方面 | catkin (ROS 1) | ament (ROS 2) |
|------|---------------|----------------|
| 基础 | CMake 封装 | CMake 或纯 Python |
| 工作空间工具 | `catkin_make` / `catkin build` | `colcon build` |
| 包配置 | `package.xml` + `CMakeLists.txt` | `package.xml` + `CMakeLists.txt`（或 `setup.py`） |
| 环境激活 | `source devel/setup.bash` | `source install/setup.bash` |
| Python 包 | CMake 处理 | `ament_python`（纯 Python 构建） |


### CMakeLists.txt 迁移

**ROS 1 (catkin)：**

```cmake
cmake_minimum_required(VERSION 3.0.2)
project(my_robot_pkg)

find_package(catkin REQUIRED COMPONENTS
  roscpp std_msgs sensor_msgs message_generation
)

add_message_files(FILES RobotStatus.msg)
generate_messages(DEPENDENCIES std_msgs)

catkin_package(
  CATKIN_DEPENDS roscpp std_msgs message_runtime
)

include_directories(${catkin_INCLUDE_DIRS})

add_executable(robot_node src/robot_node.cpp)
target_link_libraries(robot_node ${catkin_LIBRARIES})
```

**ROS 2 (ament_cmake)：**

```cmake
cmake_minimum_required(VERSION 3.8)
project(my_robot_pkg)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# 消息生成
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/RobotStatus.msg"
  DEPENDENCIES std_msgs
)

add_executable(robot_node src/robot_node.cpp)
ament_target_dependencies(robot_node rclcpp std_msgs sensor_msgs)

install(TARGETS robot_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
```

关键变化：

- `find_package(catkin ...)` 拆分为多个独立的 `find_package` 调用
- `catkin_package` 变为 `ament_package()`（必须放在文件末尾）
- `target_link_libraries` 推荐改为 `ament_target_dependencies`
- 消息生成使用 `rosidl_generate_interfaces`
- 必须显式添加 `install` 规则


### Python 包迁移

ROS 2 的纯 Python 包使用 `ament_python` 构建系统，不再需要 CMakeLists.txt：

```
my_python_pkg/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
│   └── my_python_pkg    # 空文件，用于包索引
└── my_python_pkg/
    ├── __init__.py
    └── velocity_publisher.py
```

```python
# setup.py
from setuptools import setup

package_name = 'my_python_pkg'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
            'velocity_pub = my_python_pkg.velocity_publisher:main',
        ],
    },
)
```

```ini
# setup.cfg
[develop]
script_dir=$base/lib/my_python_pkg
[install]
install_scripts=$base/lib/my_python_pkg
```


### colcon 构建工具

```bash
# 编译整个工作空间
cd ~/ros2_ws
colcon build

# 仅编译指定包
colcon build --packages-select my_robot_pkg

# 编译指定包及其依赖
colcon build --packages-up-to my_robot_pkg

# 使用符号链接（Python 包修改后无需重新编译）
colcon build --symlink-install

# Release 编译
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

# 激活工作空间
source install/setup.bash
```


## Launch 文件迁移

ROS 2 的 Launch 系统支持 Python（推荐）和 XML 两种格式。Python 格式提供了更强的逻辑控制能力。


### XML 到 Python 迁移示例

**ROS 1 (XML)：**

```xml
<launch>
  <arg name="use_sim" default="true"/>
  <arg name="robot_name" default="my_robot"/>

  <param name="robot_description"
         command="$(find xacro)/xacro
                  $(find my_robot_description)/urdf/robot.urdf.xacro"/>

  <node pkg="robot_state_publisher" type="robot_state_publisher"
        name="robot_state_publisher" output="screen"/>

  <group if="$(arg use_sim)">
    <include file="$(find gazebo_ros)/launch/empty_world.launch"/>
  </group>

  <node pkg="my_robot_pkg" type="controller_node" name="controller"
        output="screen">
    <param name="max_speed" value="1.5"/>
    <remap from="cmd_vel" to="$(arg robot_name)/cmd_vel"/>
  </node>
</launch>
```

**ROS 2 (Python)：**

```python
# launch/robot_launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, Command, FindExecutable
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # 声明参数
    use_sim_arg = DeclareLaunchArgument(
        'use_sim', default_value='true')
    robot_name_arg = DeclareLaunchArgument(
        'robot_name', default_value='my_robot')

    # 获取包路径
    pkg_dir = get_package_share_directory('my_robot_description')

    # 生成 URDF
    robot_description = Command([
        FindExecutable(name='xacro'), ' ',
        os.path.join(pkg_dir, 'urdf', 'robot.urdf.xacro')
    ])

    # robot_state_publisher 节点
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    # 控制器节点
    controller_node = Node(
        package='my_robot_pkg',
        executable='controller_node',
        name='controller',
        output='screen',
        parameters=[{'max_speed': 1.5}],
        remappings=[
            ('cmd_vel',
             [LaunchConfiguration('robot_name'), '/cmd_vel'])
        ]
    )

    return LaunchDescription([
        use_sim_arg,
        robot_name_arg,
        rsp_node,
        controller_node,
    ])
```


### Launch 文件关键变化对照

| ROS 1 XML | ROS 2 Python |
|-----------|--------------|
| `<arg name="x" default="v"/>` | `DeclareLaunchArgument('x', default_value='v')` |
| `$(arg x)` | `LaunchConfiguration('x')` |
| `$(find pkg)` | `get_package_share_directory('pkg')` |
| `<node pkg="..." type="..." name="..."/>` | `Node(package='...', executable='...', name='...')` |
| `<param name="k" value="v"/>` | `parameters=[{'k': 'v'}]` |
| `<remap from="a" to="b"/>` | `remappings=[('a', 'b')]` |
| `<include file="..."/>` | `IncludeLaunchDescription(...)` |
| `<group if="$(arg x)">` | `condition=IfCondition(LaunchConfiguration('x'))` |


## ros1_bridge：渐进式迁移

`ros1_bridge` 是 ROS 2 官方提供的桥接包，可以在 ROS 1 和 ROS 2 之间转发话题和服务，实现渐进式迁移。


### 安装与使用

```bash
# 安装 ros1_bridge（需要同时安装 ROS 1 和 ROS 2）
sudo apt install ros-humble-ros1-bridge

# 终端 1：启动 ROS 1
source /opt/ros/noetic/setup.bash
roscore

# 终端 2：启动桥接
source /opt/ros/noetic/setup.bash
source /opt/ros/humble/setup.bash
ros2 run ros1_bridge dynamic_bridge

# 终端 3：ROS 1 发布者
source /opt/ros/noetic/setup.bash
rostopic pub /chatter std_msgs/String "data: 'hello from ROS 1'"

# 终端 4：ROS 2 订阅者
source /opt/ros/humble/setup.bash
ros2 topic echo /chatter std_msgs/msg/String
```


### 桥接模式

| 模式 | 命令 | 说明 |
|------|------|------|
| 动态桥接 | `ros2 run ros1_bridge dynamic_bridge` | 自动桥接所有匹配的话题和服务 |
| 参数桥接 | `ros2 run ros1_bridge parameter_bridge` | 通过参数文件指定桥接规则 |
| 静态桥接 | 自定义编译 | 仅桥接指定的话题和服务类型 |

对于自定义消息类型，需要在 ROS 1 和 ROS 2 两侧都有对应的消息定义，并从源码编译 `ros1_bridge`。


## 消息迁移

### 消息包名变化

ROS 2 中消息类型的导入路径发生了变化：

| ROS 1 | ROS 2 |
|-------|-------|
| `std_msgs/String` | `std_msgs/msg/String` |
| `geometry_msgs/Twist` | `geometry_msgs/msg/Twist` |
| `sensor_msgs/Image` | `sensor_msgs/msg/Image` |

Python 导入语法保持不变：

```python
# ROS 1 和 ROS 2 相同
from std_msgs.msg import String
```

C++ 头文件变化：

```cpp
// ROS 1
#include <std_msgs/String.h>

// ROS 2
#include <std_msgs/msg/string.hpp>
```


### 自定义消息迁移

ROS 2 中消息文件的语法基本保持不变，但构建配置不同：

```xml
<!-- package.xml 中的依赖声明 -->
<!-- ROS 1 -->
<build_depend>message_generation</build_depend>
<exec_depend>message_runtime</exec_depend>

<!-- ROS 2 -->
<build_depend>rosidl_default_generators</build_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```


## 常见迁移陷阱

### 1. 回调函数签名变化

```cpp
// ROS 1：使用 ConstPtr
void callback(const std_msgs::String::ConstPtr &msg) {
    ROS_INFO("%s", msg->data.c_str());
}

// ROS 2：使用 SharedPtr
void callback(const std_msgs::msg::String::SharedPtr msg) {
    RCLCPP_INFO(this->get_logger(), "%s", msg->data.c_str());
}
```


### 2. 时间 API 变化

```python
# ROS 1
now = rospy.Time.now()
duration = rospy.Duration(1.0)
rospy.sleep(1.0)

# ROS 2
now = self.get_clock().now()
duration = rclpy.duration.Duration(seconds=1.0)
# 不再有 rospy.sleep()，使用定时器或 time.sleep()
```


### 3. 参数声明变化

ROS 2 要求参数必须先声明后使用：

```python
# ROS 1：直接获取
speed = rospy.get_param('~max_speed', 1.0)

# ROS 2：先声明，再获取
self.declare_parameter('max_speed', 1.0)
speed = self.get_parameter('max_speed').value
```


### 4. 命名空间差异

```python
# ROS 1 私有参数使用 ~
rospy.get_param('~param')

# ROS 2 没有 ~ 语法，改用节点名前缀或参数文件
self.declare_parameter('param', default_value)
```


### 5. 头文件命名规范

```cpp
// ROS 1：CamelCase.h
#include <geometry_msgs/PoseStamped.h>

// ROS 2：snake_case.hpp，多一层 msg/ 目录
#include <geometry_msgs/msg/pose_stamped.hpp>
```


## 逐包迁移策略

推荐的迁移顺序：

```
阶段 1：迁移消息包（_msgs）
    ↓
阶段 2：迁移工具库（无 ROS 依赖的纯算法库）
    ↓
阶段 3：迁移叶子节点（依赖最少的包）
    ↓
阶段 4：使用 ros1_bridge 集成测试
    ↓
阶段 5：迁移核心节点
    ↓
阶段 6：迁移 launch 和配置
    ↓
阶段 7：移除 ros1_bridge，全面切换
```


### 每个包的迁移检查清单

- 更新 `package.xml`：修改 `buildtool_depend` 为 `ament_cmake` 或 `ament_python`
- 更新 `CMakeLists.txt`：替换 catkin 宏为 ament 宏
- 修改源码：更新头文件、API 调用、回调签名
- 迁移 launch 文件：XML 改写为 Python
- 迁移参数文件：确认 YAML 格式兼容
- 更新 QoS 配置：为每个话题选择合适的 QoS 策略
- 编写测试：使用 `ament_cmake_gtest` 或 `pytest`
- 验证功能：通过 `ros1_bridge` 与未迁移部分集成测试


## 测试策略

### 单元测试

```python
# test/test_velocity_publisher.py
import pytest
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from my_robot_pkg.velocity_publisher import VelocityPublisher

@pytest.fixture
def node():
    rclpy.init()
    n = VelocityPublisher()
    yield n
    n.destroy_node()
    rclpy.shutdown()

def test_publisher_created(node):
    assert node.pub is not None
    assert node.pub.topic_name == '/cmd_vel'
```


### 集成测试

```python
# test/test_integration.py
import unittest
import launch
import launch_ros
import launch_testing
import rclpy
from geometry_msgs.msg import Twist

@launch_testing.post_shutdown_test()
class TestProcessOutput(unittest.TestCase):
    def test_exit_code(self, proc_info):
        launch_testing.asserts.assertExitCodes(proc_info)
```


### CMakeLists.txt 测试配置

```cmake
if(BUILD_TESTING)
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_velocity
    test/test_velocity_publisher.py
    TIMEOUT 30
  )
endif()
```


## 参考资料

- [ROS 2 迁移指南](https://docs.ros.org/en/rolling/How-To-Guides/Migrating-from-ROS1.html)
- [ros1_bridge 使用文档](https://github.com/ros2/ros1_bridge)
- [ament_cmake 用户指南](https://docs.ros.org/en/rolling/How-To-Guides/Ament-CMake-Documentation.html)
- [ROS 2 Launch 文档](https://docs.ros.org/en/rolling/Tutorials/Intermediate/Launch/Launch-Main.html)
- [从 catkin 迁移到 ament](https://docs.ros.org/en/rolling/How-To-Guides/Migrating-from-ROS1/Migrating-CMake.html)
- [ROS 2 Python 包创建](https://docs.ros.org/en/rolling/Tutorials/Beginner-Client-Libraries/Creating-Your-First-ROS2-Package.html)
