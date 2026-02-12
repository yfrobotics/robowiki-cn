# 机器人工具与软件

## 机器人操作系统
- [ROS (Robot Operating System)](http://wiki.ros.org/cn) — 最广泛使用的机器人中间件框架，提供通信、工具链和丰富的功能包生态系统
- [ROS 2](https://docs.ros.org/en/rolling/) — ROS 的下一代版本，基于 DDS 通信，支持实时性和多机器人系统，适用于工业和商用场景
- [Micro-ROS](https://micro.ros.org/) — 面向微控制器的 ROS 2 客户端库，使嵌入式设备能够直接接入 ROS 2 生态

## 机器人仿真
- [Gazebo Simulator](http://gazebosim.org/) — 与 ROS 深度集成的 3D 机器人仿真器，支持物理引擎、传感器仿真和多机器人场景
- [Mujoco](https://mujoco.org/) — DeepMind 开源的高精度物理仿真引擎，在接触动力学建模方面表现出色，广泛用于机器人学习研究
- [NVIDIA Isaac Sim](https://developer.nvidia.com/isaac-sim) — 基于 NVIDIA Omniverse 的机器人仿真平台，支持光线追踪渲染和合成数据生成
- [Webots](https://cyberbotics.com/) — 开源的 3D 机器人仿真软件，内置多种机器人模型和控制器接口，支持 ROS 集成
- [CoppeliaSim (V-REP)](https://www.coppeliarobotics.com/) — 多功能机器人仿真环境，支持多种编程接口和物理引擎
- [PyBullet](https://pybullet.org/) — 基于 Bullet 物理引擎的 Python 接口，轻量级且易于上手，常用于强化学习研究

## 可视化工具
- [RViz](http://wiki.ros.org/rviz) — ROS 生态中的 3D 可视化工具，用于显示传感器数据、机器人模型和规划结果
- [Foxglove Studio](https://foxglove.dev/) — 现代化的机器人数据可视化和调试工具，支持 ROS 1/2 数据和自定义数据格式
- [PlotJuggler](https://plotjuggler.io/) — 时间序列数据可视化工具，支持 ROS 话题的实时绘图和回放

## SLAM 与导航
- [Cartographer](https://google-cartographer.readthedocs.io/) — Google 开源的实时 SLAM 库，支持 2D 和 3D 激光雷达 SLAM
- [ORB-SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) — 基于特征点的视觉 SLAM 系统，支持单目、双目和 RGB-D 相机
- [RTAB-Map](http://introlab.github.io/rtabmap/) — 基于外观的闭环检测 SLAM 框架，支持多种传感器输入
- [GTSAM](https://gtsam.org/) — 基于因子图（Factor Graph）的 SLAM 和状态估计优化库
- [Navigation2 (Nav2)](https://navigation.ros.org/) — ROS 2 的导航框架，提供路径规划、行为树和代价地图等功能

## 计算机视觉
- [OpenCV](https://opencv.org/) — 最广泛使用的开源计算机视觉库，提供图像处理、特征检测、目标跟踪等功能
- [Open3D](http://www.open3d.org/) — 面向 3D 数据处理的开源库，支持点云处理、3D 重建和可视化
- [PCL (Point Cloud Library)](https://pointclouds.org/) — 大规模点云处理库，提供滤波、分割、配准和特征提取等功能
- [YOLO (You Only Look Once)](https://github.com/ultralytics/ultralytics) — 实时目标检测算法系列，在机器人视觉感知中广泛应用

## 机器学习与深度学习
- [TensorFlow](https://www.tensorflow.org/api_docs/python/tf) — Google 开发的开源深度学习框架，拥有完善的工具生态和部署支持
- [PyTorch](https://pytorch.org/docs/stable/index.html) — Meta 开发的深度学习框架，以动态计算图和易用性著称，是目前学术研究中使用最广泛的框架
- [JAX](https://jax.readthedocs.io/) — Google 开发的高性能数值计算库，支持自动微分和 GPU/TPU 加速，在机器人学习领域日益流行
- [Stable Baselines3](https://stable-baselines3.readthedocs.io/) — 基于 PyTorch 的强化学习算法库，提供 PPO、SAC 等主流算法的可靠实现
- [Isaac Gym](https://developer.nvidia.com/isaac-gym) — NVIDIA 的 GPU 加速物理仿真和强化学习训练平台

## 运动规划
- [MoveIt](https://moveit.ros.org/) — ROS 生态中最主流的机械臂运动规划框架，集成了运动学求解、碰撞检测和轨迹优化功能
- [OMPL (Open Motion Planning Library)](https://ompl.kavrakilab.org/) — 开源运动规划算法库，实现了 RRT、PRM 等多种采样规划算法
- [Drake](https://drake.mit.edu/) — MIT 开发的机器人建模和优化框架，支持多体动力学仿真、轨迹优化和控制器设计
- [Pinocchio](https://stack-of-tasks.github.io/pinocchio/) — 高效的刚体动力学计算库，支持正逆运动学、动力学和微分计算

## 通信与中间件
- [DDS (Data Distribution Service)](https://www.dds-foundation.org/) — ROS 2 底层使用的分布式通信标准，支持实时数据分发
- [ZeroMQ](https://zeromq.org/) — 高性能异步消息库，常用于机器人系统中的进程间通信
- [gRPC](https://grpc.io/) — Google 开源的高性能 RPC 框架，在机器人云端通信中有广泛应用
- [MQTT](https://mqtt.org/) — 轻量级物联网（IoT）通信协议，适用于资源受限的机器人和传感器设备

## CAD 与机械设计
- [SolidWorks](https://www.solidworks.com/) — 广泛用于机器人结构设计的专业 3D CAD 软件
- [Fusion 360](https://www.autodesk.com/products/fusion-360/) — Autodesk 推出的云端 CAD/CAM 工具，支持参数化设计和仿真分析
- [FreeCAD](https://www.freecad.org/) — 开源参数化 3D CAD 建模工具，适合个人和教育使用
- [URDF/Xacro](http://wiki.ros.org/urdf) — ROS 中用于描述机器人模型的 XML 格式，定义连杆、关节和传感器等信息

## 嵌入式与硬件开发
- [Arduino](https://www.arduino.cc/) — 开源电子原型开发平台，广泛用于机器人底层硬件控制和传感器接口
- [STM32](https://www.st.com/en/microcontrollers-microprocessors/stm32-32-bit-arm-cortex-mcus.html) — ST 公司的 ARM Cortex-M 系列微控制器，在机器人嵌入式控制中应用广泛
- [Jetson (NVIDIA)](https://developer.nvidia.com/embedded-computing) — NVIDIA 嵌入式 AI 计算平台，Jetson Nano/Xavier/Orin 系列为机器人提供边缘 AI 推理能力
- [Raspberry Pi](https://www.raspberrypi.org/) — 低成本单板计算机，广泛用于教育机器人和原型开发
