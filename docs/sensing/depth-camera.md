# 深度视觉相机

!!! note "引言"
    深度相机 (Depth Camera) 能够同时获取彩色图像和每个像素的深度信息，是机器人三维感知的重要工具。本页面介绍主流深度相机的技术原理、产品系列及其在机器人中的应用。


## 深度感知技术

深度相机根据获取深度信息的方式，主要分为以下三种技术路线：

- **结构光 (Structured Light)**：向场景投射已知的光学图案（如红外散斑或条纹），通过分析图案的变形程度计算深度。代表产品有 Microsoft Kinect v1 和 Intel RealSense D405。
- **飞行时间 (Time-of-Flight, ToF)**：发射调制的红外光，通过测量光往返时间或相位差来计算距离。代表产品有 Microsoft Kinect v2。ToF 的深度精度与距离大致成正比，误差随距离增加而增大。
- **主动红外双目 (Active IR Stereo)**：利用红外投射器增强纹理，通过双目立体匹配算法计算视差和深度。代表产品有 Intel RealSense D435 和 ZED 系列。这种方案在纹理丰富的场景中表现良好。


## Microsoft Kinect

Microsoft Kinect 是深度相机的先驱产品，最初为游戏主机开发，后来被广泛应用于机器人研究。

### Kinect v1

- **深度技术**：结构光 (Structured Light)
- **深度范围**：0.8m ~ 4.0m
- **深度分辨率**：640 x 480
- **RGB分辨率**：640 x 480 @ 30fps
- **接口**：USB 2.0 + 专用电源适配器
- **ROS支持**：通过 `openni_camera` 或 `freenect_stack` 驱动
- **特点**：首款大规模商用深度相机，推动了深度视觉研究的发展。在近距离（<1.2m）和远距离（>3.5m）处精度较差。已停产。

### Kinect v2

- **深度技术**：飞行时间 (ToF)
- **深度范围**：0.5m ~ 4.5m
- **深度分辨率**：512 x 424
- **RGB分辨率**：1920 x 1080 @ 30fps
- **接口**：USB 3.0
- **ROS支持**：通过 `iai_kinect2` 驱动
- **特点**：相比 v1 深度精度和分辨率均有显著提升，多人骨骼追踪能力增强。功耗较高，已停产。

### Azure Kinect DK

- **深度技术**：飞行时间 (ToF)
- **深度范围**：窄视场模式 0.25m ~ 5.46m，宽视场模式 0.25m ~ 2.88m
- **深度分辨率**：最高 1024 x 1024
- **RGB分辨率**：3840 x 2160 @ 30fps
- **接口**：USB 3.0 Type-C
- **附加传感器**：7麦克风阵列、IMU
- **ROS支持**：通过 `azure_kinect_ros_driver` 驱动
- **特点**：Microsoft 最新一代深度相机，集成 AI 加速芯片，支持身体追踪 (Body Tracking) 和空间锚点 (Spatial Anchors)。


## ZED Camera

ZED 系列由 Stereolabs 公司生产，基于主动红外双目视觉技术，以长测距范围和 SLAM 功能著称。

### ZED

- **深度技术**：被动双目立体视觉 (Passive Stereo)
- **深度范围**：0.5m ~ 20m
- **RGB分辨率**：最高 2208 x 1242 @ 15fps，或 1344 x 376 @ 100fps
- **基线距离**：120mm
- **接口**：USB 3.0
- **特点**：初代产品，深度范围远，适合室外场景。无内置 IMU。

### ZED Mini

- **深度技术**：被动双目立体视觉
- **深度范围**：0.15m ~ 12m
- **基线距离**：63mm
- **接口**：USB 3.0
- **附加传感器**：内置 IMU
- **特点**：体积更紧凑，基线更短适合近距离应用。内置 IMU 支持视觉惯性里程计 (VIO)。适合无人机和 AR/VR 头显。

### ZED 2

- **深度技术**：被动双目立体视觉 + 神经网络深度估计
- **深度范围**：0.2m ~ 20m
- **RGB分辨率**：最高 2208 x 1242 @ 15fps
- **基线距离**：120mm
- **接口**：USB 3.0
- **附加传感器**：IMU、气压计、磁力计
- **ROS支持**：通过 `zed-ros-wrapper` 或 `zed-ros2-wrapper` 驱动
- **特点**：引入 AI 增强的深度估计，支持物体检测与骨骼追踪，IP66 防护等级。
- **产品页面**：<https://www.stereolabs.com/zed-2/>

### ZED 2i

- **深度技术**：被动双目立体视觉 + 神经网络深度估计
- **深度范围**：0.2m ~ 20m
- **附加传感器**：IMU、气压计、磁力计
- **接口**：USB 3.0 / GMSL2
- **特点**：工业级设计，IP66 防护，支持 GMSL2 接口（适配 NVIDIA 平台）。适合自动驾驶和室外机器人。


## Intel RealSense

Intel RealSense 系列是目前应用最广泛的深度相机之一，产品线覆盖从近距离精密测量到远距离环境感知的多种需求。

### RealSense D405

- **深度技术**：主动红外立体视觉 (Active IR Stereo)
- **深度范围**：0.07m ~ 0.7m
- **深度分辨率**：1280 x 720
- **RGB分辨率**：1280 x 720
- **接口**：USB 3.2 Type-C
- **ROS支持**：通过 `realsense2_camera` 驱动
- **特点**：专为近距离精密应用设计，最小工作距离仅 7cm。适合机械臂末端抓取、精密装配。

### RealSense D415

- **深度技术**：主动红外立体视觉
- **深度范围**：0.16m ~ 10m
- **深度分辨率**：1280 x 720
- **视场角 (FOV)**：深度 65° x 40°
- **接口**：USB 3.2 Type-C
- **特点**：窄视场角、高精度，适合需要精确深度测量的场景。采用滚动快门 (Rolling Shutter)。

### RealSense D435 / D435i / D435f

- **深度技术**：主动红外立体视觉
- **深度范围**：0.105m ~ 10m
- **深度分辨率**：1280 x 720 @ 90fps
- **视场角 (FOV)**：深度 87° x 58°
- **接口**：USB 3.2 Type-C
- **ROS支持**：通过 `realsense2_camera` 驱动
- **D435i 附加**：内置 BMI055 IMU，支持视觉惯性里程计
- **D435f 附加**：工业级设计，IP65 防护
- **特点**：广视场角、全局快门 (Global Shutter)，适合运动场景。是 RealSense 系列中最受欢迎的型号。

### RealSense D455

- **深度技术**：主动红外立体视觉
- **深度范围**：0.6m ~ 6m（最优范围），最远可达约 10m
- **基线距离**：95mm（比 D435 更长，深度精度更高）
- **深度分辨率**：1280 x 720
- **视场角 (FOV)**：深度 87° x 58°
- **接口**：USB 3.2 Type-C
- **附加传感器**：内置 BMI055 IMU
- **ROS支持**：通过 `realsense2_camera` 驱动
- **特点**：更长的基线提供更精确的深度估计，适合需要较远距离深度感知的场景。


## 型号对比

| 特性 | Kinect v2 | ZED 2 | D435i | D455 | D405 |
|------|-----------|-------|-------|------|------|
| 深度技术 | ToF | 双目 | 主动IR双目 | 主动IR双目 | 主动IR双目 |
| 深度范围 | 0.5~4.5m | 0.2~20m | 0.1~10m | 0.6~6m | 0.07~0.7m |
| 内置IMU | 否 | 是 | 是 | 是 | 否 |
| ROS支持 | iai_kinect2 | zed-ros-wrapper | realsense2_camera | realsense2_camera | realsense2_camera |
| 适用场景 | 室内交互 | 室外/远距离 | 通用/移动机器人 | 中远距离 | 近距离精密 |

Intel RealSense 完整型号对比：<https://www.intelrealsense.com/compare-depth-cameras/>


## 选型建议

在为机器人选择深度相机时，可参考以下原则：

- **室内近距离操作（抓取、装配）**：选择最小工作距离小、精度高的型号，如 RealSense D405
- **室内移动机器人导航**：选择广视场角、支持 IMU 的型号，如 RealSense D435i
- **室外远距离感知**：选择深度范围远的型号，如 ZED 2 或 ZED 2i
- **人体追踪与交互**：选择骨骼追踪功能完善的型号，如 Azure Kinect DK
- **与 ROS 集成**：优先选择 ROS 驱动成熟、社区支持良好的产品


## 参考资料

1. Intel RealSense 官方文档：<https://dev.intelrealsense.com/docs>
2. Stereolabs ZED 文档：<https://www.stereolabs.com/docs>
3. Microsoft Azure Kinect 文档：<https://learn.microsoft.com/en-us/azure/kinect-dk/>
4. Khoshelham, K. & Elberink, S. O. (2012). Accuracy and resolution of Kinect depth data for indoor mapping applications. *Sensors*, 12(2), 1437-1454.
