# ROS 2

!!! note "引言"
    ROS 2是ROS的第二代版本，旨在解决ROS 1在实时性、安全性、多平台支持和工业应用方面的局限性。ROS 2从底层重新设计了通信架构，采用DDS (Data Distribution Service) 作为中间件，使其能够满足从科研原型到工业部署的全场景需求。

## 概述

ROS 2的开发始于2015年，由Open Source Robotics Foundation (OSRF) 主导。与ROS 1的渐进式改进不同，ROS 2是一次彻底的架构重设计，保留了ROS 1的核心理念（模块化、工具丰富、社区驱动），同时从根本上解决了ROS 1的技术短板。

## 为什么需要ROS 2

随着机器人技术从实验室走向工业和商业应用，ROS 1的设计已无法满足新的需求：

- **工业级可靠性**：工厂、仓库和公共场所中的机器人需要7x24小时稳定运行
- **实时性要求**：运动控制、安全系统等场景需要确定性的响应时间
- **安全通信**：联网机器人需要防护未授权访问和数据篡改
- **跨平台部署**：机器人系统可能运行在Linux、Windows、macOS甚至RTOS上
- **多机器人协作**：现代机器人系统常常涉及多台机器人的协调工作
- **嵌入式集成**：微控制器和资源受限设备需要与ROS系统无缝连接

## 相比ROS 1的关键改进

### DDS通信中间件

ROS 2最根本的架构变化是采用DDS (Data Distribution Service) 作为底层通信中间件。DDS是一种由OMG (Object Management Group) 制定的工业标准通信协议，广泛应用于航空航天、国防和金融领域。

DDS的核心优势包括：

- **去中心化架构**：节点之间通过分布式发现协议自动互联，无需像ROS 1那样依赖中央Master节点
- **QoS策略 (Quality of Service)**：提供细粒度的通信质量控制，包括可靠性 (Reliability)、持久性 (Durability)、截止时间 (Deadline)、存活性 (Liveliness) 等策略
- **标准化协议**：基于成熟的工业标准，经过长期验证

ROS 2支持多种DDS实现，用户可以根据需求选择：

- **Fast DDS**（eProsima）：默认的DDS实现
- **Cyclone DDS**（Eclipse）：轻量高效的实现
- **Connext DDS**（RTI）：商业级实现，提供高级功能

### 实时性支持 (Real-time Support)

ROS 2在设计层面考虑了实时性需求：

- 通信层支持确定性延迟 (deterministic latency)
- 提供实时安全的内存分配策略
- 支持与实时操作系统（如RT-Linux）的集成
- 执行器 (Executor) 框架可配置不同的调度策略

### 安全机制 (Security)

ROS 2通过SROS2 (Secure ROS 2) 提供完整的安全框架：

- **身份认证** (Authentication)：验证节点身份
- **访问控制** (Access Control)：限制节点对话题和服务的访问权限
- **数据加密** (Encryption)：保护通信数据不被窃听

### 多平台支持

ROS 2支持在多种操作系统上运行：

- Ubuntu Linux（一级支持）
- Windows 10/11
- macOS
- 其他Linux发行版

### 多机器人支持

ROS 2通过DDS的**域 (Domain)** 概念原生支持多机器人系统。不同机器人可以被分配到不同的DDS域中以隔离通信，也可以通过桥接器实现跨域数据共享。

## 架构与核心概念

### 生命周期节点 (Lifecycle Nodes)

ROS 2引入了**管理节点** (Managed Nodes) 的概念，也称为生命周期节点 (Lifecycle Nodes)。这类节点具有明确定义的状态机：

- **Unconfigured**：节点已创建但未配置
- **Inactive**：节点已配置但未激活
- **Active**：节点正在运行
- **Finalized**：节点已清理完毕

生命周期管理使得系统启动、状态监控和故障恢复更加可控，是工业部署中的重要特性。

### 组件 (Components)

ROS 2支持将多个节点作为**组件** (Components) 加载到同一进程中运行。这种方式通过进程内通信 (intra-process communication) 避免了序列化和网络传输的开销，显著提升了性能。

### Launch系统

ROS 2的launch系统使用Python脚本替代了ROS 1的XML格式launch文件，提供更强大的编程能力：

- 支持条件启动和参数传递
- 支持事件驱动的启动逻辑
- 可以与生命周期节点配合实现有序启动

## colcon构建系统

colcon (collective construction) 是ROS 2的标准构建工具。相比ROS 1的catkin，colcon具有以下特点：

- 支持多种构建系统（CMake、Python setuptools、Cargo等）
- 逐包隔离编译，避免包之间的编译干扰
- 更清晰的工作空间管理

典型的ROS 2工作空间结构如下：

```
ros2_ws/
├── src/              # 源代码目录
│   ├── package_1/
│   │   ├── CMakeLists.txt
│   │   ├── package.xml
│   │   └── src/
│   └── package_2/
├── build/            # 编译中间文件
├── install/          # 安装目录（替代catkin的devel空间）
└── log/              # 日志文件
```

常用命令包括：

- `colcon build`：编译工作空间中的所有包
- `colcon build --packages-select <pkg>`：编译指定包
- `colcon test`：运行测试

## ROS 2版本

| 版本代号                                                     | 发布时间             | Logo                                                         | 终止维护日期   |
| ------------------------------------------------------------ | -------------------- | ------------------------------------------------------------ | -------------- |
| [Foxy Fitzroy](https://docs.ros.org/en/ros2_documentation/foxy/Releases/Release-Foxy-Fitzroy.html) | June 5, 2020         | ![Foxy logo](https://docs.ros.org/en/ros2_documentation/foxy/_images/foxy-small.png) | May 2023       |
| [Eloquent Elusor](https://docs.ros.org/en/ros2_documentation/foxy/Releases/Release-Eloquent-Elusor.html) | Nov 22nd, 2019       | ![Eloquent logo](https://docs.ros.org/en/ros2_documentation/foxy/_images/eloquent-small.png) | November 2020  |
| [Dashing Diademata](https://docs.ros.org/en/ros2_documentation/foxy/Releases/Release-Dashing-Diademata.html) | May 31st, 2019       | ![Dashing logo](https://docs.ros.org/en/ros2_documentation/foxy/_images/dashing-small.png) | May 2021       |
| [Crystal Clemmys](https://docs.ros.org/en/ros2_documentation/foxy/Releases/Release-Crystal-Clemmys.html) | December 14th, 2018  | ![Crystal logo](https://docs.ros.org/en/ros2_documentation/foxy/_images/crystal-small.png) | December 2019  |
| [Bouncy Bolson](https://docs.ros.org/en/ros2_documentation/foxy/Releases/Release-Bouncy-Bolson.html) | July 2nd, 2018       | ![Bouncy logo](https://docs.ros.org/en/ros2_documentation/foxy/_images/bouncy-small.png) | July 2019      |
| [Ardent Apalone](https://docs.ros.org/en/ros2_documentation/foxy/Releases/Release-Ardent-Apalone.html) | December 8th, 2017   | ![Ardent logo](https://docs.ros.org/en/ros2_documentation/foxy/_images/ardent-small.png) | December 2018  |
| [beta3](https://docs.ros.org/en/ros2_documentation/foxy/Releases/Beta3-Overview.html) | September 13th, 2017 |                                                              | December 2017  |
| [beta2](https://docs.ros.org/en/ros2_documentation/foxy/Releases/Beta2-Overview.html) | July 5th, 2017       |                                                              | September 2017 |
| [beta1](https://docs.ros.org/en/ros2_documentation/foxy/Releases/Beta1-Overview.html) | December 19th, 2016  |                                                              | July 2017      |
| [alpha1 - alpha8](https://docs.ros.org/en/ros2_documentation/foxy/Releases/Alpha-Overview.html) | August 31st, 2015    |                                                              | December 2016  |

## ROS 1与ROS 2对比

| 特性 | ROS 1 | ROS 2 |
| --- | --- | --- |
| 通信中间件 | 自定义TCPROS/UDPROS | DDS（工业标准） |
| 节点发现 | 依赖ROS Master（中心化） | DDS自动发现（去中心化） |
| 实时性 | 不支持 | 设计层面支持 |
| 安全性 | 无内置安全机制 | SROS2（认证、加密、访问控制） |
| 操作系统 | 主要支持Ubuntu Linux | Linux、Windows、macOS |
| 构建系统 | catkin | colcon / ament |
| Launch文件 | XML格式 | Python脚本（也支持XML和YAML） |
| 生命周期管理 | 无 | Lifecycle Nodes |
| QoS配置 | 无 | 丰富的QoS策略 |
| 多机器人 | 需要额外配置 | DDS域原生支持 |

## 从ROS 1迁移到ROS 2

对于现有的ROS 1项目，迁移到ROS 2有以下几种策略：

- **ros1_bridge**：ROS官方提供的桥接工具，允许ROS 1和ROS 2节点在同一系统中并行运行并互相通信，适合渐进式迁移
- **逐步迁移**：将ROS 1软件包逐个移植到ROS 2，通常需要修改构建配置、API调用和launch文件
- **完全重写**：对于较小的项目或需要大幅重构的项目，直接用ROS 2 API重写可能更高效

迁移过程中需要注意的主要变化包括：

- 将`CMakeLists.txt`和`package.xml`适配为ament格式
- 将回调函数和API调用更新为`rclcpp`（C++）或`rclpy`（Python）
- 将`.launch`文件转换为Python launch脚本
- 根据需要配置QoS策略

## 参考资料

1. Distributions, [ROS 2 Documentation](https://docs.ros.org/en/ros2_documentation/foxy/Releases.html)
2. [Design](https://design.ros2.org/), ROS 2 Design Documentation
3. [About DDS](https://www.omg.org/spec/DDS/), Object Management Group
4. [Migration Guide from ROS 1](https://docs.ros.org/en/rolling/How-To-Guides/Migrating-from-ROS1.html), ROS 2 Documentation
