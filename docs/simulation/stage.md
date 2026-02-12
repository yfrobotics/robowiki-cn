# Stage
![5e430036ce538f09f700003a](assets/1bf6e48d7432498b967434bd91f53213.png)

- 官方网站：http://wiki.ros.org/stage
- GitHub：https://github.com/rtv/Stage
- 属于ROS生态
- 许可：GPL 开源

!!! note "引言"
    Stage是一款轻量级的二维机器人仿真器 (2D Robot Simulator)，用于二维环境（无z轴高度信息）的仿真。最早于1999年由USC Robotics Research Lab (南加州大学机器人实验室) 的Richard Vaughan开发，常用于路径规划或多机器人 (Multi-Agent) 仿真。Stage的设计哲学是提供"足够好"的仿真精度来验证算法，同时保持极高的运行效率。

## 发展历程

- **1999年**：Richard Vaughan在USC开始开发Stage，作为Player/Stage项目的一部分
- **2001年**：随Player/Stage框架一同发布，成为早期机器人研究的重要工具
- **2004年**：Gazebo从Player/Stage项目中分离出来，成为独立的三维仿真器。Stage继续专注于二维仿真
- **ROS集成**：后期通过 `stage_ros` 包集成到ROS生态中，提供标准ROS话题接口

## Player/Stage 框架

Stage最初是Player/Stage框架的重要组成部分：

- **Player**：一个网络化的机器人设备服务器 (Robot Device Server)，为各种传感器和执行器提供统一的网络接口。客户端程序通过TCP/IP连接到Player服务器，以统一的方式访问机器人硬件
- **Stage**：作为Player的仿真后端，模拟一个二维世界中的多个机器人及其传感器。Stage将仿真数据以Player接口的形式发布，使得控制程序无需修改即可在仿真和真实硬件之间切换

虽然Player项目本身已不再活跃维护，但Player/Stage框架的设计理念（硬件抽象和仿真-实物无缝切换）对后来的ROS架构产生了深远影响。

## 二维仿真特性

Stage的仿真在二维平面上进行，核心特性包括：

- **二维栅格地图 (2D Occupancy Grid Map)**：使用位图 (Bitmap) 定义仿真环境，黑色区域表示障碍物，白色区域表示自由空间
- **简化的传感器模型**：提供二维激光扫描仪 (2D Laser Scanner)、声纳 (Sonar)、红外测距 (IR Ranger)、视觉传感器等的简化仿真
- **差速驱动模型 (Differential Drive Model)**：内置差速驱动和全向驱动 (Omnidirectional Drive) 等常用移动机器人运动模型
- **碰撞检测**：基于二维多边形的碰撞检测，计算效率高

## 多机器人仿真

Stage的最大优势在于多机器人仿真的效率。由于采用二维简化模型，Stage可以在单台计算机上同时仿真数百甚至上千个机器人，这是三维仿真器难以达到的规模。典型应用场景包括：

- **多机器人协同探索 (Multi-Robot Exploration)**：验证多机器人地图探索和任务分配算法
- **集群行为研究 (Swarm Behavior)**：研究大规模机器人集群的群体智能行为
- **多机器人路径规划 (Multi-Robot Path Planning)**：测试多机器人避碰和协调策略
- **覆盖算法 (Coverage Algorithms)**：验证区域覆盖和巡逻策略

## 与ROS的集成

Stage通过 `stage_ros` 功能包集成到ROS生态中。该包将Stage仿真的传感器数据和机器人状态以标准ROS话题发布：

- `/base_scan`：激光扫描数据 (`sensor_msgs/LaserScan`)
- `/odom`：里程计数据 (`nav_msgs/Odometry`)
- `/cmd_vel`：速度指令 (`geometry_msgs/Twist`)

这意味着为ROS编写的导航和规划算法（如Navigation Stack中的 `move_base`）可以直接在Stage仿真环境中运行和测试，无需任何代码修改。

## 世界文件格式 (World File)

Stage使用 `.world` 文件定义仿真场景，语法简洁直观：

```
# 定义地图
floorplan
(
  name "map"
  bitmap "hospital.png"
  size [40.0 20.0 1.0]
)

# 定义机器人
pioneer
(
  name "robot_0"
  pose [-5.0 2.0 0.0 90.0]
  sicklaser()
)
```

世界文件引用位图图像作为地图，并通过简单的参数块定义机器人的初始位置和搭载的传感器。

## 适用场景与局限

**适用场景：**

- 需要大规模多机器人仿真的研究
- 二维导航和路径规划算法的快速验证
- 计算资源有限的环境中进行算法开发
- 教学演示中需要快速运行的仿真

**局限性：**

- 仅支持二维仿真，无法模拟三维空间中的机器人运动（如无人机、人形机器人）
- 传感器模型较为简化，不适合需要高保真传感器数据的研究
- 不支持动力学仿真，机器人运动基于运动学模型
- 项目维护已不活跃，功能更新有限

## 参考资料

- [Stage ROS Wiki页面](http://wiki.ros.org/stage)
- [Stage GitHub仓库](https://github.com/rtv/Stage)
- [stage_ros功能包](http://wiki.ros.org/stage_ros)
- Vaughan, R. (2008). Massively multi-robot simulation in Stage. *Swarm Intelligence*, 2(2-4), 189-208.
- Gerkey, B. P., Vaughan, R. T., & Howard, A. (2003). The Player/Stage project: Tools for multi-robot and distributed sensor systems. *Proceedings of the International Conference on Advanced Robotics*.
