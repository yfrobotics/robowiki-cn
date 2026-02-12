# CoppeliaSim (V-REP)
![5e430036ce538f09f700003a](assets/534887811e604afe81aa7a71c95d5303.png)

- 官方网站：http://www.coppeliarobotics.com/
- 2019年11月由V-REP更名为CoppeliaSim
- 支持的物理引擎：ODE/Bullet/Vortex/Newton
- 教育版免费 / 商业版收费

!!! note "引言"
    CoppeliaSim（前身为V-REP，即Virtual Robot Experimentation Platform）是一款功能全面的机器人仿真平台。它拥有非常完善的物理仿真引擎，支持移动机器人、飞行机器人、人型机器人、多足机器人以及多轴机械手的运动学仿真。CoppeliaSim的仿真程度非常高，不仅可以仿真机器人的本体与多种传感器，还支持障碍物以及地形 (空中、地面、水底) 的仿真。作为已经商业化的软件，相比Gazebo有更好的稳定性与交互体验。

## 核心特性

CoppeliaSim的设计理念是提供一个集成化的开发环境 (Integrated Development Environment)，将建模、编程、仿真和分析集于一体。其核心特性包括：

- **多物理引擎支持**：用户可以在ODE、Bullet、Vortex和Newton四种物理引擎之间自由切换，针对不同仿真场景选择最合适的引擎
- **正/逆运动学求解器 (Forward/Inverse Kinematics Solver)**：内置高效的运动学计算模块，支持任意运动链结构
- **碰撞检测 (Collision Detection)**：提供快速且精确的碰撞检测功能，支持网格模型 (Mesh) 之间的干涉检测
- **最小距离计算 (Minimum Distance Calculation)**：实时计算任意两个物体之间的最短距离
- **动力学仿真 (Dynamics Simulation)**：精确模拟刚体动力学、关节摩擦、接触力等

## 脚本语言支持

CoppeliaSim支持使用多种编程语言编写控制脚本，十分适合于多机器人的仿真：

- **Lua**：CoppeliaSim的内置脚本语言 (Embedded Script Language)，支持直接在仿真场景中编写和调试
- **Python**：通过ZeroMQ Remote API或Legacy Remote API实现外部控制
- **C/C++**：适合对性能有较高要求的场景，通过Remote API或插件方式接入
- **Java**：提供Java版本的Remote API接口
- **MATLAB**：支持通过Remote API从MATLAB环境控制仿真

每个仿真对象 (Simulation Object) 可以附加独立的脚本，使得多机器人协同仿真的代码组织清晰且模块化。

## 远程API (Remote API)

CoppeliaSim提供两种远程API接口方式：

- **ZeroMQ Remote API**：新一代远程接口，基于ZeroMQ消息库和CBOR数据序列化，性能优于旧版API，支持所有API函数的调用
- **Legacy Remote API**：基于自定义Socket通信的传统接口，功能完整但性能较低

通过Remote API，外部程序可以控制仿真的启动、暂停和停止，读写仿真对象的位姿 (Pose)、速度和传感器数据，实现仿真环境与外部算法的交互。

## 场景编辑器 (Scene Editor)

CoppeliaSim内置了功能强大的场景编辑器，用户可以通过图形界面 (GUI) 进行以下操作：

- 导入CAD模型 (支持STL、OBJ等格式) 并构建机器人模型
- 通过拖拽方式组装连杆 (Link) 和关节 (Joint) 的层级关系
- 配置物理属性如质量 (Mass)、惯性张量 (Inertia Tensor)、摩擦系数 (Friction Coefficient) 等
- 布置仿真场景中的环境物体和障碍物

## 路径规划 (Path Planning)

CoppeliaSim集成了OMPL (Open Motion Planning Library) 运动规划库，支持多种路径规划算法：

- RRT (Rapidly-exploring Random Trees)
- RRT*
- PRM (Probabilistic Roadmap Method)
- BiTRRT、LBKPIECE等

用户可以为移动机器人或机械臂 (Manipulator) 进行无碰撞路径规划，规划结果可以直接在仿真中执行和验证。

## 传感器仿真

CoppeliaSim提供丰富的传感器仿真功能：

- **视觉传感器 (Vision Sensor)**：模拟相机图像采集，支持RGB、深度图 (Depth Map) 输出
- **近距离传感器 (Proximity Sensor)**：模拟红外、超声波等测距传感器
- **力传感器 (Force Sensor)**：检测关节或接触点的力和力矩
- **激光扫描仪 (Laser Scanner)**：通过视觉传感器组合模拟激光雷达

## 内置机器人模型

CoppeliaSim自带大量常见的机器人模型，可直接在仿真中使用：

- 工业机械臂：UR系列、KUKA系列、ABB系列等
- 移动机器人：Pioneer系列、youBot等
- 人形机器人：NAO、Baxter等
- 无人机：四旋翼模型

## 教育与研究应用

CoppeliaSim在教育领域有广泛应用。其教育版 (Edu Version) 免费提供给学生和教育机构使用，包含完整的仿真功能。许多大学的机器人课程使用CoppeliaSim作为实验平台，学生可以在无需真实硬件的情况下学习机器人控制、运动规划和计算机视觉等内容。此外，RoboCup等国际机器人竞赛也曾使用CoppeliaSim作为仿真平台。

## 参考资料

- [CoppeliaSim官方文档](https://www.coppeliarobotics.com/helpFiles/)
- [CoppeliaSim用户手册](https://manual.coppeliarobotics.com/)
- [ZeroMQ Remote API文档](https://www.coppeliarobotics.com/helpFiles/en/zmqRemoteApiOverview.htm)
- Rohmer, E., Singh, S. P. N., & Freese, M. (2013). V-REP: A versatile and scalable robot simulation framework. *IEEE/RSJ International Conference on Intelligent Robots and Systems*.
