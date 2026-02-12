# ROS (机器人操作系统)

!!! note "引言"
    ROS (Robot Operating System) 是当今机器人领域最广泛使用的软件框架。它为机器人开发者提供了一套完整的工具、库和约定，使得构建复杂的机器人行为变得更加高效和可靠。本页面介绍ROS的基本概念、发展历史、系统架构以及生态系统。

ROS是最初用于机器人科研的操作系统。不同于一般的操作系统，ROS是在已有操作系统基础上的中间件 (middleware)。经过数十年的发展，ROS从ROS 1开始，演变出了适用于工业应用的ROS-I以及第二个大版本ROS 2. ROS目前由[OpenRobotics](https://www.openrobotics.org/)开发和维护。

## 什么是ROS

ROS并不是传统意义上的操作系统（如Windows或Linux），而是运行在操作系统之上的**中间件框架** (middleware framework)。它提供了硬件抽象 (hardware abstraction)、设备驱动 (device drivers)、进程间通信 (inter-process communication)、包管理 (package management) 等功能，使开发者能够专注于机器人应用逻辑的开发，而无需从零开始实现底层功能。

ROS的核心设计理念包括：

- **点对点通信** (Peer-to-Peer)：各节点之间直接通信，避免单点瓶颈
- **多语言支持** (Multi-language Support)：支持C++、Python等多种编程语言
- **工具丰富** (Rich Tooling)：提供可视化、调试、仿真等大量开发工具
- **开源免费** (Open Source)：采用BSD许可证，可自由使用和修改
- **社区驱动** (Community-driven)：拥有庞大的全球开发者社区

## 发展历史

ROS的发展历程可以追溯到2007年：

- **2007年**：斯坦福大学人工智能实验室 (Stanford AI Lab) 的Morgan Quigley开始开发Switchyard项目，这是ROS的前身
- **2008年**：Willow Garage公司接手开发，正式命名为ROS
- **2010年**：ROS 1.0 (Box Turtle) 首个正式版本发布
- **2012年**：Open Source Robotics Foundation (OSRF) 成立，负责ROS的长期维护
- **2013年**：ROS-Industrial (ROS-I) 项目启动，将ROS引入工业制造领域
- **2017年**：ROS 2首个正式版本Ardent Apalone发布
- **2020年**：ROS 2 Foxy Fitzroy发布，成为首个长期支持 (LTS) 版本
- **2025年**：ROS 1最后一个版本Noetic Ninjemys结束支持，ROS 2成为主要开发方向

## 系统架构

### 计算图 (Computation Graph)

ROS的核心架构基于**计算图** (Computation Graph) 的概念。计算图是由多个ROS进程组成的网络，这些进程通过ROS的通信基础设施相互连接。计算图的主要组成部分包括：

- **节点 (Nodes)**：节点是ROS中最基本的计算单元。每个节点通常负责一个特定的功能，例如控制电机、处理传感器数据或执行路径规划。通过将功能分散到多个节点中，系统具有更好的模块化和容错能力。

- **话题 (Topics)**：话题是节点之间进行异步通信的命名通道。一个节点可以向话题**发布** (publish) 消息，其他节点可以**订阅** (subscribe) 该话题来接收消息。话题采用发布-订阅 (publish-subscribe) 模式，适用于传感器数据流等连续数据传输场景。

- **服务 (Services)**：服务提供了一种同步的请求-响应 (request-response) 通信机制。一个节点作为服务端 (server) 提供服务，另一个节点作为客户端 (client) 发送请求并等待响应。服务适用于需要确认结果的短暂交互，例如查询机器人状态。

- **动作 (Actions)**：动作是一种用于长时间运行任务的通信机制，它结合了话题和服务的特点。动作允许客户端发送目标 (goal)，服务端在执行过程中提供反馈 (feedback)，并在完成时返回结果 (result)。典型应用场景包括导航到目标点、执行机械臂运动等。

- **消息 (Messages)**：消息是节点之间传输的数据结构，使用`.msg`文件定义。ROS提供了大量标准消息类型，如`geometry_msgs/Twist`（速度指令）和`sensor_msgs/Image`（图像数据）。

### 参数服务器 (Parameter Server)

参数服务器是一个共享的多变量字典，节点可以通过它存储和检索运行时的配置参数。在ROS 1中，参数服务器是集中式的；在ROS 2中，参数被分布到各个节点上管理。

## 构建系统

ROS使用专门的构建系统来编译和管理软件包 (packages)：

- **catkin**：ROS 1的标准构建系统，基于CMake。它引入了工作空间 (workspace) 的概念，使用`catkin_make`或`catkin build`命令进行编译
- **colcon**：ROS 2的标准构建系统，全称为"collective construction"。colcon支持多种构建类型（CMake、Python setuptools等），使用`colcon build`命令进行编译
- **ament**：ROS 2底层的构建系统，colcon在其基础上运行，负责处理包的依赖关系和安装

## ROS生态系统

ROS拥有丰富的生态系统，涵盖了机器人开发的各个方面：

- **Gazebo**：强大的三维物理仿真环境，支持多种传感器和机器人模型的仿真
- **RViz**：三维可视化工具，用于显示传感器数据、机器人模型和规划路径
- **MoveIt**：机械臂运动规划框架，提供运动学求解、碰撞检测和轨迹规划
- **Navigation Stack**：移动机器人导航框架，提供定位 (localization)、路径规划 (path planning) 和避障 (obstacle avoidance) 功能
- **tf/tf2**：坐标变换库，管理机器人各部件之间以及与环境之间的坐标关系
- **rosbag**：数据记录和回放工具，用于保存和重播ROS消息数据
- **rqt**：基于Qt的图形化工具集，提供话题监控、参数调整等多种插件

## 社区与资源

ROS的成功离不开其活跃的全球社区。主要社区资源包括：

- **ROS Wiki** ([wiki.ros.org](http://wiki.ros.org))：ROS 1的官方文档和教程
- **ROS 2 Documentation** ([docs.ros.org](https://docs.ros.org))：ROS 2的官方文档
- **ROS Discourse** ([discourse.ros.org](https://discourse.ros.org))：社区讨论论坛
- **ROS Answers** ([answers.ros.org](https://answers.ros.org))：技术问答平台
- **ROSCon**：每年举办的ROS开发者大会，分享最新技术和应用案例
- **GitHub**：大量开源ROS软件包托管在GitHub上，方便协作开发

## 参考资料

1. [About ROS](https://www.ros.org/about-ros/), ROS Official Website
2. [ROS Wiki](http://wiki.ros.org/), Open Source Robotics Foundation
3. [ROS 2 Documentation](https://docs.ros.org/), Open Source Robotics Foundation
4. Quigley, M., Conley, K., Gerkey, B., et al. "ROS: an open-source Robot Operating System." *ICRA Workshop on Open Source Software*, 2009
