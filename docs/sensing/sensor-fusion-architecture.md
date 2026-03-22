# 传感器融合架构

!!! note "引言"
    传感器融合架构决定了数据如何在系统中流动、在哪个层级进行融合、以及各模块之间的耦合程度。选择合适的融合架构直接影响系统的精度、鲁棒性、可扩展性和计算效率。本文介绍集中式、分散式和分布式三种架构模式，松耦合与紧耦合融合策略，传感器标定与时间同步技术，以及不同机器人类型的架构设计。


## 融合架构模式

### 集中式架构（Centralized Fusion）

集中式架构将所有传感器的原始数据汇集到一个中央处理节点，由单一滤波器（如扩展卡尔曼滤波器）统一处理。

```
传感器1 ──→ ┌─────────────┐
传感器2 ──→ │  中央融合器  │ ──→ 融合输出
传感器3 ──→ └─────────────┘
```

**优点**：理论上最优（利用所有原始信息），实现简单。

**缺点**：单点故障、计算负担集中、难以扩展、对通信带宽要求高。

### 分散式架构（Decentralized Fusion）

每个传感器有独立的本地处理器，各节点之间交换估计结果，没有中央协调节点。

```
传感器1 → [本地估计1] ←→ [本地估计2] ← 传感器2
                ↕                ↕
           [本地估计3] ← 传感器3
```

**优点**：无单点故障、高可扩展性、各节点可独立运行。

**缺点**：信息重复计算（双重计数问题）、通信协议复杂。

### 分布式架构（Distributed Fusion）

分布式架构介于集中式和分散式之间，每个传感器有本地处理器进行预处理和局部估计，然后将局部结果送入中央融合节点。

```
传感器1 → [局部处理1] ──→ ┌─────────────┐
传感器2 → [局部处理2] ──→ │  中央融合器  │ ──→ 融合输出
传感器3 → [局部处理3] ──→ └─────────────┘
```

这是**机器人系统中最常用的架构**，兼顾了计算分散和信息整合。

### 架构对比

| 特性 | 集中式 | 分散式 | 分布式 |
|------|--------|--------|--------|
| 精度 | 最优 | 次优 | 接近最优 |
| 鲁棒性 | 低（单点故障） | 高 | 中高 |
| 可扩展性 | 低 | 高 | 中 |
| 通信带宽 | 高（原始数据） | 中 | 低（局部估计） |
| 计算分布 | 集中 | 分散 | 混合 |
| 实现复杂度 | 低 | 高 | 中 |


## 松耦合与紧耦合

### 松耦合融合（Loosely-Coupled）

松耦合方案将每个传感器子系统作为独立模块运行，各模块输出自己的估计结果，然后在后端融合。

以视觉-惯性里程计（Visual-Inertial Odometry, VIO）为例：

```
相机 → [视觉里程计] → 位姿估计 ──→ ┌──────────┐
                                    │ EKF 融合 │ ──→ 最终位姿
IMU  → [惯性导航]  → 位姿估计 ──→  └──────────┘
```

**优点**：模块化设计、各子系统可独立开发和测试。

**缺点**：视觉里程计失败时（如纹理缺失场景）无法利用 IMU 辅助特征跟踪。

### 紧耦合融合（Tightly-Coupled）

紧耦合方案将不同传感器的原始测量直接融合到同一个优化框架中：

```
相机帧 → [特征提取] ──→ ┌──────────────────┐
                        │ 联合优化/滤波     │ ──→ 最终位姿
IMU 数据 → [预积分] ──→ │ (同时处理视觉和   │
                        │  惯性约束)        │
                        └──────────────────┘
```

**优点**：充分利用传感器间的互补信息，精度更高，在退化场景下更鲁棒。

**缺点**：实现复杂，计算量更大，调试困难。

### 紧耦合 VIO 的数学描述

状态向量包含位置、速度、姿态及 IMU 偏差：

$$
\mathbf{x} = [\mathbf{p}, \mathbf{v}, \mathbf{q}, \mathbf{b}_a, \mathbf{b}_g]^T
$$

优化目标函数同时包含 IMU 预积分残差和视觉重投影残差：

$$
\min_{\mathbf{x}} \sum_k \| \mathbf{r}_{IMU}(\mathbf{x}_k, \mathbf{x}_{k+1}) \|^2_{\Sigma_{IMU}} + \sum_{i,j} \| \mathbf{r}_{vis}(\mathbf{x}_i, \mathbf{l}_j) \|^2_{\Sigma_{vis}}
$$


## 传感器标定

### 内参标定（Intrinsic Calibration）

内参标定确定传感器自身的参数：

**相机内参**：焦距 \((f_x, f_y)\)、主点 \((c_x, c_y)\)、畸变系数 \((k_1, k_2, p_1, p_2, k_3)\)

```python
import cv2
import numpy as np

# 棋盘格标定
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((9*6, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2) * 0.025  # 25mm 格子

obj_points, img_points = [], []

for img_path in calibration_images:
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)
    if ret:
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        obj_points.append(objp)
        img_points.append(corners2)

ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(
    obj_points, img_points, gray.shape[::-1], None, None
)
print(f"内参矩阵:\n{K}")
print(f"畸变系数: {dist}")
print(f"重投影误差: {ret:.4f} 像素")
```

**IMU 内参**：加速度计和陀螺仪的零偏（Bias）、噪声密度（Noise Density）、随机游走（Random Walk）。通常通过 Allan 方差分析获取。

### 外参标定（Extrinsic Calibration）

外参标定确定传感器之间的相对位姿变换 \(\mathbf{T}_{AB} = [\mathbf{R} | \mathbf{t}]\)。

**相机-IMU 外参**：使用 Kalibr 工具包：

```bash
# Kalibr 相机-IMU 联合标定
rosrun kalibr kalibr_calibrate_imu_camera \
    --target april_grid.yaml \
    --cam cam_config.yaml \
    --imu imu_config.yaml \
    --bag calibration_data.bag
```

**相机-LiDAR 外参**：通过标定板同时在相机和 LiDAR 中检测对应特征，求解 PnP 或 ICP。


## 时间同步

### 硬件同步

硬件同步通过物理信号（如 PPS 脉冲、触发线）实现传感器的精确同步采样。

| 同步方式 | 精度 | 适用场景 |
|---------|------|---------|
| GPS PPS (Pulse Per Second) | ~50 ns | 室外、多机器人 |
| 硬件触发线 | ~1 μs | 相机-LiDAR 同步 |
| PTP (IEEE 1588) | ~1 μs | 以太网设备 |
| NTP | ~1 ms | 一般用途 |
| 软件时间戳 | ~10 ms | 低精度需求 |

### ROS 2 时间同步

ROS 2 中使用 `message_filters` 进行软件时间同步：

```python
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, Imu
from message_filters import Subscriber, ApproximateTimeSynchronizer

class SyncNode(Node):
    def __init__(self):
        super().__init__('sync_node')

        self.image_sub = Subscriber(self, Image, '/camera/image_raw')
        self.imu_sub = Subscriber(self, Imu, '/imu/data')

        # 近似时间同步器（容忍 50ms 时间差）
        self.sync = ApproximateTimeSynchronizer(
            [self.image_sub, self.imu_sub],
            queue_size=10,
            slop=0.05  # 最大时间差 (秒)
        )
        self.sync.registerCallback(self.synced_callback)

    def synced_callback(self, image_msg, imu_msg):
        dt = abs(
            image_msg.header.stamp.sec - imu_msg.header.stamp.sec +
            (image_msg.header.stamp.nanosec - imu_msg.header.stamp.nanosec) * 1e-9
        )
        self.get_logger().info(f'同步成功，时间差: {dt*1000:.1f} ms')
        # 处理同步后的数据
        self.fuse(image_msg, imu_msg)
```


## 不同机器人类型的架构设计

### 自动驾驶汽车

```
6×相机 + 1×LiDAR + 5×毫米波雷达 + GPS/RTK + IMU
           ↓                    ↓              ↓
   BEV 感知模块          雷达目标检测    INS/GPS 融合
           ↓                    ↓              ↓
        ┌──────── 多传感器融合跟踪 ──────────────┐
        ↓                                      ↓
   目标列表 + 自由空间                       自车定位
        ↓                                      ↓
        └──────────── 规划与控制 ───────────────┘
```

### 四旋翼无人机

```
双目相机 + IMU (200Hz) + 气压计 + GPS + 光流
                ↓
    紧耦合 VIO (VINS-Fusion / MSCKF)
                ↓
         EKF 融合 GPS + 气压计
                ↓
           全局位姿估计
                ↓
         飞行控制器 (PX4)
```

### 室内服务机器人

```
2D LiDAR + RGB-D 相机 + 轮式编码器 + IMU
     ↓              ↓            ↓
 2D SLAM      语义感知     里程计融合
 (Cartographer)           (robot_localization)
     ↓              ↓            ↓
  2D 占据栅格    物体检测      位姿估计
     ↓              ↓            ↓
     └──────── Nav2 导航栈 ──────┘
```


## 参考资料

1. Liggins, M. E., Hall, D. L., & Llinas, J. (2009). *Handbook of Multisensor Data Fusion* (2nd ed.). CRC Press.
2. Furgale, P., Rehder, J., & Siegwart, R. (2013). Unified Temporal and Spatial Calibration for Multi-Sensor Systems. *IROS*.
3. Qin, T., Li, P., & Shen, S. (2018). VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator. *IEEE Transactions on Robotics*.
4. Kalibr 标定工具包：https://github.com/ethz-asl/kalibr
5. ROS 2 message_filters 文档：https://docs.ros.org/en/humble/Concepts/Intermediate/About-Composition.html
