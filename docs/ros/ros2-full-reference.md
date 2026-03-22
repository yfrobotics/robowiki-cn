# ROS 2 参考资料

!!! note "引言"
    本页汇总了 ROS 2 开发中的常用命令速查表、核心软件包介绍、发行版时间线以及官方和社区资源，是 ROS 2 开发者的日常参考手册。


## CLI 命令速查表

### 运行与启动

```bash
# 运行单个节点
ros2 run <package> <executable>
ros2 run turtlesim turtlesim_node

# 通过 launch 文件启动
ros2 launch <package> <launch_file>
ros2 launch nav2_bringup navigation_launch.py

# 带参数启动
ros2 launch my_robot robot_launch.py use_sim:=true

# 列出包中的可执行文件
ros2 pkg executables turtlesim
```


### 节点命令 (ros2 node)

```bash
# 列出所有运行中的节点
ros2 node list

# 查看节点信息（发布者、订阅者、服务、动作）
ros2 node info /turtlesim
```


### 话题命令 (ros2 topic)

```bash
# 列出所有话题
ros2 topic list

# 列出话题及其类型
ros2 topic list -t

# 查看话题信息
ros2 topic info /cmd_vel

# 查看话题详细信息（含 QoS）
ros2 topic info /cmd_vel --verbose

# 打印话题消息
ros2 topic echo /odom

# 只打印一条消息
ros2 topic echo /odom --once

# 查看发布频率
ros2 topic hz /scan

# 查看带宽
ros2 topic bw /camera/image_raw

# 发布消息
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.5}, angular: {z: 0.3}}"

# 以固定频率发布（10 Hz）
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2}}"

# 只发布一次
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.5}}"
```


### 服务命令 (ros2 service)

```bash
# 列出所有服务
ros2 service list

# 列出服务及其类型
ros2 service list -t

# 查看服务类型
ros2 service type /spawn

# 查找特定类型的服务
ros2 service find std_srvs/srv/Empty

# 调用服务
ros2 service call /spawn turtlesim/srv/Spawn \
  "{x: 2.0, y: 2.0, theta: 0.0, name: 'turtle2'}"
```


### 参数命令 (ros2 param)

```bash
# 列出节点的所有参数
ros2 param list /turtlesim

# 获取参数值
ros2 param get /turtlesim background_r

# 设置参数值
ros2 param set /turtlesim background_r 200

# 将参数导出为 YAML 文件
ros2 param dump /turtlesim --print-yaml > params.yaml

# 从 YAML 文件加载参数
ros2 param load /turtlesim params.yaml
```


### 动作命令 (ros2 action)

```bash
# 列出所有动作
ros2 action list

# 列出动作及其类型
ros2 action list -t

# 查看动作信息
ros2 action info /navigate_to_pose

# 发送动作目标
ros2 action send_goal /navigate_to_pose \
  nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, \
    pose: {position: {x: 1.0, y: 2.0}}}}"

# 发送目标并查看反馈
ros2 action send_goal /navigate_to_pose \
  nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, \
    pose: {position: {x: 1.0, y: 2.0}}}}" \
  --feedback
```


### 数据录制与回放 (ros2 bag)

```bash
# 录制指定话题
ros2 bag record /odom /scan /cmd_vel

# 录制所有话题
ros2 bag record -a

# 指定输出文件名
ros2 bag record -o my_data /odom /scan

# 查看 bag 文件信息
ros2 bag info my_data

# 回放
ros2 bag play my_data

# 以 0.5 倍速回放
ros2 bag play my_data --rate 0.5

# 循环回放
ros2 bag play my_data --loop

# 只回放指定话题
ros2 bag play my_data --topics /scan /odom
```


### 接口命令 (ros2 interface)

```bash
# 查看消息定义
ros2 interface show geometry_msgs/msg/Twist

# 查看服务定义
ros2 interface show std_srvs/srv/SetBool

# 查看动作定义
ros2 interface show nav2_msgs/action/NavigateToPose

# 列出包中的所有接口
ros2 interface package sensor_msgs

# 列出所有可用消息类型
ros2 interface list -m
```


### 其他实用命令

```bash
# 查看 TF 树
ros2 run tf2_tools view_frames

# 查看两个坐标系之间的变换
ros2 run tf2_ros tf2_echo base_link camera_link

# 启动 RViz2
ros2 run rviz2 rviz2

# 查看运行时计算图
ros2 run rqt_graph rqt_graph

# 动态参数调节
ros2 run rqt_reconfigure rqt_reconfigure

# 系统诊断报告
ros2 doctor --report
```


## 核心软件包

### Nav2 (Navigation 2)

Nav2 是 ROS 2 的导航框架，是 ROS 1 Navigation Stack 的继承者，功能更强大。

| 组件 | 功能 |
|------|------|
| `nav2_bt_navigator` | 基于行为树的导航决策 |
| `nav2_planner` | 全局路径规划（NavFn、Smac、Theta*） |
| `nav2_controller` | 局部路径跟踪（DWB、TEB、MPPI） |
| `nav2_costmap_2d` | 2D 代价地图 |
| `nav2_recoveries` | 恢复行为（旋转、后退、等待） |
| `nav2_map_server` | 地图加载和保存 |
| `nav2_amcl` | 自适应蒙特卡洛定位 |
| `nav2_lifecycle_manager` | 生命周期管理器 |
| `nav2_waypoint_follower` | 多航点跟踪 |

```bash
# 安装 Nav2
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup

# 启动 Nav2（仿真环境）
ros2 launch nav2_bringup tb3_simulation_launch.py
```


### MoveIt 2

MoveIt 2 是 ROS 2 的运动规划框架，用于机械臂的运动规划、抓取和操作。

| 组件 | 功能 |
|------|------|
| `moveit_core` | 运动规划核心库 |
| `moveit_ros_planning` | ROS 2 规划接口 |
| `moveit_servo` | 实时伺服控制（遥操作） |
| `moveit_setup_assistant` | 可视化配置工具 |
| `moveit_visual_tools` | RViz 可视化辅助 |

```bash
# 安装 MoveIt 2
sudo apt install ros-humble-moveit
```


### micro-ROS

micro-ROS 将 ROS 2 扩展到微控制器平台，使 MCU (Microcontroller Unit，微控制器单元) 能够作为 ROS 2 节点参与通信。

支持的平台：

- STM32 系列
- ESP32
- Arduino（部分型号）
- Teensy
- Raspberry Pi Pico

```bash
# 安装 micro-ROS Agent
sudo apt install ros-humble-micro-ros-agent

# 启动 Agent（串口连接）
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0

# 启动 Agent（UDP 连接）
ros2 run micro_ros_agent micro_ros_agent udp4 --port 8888
```


### ros2_control

ros2_control 是 ROS 2 的硬件抽象和控制器管理框架。

| 组件 | 功能 |
|------|------|
| `controller_manager` | 控制器生命周期管理 |
| `joint_state_broadcaster` | 关节状态广播 |
| `diff_drive_controller` | 差速驱动控制器 |
| `joint_trajectory_controller` | 关节轨迹控制器 |
| `hardware_interface` | 硬件接口抽象层 |


### 其他重要包

| 包名 | 功能 |
|------|------|
| `slam_toolbox` | 在线和离线 2D SLAM |
| `robot_localization` | 扩展卡尔曼滤波定位 |
| `image_transport` | 图像话题的压缩传输 |
| `cv_bridge` | OpenCV 与 ROS 2 图像格式转换 |
| `pcl_conversions` | PCL 点云与 ROS 2 消息转换 |
| `tf2_ros` | 坐标变换库 |
| `foxglove_bridge` | 基于 Web 的可视化工具接口 |
| `diagnostics` | 系统诊断和监控 |


## 发行版时间线

| 发行版 | 代号 | 发布时间 | 对应 Ubuntu | 支持期限 | 类型 |
|--------|------|----------|-------------|----------|------|
| Foxy | Fitzroy | 2020-06 | Ubuntu 20.04 | 2023-05（已结束） | LTS |
| Galactic | Geochelone | 2021-05 | Ubuntu 20.04 | 2022-11（已结束） | 非 LTS |
| Humble | Hawksbill | 2022-05 | Ubuntu 22.04 | 2027-05 | LTS |
| Iron | Irwini | 2023-05 | Ubuntu 22.04 | 2024-11（已结束） | 非 LTS |
| Jazzy | Jalisco | 2024-05 | Ubuntu 24.04 | 2029-05 | LTS |
| Rolling | — | 滚动更新 | 最新 Ubuntu | 持续更新 | 开发版 |

选择建议：

- **生产环境**：使用最新的 LTS 版本（Jazzy 或 Humble）
- **新项目开发**：优先选择 Jazzy（最新 LTS）
- **尝鲜和贡献**：使用 Rolling


### Ubuntu 与 ROS 2 版本对应

```bash
# 查看当前 ROS 2 版本
echo $ROS_DISTRO

# Ubuntu 22.04 推荐安装 Humble
sudo apt install ros-humble-desktop

# Ubuntu 24.04 推荐安装 Jazzy
sudo apt install ros-jazzy-desktop
```


## 开发环境配置

### 基本环境设置

```bash
# 添加到 ~/.bashrc
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash

# 设置 Domain ID（可选，默认为 0）
export ROS_DOMAIN_ID=42

# 选择 DDS 实现（可选）
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# 启用 colcon 自动补全
source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
```


### 常用别名

```bash
# 推荐添加到 ~/.bashrc 的别名
alias cb='cd ~/ros2_ws && colcon build --symlink-install'
alias cs='source ~/ros2_ws/install/setup.bash'
alias cbs='cb && cs'
alias rt='ros2 topic'
alias rn='ros2 node'
alias rp='ros2 param'
alias ri='ros2 interface'
```


## ROS 1 与 ROS 2 命令对照

| 功能 | ROS 1 命令 | ROS 2 命令 |
|------|-----------|-----------|
| 运行节点 | `rosrun pkg node` | `ros2 run pkg exe` |
| 启动 | `roslaunch pkg file.launch` | `ros2 launch pkg file_launch.py` |
| 话题列表 | `rostopic list` | `ros2 topic list` |
| 打印话题 | `rostopic echo /topic` | `ros2 topic echo /topic` |
| 发布话题 | `rostopic pub /topic type data` | `ros2 topic pub /topic type data` |
| 服务列表 | `rosservice list` | `ros2 service list` |
| 调用服务 | `rosservice call /srv data` | `ros2 service call /srv type data` |
| 参数列表 | `rosparam list` | `ros2 param list` |
| 获取参数 | `rosparam get /param` | `ros2 param get /node param` |
| 消息定义 | `rosmsg show type` | `ros2 interface show type` |
| 录制 | `rosbag record` | `ros2 bag record` |
| 回放 | `rosbag play file.bag` | `ros2 bag play file` |
| 节点列表 | `rosnode list` | `ros2 node list` |
| 节点信息 | `rosnode info /node` | `ros2 node info /node` |
| 计算图 | `rqt_graph` | `ros2 run rqt_graph rqt_graph` |


## 官方资源

### 文档与教程

- [ROS 2 官方文档](https://docs.ros.org/) — 最权威的 ROS 2 参考文档
- [ROS 2 教程](https://docs.ros.org/en/rolling/Tutorials.html) — 从入门到进阶的完整教程
- [ROS 2 API 文档](https://docs.ros2.org/latest/api/) — C++ 和 Python API 参考
- [ROS Index](https://index.ros.org/) — ROS 2 包索引和搜索


### 设计文档

- [ROS 2 Design](https://design.ros2.org/) — ROS 2 架构设计文档
- [REP (ROS Enhancement Proposals)](https://ros.org/reps/rep-0000.html) — ROS 增强提案


### 代码仓库

- [ros2 GitHub](https://github.com/ros2) — ROS 2 核心代码仓库
- [ros-planning](https://github.com/ros-planning) — MoveIt 等规划相关包
- [ros-navigation](https://github.com/ros-navigation) — Nav2 导航框架


## 社区资源

### 交流平台

- [ROS Discourse](https://discourse.ros.org/) — 开发者讨论区，ROS 2 新闻和公告
- [Robotics Stack Exchange](https://robotics.stackexchange.com/) — 技术问答（已替代 ROS Answers）
- [ROS Discord](https://discord.gg/ros) — 实时聊天社区


### 学习资源

| 资源 | 类型 | 说明 |
|------|------|------|
| [The Construct](https://www.theconstructsim.com/) | 在线平台 | 浏览器中的 ROS 2 学习环境 |
| [Articulated Robotics](https://articulatedrobotics.xyz/) | 博客和视频 | ROS 2 入门系列教程 |
| [Navigation 2 教程](https://docs.nav2.org/) | 文档 | Nav2 详细使用指南 |
| [MoveIt 2 教程](https://moveit.picknik.ai/) | 文档 | MoveIt 2 入门和进阶教程 |
| [micro-ROS 教程](https://micro.ros.org/docs/tutorials/) | 文档 | 嵌入式 ROS 2 开发指南 |


### 会议与活动

- **ROSCon**：每年举办的 ROS 开发者大会，所有演讲视频均在 [Vimeo](https://vimeo.com/osaborobotics) 上免费公开
- **ROS World**：线上 ROS 社区活动


## 参考资料

- [ROS 2 官方文档](https://docs.ros.org/)
- [ROS 2 发行版列表 (REP 2000)](https://www.ros.org/reps/rep-2000.html)
- [Nav2 文档](https://docs.nav2.org/)
- [MoveIt 2 文档](https://moveit.picknik.ai/)
- [micro-ROS 官网](https://micro.ros.org/)
- [ros2_control 文档](https://control.ros.org/)
- [ROS Discourse](https://discourse.ros.org/)
