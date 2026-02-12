# ROS 1

!!! note "引言"
    ROS 1是ROS的第一代版本，自2010年首个正式发行版Box Turtle发布以来，已成为学术研究和机器人原型开发的事实标准。ROS 1以其成熟的工具链、丰富的软件包和庞大的社区支持著称。尽管ROS 2已逐步成为主流，ROS 1仍然在众多现有项目中发挥着重要作用。

## 概述

ROS 1最初由Willow Garage公司开发，后由Open Source Robotics Foundation (OSRF) 维护。它主要面向学术研究和单机器人系统的开发，在Ubuntu Linux上有最好的支持。ROS 1的最后一个版本是Noetic Ninjemys（2020年发布），支持至2025年5月。

ROS 1的设计目标是降低机器人软件开发的门槛，通过提供标准化的通信机制、丰富的工具和大量可复用的软件包，使开发者能够快速构建功能丰富的机器人系统。

## 核心概念

### ROS Master

ROS Master是ROS 1架构的核心组件，负责管理节点之间的命名和注册服务。所有节点在启动时都需要向Master注册，Master负责维护节点的查找表，使节点能够相互发现和建立通信。通过`roscore`命令启动Master。

ROS Master是ROS 1的一个关键特征，同时也是其局限性之一。如果Master崩溃，整个系统的通信将会中断。

### 节点 (Nodes)

节点是ROS 1中执行计算的基本进程。ROS 1鼓励开发者创建大量小型、功能单一的节点，而不是少量庞大的多功能进程。这种设计使系统具有更好的模块化特性，便于调试和复用。

### 话题与消息 (Topics & Messages)

话题 (Topics) 是ROS 1中最常用的通信方式，采用发布-订阅 (publish-subscribe) 模式。发布者 (Publisher) 向一个命名话题发送消息，订阅者 (Subscriber) 从该话题接收消息。通信是异步的，发布者和订阅者之间无需知道对方的存在。

消息 (Messages) 是话题传输的数据结构，使用`.msg`文件定义。常见的消息类型包括：

- `std_msgs`：标准基础类型，如`String`、`Int32`、`Float64`
- `geometry_msgs`：几何相关消息，如`Twist`（速度）、`Pose`（位姿）
- `sensor_msgs`：传感器数据，如`Image`（图像）、`LaserScan`（激光扫描）、`PointCloud2`（点云）
- `nav_msgs`：导航相关消息，如`Odometry`（里程计）、`Path`（路径）

### 服务 (Services)

服务 (Services) 提供同步的请求-响应通信机制，使用`.srv`文件定义请求和响应的数据结构。与话题不同，服务是一对一的通信，适用于需要立即获得结果的场景。

### 参数服务器 (Parameter Server)

参数服务器 (Parameter Server) 是一个集中式的键值存储系统，允许节点在运行时存储和检索配置参数。参数服务器由ROS Master维护，支持整数、浮点数、字符串、布尔值、列表和字典等数据类型。

## catkin构建系统

catkin是ROS 1的官方构建系统，基于CMake开发。它使用**工作空间** (workspace) 来组织和编译ROS软件包。

典型的catkin工作空间结构如下：

```
catkin_ws/
├── src/              # 源代码目录
│   ├── CMakeLists.txt
│   ├── package_1/
│   │   ├── CMakeLists.txt
│   │   ├── package.xml
│   │   └── src/
│   └── package_2/
├── build/            # 编译中间文件
├── devel/            # 开发空间（编译产物）
└── logs/             # 日志文件
```

常用的catkin命令包括：

- `catkin_make`：编译整个工作空间
- `catkin build`：逐包编译（由catkin_tools提供，更灵活）
- `catkin_create_pkg`：创建新的ROS软件包

## 常用工具

ROS 1提供了大量实用的命令行和图形化工具：

- **roscore**：启动ROS Master、参数服务器和rosout日志节点
- **rosrun**：运行单个ROS节点，如`rosrun turtlesim turtlesim_node`
- **roslaunch**：通过`.launch`文件同时启动多个节点并设置参数
- **rostopic**：查看、发布和监控话题消息
- **rosservice**：调用和查看ROS服务
- **rosparam**：获取和设置参数服务器中的参数
- **rosbag**：记录和回放话题数据，用于数据采集和离线分析
- **RViz**：三维可视化工具，用于显示传感器数据和机器人模型
- **rqt**：基于Qt的模块化图形工具，包含rqt_graph（节点关系图）、rqt_plot（数据绘图）、rqt_console（日志查看）等插件

## 常用软件包

ROS 1拥有数千个社区贡献的软件包，以下是一些最常用的核心包：

| 软件包 | 功能描述 |
| --- | --- |
| `navigation` | 移动机器人自主导航，包含路径规划、定位和避障 |
| `moveit` | 机械臂运动规划、抓取和操作 |
| `gmapping` | 基于激光雷达的SLAM建图 |
| `amcl` | 自适应蒙特卡洛定位 (Adaptive Monte Carlo Localization) |
| `tf` | 坐标变换管理 |
| `robot_state_publisher` | 发布机器人关节状态到tf树 |
| `rviz` | 三维可视化 |
| `gazebo_ros` | Gazebo仿真环境的ROS接口 |
| `image_transport` | 图像传输和压缩 |
| `pcl_ros` | 点云库 (Point Cloud Library) 的ROS封装 |

## ROS 1版本

| 版本代号                                                     | 发布日期            | Logo                                                         | 教程海龟的图标                                               | 终止维护日期             |
| ------------------------------------------------------------ | ------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------ |
| [ROS Noetic Ninjemys](http://wiki.ros.org/noetic) (**Recommended**) | May 23rd, 2020      | ![Noetic Ninjemys](https://raw.githubusercontent.com/ros-infrastructure/artwork/master/distributions/noetic.png) | ![https://raw.githubusercontent.com/ros/ros_tutorials/noetic-devel/turtlesim/images/noetic.png](https://raw.githubusercontent.com/ros/ros_tutorials/noetic-devel/turtlesim/images/noetic.png) | May, 2025 (Focal EOL)    |
| [ROS Melodic Morenia](http://wiki.ros.org/melodic)           | May 23rd, 2018      | [![Melodic Morenia](https://raw.githubusercontent.com/ros-infrastructure/artwork/master/distributions/melodic_with_bg.png)](http://wiki.ros.org/melodic) | ![Melodic Morenia](https://raw.githubusercontent.com/ros/ros_tutorials/melodic-devel/turtlesim/images/melodic.png) | May, 2023 (Bionic EOL)   |
| [ROS Lunar Loggerhead](http://wiki.ros.org/lunar)            | May 23rd, 2017      | [![Lunar Loggerhead](https://raw.githubusercontent.com/ros-infrastructure/artwork/master/distributions/lunar_with_bg.png)](http://wiki.ros.org/lunar) | ![Lunar Loggerhead](https://raw.githubusercontent.com/ros/ros_tutorials/lunar-devel/turtlesim/images/lunar.png) | May, 2019                |
| [ROS Kinetic Kame](http://wiki.ros.org/kinetic)              | May 23rd, 2016      | [![Kinetic Kame](https://raw.githubusercontent.com/ros-infrastructure/artwork/master/distributions/kinetic.png)](http://wiki.ros.org/kinetic) | ![Kinetic Kame](https://raw.github.com/ros/ros_tutorials/kinetic-devel/turtlesim/images/kinetic.png) | April, 2021 (Xenial EOL) |
| [ROS Jade Turtle](http://wiki.ros.org/jade)                  | May 23rd, 2015      | [![Jade Turtle](http://i.imgur.com/99oTyT5.png)](http://wiki.ros.org/jade) | ![Jade Turtle](https://raw.github.com/ros/ros_tutorials/jade-devel/turtlesim/images/jade.png) | May, 2017                |
| [ROS Indigo Igloo](http://wiki.ros.org/indigo)               | July 22nd, 2014     | [![I-turtle](http://i.imgur.com/YBCUixi.png)](http://wiki.ros.org/indigo) | ![I-turtle](https://raw.github.com/ros/ros_tutorials/indigo-devel/turtlesim/images/indigo.png) | April, 2019 (Trusty EOL) |
| [ROS Hydro Medusa](http://wiki.ros.org/hydro)                | September 4th, 2013 | [![H-turtle](http://i.imgur.com/xvfZPAo.png)](http://wiki.ros.org/hydro) | ![H-turtle](https://raw.github.com/ros/ros_tutorials/hydro-devel/turtlesim/images/hydro.png) | May, 2015                |
| [ROS Groovy Galapagos](http://wiki.ros.org/groovy)           | December 31, 2012   | [![G-turtle](http://www.ros.org/images/groovygalapagos-320w.jpg)](http://wiki.ros.org/groovy) | ![G-turtle](https://raw.github.com/ros/ros_tutorials/groovy-devel/turtlesim/images/groovy.png) | July, 2014               |
| [ROS Fuerte Turtle](http://wiki.ros.org/fuerte)              | April 23, 2012      | [![F-turtle](http://www.ros.org/images/fuerte-320w.jpg)](http://wiki.ros.org/fuerte) | ![F-turtle](https://raw.github.com/ros/ros_tutorials/groovy-devel/turtlesim/images/fuerte.png) | --                       |
| [ROS Electric Emys](http://wiki.ros.org/electric)            | August 30, 2011     | [![E-turtle](http://www.ros.org/news/resources/2011/electric_640w.png)](http://wiki.ros.org/electric) | ![E-turtle](https://raw.github.com/ros/ros_tutorials/groovy-devel/turtlesim/images/electric.png) | --                       |
| [ROS Diamondback](http://wiki.ros.org/diamondback)           | March 2, 2011       | [![D-turtle](http://ros.org/images/wiki/diamondback_posterLo-240w.jpg)](http://wiki.ros.org/diamondback) | ![D-turtle](https://raw.github.com/ros/ros_tutorials/groovy-devel/turtlesim/images/diamondback.png) | --                       |
| [ROS C Turtle](http://wiki.ros.org/cturtle)                  | August 2, 2010      | [![C-turtle](http://ros.org/images/wiki/cturtle.jpg)](http://wiki.ros.org/cturtle) | ![C-turtle](https://raw.github.com/ros/ros_tutorials/groovy-devel/turtlesim/images/sea-turtle.png) | --                       |
| [ROS Box Turtle](http://wiki.ros.org/boxturtle)              | March 2, 2010       | [![B-turtle](http://ros.org/wiki/boxturtle?action=AttachFile&do=get&target=Box_Turtle.320.png)](http://wiki.ros.org/boxturtle) | ![B-turtle](https://raw.github.com/ros/ros_tutorials/groovy-devel/turtlesim/images/box-turtle.png) | --                       |

## 安装指南

ROS 1通常安装在Ubuntu Linux上，每个ROS 1版本对应特定的Ubuntu版本：

- **Noetic**：Ubuntu 20.04 (Focal Fossa)
- **Melodic**：Ubuntu 18.04 (Bionic Beaver)
- **Kinetic**：Ubuntu 16.04 (Xenial Xerus)

安装的基本步骤包括：配置软件源 (sources.list)、添加密钥 (keys)、通过`apt`安装ROS、初始化`rosdep`以及配置环境变量。详细安装教程请参考[ROS Wiki安装页面](http://wiki.ros.org/ROS/Installation)。

## ROS 1的局限性

尽管ROS 1在学术领域取得了巨大成功，但随着机器人技术向工业化和商业化发展，其设计上的一些局限性逐渐显现，这也是ROS 2被开发的直接原因：

- **单点故障** (Single Point of Failure)：ROS Master是系统的单一故障点，一旦崩溃将导致整个系统通信中断
- **缺乏实时性支持** (No Real-time Support)：ROS 1的通信层不支持实时性保障，无法满足工业控制等对时间敏感的应用需求
- **安全性不足** (Lack of Security)：ROS 1没有内置的认证和加密机制，不适合部署在开放网络环境中
- **仅支持Linux**：ROS 1主要支持Ubuntu Linux，在其他操作系统上的支持有限
- **不支持多机器人系统** (No Native Multi-robot Support)：缺乏对多机器人协作场景的原生支持
- **嵌入式支持有限**：对资源受限的嵌入式平台支持不够完善

这些局限性促使社区开发了ROS 2，以更好地满足工业级和商业级机器人应用的需求。

## 参考资料

1. ROS Wiki, [ROS Distributions](http://wiki.ros.org/Distributions)
2. [ROS/Introduction](http://wiki.ros.org/ROS/Introduction), ROS Wiki
3. [catkin/conceptual_overview](http://wiki.ros.org/catkin/conceptual_overview), ROS Wiki
4. [ROS/Installation](http://wiki.ros.org/ROS/Installation), ROS Wiki
