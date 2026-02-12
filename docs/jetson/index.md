# Nvidia Jetson

!!! note "引言"
    Nvidia Jetson是英伟达（Nvidia）推出的面向边缘AI计算的嵌入式硬件平台。与传统的嵌入式处理器不同，Jetson系列集成了Nvidia GPU，能够在低功耗条件下运行深度学习推理、计算机视觉和传感器融合等计算密集型任务。Jetson平台在自主机器人、无人机、自动驾驶和智能摄像头等领域得到广泛应用。

Jetson是英伟达推出的面向嵌入式计算的硬件平台。

## 1. Jetson型号

Jetson的型号包括：

- Jetson Nano
- Jetson TX1
- Jetson TX2
- Jetson Xaiver
- Jetson Xavier Nx

## 2. Jetson各型号对比

Jetson各个型号的对比如下：

| Hardware feature \ Jetson module | Jetson Nano                                        | Jetson TX1                                         | Jetson TX2/TX2i                                       | Jetson Xavier                         | Jetson Xavier Nx                                             |
| -------------------------------- | -------------------------------------------------- | -------------------------------------------------- | ----------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------ |
| CPU (ARM)                        | 4-core ARM A57 @ 1.43 GHz                          | 4-core ARM Cortex A57 @ 1.73 GHz                   | 4-core ARM Cortex-A57 @ 2 GHz, 2-core Denver2 @ 2 GHz | 8-core ARM Carmel v.8.2 @ 2.26 GHz    | 6-core NVIDIA Carmel ARM®v8.2 64-bit CPU                     |
| GPU                              | 128-core Maxwell @ 921 MHz                         | 256-core Maxwell @ 998 MHz                         | 256-core Pascal @ 1.3 GHz                             | 512-core Volta @ 1.37 GHz             | 384-core NVIDIA Volta™ GPU                                   |
| Memory                           | 4 GB LPDDR4, 25.6 GB/s                             | 4 GB LPDDR4, 25.6 GB/s                             | 8 GB 128-bit LPDDR4, 58.3 GB/s                        | 16 GB 256-bit LPDDR4, 137 GB/s        | 8 GB 128-bit LPDDR4x @ 1600 MHz51.2GB/s                      |
| Storage                          | MicroSD                                            | 16 GB eMMC 5.1                                     | 32 GB eMMC 5.1                                        | 32 GB eMMC 5.1                        | 16 GB eMMC 5.1                                               |
| Tensor cores                     | --                                                 | --                                                 | --                                                    | 64                                    | 48                                                           |
| Video encoding                   | (1x) 4Kp30, (2x) 1080p60, (4x) 1080p30             | (1x) 4Kp30, (2x) 1080p60, (4x) 1080p30             | (1x) 4Kp60, (3x) 4Kp30, (4x) 1080p60, (8x) 1080p30    | (4x) 4Kp60, (8x) 4Kp30, (32x) 1080p30 | 2x464MP/sec (HEVC)2x 4K @ 30 (HEVC)6x 1080p @ 60 (HEVC)14x 1080p @ 30 (HEVC) |
| Video decoding                   | (1x) 4Kp60, (2x) 4Kp30, (4x) 1080p60, (8x) 1080p30 | (1x) 4Kp60, (2x) 4Kp30, (4x) 1080p60, (8x) 1080p30 | (2x) 4Kp60, (4x) 4Kp30, (7x) 1080p60                  | (2x) 8Kp30, (6x) 4Kp60, (12x) 4Kp30   | 2x690MP/sec (HEVC)2x 4K @ 60 (HEVC)4x 4K @ 30 (HEVC)12x 1080p @ 60 (HEVC)32x 1080p @ 30 (HEVC)16x 1080p @ 30 (H.264) |
| USB                              | (4x) USB 3.0 + Micro-USB 2.0                       | (1x) USB 3.0 + (1x) USB 2.0                        | (1x) USB 3.0 + (1x) USB 2.0                           | (3x) USB 3.1 + (4x) USB 2.0           |                                                              |
| PCI-Express lanes                | 4 lanes PCIe Gen 2                                 | 5 lanes PCIe Gen 2                                 | 5 lanes PCIe Gen 2                                    | 16 lanes PCIe Gen 4                   | 1 x1 + 1x4(PCIe Gen3, Root Port & Endpoint)                  |
| Power                            | 5W / 10W                                           | 10W                                                | 7.5W / 15W                                            | 10W / 15W / 30W                       | 10W / 15W                                                    |


## 3. JetPack SDK

JetPack是Nvidia为Jetson平台提供的官方软件开发套件（Software Development Kit），包含了开发Jetson应用所需的全部软件组件：

- **L4T（Linux for Tegra）**：基于Ubuntu的操作系统，针对Jetson硬件优化。
- **CUDA**：Nvidia的并行计算平台和编程模型，允许开发者利用GPU进行通用计算。
- **cuDNN**：CUDA深度神经网络库，提供了高度优化的深度学习基础运算（卷积、池化、归一化等）。
- **TensorRT**：高性能深度学习推理优化器和运行时库。
- **VisionWorks / VPI**：计算机视觉基础库。
- **Multimedia API**：视频编解码和图像处理接口。
- **开发工具**：包括CUDA编译器（nvcc）、调试器（cuda-gdb）和性能分析器（Nsight Systems）。


## 4. CUDA与TensorRT

### CUDA

CUDA（Compute Unified Device Architecture）是Nvidia的并行计算平台。在Jetson上，CUDA允许开发者编写在GPU上运行的核函数（Kernel），实现大规模并行计算。对于机器人应用中的图像处理、点云处理和矩阵运算等任务，CUDA可以提供数倍到数十倍的性能提升。

### TensorRT

TensorRT是Nvidia的深度学习推理优化引擎。它的核心功能包括：

- **模型优化**：对训练好的深度学习模型进行层融合（Layer Fusion）、精度校准（Calibration）和内核自动调优（Kernel Auto-Tuning），显著提高推理速度。
- **精度模式**：支持FP32、FP16和INT8三种推理精度。在Jetson Xavier和Xavier NX上使用INT8模式可以获得最高的推理性能。
- **动态形状支持**：支持运行时动态调整输入张量的形状。
- **多框架支持**：可以导入TensorFlow、PyTorch（通过ONNX）和Caffe等框架训练的模型。

在机器人视觉应用中，TensorRT常用于加速目标检测（如YOLO、SSD）、语义分割和姿态估计等深度学习模型的推理。


## 5. DeepStream SDK

DeepStream是Nvidia提供的流媒体分析SDK，专为构建智能视频分析（Intelligent Video Analytics, IVA）应用而设计。其核心特点包括：

- **端到端的视频处理流水线**：从视频解码、预处理、深度学习推理到后处理和输出，全部通过GStreamer插件实现。
- **多流并行处理**：可以同时处理多路视频流，充分利用Jetson的GPU算力。
- **与TensorRT集成**：推理环节自动调用TensorRT，获得最优推理性能。
- **消息代理（Message Broker）**：支持将分析结果通过Kafka、MQTT等协议发送到云端或其他系统。

DeepStream在机器人领域可用于：多摄像头环境感知、实时目标追踪、异常行为检测等场景。


## 6. 机器人应用

Jetson平台在机器人领域的主要应用方向包括：

### 感知 (Perception)

- **目标检测与识别**：运行YOLO、SSD等检测模型，实时识别障碍物、行人和交通标志。
- **语义分割**：对摄像头图像进行像素级分类，区分道路、人行道、建筑物等。
- **深度估计**：利用立体视觉或单目深度估计网络获取场景深度信息。
- **3D点云处理**：对激光雷达点云进行目标检测和分割。

### 导航 (Navigation)

- **视觉SLAM**：运行ORB-SLAM2/3、RTAB-Map等视觉SLAM算法，实现实时定位与地图构建。
- **路径规划**：在ROS/ROS 2框架下运行Navigation2等导航栈。
- **传感器融合**：融合摄像头、激光雷达、IMU等多传感器数据，提高定位精度和鲁棒性。

### Isaac SDK

Nvidia Isaac SDK是面向机器人应用的专用开发框架，提供：

- 预构建的感知、导航和操控模块
- 基于计算图（Compute Graph）的应用框架
- 与Isaac Sim仿真环境的集成
- 针对Jetson硬件优化的算法实现


## 7. 功耗模式

Jetson平台支持多种功耗模式（Power Mode），允许开发者在性能和功耗之间进行权衡。以Jetson Xavier NX为例：

| 模式 | 功耗 | CPU | GPU |
|------|------|-----|-----|
| 10W（2核） | 10W | 2核 Carmel @ 1.2GHz | 2核 @ 510MHz |
| 10W（4核） | 10W | 4核 Carmel @ 1.2GHz | 2核 @ 510MHz |
| 15W（6核） | 15W | 6核 Carmel @ 1.4GHz | 2核 @ 510MHz |
| 20W（6核） | 20W | 6核 Carmel @ 1.9GHz | 4核 @ 1.1GHz |

功耗模式可以通过`nvpmodel`命令进行切换：

```bash
# 查看当前功耗模式
sudo nvpmodel -q

# 切换到15W模式
sudo nvpmodel -m 2

# 启用最大性能模式
sudo jetson_clocks
```

对于电池供电的机器人，合理配置功耗模式是延长续航时间的关键。


## 8. 快速入门

以下是在Jetson平台上开始机器人开发的基本步骤：

1. **烧录系统镜像**：从Nvidia开发者网站下载JetPack SDK，使用SDK Manager将系统镜像烧录到Jetson模块。
2. **初始设置**：首次启动后完成Ubuntu系统的基本配置（用户名、密码、网络等）。
3. **安装开发工具**：JetPack已预装CUDA、cuDNN和TensorRT，可额外安装PyTorch、TensorFlow等深度学习框架。
4. **安装ROS**：根据需要安装ROS Noetic或ROS 2 Humble。
5. **连接传感器**：通过USB、CSI或I2C接口连接摄像头、激光雷达和IMU等传感器。
6. **运行示例**：JetPack附带了大量示例代码，包括CUDA示例、TensorRT推理示例和视觉处理示例。

---

**参考资料：**

1. Benchmark comparison for Jetson Nano, TX1, TX2 and AGX Xavier, https://www.fastcompression.com/blog/jetson-benchmark-comparison.htm
2. Jetson Xavier NX, https://developer.nvidia.com/embedded/jetson-xavier-nx
3. [Nvidia JetPack SDK文档](https://developer.nvidia.com/embedded/jetpack)
4. [Nvidia Isaac SDK](https://developer.nvidia.com/isaac-sdk)
5. [Jetson开发者论坛](https://forums.developer.nvidia.com/c/agx-autonomous-machines/jetson-embedded-systems/)

---

(本条目需要完善，[立刻参与知识公共编辑](/how-to-contribute/))
