# Linux

!!! note "引言"
    Linux是机器人系统中最常用的操作系统。其开源特性、高度可定制性以及对ROS等机器人框架的原生支持，使其成为机器人开发者的首选平台。本页面介绍Linux在机器人领域的应用、常用发行版、内核架构以及实时Linux技术。

Linux是机器人系统中最常用的操作系统之一。

## 为什么机器人开发首选Linux

与Windows和macOS相比，Linux在机器人领域具有显著优势：

- **开源免费**：Linux内核和大部分软件工具都是开源的，开发者可以自由使用、修改和分发，无需支付许可费用
- **ROS原生支持**：ROS (Robot Operating System) 主要面向Linux开发，Ubuntu是ROS官方支持的首选平台
- **高度可定制**：可以针对特定的机器人硬件裁剪和优化系统，去除不必要的组件以降低资源占用
- **强大的命令行工具**：Linux提供了丰富的命令行工具，便于远程管理、自动化脚本编写和系统调试
- **稳定性和可靠性**：Linux系统以长时间稳定运行著称，适合需要7x24小时工作的机器人系统
- **硬件支持广泛**：支持从微型单板计算机（如Raspberry Pi、NVIDIA Jetson）到高性能工作站的各种硬件平台
- **实时性扩展**：通过内核补丁和特殊配置，Linux可以满足实时控制的需求

## 机器人领域常用Linux发行版

在机器人开发中，最常使用的Linux发行版包括：

- **Ubuntu**：最主流的选择，是ROS官方推荐的操作系统。每个ROS版本对应特定的Ubuntu版本（如ROS 2 Humble对应Ubuntu 22.04）。Ubuntu提供了良好的硬件兼容性和丰富的软件包
- **Debian**：Ubuntu的上游发行版，更加稳定和精简，适合嵌入式机器人平台
- **Yocto / OpenEmbedded**：用于构建定制嵌入式Linux系统的框架，适合资源受限的机器人控制器和量产设备
- **Buildroot**：另一种嵌入式Linux构建系统，比Yocto更简单，适合快速构建小型系统

## 内核架构

Linux内核 (kernel) 是操作系统的核心，负责管理硬件资源和提供系统服务。其主要组成部分包括：

- **进程管理** (Process Management)：负责进程的创建、调度和终止。Linux使用CFS (Completely Fair Scheduler) 作为默认调度器
- **内存管理** (Memory Management)：管理物理内存和虚拟内存，包括页面分配、内存映射和交换空间 (swap)
- **文件系统** (File System)：支持多种文件系统格式，如ext4、Btrfs、XFS等。Linux遵循"一切皆文件"的设计哲学，设备和系统信息都通过文件接口访问
- **设备驱动** (Device Drivers)：提供与硬件设备交互的接口，包括传感器、电机控制器、摄像头等机器人常用设备
- **网络子系统** (Networking)：支持TCP/IP协议栈以及各种网络协议，为机器人之间以及机器人与云端的通信提供基础

## 实时Linux (Real-time Linux)

一般来说，在机器人系统中使用的Linux分为：

- 标准Linux
- 实时Linux（即RT-Linux；可以提供更好的实时性保障）

标准Linux内核采用抢占式调度 (preemptive scheduling)，但不能保证硬实时 (hard real-time) 的响应时间。对于机器人控制系统中需要严格时间保证的场景（如伺服电机控制、力控制），需要使用实时Linux。

其中，实时Linux又分为以下实现方式：

- RT-Patch
- Dual OS，如[Xenomai](https://source.denx.de/Xenomai/xenomai/-/wikis/home)和[RTAI](https://www.rtai.org/)

### PREEMPT_RT补丁 (RT-Patch)

PREEMPT_RT是Linux内核的实时性补丁，通过以下改造使标准Linux内核具备实时能力：

- 将内核中大部分不可抢占的区域改为可抢占
- 将硬中断处理程序转换为可调度的内核线程
- 使用优先级继承 (priority inheritance) 的互斥锁替代标准自旋锁
- 提供高精度定时器 (high-resolution timers) 支持

PREEMPT_RT的优势在于它保持了与标准Linux用户空间的完全兼容性，开发者可以使用常规的Linux API和工具。随着Linux内核的发展，PREEMPT_RT补丁正逐步被合并到主线内核中。

### Xenomai

[Xenomai](https://source.denx.de/Xenomai/xenomai/-/wikis/home)采用双内核 (Dual Kernel) 架构，在标准Linux内核之下运行一个实时微内核 (Cobalt)。实时任务直接由微内核调度，能够获得极低的延迟和极高的确定性。非实时任务则由标准Linux内核处理，两者通过共享机制协同工作。

### RTAI

[RTAI](https://www.rtai.org/) (Real-Time Application Interface) 与Xenomai类似，也采用双内核架构。RTAI在Linux内核之下插入一个实时硬件抽象层，实时任务具有最高优先级，标准Linux内核作为最低优先级的任务运行。

## 包管理 (Package Management)

Linux通过包管理器安装、更新和管理软件。在机器人开发中常用的包管理工具：

- **apt**：Debian/Ubuntu系列的包管理器，也是安装ROS的主要方式。常用命令如`apt update`、`apt install`、`apt upgrade`
- **pip**：Python包管理器，用于安装Python库和ROS 2的Python依赖
- **rosdep**：ROS专用的依赖管理工具，可以自动安装ROS软件包的系统依赖

## 网络基础

机器人系统通常需要网络通信来实现远程控制、多机协作和数据传输。Linux提供了完善的网络支持：

- **SSH (Secure Shell)**：远程登录机器人系统的标准方式，支持命令行操作和文件传输
- **ROS网络配置**：ROS 1需要配置`ROS_MASTER_URI`和`ROS_IP`环境变量；ROS 2基于DDS自动发现，配置更为简便
- **CAN总线**：Linux通过SocketCAN支持CAN (Controller Area Network) 总线通信，这是工业机器人和自动驾驶中常用的通信协议
- **EtherCAT**：通过IgH EtherCAT Master等开源实现，Linux支持EtherCAT工业以太网协议，广泛用于高性能运动控制

## 参考资料

1. [Xenomai](https://en.wikipedia.org/wiki/Xenomai), Wikipedia
2. [The Linux Kernel Archives](https://www.kernel.org/), Linux Kernel Organization
3. [PREEMPT_RT](https://wiki.linuxfoundation.org/realtime/start), The Linux Foundation
4. [Ubuntu for Robotics](https://ubuntu.com/robotics), Canonical
