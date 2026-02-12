# Gazebo
![5e430036ce538f09f700003a](assets/60a72bfdcfe94089a089280ea3a1c14e.png)

- 官方网站：http://gazebosim.org/
- 支持的物理引擎：ODE/Bullet/Simbody/DART
- 开源仿真环境
- 属于ROS生态

!!! note "引言"
    Gazebo是目前最广泛使用的机器人仿真环境，最早在2004年由USC Robotics Research Lab (南加州大学机器人实验室) 开发。依托于ROS的发展，Gazebo具有很强的仿真能力，同时也在机器人研究和开发中得到了广泛应用。Gazebo的功能包括：动力学仿真 (Dynamics Simulation)、传感器仿真 (Sensor Simulation)、三维环境仿真 (3D Environment Simulation)，同时支持多种机器人模型：包括PR2、Turtlebot、AR.Drone等。

## Gazebo Classic 与 Gazebo (Ignition/Gz)

Gazebo项目经历了重要的版本演变。**Gazebo Classic**（版本1至11）是长期以来被广泛使用的版本，其最终版本Gazebo 11已于2025年停止官方支持。**Gazebo**（前称Ignition Gazebo，后更名为Gz）是新一代仿真平台，采用模块化架构 (Modular Architecture) 重新设计，提供更灵活的组件化系统。新版Gazebo使用Gz Transport通信层替代了旧版的自定义通信方式，并引入了更先进的渲染引擎Ogre2。

## 系统架构

Gazebo采用客户端-服务器架构 (Client-Server Architecture)：

- **gzserver**：负责物理仿真计算、传感器数据生成以及世界状态的维护。该进程在后台运行，不依赖图形界面。
- **gzclient**：提供三维可视化界面，用户可以通过图形界面观察仿真场景、插入模型以及调整仿真参数。

这种架构设计使得仿真计算与可视化分离，允许在无头模式 (Headless Mode) 下运行仿真，适合在服务器或CI/CD流水线中进行自动化测试。

## 传感器支持

Gazebo内置了丰富的传感器模型 (Sensor Models)，覆盖了机器人常用的感知设备：

- **相机 (Camera)**：包括单目相机、双目相机 (Stereo Camera)、深度相机 (Depth Camera) 以及全景相机
- **激光雷达 (LiDAR)**：支持二维和三维激光扫描仪，可配置扫描范围、分辨率和噪声参数
- **惯性测量单元 (IMU)**：模拟加速度计和陀螺仪数据
- **GPS**：提供全局定位信息仿真
- **力/力矩传感器 (Force/Torque Sensor)**：用于检测关节处的力和力矩
- **接触传感器 (Contact Sensor)**：检测物体间的碰撞和接触状态

每种传感器均支持噪声模型 (Noise Model) 配置，使仿真数据更加贴近真实传感器的输出特性。

## 与ROS的集成

Gazebo与ROS (Robot Operating System) 的深度集成是其核心优势之一。通过 `gazebo_ros_pkgs` 功能包集，Gazebo能够将仿真数据以ROS话题 (Topic)、服务 (Service) 和动作 (Action) 的形式发布，使得相同的ROS节点代码可以无缝地在仿真环境与真实硬件之间切换。对于ROS 2，集成方式通过 `ros_gz_bridge` 桥接包实现，支持在Gz仿真与ROS 2之间转换消息格式。

## 模型格式：URDF 与 SDF

Gazebo支持两种主要的模型描述格式：

- **URDF (Unified Robot Description Format)**：ROS生态中标准的机器人描述格式，用于定义机器人的连杆 (Link)、关节 (Joint) 和运动学结构。URDF的局限性在于仅支持树状结构，不支持闭合运动链 (Closed Kinematic Chain)。
- **SDF (Simulation Description Format)**：Gazebo原生支持的仿真描述格式，功能比URDF更加丰富。SDF不仅可以描述机器人模型，还可以定义完整的仿真世界 (World)，包括光照、地形、物理参数等。SDF支持闭合运动链以及更复杂的传感器定义。

## 插件系统

Gazebo提供灵活的插件系统 (Plugin System)，允许用户在不修改源代码的情况下扩展仿真功能。插件主要分为以下几类：

- **World Plugin**：控制仿真世界的全局行为
- **Model Plugin**：附加到特定模型上，控制模型的运动或行为
- **Sensor Plugin**：自定义传感器的数据处理逻辑
- **Visual Plugin**：控制可视化渲染效果

插件使用C++编写，通过共享库 (Shared Library) 的方式动态加载。

## 安装方式

在Ubuntu系统上，可以通过APT包管理器安装Gazebo。以ROS 2 Humble配合Gz Fortress为例：

```bash
sudo apt install ros-humble-ros-gz
```

安装完成后，可以通过以下命令启动一个空白世界进行验证：

```bash
gz sim empty.sdf
```

## 优势与局限

**优势：**

- 与ROS生态无缝集成，社区庞大，文档资源丰富
- 支持多种物理引擎，灵活切换
- 传感器模型种类齐全，噪声模型可配置
- 插件系统扩展性强

**局限：**

- 视觉渲染质量相比游戏引擎 (如Unreal、Unity) 仍有差距
- 对于大规模场景或高精度接触仿真，性能可能成为瓶颈
- Gazebo Classic到新版Gazebo的迁移存在一定学习成本

## 参考资料

- [Gazebo官方文档](https://gazebosim.org/docs)
- [ROS 2与Gazebo集成教程](https://gazebosim.org/docs/fortress/ros2_integration)
- [SDF格式规范](http://sdformat.org/spec)
- Koenig, N., & Howard, A. (2004). Design and use paradigms for Gazebo, an open-source multi-robot simulator. *IEEE/RSJ International Conference on Intelligent Robots and Systems*.
