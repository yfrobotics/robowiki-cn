# SLAM 系统对比

!!! note "引言"
    即时定位与地图构建（Simultaneous Localization and Mapping, SLAM）领域有众多成熟的开源系统，各具特色。选择合适的 SLAM 系统需要综合考虑传感器配置、应用场景、计算资源和精度需求。本文对主流 SLAM 系统进行横向对比，并提供基准测试结果和选型指南。


## 主流 SLAM 系统概览

### 视觉 SLAM

| 系统 | 传感器 | 地图类型 | 前端 | 后端 | 回环检测 | ROS 支持 |
|------|--------|---------|------|------|---------|---------|
| ORB-SLAM3 | 单目/双目/RGB-D + IMU | 稀疏点云 | ORB 特征 | 因子图 (g2o) | DBoW2 | ROS 1/2 |
| VINS-Mono | 单目 + IMU | 稀疏点云 | 光流跟踪 | 滑窗优化 + 因子图 | DBoW2 | ROS 1/2 |
| VINS-Fusion | 单目/双目 + IMU + GPS | 稀疏点云 | 光流跟踪 | 滑窗优化 | DBoW2 | ROS 1/2 |
| Kimera | 双目 + IMU | 3D 语义网格 | 特征跟踪 | iSAM2 | DBoW2 | ROS 1 |
| RTAB-Map | RGB-D/双目/LiDAR | 稠密点云/栅格 | 多种特征 | g2o/GTSAM | 多种方法 | ROS 1/2 |

### LiDAR SLAM

| 系统 | 传感器 | 地图类型 | 前端 | 后端 | 回环检测 | ROS 支持 |
|------|--------|---------|------|------|---------|---------|
| LOAM | 3D LiDAR | 稀疏点云 | 边缘/平面特征 | 无 | 无 | ROS 1 |
| A-LOAM | 3D LiDAR | 稀疏点云 | 边缘/平面特征 | Ceres | 无 | ROS 1 |
| LeGO-LOAM | 3D LiDAR + IMU | 稀疏点云 | 地面分割 + 特征 | GTSAM | ICP | ROS 1 |
| LIO-SAM | 3D LiDAR + IMU + GPS | 稀疏点云 | 特征提取 | iSAM2 | Scan Context | ROS 1/2 |
| Cartographer | 2D/3D LiDAR + IMU | 子地图 + 概率栅格 | 扫描匹配 | 位姿图 (Ceres) | 分支定界 | ROS 1/2 |
| FAST-LIO2 | 3D LiDAR + IMU | 稠密点云 | 直接配准 (ikd-Tree) | 紧耦合 EKF | 无 | ROS 1/2 |


## 系统详细对比

### 精度与速度

| 系统 | KITTI ATE (m) | EuRoC ATE (m) | 实时性 | GPU 需求 |
|------|--------------|---------------|--------|---------|
| ORB-SLAM3 (V-I) | — | 0.035 | 是 | 否 |
| VINS-Mono | — | 0.055 | 是 | 否 |
| VINS-Fusion | — | 0.045 | 是 | 否 |
| LIO-SAM | 0.9 | — | 是 | 否 |
| Cartographer | 1.2 | — | 是 | 否 |
| FAST-LIO2 | 0.7 | — | 是 | 否 |
| RTAB-Map | 1.5 | 0.08 | 是 | 可选 |

### 计算资源需求

| 系统 | CPU 占用 | 内存占用 | 最低平台 |
|------|---------|---------|---------|
| ORB-SLAM3 | 中 | 500 MB–2 GB | i5 / Jetson Xavier |
| VINS-Fusion | 中 | 300 MB–1 GB | i5 / Jetson Xavier |
| LIO-SAM | 中高 | 1–4 GB | i5 / Jetson Orin |
| Cartographer | 中 | 500 MB–2 GB | i3 / Jetson Nano |
| FAST-LIO2 | 低 | 300 MB–1 GB | i3 / Jetson Nano |
| RTAB-Map | 高 | 2–8 GB | i7 / Jetson Xavier |

### 特殊场景表现

| 场景 | 推荐系统 | 原因 |
|------|---------|------|
| 纹理缺失室内 | LIO-SAM, Cartographer | LiDAR 不依赖视觉纹理 |
| 光照变化剧烈 | LIO-SAM, FAST-LIO2 | LiDAR 不受光照影响 |
| 长走廊 | Cartographer (2D) | 分支定界回环检测鲁棒 |
| 室外大范围 | LIO-SAM + GPS | GPS 提供全局约束 |
| 动态环境 | ORB-SLAM3 | 运动一致性检查 |
| 资源受限 | FAST-LIO2 | 计算量最小 |
| 需要稠密重建 | RTAB-Map | 支持稠密点云/网格 |


## 各系统安装与快速使用

### ORB-SLAM3

```bash
# 依赖：OpenCV 4.x, Eigen3, Pangolin, g2o (内置)
cd ORB_SLAM3
chmod +x build.sh
./build.sh

# 运行示例（EuRoC 数据集，双目+IMU）
./Examples/Stereo-Inertial/stereo_inertial_euroc \
    Vocabulary/ORBvoc.txt \
    Examples/Stereo-Inertial/EuRoC.yaml \
    /path/to/MH_01_easy \
    Examples/Stereo-Inertial/EuRoC_TimeStamps/MH01.txt
```

### LIO-SAM (ROS 2)

```bash
# 安装
cd ~/ros2_ws/src
git clone https://github.com/TixiaoShan/LIO-SAM.git -b ros2
cd ~/ros2_ws && colcon build --packages-select lio_sam

# 配置关键参数 (config/params.yaml)
# N_SCAN: LiDAR 线数 (16, 32, 64, 128)
# Horizon_SCAN: 水平分辨率
# extrinsicRot/Trans: LiDAR-IMU 外参

# 运行
ros2 launch lio_sam run.launch.py
ros2 bag play dataset.db3
```

### Cartographer (ROS 2)

```bash
sudo apt install ros-humble-cartographer ros-humble-cartographer-ros

# 配置 lua 参数文件
# tracking_frame = "imu_link"
# published_frame = "base_link"
# use_imu_data = true
# num_subdivisions_per_laser_scan = 10

ros2 launch cartographer_ros cartographer.launch.py
```


## 选型决策指南

选择 SLAM 系统的关键考虑因素：

1. **传感器配置**：你有什么传感器？
    - 仅相机 → ORB-SLAM3, VINS-Mono
    - 相机 + IMU → VINS-Fusion, ORB-SLAM3 (VIO 模式)
    - LiDAR + IMU → LIO-SAM, FAST-LIO2
    - 2D LiDAR → Cartographer
    - RGB-D → RTAB-Map, ORB-SLAM3

2. **地图需求**：你需要什么样的地图？
    - 导航用栅格地图 → Cartographer, RTAB-Map
    - 稀疏特征地图 → ORB-SLAM3, LIO-SAM
    - 稠密重建 → RTAB-Map, Kimera

3. **计算预算**：你的计算平台是什么？
    - Jetson Nano/低算力 → FAST-LIO2, Cartographer (2D)
    - Jetson Xavier/中算力 → LIO-SAM, ORB-SLAM3
    - 桌面 PC → 均可

4. **应用场景**：
    - 室内服务机器人 → Cartographer (2D) + Navigation2
    - 室外自动驾驶 → LIO-SAM + GPS
    - 无人机 → VINS-Fusion
    - 地下/矿井 → FAST-LIO2（无 GPS 可用）


## 参考资料

1. Campos, C., et al. (2021). ORB-SLAM3: An Accurate Open-Source Library for Visual, Visual-Inertial and Multi-Map SLAM. *IEEE Transactions on Robotics*.
2. Shan, T., et al. (2020). LIO-SAM: Tightly-coupled Lidar Inertial Odometry via Smoothing and Mapping. *IROS*.
3. Qin, T., Li, P., & Shen, S. (2018). VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator. *IEEE Transactions on Robotics*.
4. Hess, W., et al. (2016). Real-Time Loop Closure in 2D LIDAR SLAM. *ICRA*.
5. Xu, W., & Zhang, F. (2022). FAST-LIO2: Fast Direct LiDAR-Inertial Odometry. *IEEE Transactions on Robotics*.
6. Labbé, M., & Michaud, F. (2019). RTAB-Map as an Open-Source Lidar and Visual SLAM Library for Large-Scale and Long-Term Online Operation. *Journal of Field Robotics*.
