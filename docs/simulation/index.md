# 机器人仿真

!!! note "引言"
    机器人系统的开发与验证离不开仿真（Simulation）工具的支持。在真实硬件平台上调试算法代价高昂：一次失误可能损坏价值数万元的机械臂或移动底盘，强化学习（Reinforcement Learning）所需的数百万次探索在物理机器人上几乎无法实现，而危险场景（如消防机器人、核电检修机器人）更无法反复重演。仿真环境让研究者和工程师能够在安全、快速、可重复的虚拟世界中完成大部分开发工作，再将经过验证的算法迁移到真实机器人上。本章系统介绍机器人仿真的核心价值、主流工具与典型工作流程，并为不同应用场景提供选型建议。


## 仿真的核心价值

### 安全性

在真实机器人上进行算法测试存在不可忽视的风险。探索阶段的控制器输出可能导致机器人碰撞、摔倒或损坏周围设备；在工业场景中，机器人失控还可能危及操作人员的人身安全。仿真环境中的"碰撞"只是一次数值计算错误，不会造成任何实际损失，研究者可以放心地让机器人尝试各种激进策略。

### 速度

仿真通常可以以远超实时的速度运行。以 MuJoCo 为例，在现代 GPU 上进行并行仿真时，其运行速度可以达到真实时间的数千倍。这意味着强化学习智能体在数小时内可以积累相当于真实世界数年的经验，极大地压缩了研究周期。

### 可扩展性

仿真支持大规模并行化（Parallelization）。同一套代码可以在数千个独立的仿真环境中同时运行，每个环境使用不同的随机种子或参数配置，从而高效地进行超参数搜索、策略评估和数据采集。这在真实硬件上几乎无法实现。

### 可重复性

仿真环境可以精确复现任意场景：相同的初始状态、相同的控制指令、相同的随机种子将产生完全一致的运行结果。这一特性对于算法调试（逐步分析失败原因）、基准测试（公平比较不同算法）和论文复现（他人验证研究结论）都至关重要。

### 边缘场景测试

真实世界中的罕见事件（如传感器突发故障、极端天气、意外障碍物）难以在实验室中刻意重现。仿真可以按需构造这些边缘情况（Edge Case），系统性地验证机器人在异常条件下的鲁棒性，确保部署前充分覆盖各类故障模式。


## 仿真的主要应用场景

### 算法开发与快速迭代

控制算法（路径规划、轨迹优化、运动控制）在仿真中的验证周期远短于在硬件上的验证周期。开发者可以在几分钟内完成"修改代码 → 重新编译 → 仿真运行 → 分析结果"的完整迭代循环，而无需等待机器人复位、充电或维修。

### 强化学习训练与 Sim-to-Real 迁移

当前最先进的足式机器人运动控制（如 ANYmal、Unitree 等平台上的敏捷运动策略）几乎全部依赖仿真训练。训练一个能够在复杂地形上稳定行走的策略通常需要数十亿次环境交互，这只能在仿真中完成。训练完成后，通过域随机化（Domain Randomization）等技术将策略迁移到真实机器人，这一过程称为 Sim-to-Real 迁移。

### 安全验证

自动驾驶汽车、手术机器人、工业协作机器人在实际部署前必须经过严格的安全验证。仿真提供了一种系统性的测试手段：可以构造数万种危险场景（行人突然横穿、传感器遮挡、电源波动），验证机器人的安全保护机制是否可靠，而无需将真人或昂贵设备置于风险之中。

### 合成数据生成

计算机视觉（Computer Vision）模型的训练需要大量标注数据。在仿真中，相机、激光雷达（LiDAR）等传感器的输出可以自动附带精确的标注信息（物体类别、实例分割掩码、深度图、3D 包围框），无需人工标注。NVIDIA Isaac Sim 等平台已将合成数据生成（Synthetic Data Generation）作为核心功能之一。

### 数字孪生

数字孪生（Digital Twin）是与真实物理系统实时同步的高精度仿真模型。通过将真实机器人的传感器数据持续输入仿真，可以实现远程监控、故障预测、操作员培训和虚拟调试。工业机器人制造商（如 KUKA、ABB）和工厂自动化领域已广泛应用这一概念。


## 仿真引擎与物理引擎

理解"物理引擎"与"仿真平台"的区别，有助于正确选择工具。

### 物理引擎

物理引擎（Physics Engine）负责数值求解刚体动力学方程，处理碰撞检测（Collision Detection）与接触力计算（Contact Force Computation）。它是仿真的计算核心，通常以库的形式提供，本身不包含可视化界面。

| 物理引擎 | 开发方 | 主要特点 | 典型应用场景 |
|---------|--------|---------|------------|
| ODE（Open Dynamics Engine） | Russell Smith | 成熟稳定，开源，接触处理较为简单 | Gazebo 早期默认引擎 |
| Bullet Physics | Erwin Coumans | 开源，支持软体仿真，PyBullet Python 接口成熟 | 游戏、研究 |
| PhysX 5 | NVIDIA | 高性能，GPU 加速，支持流体和软体 | Isaac Sim、游戏引擎 |
| MuJoCo（MJX） | DeepMind / Google | 约束求解器精度高，JAX 后端支持 GPU 并行 | 强化学习研究 |
| DART | Georgia Tech | 接触动力学精确，支持多种积分方案 | 学术研究、Gazebo |
| Simbody | SimTK | 面向生物力学，约束处理严谨 | OpenSim、Gazebo |

### 仿真平台

仿真平台（Simulation Platform）在物理引擎之上进行封装，额外提供以下功能：

- **可视化渲染（Visualization）**：实时 3D 场景显示，便于观察机器人行为；
- **机器人模型库**：内置常见机器人（机械臂、移动底盘、无人机）的模型或导入接口；
- **传感器仿真**：模拟摄像头（RGB/深度）、激光雷达、IMU（惯性测量单元）、力/力矩传感器等；
- **中间件集成**：提供 ROS（Robot Operating System）话题接口或专用 Python/C++ API；
- **场景编辑器**：图形化的环境搭建工具，支持拖放障碍物、调整光照等操作。

理解这一分层结构后，在评估一个仿真平台时，应当同时考察其底层物理引擎的特性和上层工具链的完善程度。


## 主流仿真平台对比

下表汇总了当前机器人领域最常用的仿真平台，供选型参考。

| 平台 | 开发方 | 物理引擎 | 开源/商业 | ROS 支持 | 强化学习支持 | 适用场景 |
|------|--------|---------|---------|---------|------------|---------|
| Gazebo / Harmonic | OSRF | ODE / Bullet / DART | 开源（Apache 2.0） | 深度集成（原生） | 一般 | 移动机器人、ROS 生态 |
| MuJoCo | DeepMind | 自研（MJX） | 开源（Apache 2.0） | 有限 | 极强 | 强化学习研究 |
| Isaac Sim | NVIDIA | PhysX 5 | 商业（提供免费许可） | 支持（ROS 2） | 强（Isaac Lab） | AI 训练、工业仿真、合成数据 |
| Webots | Cyberbotics | ODE | 开源（Apache 2.0） | 支持 | 一般 | 教育、快速原型 |
| CoppeliaSim（原 V-REP） | Coppelia Robotics | 多引擎可选 | 商业（提供教育版） | 支持 | 有限 | 工业机械臂、复杂场景 |
| PyBullet | Bullet Physics | Bullet | 开源（zlib） | 有限 | 强 | 轻量级研究、强化学习 |
| Robotics Toolbox | Peter Corke | 纯数值（无物理） | 开源（MIT） | 可选 | 一般 | 教学、算法验证 |
| Stage | Player Project | 2D 近似 | 开源（GPL） | 支持 | — | 大规模 2D 移动机器人 |
| Unreal Engine | Epic Games | PhysX / Chaos | 商业（提供免费许可） | 有限 | 有限 | 高保真渲染、无人机仿真 |
| Unity | Unity Technologies | PhysX / Havok | 商业（提供免费许可） | 有限 | 有限（ML-Agents） | 具身智能研究、数据采集 |

### 各平台简述

**Gazebo / Harmonic**：由开源机器人基金会（Open Source Robotics Foundation, OSRF）维护，是 ROS 生态系统的标准仿真平台。新版本 Gazebo Harmonic（原称 Ignition Gazebo）采用模块化架构，支持多物理引擎切换。对 ROS 2 的支持最为完善，是移动机器人和 ROS 开发者的首选。

**MuJoCo**：以其高精度的接触动力学和简洁的 XML 模型格式著称，被学术界强化学习研究广泛采用。DeepMind 于 2022 年将其开源，并推出基于 JAX 的 MJX 后端，支持在 GPU 上进行大规模并行仿真。OpenAI Gym / Gymnasium 的大量标准环境（如 HalfCheetah、Ant、Humanoid）均基于 MuJoCo。

**Isaac Sim / Isaac Lab**：NVIDIA 推出的高端仿真平台，构建于 Omniverse 平台之上，使用 USD（Universal Scene Description）格式描述场景，支持光线追踪（Ray Tracing）级别的高保真渲染和 PhysX 5 的 GPU 加速物理计算。Isaac Lab 是其上层的强化学习训练框架，已成为足式机器人和灵巧手研究的重要工具。

**Webots**：界面友好，内置丰富的机器人和传感器模型库，跨平台支持良好（Windows / macOS / Linux）。因其上手门槛低、文档完善，在高校教学和机器人竞赛中应用广泛。

**CoppeliaSim（V-REP）**：功能全面，脚本编程灵活，支持 Lua、Python、MATLAB、Java 等多种控制接口，尤其擅长工业机械臂和多机器人协作场景的仿真。

**PyBullet**：Bullet 物理引擎的 Python 接口，安装简便（`pip install pybullet`），无需复杂环境配置。对于需要快速构建自定义强化学习环境的研究者而言，PyBullet 是轻量高效的选择。

**Robotics Toolbox（Peter Corke 版）**：专注于机器人运动学和动力学的数值计算，而非物理仿真。适合学习和验证正向运动学（Forward Kinematics）、逆向运动学（Inverse Kinematics）、雅可比矩阵（Jacobian）等算法，是机器人学课程的常用工具。

**Stage**：专为大规模二维移动机器人仿真设计，计算开销极低，可以同时运行数百个机器人，历史上常与 Player 中间件配合使用，在多机器人系统研究中发挥过重要作用。

**Unreal Engine**：以极高的渲染质量著称，Microsoft AirSim 项目曾基于 UE 构建无人机和自动驾驶仿真环境。适合对视觉逼真度有极高要求的感知算法研究，但学习曲线较陡。

**Unity**：凭借 Unity ML-Agents 工具包在具身智能（Embodied AI）研究中获得关注。Unity Robotics Hub 提供了与 ROS 的通信接口，适合需要高质量渲染且希望利用 Unity 丰富生态的场景。


## 典型仿真工作流程

一个完整的机器人仿真项目通常包含以下步骤：

### 第一步：机器人模型导入

仿真的基础是机器人的数字化模型。常用的机器人模型格式包括：

- **URDF（Unified Robot Description Format）**：XML 格式，ROS 生态系统的标准格式，描述机器人的连杆（Link）和关节（Joint）结构、惯性参数和碰撞几何体；
- **SDF（Simulation Description Format）**：Gazebo 使用的扩展格式，在 URDF 基础上增加了传感器、插件和世界描述；
- **USD（Universal Scene Description）**：NVIDIA Omniverse / Isaac Sim 使用的格式，支持复杂场景的层级化描述和高保真材质。

大多数机器人制造商会提供官方 URDF 模型（如 Franka Emika Panda、Universal Robots UR5、Boston Dynamics Spot）。若没有现成模型，可以从 CAD 文件（STEP/STL 格式）转换生成。

### 第二步：环境搭建

在机器人模型就位后，需要构建仿真世界：

- **地形与障碍物**：平坦地面、楼梯、斜坡、砂石地形等；
- **可交互物体**：桌子、箱子、门等，用于抓取、推拉、开关等任务；
- **光照设置**：影响视觉传感器的仿真效果，对合成数据生成尤为重要。

### 第三步：传感器配置

仿真平台可以模拟各类传感器，使算法在仿真中获得与真实机器人类似的感知输入：

- **RGB 摄像头**：返回彩色图像，可配置分辨率、视场角、帧率；
- **深度摄像头（Depth Camera）**：返回深度图像或点云（Point Cloud）；
- **激光雷达（LiDAR）**：返回 2D 或 3D 扫描点云，可配置线数和扫描范围；
- **IMU（Inertial Measurement Unit）**：返回加速度和角速度数据，可添加噪声模型；
- **关节编码器（Joint Encoder）**：返回关节位置、速度和力矩；
- **力/力矩传感器（Force/Torque Sensor）**：用于接触力感知和阻抗控制。

### 第四步：控制接口对接

仿真平台通常提供以下控制接口：

- **ROS 话题（Topic）与服务（Service）**：与真实机器人使用相同的通信接口，便于算法无缝切换；
- **Python API**：直接通过脚本控制仿真，适合强化学习训练循环；
- **C++ API**：性能更高，适合对延迟敏感的实时控制仿真；
- **Gym / Gymnasium 接口**：标准化的强化学习环境接口，输入动作、输出观测和奖励。

### 第五步：数据采集与分析

仿真运行结束后，需要对采集的数据进行分析：

- 关节轨迹、末端执行器位置的可视化与分析；
- 任务完成率、累积奖励等性能指标的统计；
- 传感器数据的录制与回放；
- 与真实硬件数据的对比，评估仿真精度。


## 仿真精度与计算代价的权衡

仿真精度越高，所需的计算资源通常也越大。工程实践中需要在仿真保真度（Fidelity）与运行效率之间找到平衡点。

### 不同保真度层次

**低保真度仿真（Low-Fidelity）**：忽略接触动力学细节，使用简化的运动学模型，运行速度极快。Stage 的 2D 仿真和 Robotics Toolbox 的纯数值计算属于这一类。适合概念验证阶段和对精度要求不高的导航算法研究。

**中等保真度仿真（Mid-Fidelity）**：使用完整的刚体动力学方程和近似接触模型，兼顾精度与效率。Gazebo（ODE 引擎）、PyBullet 和 Webots 属于这一类，是大多数机器人算法研究的主流选择。

**高保真度仿真（High-Fidelity）**：精细建模接触动力学、柔性体形变、流体-固体耦合、传感器物理特性（如相机的景深模糊、激光雷达的多径反射），以及高质量光线追踪渲染。Isaac Sim 和 MuJoCo（精细调参后）属于这一类，但计算代价显著更高。

### 根据任务选择保真度

实际项目中常用"粗筛细验"策略：

1. 在低/中保真度仿真中快速迭代算法设计，筛选有潜力的方案；
2. 在高保真度仿真中对筛选出的方案进行精细验证；
3. 最终在真实硬件上进行少量实验确认。

这一分层验证策略在保证研究质量的同时，大幅降低了总体计算成本和硬件损耗。


## Sim-to-Real 挑战

仿真与现实之间存在不可消除的差距，称为"现实差距"（Reality Gap）。理解其根本原因，是设计有效迁移策略的前提。

### 主要差距来源

**接触与摩擦建模（Contact and Friction Modelling）**

接触力的精确仿真是机器人仿真最困难的问题之一。真实接触涉及微观表面变形、材料弹性、热效应等复杂物理现象，而仿真中通常使用简化的弹簧-阻尼模型或约束求解器近似处理。摩擦系数的微小偏差即可导致灵巧手抓取策略在真实硬件上失效。

**执行器动力学（Actuator Dynamics）**

真实电机存在反向间隙（Backlash）、摩擦（Friction）、电气延迟（Electrical Delay）和热效应，而仿真中的关节通常被理想化为能够精确跟踪目标力矩或速度的理想执行器。这一差异在高频控制场景下尤为显著。

**传感器噪声（Sensor Noise）**

真实传感器的输出包含系统误差和随机噪声。例如，真实激光雷达在玻璃、镜面或黑色吸光材料上会产生异常测量值，而仿真中的激光雷达通常是完美的射线检测。

**模型参数误差（Model Parameter Uncertainty）**

机器人的惯性参数（质量、质心位置、转动惯量）、关节刚度和阻尼系数往往只能通过近似测量获得，真实值与仿真模型之间存在偏差。

### 缓解策略

**域随机化（Domain Randomization）**

在训练过程中，对仿真中的物理参数（摩擦系数、质量、阻尼）、视觉参数（纹理、光照、相机位置）进行随机化，使训练出的策略对参数变化具有鲁棒性。当真实世界被视为随机化参数空间中的"一个实例"时，策略自然能够泛化到真实环境。这一方法由 OpenAI 在灵巧手操作研究中得到广泛验证。

**系统辨识（System Identification）**

通过对真实机器人进行受控实验，测量并拟合仿真模型的关键参数，使仿真尽可能准确地反映真实系统的动力学特性。自适应系统辨识方法可以在机器人运行过程中持续更新模型参数。

**渐进式迁移（Progressive Transfer）**

采用课程学习（Curriculum Learning）策略，先在精确仿真中训练，逐步引入噪声和不确定性，最终在真实硬件上进行少量微调（Fine-tuning）。一些研究在仿真预训练后，仅需真实机器人数分钟的交互即可完成有效迁移。

**仿真-真实混合训练（Sim-Real Hybrid Training）**

将少量真实硬件数据与大量仿真数据混合使用。真实数据弥补仿真的系统偏差，仿真数据弥补真实数据的稀缺性，两者形成互补。

**自适应仿真参数更新（Adaptive Simulation Update）**

利用真实机器人在部署后收集的数据，持续更新仿真模型的参数估计，使仿真随时间越来越接近真实系统。这一思路在数字孪生框架下尤为自然，也是当前工业机器人领域的研究热点。


## 选型建议

根据不同的应用场景，以下是仿真平台的推荐选择：

| 应用场景 | 推荐平台 | 理由 |
|---------|---------|------|
| 移动机器人 + ROS 开发 | Gazebo / Harmonic | 与 ROS 2 深度集成，导航、SLAM 工具链完善 |
| 强化学习 + 足式机器人 | MuJoCo / Isaac Lab | 接触动力学精度高，GPU 并行训练效率高 |
| 工业机械臂仿真 | CoppeliaSim / Isaac Sim | 运动规划接口完善，支持工业流程建模 |
| 灵巧手抓取研究 | MuJoCo / Isaac Sim | 高精度接触仿真，支持复杂物体交互 |
| 合成数据生成 | Isaac Sim | 光线追踪渲染，自动标注，域随机化工具完善 |
| 教学与课程 | Webots / PyBullet | 安装简便，文档丰富，学习曲线平缓 |
| 快速算法验证 | PyBullet / Robotics Toolbox | 零配置，Python 原生，适合快速迭代 |
| 2D 大规模多机器人 | Stage | 计算开销极低，支持数百机器人并发 |
| 无人机 / 自动驾驶感知 | Unreal Engine (AirSim) | 高保真视觉渲染，逼真的户外环境 |
| 具身智能 / 视觉导航 | Unity (ML-Agents) | 场景多样，渲染质量高，Gym 接口支持 |

**一般性建议：**

1. 如果项目以 ROS 为核心中间件，优先选择 **Gazebo**，其余平台均需额外的桥接工作；
2. 如果核心任务是强化学习训练，**MuJoCo** 是学术界的基准平台，**Isaac Lab** 则适合工业规模训练；
3. 对于初学者，**Webots** 或 **PyBullet** 的入门门槛最低；
4. 对于需要高保真渲染（合成数据、感知研究），**Isaac Sim** 是当前最成熟的选择；
5. 不同平台并不互斥，同一项目中可以组合使用：例如用 MuJoCo 训练控制策略，再用 Isaac Sim 验证感知模块；
6. 在计算资源有限的情况下，优先考虑 **PyBullet** 或 **Webots**；在拥有多块 NVIDIA GPU 的工作站或集群上，**Isaac Sim / Isaac Lab** 和 **MuJoCo MJX** 能够充分发挥硬件性能。


## 本章内容

面向机器人学习的完整实验流程，见[机器人学习仿真与评测](robot-learning-benchmarks.md)：涵盖 ManiSkill、LIBERO、SimplerEnv、并行采样、域随机化和可复现评测。


本章依次介绍各主流仿真平台的功能特性、安装方式与典型使用示例，涵盖以下工具：

- **[Gazebo](gazebo.md)**：ROS 生态系统的标准仿真平台，支持 ODE、Bullet、DART 等多种物理引擎，适合移动机器人与 ROS 开发；
- **[MuJoCo](mujoco.md)**：DeepMind 开源的高精度物理仿真引擎，强化学习研究的事实标准，提供 MJX GPU 并行后端；
- **[NVIDIA Isaac Sim](nvidiaomniverse.md)**：基于 NVIDIA Omniverse 平台构建，集高保真渲染、PhysX 5 物理引擎与 Isaac Lab 强化学习框架于一体；
- **[PyBullet](pybullet.md)**：Bullet 物理引擎的 Python 接口，轻量易用，是强化学习研究的常用工具；
- **[Webots](webots.md)**：Cyberbotics 维护的开源仿真平台，内置丰富的机器人模型库，适合教育与快速原型开发；
- **[CoppeliaSim（V-REP）](vrep.md)**：支持多种物理引擎和脚本语言，功能全面，擅长工业机械臂和复杂多机器人场景；
- **[MATLAB Robotics Toolbox](robotics-toolbox.md)**：Peter Corke 开发的机器人学计算工具箱，涵盖运动学、动力学和路径规划算法；
- **[Stage](stage.md)**：专为 2D 大规模移动机器人仿真设计，计算效率极高，支持数百机器人并发运行；
- **[Unreal Engine](unreal.md)**：Epic Games 的高保真游戏引擎，通过 AirSim 等插件支持无人机和自动驾驶仿真；
- **[Unity](unity.md)**：Unity Technologies 的游戏引擎，通过 ML-Agents 和 Robotics Hub 支持具身智能研究与 ROS 集成。

读者可以根据自身项目需求，结合本页的选型建议，选择对应的子章节深入阅读。


## 参考资料

1. Korber, M., Lange, J., Rediske, S., Steinmann, S., & Glück, R. (2021). Comparing popular simulation environments in the scope of robotics and reinforcement learning. *arXiv preprint arXiv:2103.04616*.
2. Muratore, F., Ramos, F., Turk, G., Yu, W., Gienger, M., & Peters, J. (2022). Robot learning from randomized simulations: A review. *Frontiers in Robotics and AI, 9*, 799893.
3. Tobin, J., Fong, R., Ray, A., Schneider, J., Zaremba, W., & Abbeel, P. (2017). Domain randomization for transferring deep neural networks from simulation to the real world. *IROS 2017*.
4. OpenAI, Andrychowicz, M., et al. (2019). Solving Rubik's cube with a robot hand. *arXiv preprint arXiv:1910.07113*.
5. Kumar, V., & Todorov, E. (2015). MuJoCo HAPTIX: A virtual reality system for hand manipulation. *IEEE-RAS HUMANOIDS 2015*.
6. 胡春旭, [ROS探索总结（五十八）—— Gazebo物理仿真平台](https://www.guyuehome.com/2256), 古月居.
7. 胡春旭, [ROS史话36篇 | 25. ROS之皆大欢喜（Player与Stage）](https://zhuanlan.zhihu.com/p/74552944), 知乎.
8. 任赜宇, [为什么要机器人仿真](https://www.zhihu.com/question/356929288/answer/913298986), 知乎.
9. 幻生如梦, [PyBullet快速上手教程](https://blog.csdn.net/yingyue20141003/article/details/89044438), CSDN.
10. 戴晓天, [机器人常用可视化仿真工具 - 云飞机器人实验室](https://www.yfworld.com/?p=5453).
11. NVIDIA, [Isaac Lab Documentation](https://isaac-sim.github.io/IsaacLab/), NVIDIA Developer.
12. Todorov, E., Erez, T., & Tassa, Y. (2012). MuJoCo: A physics engine for model-based control. *IROS 2012*.
