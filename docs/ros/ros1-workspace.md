# ROS 1 工作空间

!!! note "引言"
    catkin 工作空间 (workspace) 是 ROS 1 中组织、编译和管理软件包的核心机制。理解工作空间的结构和使用方法，是高效进行 ROS 1 开发的基础。本文详细介绍工作空间的创建、软件包的构建配置、编译工具的选择以及多工作空间叠加等实用技巧。


## 工作空间结构

一个标准的 catkin 工作空间由四个目录组成：

```
catkin_ws/
├── src/          # 源代码空间：存放所有 ROS 软件包的源码
│   └── CMakeLists.txt  # 顶层 CMakeLists（由 catkin_init_workspace 生成）
├── build/        # 编译空间：CMake 和 Make 的中间文件
├── devel/        # 开发空间：编译产物（可执行文件、库、脚本等）
└── logs/         # 日志空间（仅 catkin_tools 生成）
```

| 目录 | 用途 | 是否纳入版本控制 |
|------|------|------------------|
| `src/` | 存放软件包源代码 | 是 |
| `build/` | CMake 编译中间文件 | 否 |
| `devel/` | 编译生成的可执行文件和库 | 否 |
| `install/` | 安装后的文件（可选） | 否 |
| `logs/` | 编译日志 | 否 |


### 创建工作空间

使用以下命令创建并初始化一个 catkin 工作空间：

```bash
# 创建目录
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src

# 初始化工作空间（在 src 目录下生成顶层 CMakeLists.txt）
catkin_init_workspace

# 回到工作空间根目录进行首次编译
cd ~/catkin_ws
catkin_make

# 激活工作空间环境
source devel/setup.bash
```

激活工作空间后，可以使用 `echo $ROS_PACKAGE_PATH` 验证当前工作空间是否已被识别。输出应包含 `~/catkin_ws/src` 路径。

建议在 `~/.bashrc` 中添加 `source` 命令，以便每次打开终端时自动激活：

```bash
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
```


## 创建软件包

### catkin_create_pkg

`catkin_create_pkg` 是 ROS 1 提供的软件包生成工具，它会自动创建标准目录结构和配置文件。

```bash
cd ~/catkin_ws/src

# 语法：catkin_create_pkg <包名> [依赖1] [依赖2] ...
catkin_create_pkg my_robot_pkg std_msgs rospy roscpp sensor_msgs
```

执行后生成的目录结构如下：

```
my_robot_pkg/
├── CMakeLists.txt    # 编译配置
├── package.xml       # 包元数据和依赖声明
├── include/
│   └── my_robot_pkg/ # C++ 头文件目录
└── src/              # C++ 源文件目录
```

对于 Python 包，通常还需要手动创建以下目录：

```bash
mkdir -p my_robot_pkg/scripts    # Python 可执行脚本
mkdir -p my_robot_pkg/launch     # launch 文件
mkdir -p my_robot_pkg/msg        # 自定义消息
mkdir -p my_robot_pkg/srv        # 自定义服务
mkdir -p my_robot_pkg/config     # 参数配置文件（YAML）
```


### 软件包命名规范

ROS 社区推荐的包命名规范：

- 使用小写字母和下划线（如 `my_robot_driver`）
- 名称应具有描述性，避免过于通用（如 `utils`）
- 功能包 (metapackage) 通常以项目名为前缀（如 `turtlebot3_navigation`）
- 消息包通常以 `_msgs` 结尾（如 `my_robot_msgs`）


## CMakeLists.txt 详解

`CMakeLists.txt` 是 catkin 包的编译配置文件，定义了如何编译源代码、链接库和安装目标。以下是一个完整示例：

```cmake
cmake_minimum_required(VERSION 3.0.2)
project(my_robot_pkg)

## 查找 catkin 和依赖包
find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  sensor_msgs
  message_generation  # 如果使用自定义消息/服务
)

## 声明自定义消息文件
add_message_files(
  FILES
  RobotStatus.msg
)

## 声明自定义服务文件
add_service_files(
  FILES
  GetPose.srv
)

## 生成消息和服务的代码
generate_messages(
  DEPENDENCIES
  std_msgs
  sensor_msgs
)

## catkin 包声明
catkin_package(
  INCLUDE_DIRS include
  LIBRARIES my_robot_lib
  CATKIN_DEPENDS roscpp rospy std_msgs sensor_msgs message_runtime
)

## 头文件路径
include_directories(
  include
  ${catkin_INCLUDE_DIRS}
)

## 编译 C++ 库
add_library(my_robot_lib
  src/robot_controller.cpp
)
target_link_libraries(my_robot_lib ${catkin_LIBRARIES})

## 编译 C++ 可执行文件
add_executable(robot_node src/robot_node.cpp)
target_link_libraries(robot_node my_robot_lib ${catkin_LIBRARIES})
add_dependencies(robot_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

## 安装 Python 脚本
catkin_install_python(PROGRAMS
  scripts/sensor_reader.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

## 安装 launch 文件和配置
install(DIRECTORY launch config
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
```

关键注意事项：

- 使用自定义消息时，必须在 `find_package` 中添加 `message_generation`，在 `catkin_package` 的 `CATKIN_DEPENDS` 中添加 `message_runtime`
- `add_dependencies` 确保在编译节点前先生成消息头文件
- Python 脚本需要通过 `catkin_install_python` 安装而非手动复制


## package.xml 详解

`package.xml` 声明包的元信息和依赖关系。ROS 1 支持 format 1 和 format 2 两种格式，推荐使用 format 2：

```xml
<?xml version="1.0"?>
<package format="2">
  <name>my_robot_pkg</name>
  <version>1.0.0</version>
  <description>我的机器人控制包</description>

  <maintainer email="dev@example.com">开发者</maintainer>
  <license>BSD</license>

  <!-- 编译工具依赖 -->
  <buildtool_depend>catkin</buildtool_depend>

  <!-- 编译时依赖 -->
  <build_depend>roscpp</build_depend>
  <build_depend>rospy</build_depend>
  <build_depend>std_msgs</build_depend>
  <build_depend>message_generation</build_depend>

  <!-- 运行时依赖 -->
  <exec_depend>roscpp</exec_depend>
  <exec_depend>rospy</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  <exec_depend>message_runtime</exec_depend>

  <!-- 也可以使用 depend 标签同时声明编译和运行时依赖（format 2） -->
  <depend>sensor_msgs</depend>
</package>
```

| 依赖标签 | 含义 | 常见用例 |
|----------|------|----------|
| `buildtool_depend` | 编译工具 | `catkin` |
| `build_depend` | 编译时需要 | 消息生成、头文件引用 |
| `exec_depend` | 运行时需要 | 节点运行所需的库 |
| `depend` | 编译+运行时都需要 | 大多数 ROS 包依赖 |
| `test_depend` | 仅测试时需要 | `rostest`、`gtest` |


## 编译工具对比：catkin_make 与 catkin build

ROS 1 有两种主流编译工具，各有特点。


### catkin_make

`catkin_make` 是 ROS 1 默认的编译工具，将所有包合并到一个 CMake 项目中编译：

```bash
cd ~/catkin_ws
catkin_make                    # 编译整个工作空间
catkin_make --pkg my_robot_pkg # 仅编译指定包
catkin_make install            # 编译并安装
catkin_make -DCMAKE_BUILD_TYPE=Release  # Release 编译
```


### catkin build（catkin_tools）

`catkin build` 来自 `catkin_tools` 包，对每个包进行独立编译，隔离性更好：

```bash
# 安装 catkin_tools
sudo pip install catkin_tools

cd ~/catkin_ws
catkin build                    # 编译整个工作空间
catkin build my_robot_pkg       # 仅编译指定包
catkin build --force-cmake      # 强制重新运行 CMake
catkin clean                    # 清除编译产物
catkin config --cmake-args -DCMAKE_BUILD_TYPE=Release
```

两者的主要区别：

| 特性 | catkin_make | catkin build |
|------|-------------|--------------|
| 编译隔离 | 所有包共享一个 CMake 空间 | 每个包独立编译 |
| 并行编译 | 包级别无法并行 | 包级别并行编译 |
| 编译日志 | 混合在一起 | 每个包独立日志 |
| 配置管理 | 命令行参数 | `catkin config` 持久化 |
| 包冲突 | 可能出现命名冲突 | 完全隔离，冲突少 |

**注意**：`catkin_make` 和 `catkin build` 不能在同一工作空间混用。如需切换工具，需先清除 `build/` 和 `devel/` 目录。


## Overlay 工作空间

ROS 1 支持工作空间叠加 (overlay)，允许在不修改底层工作空间的情况下，在上层工作空间覆盖或扩展软件包。

```
/opt/ros/noetic/         ← 系统安装的 ROS（underlay）
    ↑
~/catkin_ws/             ← 基础开发工作空间（overlay 1）
    ↑
~/experiment_ws/         ← 实验工作空间（overlay 2）
```

配置 overlay 的关键是 `source` 的顺序：

```bash
# 先激活底层工作空间
source /opt/ros/noetic/setup.bash

# 再激活上层工作空间
source ~/catkin_ws/devel/setup.bash

# 最后激活最顶层工作空间
source ~/experiment_ws/devel/setup.bash
```

工作空间叠加的查找规则是"就近优先"：如果多个工作空间中存在同名包，ROS 会使用最后 `source` 的工作空间中的版本。可以通过 `rospack find <包名>` 验证当前使用的是哪个工作空间中的包。

典型应用场景：

- 在不修改原始包的前提下测试修改
- 隔离稳定代码和实验代码
- 团队协作中使用共享的基础工作空间


## 依赖管理：rosdep

`rosdep` 是 ROS 的系统依赖管理工具，可以自动安装 `package.xml` 中声明的系统级依赖。


### 初始化与更新

```bash
# 首次使用需要初始化（仅需一次）
sudo rosdep init
rosdep update
```


### 安装依赖

```bash
# 安装工作空间中所有包的依赖
cd ~/catkin_ws
rosdep install --from-paths src --ignore-src -r -y

# 参数说明：
# --from-paths src  : 从 src 目录扫描所有包
# --ignore-src      : 忽略工作空间中已有的包
# -r                : 遇到无法解析的依赖时继续
# -y                : 自动确认安装
```


### 检查依赖

```bash
# 检查某个包的依赖状态
rosdep check my_robot_pkg

# 列出某个包需要的系统依赖
rosdep keys my_robot_pkg
```


## 软件包组织最佳实践

### 单一职责原则

每个包应专注于一个功能领域。推荐的包划分方式：

```
my_robot/                    # 功能包（metapackage）
├── my_robot_description/    # URDF 模型和 mesh 文件
├── my_robot_driver/         # 硬件驱动
├── my_robot_msgs/           # 自定义消息和服务定义
├── my_robot_navigation/     # 导航配置和 launch 文件
├── my_robot_perception/     # 感知算法
└── my_robot_bringup/        # 系统启动脚本和顶层 launch 文件
```


### 消息包独立

将自定义消息、服务和动作定义放在独立的 `_msgs` 包中，避免循环依赖：

```bash
catkin_create_pkg my_robot_msgs std_msgs geometry_msgs message_generation message_runtime
```


### launch 文件组织

推荐在 `_bringup` 包中使用分层 launch 文件：

```xml
<!-- my_robot_bringup/launch/robot.launch -->
<launch>
  <!-- 硬件驱动层 -->
  <include file="$(find my_robot_driver)/launch/driver.launch">
    <arg name="port" value="/dev/ttyUSB0"/>
  </include>

  <!-- 感知层 -->
  <include file="$(find my_robot_perception)/launch/perception.launch"/>

  <!-- 导航层 -->
  <include file="$(find my_robot_navigation)/launch/navigation.launch">
    <arg name="map_file" value="$(find my_robot_navigation)/maps/office.yaml"/>
  </include>
</launch>
```


### 版本控制建议

```
catkin_ws/
├── src/
│   ├── .rosinstall          # wstool 配置（可选）
│   ├── my_robot/            # 自己的包（Git 仓库 1）
│   └── third_party_pkg/     # 第三方包（Git 仓库 2）
├── .gitignore               # 忽略 build/, devel/, logs/
└── README.md
```

使用 `wstool` 或 `vcstool` 管理多仓库工作空间：

```bash
# 使用 vcstool 批量拉取仓库
cd ~/catkin_ws/src
vcs import < repos.yaml

# repos.yaml 示例
# repositories:
#   my_robot:
#     type: git
#     url: https://github.com/user/my_robot.git
#     version: main
```


## 常见问题排查

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| `Could not find a package` | 未 source 工作空间 | `source devel/setup.bash` |
| `CMake Error: package not found` | 缺少依赖 | `rosdep install --from-paths src --ignore-src -y` |
| 消息头文件找不到 | 缺少 `add_dependencies` | 在 CMakeLists.txt 中添加依赖声明 |
| catkin_make 与 catkin build 冲突 | 混用两种工具 | 删除 `build/` 和 `devel/` 后重新编译 |
| Python 脚本权限错误 | 脚本无执行权限 | `chmod +x scripts/*.py` |
| overlay 包未生效 | source 顺序错误 | 检查 `ROS_PACKAGE_PATH` 顺序 |


## 参考资料

- [ROS Wiki: catkin/workspaces](http://wiki.ros.org/catkin/workspaces)
- [ROS Wiki: catkin/CMakeLists.txt](http://wiki.ros.org/catkin/CMakeLists.txt)
- [ROS Wiki: catkin_tools](https://catkin-tools.readthedocs.io/)
- [ROS Wiki: rosdep](http://wiki.ros.org/rosdep)
- [ROS Enhancement Proposal (REP) 140: package.xml format 2](https://www.ros.org/reps/rep-0140.html)
