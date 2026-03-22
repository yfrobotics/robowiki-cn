# ROS 1 参考资料

!!! note "引言"
    本页汇总了 ROS 1 开发中的常用命令速查表、核心软件包生态、常见问题排查指南以及向 ROS 2 迁移的参考入口，是 ROS 1 开发者的日常参考手册。


## 常用命令速查表

### 核心命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `roscore` | 启动 ROS Master、参数服务器和 rosout | `roscore` |
| `rosrun` | 运行指定包中的节点 | `rosrun turtlesim turtlesim_node` |
| `roslaunch` | 通过 launch 文件启动多个节点 | `roslaunch my_pkg robot.launch` |
| `rosnode` | 查看运行中的节点信息 | `rosnode list` / `rosnode info /node` |
| `rosparam` | 操作参数服务器 | `rosparam list` / `rosparam get /param` |


### 话题命令 (rostopic)

```bash
# 列出所有活跃话题
rostopic list

# 查看话题信息（类型、发布者、订阅者）
rostopic info /cmd_vel

# 实时打印话题消息
rostopic echo /odom

# 只打印一条消息
rostopic echo /odom -n 1

# 查看话题发布频率
rostopic hz /camera/image_raw

# 查看话题带宽
rostopic bw /camera/image_raw

# 查看消息类型
rostopic type /cmd_vel

# 手动发布消息（测试用）
rostopic pub /cmd_vel geometry_msgs/Twist \
  "linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.3}"

# 以固定频率发布（10 Hz）
rostopic pub -r 10 /cmd_vel geometry_msgs/Twist '{linear: {x: 0.2}}'
```


### 服务命令 (rosservice)

```bash
# 列出所有服务
rosservice list

# 查看服务类型
rosservice type /spawn

# 查看服务参数格式
rossrv show turtlesim/Spawn

# 调用服务
rosservice call /spawn "x: 2.0
y: 2.0
theta: 0.0
name: 'turtle2'"

# 查看服务所属节点
rosservice node /spawn
```


### 数据录制与回放 (rosbag)

```bash
# 录制所有话题
rosbag record -a

# 录制指定话题
rosbag record /odom /scan /camera/image_raw -O my_data.bag

# 限时录制（60 秒）
rosbag record /scan --duration=60

# 查看 bag 文件信息
rosbag info my_data.bag

# 回放 bag 文件
rosbag play my_data.bag

# 以 0.5 倍速回放
rosbag play my_data.bag -r 0.5

# 循环回放
rosbag play my_data.bag -l

# 从指定时间开始回放
rosbag play my_data.bag -s 10.0

# 只回放指定话题
rosbag play my_data.bag --topics /scan /odom
```


### 可视化与调试 (rqt)

```bash
# 启动 rqt 主界面
rqt

# 查看节点与话题的连接关系图
rqt_graph

# 实时绘制数据曲线
rqt_plot /odom/pose/pose/position/x /odom/pose/pose/position/y

# 查看日志输出
rqt_console

# 动态参数调节（需包支持 dynamic_reconfigure）
rosrun rqt_reconfigure rqt_reconfigure

# 查看 TF 坐标变换树
rosrun rqt_tf_tree rqt_tf_tree

# 查看图像话题
rqt_image_view
```


### 其他实用命令

```bash
# 查找包的路径
rospack find my_robot_pkg

# 进入包的目录
roscd my_robot_pkg

# 列出包中的文件
rosls my_robot_pkg

# 查看消息定义
rosmsg show geometry_msgs/Twist

# 列出某个包的所有消息类型
rosmsg package sensor_msgs

# 编辑包中的文件
rosed my_robot_pkg CMakeLists.txt

# 查看 TF 坐标变换
rosrun tf tf_echo base_link camera_link

# 将 TF 树导出为 PDF
rosrun tf view_frames
```


## 核心软件包生态

### 导航 (Navigation Stack)

| 包名 | 功能 |
|------|------|
| `move_base` | 导航框架核心，整合全局与局部路径规划 |
| `amcl` | 自适应蒙特卡洛定位 (Adaptive Monte Carlo Localization) |
| `gmapping` | 基于粒子滤波的 2D SLAM |
| `map_server` | 加载和提供静态地图 |
| `costmap_2d` | 2D 代价地图（障碍物层、膨胀层等） |
| `global_planner` | 全局路径规划（A*、Dijkstra） |
| `dwa_local_planner` | 动态窗口法局部规划 |
| `teb_local_planner` | 时间弹性带局部规划 |


### 机械臂 (MoveIt)

| 包名 | 功能 |
|------|------|
| `moveit_core` | 运动规划核心库 |
| `moveit_ros_planning` | ROS 接口层 |
| `moveit_ros_visualization` | RViz 交互界面 |
| `moveit_setup_assistant` | 可视化配置工具 |


### 感知与视觉

| 包名 | 功能 |
|------|------|
| `image_transport` | 图像话题的压缩传输 |
| `cv_bridge` | OpenCV 与 ROS 图像格式转换 |
| `pcl_ros` | 点云库 (Point Cloud Library) 的 ROS 接口 |
| `laser_geometry` | 激光扫描数据几何处理 |
| `image_pipeline` | 图像去畸变、深度图生成 |
| `ar_track_alvar` | AR 标记检测与跟踪 |


### 机器人描述与仿真

| 包名 | 功能 |
|------|------|
| `urdf` | 统一机器人描述格式 (Unified Robot Description Format) 解析 |
| `xacro` | URDF 宏扩展工具 |
| `robot_state_publisher` | 根据关节状态发布 TF |
| `joint_state_publisher` | 发布关节状态（可带 GUI 滑块） |
| `gazebo_ros` | Gazebo 仿真器 ROS 接口 |
| `rviz` | 3D 可视化工具 |


### 坐标变换

| 包名 | 功能 |
|------|------|
| `tf` | 坐标变换库（旧版） |
| `tf2_ros` | 坐标变换库（推荐使用） |
| `tf2_geometry_msgs` | geometry_msgs 的 TF2 转换 |


## 常见问题排查

### 连接与通信问题

**问题：节点无法通信**

```bash
# 检查 ROS Master 是否运行
rostopic list

# 检查 ROS_MASTER_URI 设置
echo $ROS_MASTER_URI
# 默认应为 http://localhost:11311

# 多机通信时检查网络配置
echo $ROS_IP
echo $ROS_HOSTNAME

# 确保主机名可解析
ping <远程主机名>
```

**问题：多机通信配置**

```bash
# 机器人端（Master 所在机器）
export ROS_MASTER_URI=http://192.168.1.100:11311
export ROS_IP=192.168.1.100

# 工作站端
export ROS_MASTER_URI=http://192.168.1.100:11311
export ROS_IP=192.168.1.200
```


### 编译问题

**问题：找不到包或消息**

```bash
# 确保已 source 工作空间
source ~/catkin_ws/devel/setup.bash

# 重新编译消息包
catkin_make --pkg my_robot_msgs

# 检查消息是否生成成功
rosmsg show my_robot_msgs/RobotStatus
```

**问题：依赖缺失**

```bash
# 安装所有未满足的依赖
cd ~/catkin_ws
rosdep install --from-paths src --ignore-src -r -y
```


### 时间同步问题

**问题：TF 时间戳警告**

```bash
# 常见警告信息：
# "TF_OLD_DATA" 或 "Lookup would require extrapolation into the past"

# 检查系统时间同步
ntpdate -q ntp.ubuntu.com

# 多机环境下使用 chrony 同步
sudo apt install chrony
```


### 性能问题

**问题：话题延迟过高**

```bash
# 检查话题发布频率是否正常
rostopic hz /camera/image_raw

# 检查带宽使用
rostopic bw /camera/image_raw

# 使用 image_transport 压缩图像传输
# 将 image_raw 替换为 image_raw/compressed
rosrun image_view image_view image:=/camera/image_raw compressed
```


## 发行版时间线

| 发行版 | 代号 | 发布时间 | 对应 Ubuntu | EOL |
|--------|------|----------|-------------|-----|
| ROS Indigo | Igloo | 2014-07 | Ubuntu 14.04 | 2019-04 |
| ROS Kinetic | Kame | 2016-05 | Ubuntu 16.04 | 2021-04 |
| ROS Melodic | Morenia | 2018-05 | Ubuntu 18.04 | 2023-05 |
| ROS Noetic | Ninjemys | 2020-05 | Ubuntu 20.04 | 2025-05 |

ROS Noetic 是 ROS 1 的最后一个发行版。此后 ROS 1 将不再有新版本发布，社区开发重心已转向 ROS 2。


## 迁移到 ROS 2

ROS 1 已进入维护末期，建议新项目直接使用 ROS 2。以下是迁移参考要点：

### 关键变化概览

| 方面 | ROS 1 | ROS 2 |
|------|-------|-------|
| 通信中间件 | 自研 XMLRPC/TCPROS | DDS (Data Distribution Service) |
| 中心节点 | 需要 roscore (Master) | 去中心化，无需 Master |
| 编译系统 | catkin (CMake) | ament (CMake/Python) |
| Launch 文件 | XML 格式 | Python（推荐）或 XML |
| 客户端库 | roscpp / rospy | rclcpp / rclpy |
| 生命周期 | 无 | 支持托管节点 (Lifecycle Nodes) |
| QoS | 无 | 细粒度的 QoS 策略 |

### 迁移资源

- **ros1_bridge**：在迁移过渡期，使用 `ros1_bridge` 包实现 ROS 1 和 ROS 2 之间的话题和服务桥接
- **迁移指南**：详见本站 [ROS 2 迁移手册](ros2-migration-playbook.md)

### 建议迁移策略

1. **新功能用 ROS 2 开发**，通过 `ros1_bridge` 与现有 ROS 1 节点通信
2. **逐包迁移**，从叶子节点（依赖最少的包）开始
3. **优先迁移自定义消息包**，因为它们被其他包广泛依赖
4. 充分利用 ROS 2 的 QoS、生命周期节点等新特性


## 官方文档与社区

### 官方资源

- [ROS Wiki](http://wiki.ros.org/) — ROS 1 的主要文档平台
- [ROS Tutorials](http://wiki.ros.org/ROS/Tutorials) — 官方入门教程
- [ROS Answers](https://answers.ros.org/) — 问答社区
- [ROS Index](https://index.ros.org/) — 软件包索引
- [ROS Discourse](https://discourse.ros.org/) — 开发者讨论区


### 学习资源

- [Programming Robots with ROS](http://shop.oreilly.com/product/0636920024736.do) — O'Reilly 出版的 ROS 实践书籍
- [A Gentle Introduction to ROS](https://jokane.net/agitr/) — Jason O'Kane 编写的免费教材
- [ROS Robot Programming](https://community.robotsource.org/t/download-the-ros-robot-programming-book-for-free/51) — 开源 ROS 书籍
- [The Construct](https://www.theconstructsim.com/) — 在线 ROS 学习平台，提供浏览器中的仿真环境


### 常用第三方资源

- [ROS Cheat Sheet (Clearpath)](https://www.clearpathrobotics.com/ros-cheat-sheet/) — Clearpath Robotics 制作的命令速查卡
- [ROS Best Practices](https://github.com/leggedrobotics/ros_best_practices) — ETH Zurich 整理的 ROS 最佳实践


## 参考资料

- [ROS Wiki](http://wiki.ros.org/)
- [ROS Noetic Installation](http://wiki.ros.org/noetic/Installation)
- [ROS Distribution Timeline (REP 3)](https://www.ros.org/reps/rep-0003.html)
- [ROS 2 Migration Guide](https://docs.ros.org/en/rolling/How-To-Guides/Migrating-from-ROS1.html)
