# 机器人资源

本栏目包括机器人相关的软件、硬件、信息及图书等资源。

## 栏目概览

本资源栏目旨在为机器人领域的学习者和从业者提供系统化的参考资料，内容包括：

- **工具与软件**：机器人开发常用的操作系统、仿真平台、算法库和开发工具
- **图书**：机器人各个子领域的经典教材和参考书籍
- **视频课程**：来自国际知名高校和在线教育平台的机器人相关课程
- **硬件资源**：常用的传感器、执行器、开发板和机器人套件

## 栏目内容导航

| 页面 | 内容 |
|------|------|
| [软件工具](software.md) | 仿真器、算法库、开发工具、IDE、版本控制 |
| [图书推荐](books.md) | 控制、感知、规划、机器学习各方向经典教材 |
| [视频课程](videos.md) | Coursera、YouTube、Bilibili 精选机器人课程 |

## 相关项目

除本维基外，云飞机器人实验室（YF Robotics）及本站作者还维护以下中文资料，可作为延伸阅读：

| 项目 | 内容 | 链接 |
|------|------|------|
| 宇树 G1 使用手册 | 宇树科技 G1 人形机器人的上手、开发与调试指南 | [yfrobotics.github.io/unitree-g1-handbook](https://yfrobotics.github.io/unitree-g1-handbook/) |
| 自动驾驶技术指南 | 自动驾驶（Autonomous Driving）从基础概念到工程实践的系统性中文教程 | [yfrobotics.github.io/self-driving-handbook-cn](https://yfrobotics.github.io/self-driving-handbook-cn/) |
| 机器人与电子设计开源项目列表 | 机器人、电子设计与机器学习方向的中文开源项目清单 | [github.com/automaticdai/awesome-robotics-ee-opensource](https://github.com/automaticdai/awesome-robotics-ee-opensource) |

## 如何入门机器人学

机器人学（Robotics）是一个高度交叉的学科，涉及机械工程、电子工程、计算机科学和控制工程等多个领域。对于初学者，建议按照以下路径循序渐进：

### 学习路线图

| 阶段 | 学习内容 | 推荐资源 | 建议时长 |
|------|---------|---------|---------|
| **第一阶段** 数学与编程基础 | 线性代数、概率论、微积分；Python / C++ | MIT 18.06（线代）；Python 官方教程 | 3–6 个月 |
| **第二阶段** 机器人核心理论 | 运动学、动力学、控制理论、感知、规划 | Craig《Introduction to Robotics》；Thrun《Probabilistic Robotics》 | 6–12 个月 |
| **第三阶段** 工具链实践 | ROS 2、仿真器（Gazebo/MuJoCo）、OpenCV | ROS 2 官方 Tutorials；Clearpath 教程 | 3–6 个月 |
| **第四阶段** 进阶专方向 | SLAM、机器人学习、人形控制、多机器人 | 论文精读 + 开源项目复现 | 持续深入 |

### 数学与编程基础

学习线性代数（Linear Algebra）、概率论（Probability Theory）和微积分（Calculus）等数学基础。编程方面建议掌握 Python 和 C++ 两种语言，它们是机器人开发中使用最广泛的编程语言。

推荐起点：
- **线性代数**：MIT OpenCourseWare 18.06（Gilbert Strang 主讲，免费在线）
- **概率论**：Stanford CS109 概率基础（适合计算机背景学习者）
- **Python 入门**：Google 的 Python 速成课（Crash Course on Python，Coursera）

### 核心理论

在具备基础后，可以进入机器人学的核心领域：

- **运动学与动力学（Kinematics & Dynamics）**：理解机器人机械结构的数学描述，推荐阅读 Craig 的《Introduction to Robotics》
- **控制理论（Control Theory）**：学习 PID 控制、状态空间控制和最优控制等方法
- **感知（Perception）**：包括计算机视觉（Computer Vision）和传感器融合（Sensor Fusion）
- **规划（Planning）**：路径规划（Path Planning）和运动规划（Motion Planning）的基本算法

### 实践动手

理论学习需要与实践结合：

- 安装并学习 ROS（Robot Operating System），这是目前机器人领域最主流的软件框架
- 使用 Gazebo 或 MuJoCo 等仿真环境进行算法验证
- 从简单的移动机器人或机械臂项目开始积累实践经验
- 参加机器人竞赛是提升综合能力的有效途径

### 进阶方向

在掌握基础后，可以根据兴趣选择深入方向，例如 SLAM（同步定位与建图）、机器人学习（Robot Learning）、人形机器人控制或多机器人系统等。

## 在线课程与视频资源

### 国际知名课程

| 课程名称 | 授课机构 | 平台 | 语言 |
|---------|---------|------|------|
| Modern Robotics | 西北大学 | Coursera | 英语 |
| Robotics Specialization | 宾夕法尼亚大学 | Coursera | 英语 |
| Robot Autonomy | 卡内基梅隆大学 CMU | 公开课 | 英语 |
| CS 223A: Introduction to Robotics | 斯坦福大学 | YouTube | 英语 |
| 6.832: Underactuated Robotics | MIT | MIT OCW | 英语 |
| Deep Reinforcement Learning | UC Berkeley | YouTube | 英语 |

### 中文优质资源

| 内容 | 来源 | 平台 |
|------|------|------|
| ROS 2 入门与进阶 | 古月居 | Bilibili |
| 深度学习与计算机视觉 | 李沐（动手学深度学习）| Bilibili / 官网 |
| SLAM 十四讲配套讲解 | 各大高校 | Bilibili |
| 机器人运动规划 | 深蓝学院 | 官网 |
| 强化学习实战 | 蘑菇书 EasyRL | GitHub / B 站 |

## 重要开源项目与社区

### 核心开源项目

| 项目 | 用途 | 链接 |
|------|------|------|
| ROS 2 | 机器人操作系统 | [github.com/ros2](https://github.com/ros2) |
| MoveIt 2 | 机械臂运动规划 | [moveit.ros.org](https://moveit.ros.org) |
| Nav2 | 移动机器人导航 | [navigation.ros.org](https://navigation.ros.org) |
| OpenCV | 计算机视觉库 | [opencv.org](https://opencv.org) |
| PCL | 点云处理库 | [pointclouds.org](https://pointclouds.org) |
| Isaac Lab | GPU 加速 RL 训练 | [github.com/isaac-sim/IsaacLab](https://github.com/isaac-sim/IsaacLab) |
| Stable Baselines3 | 强化学习算法库 | [stable-baselines3.readthedocs.io](https://stable-baselines3.readthedocs.io) |

### 学术与技术社区

- **Robotics Stack Exchange**：机器人技术问答社区，适合工程实践问题
- **Reddit r/robotics**：机器人爱好者讨论社区
- **ROS Discourse**：ROS 官方论坛，活跃的 ROS 用户社区
- **知乎机器人专栏**：中文高质量机器人技术文章
- **机器人大讲堂（Bilibili）**：国内机器人技术直播与录播

## 竞赛与活动

参加机器人竞赛是快速积累实战经验的有效途径。主要国际竞赛包括：

- **RoboCup**：世界最大规模的机器人竞赛，涵盖足球、救援、家庭服务等多个项目
- **DARPA Robotics Challenge（DRC）**：着眼于灾难救援场景的人形机器人竞赛
- **FIRST Robotics**：面向青少年的工程实践竞赛
- **AWS RoboMaker**：基于云平台的机器人仿真竞赛

国内主要竞赛见[竞赛专页](../database/competitions.md)。
