# 机器人与视觉数据集

!!! note "引言"
    数据集是机器人感知、控制与学习算法研究的基石。从图像分类到三维物体位姿估计，从自动驾驶场景理解到机器人操作演示采集，高质量的标注数据集直接决定了算法研究的深度与广度。本文系统整理了计算机视觉（Computer Vision）、人体感知、自动驾驶、机器人操作、SLAM 导航、强化学习（Reinforcement Learning）等领域的主流公开数据集，并介绍常用的标注与管理工具，供研究人员快速查阅与选型。


## 计算机视觉基础数据集

### 目标检测与图像分类

目标检测（Object Detection）与图像分类（Image Classification）是计算机视觉最基础的任务，以下数据集长期作为该领域的标准基准。

| 数据集 | 年份 | 图像数 | 类别数 | 主要特点 | 下载链接 |
|--------|------|--------|--------|----------|----------|
| ImageNet | 2009 | ~1,400 万（ILSVRC 竞赛子集约 120 万） | 1,000（竞赛） / 21,841（完整） | 深度学习视觉研究的奠基性基准，AlexNet 等划时代模型均在此验证 | [image-net.org](https://www.image-net.org/) |
| COCO | 2014 | ~33 万 | 80（目标）/ 133（全景） | 综合视觉基准，支持目标检测、实例分割、全景分割、关键点检测及图像描述文字生成 | [cocodataset.org](https://cocodataset.org/) |
| Pascal VOC | 2005–2012 | ~11,000（精标注） | 20 | 早期目标检测标准基准，标注质量高，常用 VOC2007 和 VOC2012 | [host.robots.ox.ac.uk](http://host.robots.robots.ox.ac.uk/pascal/VOC/) |
| Objects365 | 2019 | ~200 万 | 365 | 由旷视科技发布，大规模、多样化，类别覆盖广，有效提升检测模型的泛化能力 | [objects365.org](https://www.objects365.org/) |
| OpenImages v7 | 2022 | ~900 万 | 600 | 谷歌（Google）发布，世界上最大的带标注图像数据集之一，支持分类、检测、分割、关系检测 | [storage.googleapis.com](https://storage.googleapis.com/openimages/web/index.html) |
| CIFAR-10/100 | 2009 | 60,000（32×32） | 10 / 100 | 小分辨率基准，适合快速原型验证与轻量模型研究 | [cs.toronto.edu](https://www.cs.toronto.edu/~kriz/cifar.html) |
| MNIST | 1998 | 70,000（28×28） | 10 | 手写数字识别入门基准，深度学习教学经典数据集 | [yann.lecun.com](http://yann.lecun.com/exdb/mnist/) |

**COCO 数据集**是目前目标检测领域最常用的综合性基准，其评价指标 COCO AP（Average Precision，平均精度）已成为衡量检测模型性能的工业标准。数据集还提供关键点标注（17 个人体关键点，约 25 万人实例）和全景分割（Panoptic Segmentation）任务。

**Objects365** 在训练集规模和类别多样性上显著超越 COCO，常被用于预训练检测模型的骨干网络，再迁移至下游任务。

### 图像分割

图像分割（Image Segmentation）包括语义分割（Semantic Segmentation）、实例分割（Instance Segmentation）和全景分割，以下是主要基准数据集。

| 数据集 | 年份 | 图像数 | 类别数 | 场景类型 | 主要特点 |
|--------|------|--------|--------|----------|----------|
| Cityscapes | 2016 | 25,000（5,000 精标注） | 30（19 评估类） | 城市街景 | 自动驾驶语义分割标准基准，覆盖 50 个欧洲城市 |
| ADE20K | 2017 | 25,000 | 150 | 室内外通用 | MIT 场景解析基准，语义类别丰富，覆盖室内外多种场景 |
| Mapillary Vistas | 2017 | 25,000（高分辨率） | 66 | 街景 | 来自全球多样化地理位置，分辨率高，标注精细 |
| LVIS | 2019 | ~16 万 | 1,203 | 通用 | 长尾分布实例分割基准，类别分布不均衡，更贴近真实世界 |
| ScanNet | 2017 | 250 万帧视频 | 20 | 室内三维场景 | RGB-D 视频序列，含三维网格与语义标注，适合室内场景理解 |

**Cityscapes** 对每张精标注图像的标注耗时约 1.5 小时，数据质量在自动驾驶分割领域首屈一指。训练集 2,975 张，验证集 500 张，测试集 1,525 张，另有 20,000 张弱标注图像。

**ADE20K** 由麻省理工学院（MIT）发布，是场景理解（Scene Understanding）领域的权威基准，支持 PSPNet、SegFormer 等分割模型的标准评测。


## 人体感知数据集

### 人体姿态估计

人体姿态估计（Human Pose Estimation，HPE）旨在从图像或视频中预测人体关节点的位置，分为二维（2D）和三维（3D）两大方向。

| 数据集 | 年份 | 规模 | 关键点数 | 场景 | 主要特点 |
|--------|------|------|----------|------|----------|
| COCO Keypoints | 2016 | ~25 万人实例 | 17 | 自然场景 | 基于 COCO 图像，多人姿态，与检测任务联合评测 |
| MPII Human Pose | 2014 | ~25,000 张 | 16 | 自然场景 | 来自 YouTube 视频截帧，覆盖 410 种人类活动，场景多样 |
| Human3.6M | 2014 | ~350 万帧 | 17 | 室内受控 | 11 名演员、17 种动作，含精确三维真值（Ground Truth），人体三维姿态估计标准基准 |
| MPI-INF-3DHP | 2017 | ~130 万帧 | 17 | 室内外混合 | 使用多摄像机捕捉系统，测试集包含室外场景，泛化性评测更全面 |
| PoseTrack | 2018 | 66,000 帧（视频） | 15 | 自然场景 | 多人视频姿态估计与跟踪联合基准 |
| 3DPW | 2018 | 60 段视频 | 24 | 室外真实场景 | 使用惯性测量单元（IMU）获取三维真值，室外真实场景下的三维姿态基准 |

**Human3.6M** 是三维人体姿态估计领域引用量最高的数据集，采用运动捕捉（Motion Capture）系统记录真值，被几乎所有三维姿态估计方法用于性能评估。

**MPI-INF-3DHP** 由德国马克斯·普朗克信息研究所（Max Planck Institute for Informatics）发布，其测试集包含室外场景，对模型泛化能力要求更高。

### 人脸与手势识别

| 数据集 | 年份 | 规模 | 主要任务 | 特点 |
|--------|------|------|----------|------|
| 300W | 2013 | ~4,000 张 | 人脸关键点检测 | 68 个人脸关键点，多姿态、多光照条件 |
| WFLW | 2018 | 10,000 张 | 人脸关键点检测 | 98 个关键点，包含遮挡、模糊、妆容等挑战属性 |
| FreiHAND | 2019 | 130,240 张 | 手部姿态与形状估计 | 单目 RGB 图像，含三维手部网格真值，适合手部重建研究 |
| InterHand2.6M | 2020 | 260 万帧 | 双手交互姿态估计 | 单/双手交互场景，三维关节点与网格标注 |
| HanCo | 2021 | 135 万帧 | 手部多视角重建 | 多摄像机视角，手部三维重建基准 |


## 自动驾驶数据集

自动驾驶（Autonomous Driving）感知系统依赖激光雷达（LiDAR）、摄像机、毫米波雷达（Radar）等多种传感器。以下数据集是自动驾驶感知研究的核心基准。

| 数据集 | 机构 | 年份 | 传感器配置 | 规模 | 主要特点 |
|--------|------|------|-----------|------|----------|
| KITTI | 卡尔斯鲁厄理工学院（KIT）/ 丰田 | 2012 | 双目相机 + Velodyne 64 线激光雷达 + GPS | 15,000 帧（三维检测） | 自动驾驶元老级基准，覆盖三维检测、立体视觉、视觉里程计等多项任务 |
| nuScenes | Motional | 2020 | 6 相机 + 1 激光雷达 + 5 毫米波雷达 | 1,000 段场景（40,000 帧） | 全传感器配置，360° 全覆盖标注，支持三维检测与跟踪 |
| Waymo Open Dataset | Waymo | 2019 | 5 激光雷达 + 5 相机 | 2,030 段场景 | 超大规模，标注质量高，是自动驾驶竞赛最常用基准之一 |
| Argoverse 2 | Argo AI | 2022 | 7 环视相机 + 2 激光雷达 | 150,000 段场景 | 专注运动预测（Motion Forecasting）与三维检测，地图数据丰富 |
| nuPlan | Motional | 2021 | 与 nuScenes 类似 | 1,500 小时驾驶数据 | 专为规划（Planning）任务设计，是闭环规划基准 |
| CARLA Leaderboard | 仿真（Carla 引擎） | 2019 | 仿真多传感器 | 虚拟场景 | 闭环端到端自动驾驶仿真测试基准，支持模型在线提交评测 |
| Lyft Level 5 | Lyft | 2019 | 3 激光雷达 + 6 相机 | 170,000 段场景 | 大规模运动预测数据集 |
| A2D2 | 奥迪（Audi） | 2020 | 6 相机 + 5 激光雷达 | 41,000 帧（精标注） | 涵盖语义分割、三维检测、驾驶行为标注 |

### KITTI 数据集详解

**KITTI** 是使用历史最长的自动驾驶基准，数据采集平台搭载：

- 2 个灰度摄像机 + 2 个彩色摄像机（双目立体视觉）
- 1 个 Velodyne HDL-64E 三维激光雷达
- 1 套 GPS/IMU 惯性导航系统

KITTI 包含 22 个驾驶序列，支持视觉里程计（Visual Odometry）、三维物体检测与跟踪、立体深度估计等任务的评测。

### nuScenes 数据集详解

**nuScenes** 由 Motional 公司（原 nuTonomy）发布，是第一个提供完整传感器套件（Camera + LiDAR + Radar）全标注的自动驾驶数据集，主要特点：

- 场景覆盖波士顿和新加坡两座城市
- 每帧标注 23 个类别、80 万个三维边界框
- 提供标准化开发套件（devkit）与在线排行榜


## 机器人操作数据集

数据下载后的处理流程见[开放机器人数据集实践](open-robot-datasets.md)，包括 OXE、BridgeData V2、DROID、RLDS 与 LeRobotDataset 的使用入口，以及转换、质量检查、划分和数据混合方法。


机器人操作（Robot Manipulation）数据集记录机械臂完成抓取、装配、整理等任务的过程数据，是模仿学习（Imitation Learning）和具身智能（Embodied Intelligence）研究的核心资源。

| 数据集 | 发布机构 | 年份 | 规模 | 机器人平台 | 主要特点 |
|--------|----------|------|------|-----------|----------|
| YCB-Video | 卡内基梅隆大学（CMU） | 2018 | 92 段视频，133,827 帧 | 固定相机 | 六自由度（6DoF）物体位姿估计，使用 YCB 物体集，含深度图 |
| OCID | 格拉茨技术大学 | 2019 | 2,300 张 | 深度相机 | 杂乱桌面（Object Cluttered Indoor Dataset）场景分割，适合抓取研究 |
| Open X-Embodiment | Google DeepMind 等 | 2023 | 100 万+ 演示片段 | 22 种机器人平台 | 跨具身学习（Cross-Embodiment）基准，汇聚全球 33 个研究机构数据 |
| RH20T | 清华大学 | 2023 | 140,000 段操作演示 | 双臂机器人 | 多模态传感器（视觉、力觉、触觉），涵盖 140 种操作任务 |
| DROID | 斯坦福大学等 | 2024 | 76,000 段演示 | Franka Emika Panda | 多样化家庭操作场景，数据采集跨越多个机构，分布多样性强 |
| BridgeData V2 | UC Berkeley | 2023 | 60,096 段演示 | WidowX 机械臂 | 厨房与桌面操作场景，支持跨环境泛化研究 |
| RT-2 数据（仅参考） | Google DeepMind | 2023 | 互联网规模视觉语言数据 + 机器人数据 | 多种 | 视觉语言动作模型（VLA）训练数据，未完全公开 |
| RoboSet | 印度理工学院孟买校区 | 2023 | 100,000 段演示 | Franka Panda | 厨房操作任务，多视角，含失败样本 |

### Open X-Embodiment 详解

**Open X-Embodiment（OXE）** 是机器人操作领域规模最大的开放数据集联合体，由 Google DeepMind 联合全球 33 家机构共同发布：

- 汇聚了 22 种不同机械臂与移动操作平台的数据
- 覆盖抓取、放置、开关门、倒水等多种操作任务
- 使用 RLDS（Reinforcement Learning Datasets）组织 episode 与 step；统一存储结构后仍需检查各子集的动作语义，见 [RLDS 官方规范](https://github.com/google-research/rlds)
- 与 RT-X 模型（Robotics Transformer X）联合发布，支持跨具身模型训练

### YCB 物体集

**YCB 物体集（Yale-CMU-Berkeley Object Set）** 是机器人抓取与操作研究中使用最广泛的标准物体集合，包含 77 种日常物品（罐头、工具、食品等），所有物品均提供三维点云模型与物理属性参数，被 YCBV、YCB-Video 等多个数据集采用。


## 导航与 SLAM 数据集

同步定位与地图构建（Simultaneous Localization and Mapping，SLAM）数据集用于评估机器人在未知环境中的自主导航能力。

| 数据集 | 发布机构 | 传感器 | 环境 | 主要特点 |
|--------|----------|--------|------|----------|
| TUM RGB-D | 慕尼黑工业大学（TUM） | RGB-D 相机（Kinect） | 室内 | 39 个序列，含精确真值轨迹（运动捕捉系统），视觉里程计与 SLAM 标准基准 |
| EuRoC MAV | ETH 苏黎世 | 双目相机 + IMU | 无人机室内飞行 | 11 个序列，分易/中/难三级难度，视觉惯性里程计（VIO）标准基准 |
| NCLT | 密歇根大学 | LiDAR + GPS + IMU + 相机 | 校园室外 | 27 次重复采集，跨越四季，适合长期建图与定位研究 |
| Newer College Dataset | 牛津大学 | LiDAR（Ouster OS1）+ IMU | 校园室外 | 三维激光 SLAM 基准，地形变化丰富，含动态行人 |
| MulRan | 韩国科学技术院（KAIST） | LiDAR + FMCW 毫米波雷达 | 城市场景 | 多次重访，专门评估雷达里程计与场所识别 |
| UTBM | 法国贝尔福-蒙贝利亚大学 | LiDAR + IMU + GPS + 相机 | 城市室外 | 多路径重复采集，支持四维地图与时序建图研究 |
| Hilti SLAM Challenge | Hilti 集团 | LiDAR + IMU + 相机 | 建筑工地 | 专注建筑工地环境，挑战性强 |
| ReFusion | 波恩大学（Uni Bonn） | RGB-D 相机 | 室内动态场景 | 24 段视频，含动态物体，用于动态环境三维重建评测 |

### TUM RGB-D 数据集详解

**TUM RGB-D** 是视觉 SLAM 与视觉里程计领域引用最广泛的室内基准，主要特点：

- 使用 Microsoft Kinect 传感器录制
- 通过高精度运动捕捉（Motion Capture）系统获取六自由度真值轨迹
- 数据分类涵盖：手持 SLAM、机器人 SLAM、动态物体、三维物体重建等多种场景
- 提供在线评测工具，可直接上传轨迹文件获取绝对轨迹误差（ATE）和相对位姿误差（RPE）

动态子集（Dynamic Objects）包含 9 个序列，覆盖坐姿/行走两种动态程度以及四种相机运动模式（xyz、rpy、halfsphere、static），是动态 SLAM 研究（如 DynaSLAM、DS-SLAM）的核心评测数据集。

### EuRoC MAV 数据集详解

**EuRoC MAV（Micro Aerial Vehicle）** 由 ETH 苏黎世机器人与感知组（Robotics and Perception Group）发布，专为无人机视觉惯性里程计设计：

- 11 个序列分为机器大厅（Machine Hall）和 Vicon Room 两类场景
- 采用 Vicon 运动捕捉系统提供厘米级真值轨迹
- 时间戳对齐的双目相机（20 Hz）和 IMU（200 Hz）数据
- 是 VINS-Mono、ORB-SLAM3 等算法的标准评测基准


## 强化学习与仿真数据集/基准

强化学习（Reinforcement Learning，RL）在机器人控制领域被广泛应用，以下列出主要的离线强化学习数据集和仿真基准环境。

### 离线强化学习数据集

| 数据集 | 发布机构 | 年份 | 任务类型 | 主要特点 |
|--------|----------|------|----------|----------|
| D4RL | UC Berkeley | 2020 | 迷宫导航、机械臂操作、MuJoCo 运动控制 | 离线强化学习（Offline RL）标准基准，包含专家/随机/混合等多种质量的数据 |
| RL Unplugged | DeepMind | 2020 | Atari、DM Control、RealWorld RL | 大规模离线 RL 数据集套件 |
| AWAC Data | UC Berkeley | 2021 | 机械臂操作 | 在线/离线混合学习场景，附带预训练数据 |

**D4RL（Datasets for Deep Data-Driven Reinforcement Learning）** 由 UC Berkeley 发布，是目前离线强化学习研究中使用最广泛的基准，包含：

- **Maze2D / AntMaze**：迷宫导航任务，测试稀疏奖励下的长程规划能力
- **Gym-MuJoCo**：HalfCheetah、Hopper、Walker2d 等经典运动控制任务
- **Adroit**：灵巧手（Dexterous Hand）操作任务（抓笔、开门等）
- **Kitchen**：厨房多步骤操作任务

### 仿真基准平台

| 平台 | 发布机构 | 任务类型 | 主要特点 |
|------|----------|----------|----------|
| ManiSkill2 | 上海人工智能实验室 | 20 类操作任务 | GPU 并行仿真，提供演示数据，支持模仿学习与强化学习 |
| IsaacGym / Isaac Lab | NVIDIA | 运动控制、操作 | GPU 大规模并行仿真，支持数千环境并行训练，适合深度强化学习 |
| RLBench | Imperial College London | 18 种操作任务 | 基于 Pyrep/CoppeliaSim 构建，提供任务演示与变体 |
| MuJoCo（Gymnasium） | DeepMind / Farama | 运动控制 | 物理精确仿真器，强化学习控制策略基础测试平台 |
| Habitat 2.0 | Meta AI | 室内导航、移动操作 | 光照真实感渲染，支持移动抓取等具身任务 |
| AI2-THOR | Allen Institute for AI | 室内交互 | 支持物体交互、任务规划，具身导航基准 |

**ManiSkill2** 由上海人工智能实验室发布，提供标准化的操作任务接口与可微分仿真支持，是目前操作学习领域主流的仿真基准之一。

**Isaac Lab**（前身 IsaacGym）基于 NVIDIA PhysX 物理引擎，支持在单块 GPU 上同时运行数千个并行环境，大幅降低深度强化学习策略训练的时间成本，广泛应用于四足机器人、灵巧手等运动控制研究。


## 数据集管理与标注工具

高质量的数据集离不开便捷的标注与管理工具。以下是机器人与计算机视觉领域常用的工具平台。

### 数据标注工具

| 工具 | 类型 | 支持任务 | 主要特点 |
|------|------|----------|----------|
| CVAT | 开源 | 检测、分割、关键点、视频跟踪 | Computer Vision Annotation Tool，Web 端运行，支持图像/视频，社区活跃 |
| Label Studio | 开源 | 图像、文本、音频、视频 | 灵活的多模态标注平台，支持 ML 辅助标注后端 |
| Labelme | 开源 | 多边形分割、关键点 | 轻量级本地桌面工具，JSON 格式输出，适合小规模快速标注 |
| Scale AI | 商业 | 全类型视觉标注 | 专业数据标注服务，质量高，支持自动驾驶、机器人数据集 |
| Supervisely | 商业/社区版 | 检测、分割、关键点 | 支持团队协作与版本管理，内置模型辅助标注 |

**CVAT（Computer Vision Annotation Tool）** 由 Intel 开源，现由社区维护，支持：

- 图像与视频的边界框、多边形、折线、关键点标注
- 半自动标注（与 SAM、DINO 等模型集成）
- 多用户协作与权限管理
- 导出格式：COCO、Pascal VOC、YOLO、CVAT XML 等

### 数据集管理平台

| 工具 | 发布机构 | 主要功能 |
|------|----------|----------|
| Roboflow | Roboflow Inc. | 数据集版本控制、格式转换（YOLO/COCO/VOC）、在线标注、数据增强、模型训练 |
| FiftyOne | Voxel51 | 数据集可视化与分析、质量评估、标注错误排查、与 Hugging Face 集成 |
| Hugging Face Datasets | Hugging Face | 机器人与视觉数据集托管，标准化 LeRobot Dataset 格式，支持流式加载 |
| DVC（Data Version Control） | Iterative AI | 大文件数据集版本管理，与 Git 协同工作 |

**Roboflow** 提供从标注、增强到部署的一站式数据管道，支持将数据集导出为 YOLO、COCO JSON、Pascal VOC、TFRecord 等多种格式，并内置数据质量检测（重复图像、标注异常检测）功能。

**FiftyOne** 由 Voxel51 开发，是目前最强大的数据集可视化与质量分析工具之一：

- 支持浏览 COCO、Open Images、ImageNet 等标准数据集
- 内置标注错误检测算法（Label Studio Integration）
- 支持嵌入空间可视化（使用 UMAP/t-SNE 分析数据分布）
- 与 Hugging Face Hub 和 Roboflow 直接集成

**Hugging Face Datasets** 为机器人学习数据集提供统一的托管与访问接口，LeRobot 项目定义的 `LeRobotDataset` 格式正在成为机器人演示数据的标准格式，支持高效流式加载与多模态数据对齐。


## 数据集选型建议

不同研究场景对数据集的需求差异显著，以下给出简要选型指引：

| 研究方向 | 推荐数据集 |
|----------|-----------|
| 目标检测模型训练 | COCO、Objects365（预训练）、Pascal VOC（经典基准） |
| 语义分割（自动驾驶） | Cityscapes、Mapillary Vistas |
| 语义分割（通用场景） | ADE20K、COCO（全景分割） |
| 三维人体姿态估计 | Human3.6M、MPI-INF-3DHP |
| 自动驾驶感知 | nuScenes、Waymo Open Dataset、KITTI |
| 运动预测 | Argoverse 2、nuScenes Prediction |
| 室内视觉 SLAM | TUM RGB-D、ScanNet |
| 无人机视觉惯性里程计 | EuRoC MAV |
| 激光雷达 SLAM | Newer College Dataset、MulRan、NCLT |
| 机器人操作（模仿学习） | Open X-Embodiment、BridgeData V2、DROID |
| 物体位姿估计 | YCB-Video、BOP Benchmark |
| 离线强化学习 | D4RL、RL Unplugged |
| 仿真训练环境 | IsaacGym/Isaac Lab、ManiSkill2、RLBench |


## 参考资料

- Lin, T.-Y., et al. "Microsoft COCO: Common Objects in Context." ECCV 2014. [cocodataset.org](https://cocodataset.org/)
- Geiger, A., et al. "Are We Ready for Autonomous Driving? The KITTI Vision Benchmark Suite." CVPR 2012. [cvlibs.net](http://www.cvlibs.net/datasets/kitti/)
- Caesar, H., et al. "nuScenes: A Multimodal Dataset for Autonomous Driving." CVPR 2020. [nuscenes.org](https://www.nuscenes.org/)
- Sturm, J., et al. "A Benchmark for the Evaluation of RGB-D SLAM Systems." IROS 2012. [tum.de](https://vision.in.tum.de/data/datasets/rgbd-dataset)
- Burri, M., et al. "The EuRoC Micro Aerial Vehicle Datasets." IJRR 2016. [rpg.ifi.uzh.ch](https://rpg.ifi.uzh.ch/docs/IJRR17_Burri.pdf)
- Open X-Embodiment Collaboration. "Open X-Embodiment: Robotic Learning Datasets and RT-X Models." 2023. [robotics-transformer-x.github.io](https://robotics-transformer-x.github.io/)
- Fu, Z., et al. "D4RL: Datasets for Deep Data-Driven Reinforcement Learning." 2020. [github.com/Farama-Foundation/d4rl](https://github.com/Farama-Foundation/d4rl)
- Gu, J., et al. "ManiSkill2: A Unified Benchmark for Generalizable Manipulation Skills." ICLR 2023. [maniskill2.github.io](https://maniskill2.github.io/)
- Deitke, M., et al. "RoboSet: A Large-Scale Robot Manipulation Dataset." 2023.
- CVAT 项目主页：[github.com/cvat-ai/cvat](https://github.com/cvat-ai/cvat)
- FiftyOne 文档：[docs.voxel51.com](https://docs.voxel51.com/)
- Roboflow 平台：[roboflow.com](https://roboflow.com/)
- Hugging Face LeRobot：[github.com/huggingface/lerobot](https://github.com/huggingface/lerobot)
