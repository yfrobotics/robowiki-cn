# SLAM 工程实践手册

!!! note "引言"
    将 SLAM 系统从数据集演示部署到真实机器人上需要大量的工程调试工作。本手册总结传感器选型、标定流程、参数调优、回环检测调优、地图管理和导航集成的实践经验，以及常见故障排查方法。


## 传感器选型

### LiDAR 选型

| 类型 | 代表产品 | 线数/FOV | 测距范围 | 价格区间 | 适用场景 |
|------|---------|---------|---------|---------|---------|
| 2D 单线 | RPLiDAR A2/A3 | 360° | 12–25 m | ¥500–2000 | 室内机器人 |
| 2D 单线 | Hokuyo UTM-30LX | 270° | 30 m | ¥20,000+ | 工业 AGV |
| 3D 机械式 | Velodyne VLP-16 | 16 线 360° | 100 m | ¥30,000+ | 室外移动 |
| 3D 固态 | Livox Mid-360 | 非重复扫描 | 40 m | ¥3,000+ | 低成本 3D |
| 3D 机械式 | Ouster OS1-128 | 128 线 360° | 120 m | ¥50,000+ | 自动驾驶 |

### 相机选型

| 类型 | 代表产品 | 分辨率 | 帧率 | 特点 |
|------|---------|--------|------|------|
| 全局快门单目 | FLIR Blackfly S | 1440p | 60 fps | VIO 首选 |
| RGB-D | Intel RealSense D435i | 1280×720 | 30 fps | 内置 IMU |
| 双目 | ZED 2 | 2K | 15 fps | 长基线，内置 IMU |
| 事件相机 | iniVation DAVIS | 640×480 | >1000 fps（事件） | 极端光照、高速 |

### IMU 选型

| 等级 | 代表产品 | 陀螺零偏稳定性 | 价格 | 适用 |
|------|---------|---------------|------|------|
| 消费级 (MEMS) | BMI088, MPU9250 | 1–10 °/h | <¥100 | 教育、低成本 |
| 战术级 (MEMS) | ADIS16470 | 0.1–1 °/h | ¥2,000–5,000 | 机器人、无人机 |
| 导航级 | 光纤陀螺 | <0.01 °/h | ¥50,000+ | 自动驾驶、航空 |


## 标定流程

### 相机-IMU 标定（Kalibr）

```bash
# 1. 录制标定数据
# 手持相机+IMU 面对标定板，做丰富的旋转和平移运动
ros2 bag record /camera/image_raw /imu/data -o calib_bag

# 2. 准备标定板配置文件 (april_grid.yaml)
# target_type: 'aprilgrid'
# tagCols: 6
# tagRows: 6
# tagSize: 0.088    # 标签边长 (m)
# tagSpacing: 0.3   # 标签间距比

# 3. 准备 IMU 噪声参数文件 (imu.yaml)
# rostopic: /imu/data
# update_rate: 200
# accelerometer_noise_density: 0.01    # m/s^2/sqrt(Hz)
# accelerometer_random_walk: 0.0002
# gyroscope_noise_density: 0.005       # rad/s/sqrt(Hz)
# gyroscope_random_walk: 3.0e-05

# 4. 运行标定
rosrun kalibr kalibr_calibrate_imu_camera \
    --target april_grid.yaml \
    --cam cam.yaml \
    --imu imu.yaml \
    --bag calib_bag.db3 \
    --bag-freq 20
```

标定质量检查：

- 重投影误差应 < 0.5 像素
- IMU 残差应无明显趋势
- 外参结果应与物理测量一致（粗略验证）

### LiDAR-IMU 外参标定

多数 LiDAR SLAM 系统（如 LIO-SAM）要求精确的 LiDAR-IMU 外参。实践中常用方法：

1. **CAD 测量**：从机械图纸获取粗略外参
2. **手动调整**：运行 SLAM，观察点云对齐情况，微调旋转参数
3. **自动标定**：使用 LI-Init 等自动标定工具


## 参数调优

### 室内环境

```yaml
# Cartographer 2D 室内调优
TRAJECTORY_BUILDER_2D.min_range = 0.2        # 过滤近距离噪声
TRAJECTORY_BUILDER_2D.max_range = 20.0       # 室内不需要太远
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 5.0
TRAJECTORY_BUILDER_2D.num_accumulated_range_data = 1
TRAJECTORY_BUILDER_2D.use_imu_data = true

# 子地图参数
TRAJECTORY_BUILDER_2D.submaps.num_range_data = 90  # 子地图大小
TRAJECTORY_BUILDER_2D.submaps.grid_options_2d.resolution = 0.05  # 5cm 分辨率

# 回环检测
POSE_GRAPH.optimize_every_n_nodes = 90
POSE_GRAPH.constraint_builder.min_score = 0.55     # 匹配阈值
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.6
```

### 室外环境

```yaml
# LIO-SAM 室外调优 (params.yaml)
lio_sam:
  ros__parameters:
    # LiDAR 参数
    N_SCAN: 16             # VLP-16 线数
    Horizon_SCAN: 1800     # 水平分辨率
    downsampleRate: 1

    # IMU 参数
    imuAccNoise: 3.9939570888238808e-03
    imuGyrNoise: 1.5636343949698187e-03
    imuAccBiasN: 6.4356659353532566e-05
    imuGyrBiasN: 3.5640318696367613e-05
    imuGravity: 9.80511

    # 里程计参数
    edgeFeatureMinValidNum: 10    # 最少边缘特征数
    surfFeatureMinValidNum: 100   # 最少平面特征数

    # 回环检测
    loopClosureEnableFlag: true
    loopClosureFrequency: 1.0     # Hz
    surroundingKeyframeSearchRadius: 50.0  # 搜索半径 (m)
    historyKeyframeSearchNum: 25

    # GPS 融合
    useGpsElevation: false
    gpsCovThreshold: 2.0   # GPS 协方差阈值
```

### 地下/矿井环境

地下环境特殊挑战：无 GPS、重复结构、灰尘干扰。

关键调整：

- 增大特征提取密度
- 关闭 GPS 相关模块
- 增大回环检测搜索范围
- 降低回环匹配阈值（更积极地尝试回环）
- 使用 IMU 预积分抵消 LiDAR 退化


## 回环检测调优

### 回环检测方法对比

| 方法 | 输入 | 优点 | 缺点 |
|------|------|------|------|
| DBoW2 | 视觉特征 | 成熟、快速 | 依赖视觉 |
| Scan Context | LiDAR 点云 | 旋转不变、视角不变 | 需要 3D LiDAR |
| ICP 验证 | 点云 | 精确对齐 | 计算量大 |
| RING | LiDAR 点云 | 快速、鲁棒 | 较新 |

### 回环闭合的影响

回环检测参数过松会导致错误回环（False Positive），表现为地图突然扭曲变形。过严则无法修正漂移。

建议策略：

1. 初始运行时关闭回环检测，观察里程计漂移程度
2. 启用回环，从高阈值开始逐步降低
3. 观察优化后的轨迹是否合理
4. 如果出现错误回环，提高匹配阈值或增加 ICP 验证


## 地图管理

### 地图保存与加载

```bash
# Cartographer: 保存 .pbstream 地图
ros2 service call /write_state cartographer_ros_msgs/srv/WriteState \
    "{filename: '/maps/building_1f.pbstream'}"

# RTAB-Map: 保存数据库
# 默认保存在 ~/.ros/rtabmap.db
# 加载时指定数据库文件

# Nav2: 保存 2D 栅格地图
ros2 run nav2_map_server map_saver_cli -f /maps/building_1f
# 生成 building_1f.yaml + building_1f.pgm
```

### 地图更新策略

- **完全重建**：简单直接，适合环境变化较大时
- **增量更新**：在已有地图基础上添加新区域（RTAB-Map 原生支持）
- **多层地图**：不同时期的地图作为不同层，运行时选择最匹配的层


## 与导航栈集成

### Nav2 集成

```yaml
# nav2_params.yaml 中的定位配置
amcl:
  ros__parameters:
    use_sim_time: false
    alpha1: 0.2    # 旋转对旋转的噪声
    alpha2: 0.2    # 旋转对平移的噪声
    alpha3: 0.2    # 平移对平移的噪声
    alpha4: 0.2    # 平移对旋转的噪声
    base_frame_id: "base_link"
    global_frame_id: "map"
    laser_model_type: "likelihood_field"
    max_particles: 2000
    min_particles: 500
    update_min_a: 0.2   # 最小旋转更新阈值 (rad)
    update_min_d: 0.25  # 最小平移更新阈值 (m)
```

### TF 树

SLAM 系统与导航栈通过 TF 变换连接：

```
map → odom → base_link → sensors
 ↑      ↑
SLAM  里程计
(或 AMCL)
```

确保 TF 树中没有重复的发布者（常见错误：robot_localization 和 SLAM 同时发布 `odom → base_link`）。


## 常见故障排查

| 故障现象 | 可能原因 | 排查与修复 |
|---------|---------|----------|
| 建图开始即漂移 | IMU 轴向配置错误 | 检查 IMU 安装方向与配置一致 |
| 旋转时地图变形 | LiDAR-IMU 外参旋转分量错误 | 重新标定或手动调整 |
| 回环后地图扭曲 | 错误回环检测 | 提高匹配阈值 |
| 长走廊漂移 | 几何退化（平行墙面） | 启用 IMU 辅助、增大特征搜索范围 |
| 点云不对齐 | 时间同步问题 | 检查时间戳，使用硬件同步 |
| 内存持续增长 | 关键帧未清理 | 配置最大关键帧数或滑窗大小 |
| 开门/关门后定位丢失 | 环境变化超出容忍范围 | 使用 AMCL 全局重定位 |


## 参考资料

1. Furgale, P., Rehder, J., & Siegwart, R. (2013). Unified Temporal and Spatial Calibration for Multi-Sensor Systems. *IROS*.
2. Kalibr 标定工具包：https://github.com/ethz-asl/kalibr
3. Cartographer 调优指南：https://google-cartographer-ros.readthedocs.io/en/latest/tuning.html
4. LIO-SAM 项目：https://github.com/TixiaoShan/LIO-SAM
5. Navigation2 文档：https://docs.nav2.org/
6. Kim, G., & Kim, A. (2018). Scan Context: Egocentric Spatial Descriptor for Place Recognition within 3D Point Cloud Map. *IROS*.
