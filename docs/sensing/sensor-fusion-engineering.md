# 传感器融合工程实践

!!! note "引言"
    本页面是[传感器融合](sensor-fusion.md)专题的工程实践部分，涵盖扩展卡尔曼滤波器（EKF）的 Python 实现、互补滤波器、ROS 2 robot_localization 包的配置与使用、融合系统调试技巧、异常值剔除以及性能评测方法。


## 扩展卡尔曼滤波器实现

### EKF 算法概述

扩展卡尔曼滤波器（Extended Kalman Filter, EKF）通过一阶泰勒展开将非线性系统线性化，然后应用标准卡尔曼滤波。两个核心步骤：

**预测步骤**：

$$
\hat{\mathbf{x}}_{k|k-1} = f(\hat{\mathbf{x}}_{k-1|k-1}, \mathbf{u}_k)
$$

$$
P_{k|k-1} = F_k P_{k-1|k-1} F_k^T + Q_k
$$

**更新步骤**：

$$
K_k = P_{k|k-1} H_k^T (H_k P_{k|k-1} H_k^T + R_k)^{-1}
$$

$$
\hat{\mathbf{x}}_{k|k} = \hat{\mathbf{x}}_{k|k-1} + K_k (\mathbf{z}_k - h(\hat{\mathbf{x}}_{k|k-1}))
$$

$$
P_{k|k} = (I - K_k H_k) P_{k|k-1}
$$

### GPS + IMU 融合示例

```python
import numpy as np

class EKF_GPS_IMU:
    """GPS + IMU 融合的简化 EKF 实现"""

    def __init__(self, dt=0.01):
        self.dt = dt
        # 状态: [x, y, vx, vy, yaw]
        self.x = np.zeros(5)
        self.P = np.eye(5) * 1.0

        # 过程噪声
        self.Q = np.diag([0.1, 0.1, 0.5, 0.5, 0.01])

        # GPS 观测噪声 (位置)
        self.R_gps = np.diag([2.0, 2.0])  # GPS 精度 ~2m

        # IMU 观测噪声 (加速度 + 角速度)
        self.R_imu = np.diag([0.1, 0.1, 0.01])

    def predict(self, accel, gyro):
        """IMU 预测步骤"""
        x, y, vx, vy, yaw = self.x
        dt = self.dt

        # 将 body 系加速度转换到世界系
        ax_w = accel[0] * np.cos(yaw) - accel[1] * np.sin(yaw)
        ay_w = accel[0] * np.sin(yaw) + accel[1] * np.cos(yaw)

        # 状态转移
        self.x = np.array([
            x + vx * dt + 0.5 * ax_w * dt**2,
            y + vy * dt + 0.5 * ay_w * dt**2,
            vx + ax_w * dt,
            vy + ay_w * dt,
            yaw + gyro * dt
        ])

        # 雅可比矩阵
        F = np.eye(5)
        F[0, 2] = dt
        F[1, 3] = dt
        F[2, 4] = (-accel[0] * np.sin(yaw) - accel[1] * np.cos(yaw)) * dt
        F[3, 4] = (accel[0] * np.cos(yaw) - accel[1] * np.sin(yaw)) * dt

        self.P = F @ self.P @ F.T + self.Q

    def update_gps(self, gps_pos):
        """GPS 位置更新"""
        H = np.zeros((2, 5))
        H[0, 0] = 1.0  # 观测 x
        H[1, 1] = 1.0  # 观测 y

        z = np.array(gps_pos)
        y = z - H @ self.x  # 新息 (innovation)

        S = H @ self.P @ H.T + self.R_gps
        K = self.P @ H.T @ np.linalg.inv(S)

        self.x = self.x + K @ y
        self.P = (np.eye(5) - K @ H) @ self.P

    def get_state(self):
        return self.x.copy()

# 使用示例
ekf = EKF_GPS_IMU(dt=0.01)

for i in range(10000):
    # IMU 数据 (100Hz)
    accel = read_accelerometer()  # [ax, ay] in body frame
    gyro = read_gyroscope()       # yaw rate
    ekf.predict(accel, gyro)

    # GPS 数据 (1Hz)
    if i % 100 == 0:
        gps = read_gps()  # [x, y]
        ekf.update_gps(gps)

    state = ekf.get_state()
```


## 互补滤波器

互补滤波器（Complementary Filter）是一种简单高效的融合方法，特别适合 IMU 姿态估计。核心思想：利用陀螺仪的短期精度和加速度计的长期稳定性。

```python
class ComplementaryFilter:
    """IMU 姿态互补滤波器"""

    def __init__(self, alpha=0.98, dt=0.01):
        self.alpha = alpha  # 陀螺仪权重 (0.95-0.99)
        self.dt = dt
        self.roll = 0.0
        self.pitch = 0.0

    def update(self, gyro, accel):
        # 陀螺仪积分（短期准确）
        self.roll += gyro[0] * self.dt
        self.pitch += gyro[1] * self.dt

        # 加速度计估计（长期稳定）
        accel_roll = np.arctan2(accel[1], accel[2])
        accel_pitch = np.arctan2(-accel[0],
                                  np.sqrt(accel[1]**2 + accel[2]**2))

        # 互补融合
        self.roll = self.alpha * self.roll + (1 - self.alpha) * accel_roll
        self.pitch = self.alpha * self.pitch + (1 - self.alpha) * accel_pitch

        return self.roll, self.pitch
```

\(\alpha\) 越大越信任陀螺仪（高频响应好），越小越信任加速度计（低频稳定）。


## ROS 2 robot_localization 配置

`robot_localization` 是 ROS 2 中最常用的传感器融合包，提供 EKF 和 UKF 两种滤波器节点。

### 基本配置

```yaml
# ekf.yaml
ekf_filter_node:
  ros__parameters:
    frequency: 30.0
    sensor_timeout: 0.1
    two_d_mode: false
    publish_tf: true

    map_frame: map
    odom_frame: odom
    base_link_frame: base_link
    world_frame: odom

    # 里程计输入（编码器）
    odom0: /wheel_odom
    odom0_config: [false, false, false,   # x, y, z
                   false, false, false,   # roll, pitch, yaw
                   true,  true,  false,   # vx, vy, vz
                   false, false, true,    # vroll, vpitch, vyaw
                   false, false, false]   # ax, ay, az

    # IMU 输入
    imu0: /imu/data
    imu0_config: [false, false, false,   # x, y, z
                  true,  true,  true,    # roll, pitch, yaw
                  false, false, false,   # vx, vy, vz
                  true,  true,  true,    # vroll, vpitch, vyaw
                  true,  true,  true]    # ax, ay, az
    imu0_remove_gravitational_acceleration: true

    # GPS 输入（需要 navsat_transform_node 转换）
    odom1: /odometry/gps
    odom1_config: [true,  true,  false,
                   false, false, false,
                   false, false, false,
                   false, false, false,
                   false, false, false]

    # 过程噪声协方差（对角线元素）
    process_noise_covariance: [0.05, 0.05, 0.06, 0.03, 0.03, 0.06,
                               0.025, 0.025, 0.04, 0.01, 0.01, 0.02,
                               0.01, 0.01, 0.015]
```

### 双 EKF 架构

对于需要全局定位的机器人，推荐使用双 EKF 架构：

- **EKF Local**（odom 帧）：融合连续传感器（编码器 + IMU），提供平滑的局部里程计
- **EKF Global**（map 帧）：在 Local 基础上融合绝对定位（GPS/AMCL），提供全局位姿

```python
# launch 文件片段
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_local',
            parameters=['ekf_local.yaml'],
            remappings=[('odometry/filtered', '/odom/local')],
        ),
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_global',
            parameters=['ekf_global.yaml'],
            remappings=[('odometry/filtered', '/odom/global')],
        ),
        Node(
            package='robot_localization',
            executable='navsat_transform_node',
            parameters=['navsat.yaml'],
        ),
    ])
```


## 异常值剔除

### 马氏距离门控

马氏距离（Mahalanobis Distance）门控通过检查新息是否在合理范围内来剔除异常测量：

$$
d_M = \sqrt{(\mathbf{z} - \hat{\mathbf{z}})^T S^{-1} (\mathbf{z} - \hat{\mathbf{z}})}
$$

其中 \(S = H P H^T + R\) 是新息协方差。当 \(d_M\) 超过阈值（如 \(\chi^2\) 分布的 95% 分位数）时拒绝该测量。

```python
def mahalanobis_gate(z, z_pred, S, threshold=5.991):
    """
    马氏距离门控（2 自由度 95% 阈值 = 5.991）
    """
    innovation = z - z_pred
    d_sq = innovation.T @ np.linalg.inv(S) @ innovation
    return d_sq < threshold  # True 表示接受
```

### 传感器健康监测

```python
class SensorHealthMonitor:
    def __init__(self, timeout=1.0, max_consecutive_rejects=5):
        self.last_update_time = {}
        self.consecutive_rejects = {}
        self.timeout = timeout
        self.max_rejects = max_consecutive_rejects

    def check_timeout(self, sensor_name, current_time):
        if sensor_name in self.last_update_time:
            dt = current_time - self.last_update_time[sensor_name]
            if dt > self.timeout:
                return False  # 超时
        self.last_update_time[sensor_name] = current_time
        return True

    def record_reject(self, sensor_name):
        self.consecutive_rejects[sensor_name] = \
            self.consecutive_rejects.get(sensor_name, 0) + 1
        if self.consecutive_rejects[sensor_name] > self.max_rejects:
            print(f"警告: {sensor_name} 连续 {self.max_rejects} 次被拒绝")

    def record_accept(self, sensor_name):
        self.consecutive_rejects[sensor_name] = 0
```


## 调试技巧

### 常见问题诊断

| 症状 | 可能原因 | 排查方法 |
|------|---------|---------|
| 位姿漂移 | IMU 偏差未校正 | 检查静止时 IMU 读数 |
| 位姿跳变 | GPS 多径效应 | 检查 GPS 精度因子（DOP） |
| 协方差发散 | 过程噪声 Q 过小 | 增大 Q 矩阵对应项 |
| 滤波器延迟 | 传感器时间戳不准 | 检查时间同步 |
| 估计震荡 | 观测噪声 R 过小 | 增大 R 矩阵对应项 |
| 融合后精度不如单传感器 | 外参标定错误 | 重新标定传感器外参 |

### 可视化调试

```bash
# ROS 2 中可视化融合结果
ros2 launch robot_localization ekf.launch.py

# 在 RViz 中查看:
# - /odom/filtered (融合后里程计)
# - /odom/filtered 的协方差椭圆
# - 各传感器原始数据对比

# 记录数据用于离线分析
ros2 bag record /odom/filtered /wheel_odom /imu/data /gps/fix
```


## 性能评测

### EVO 评测工具

EVO（Evaluation of Odometry and SLAM）是评测定位精度的标准工具：

```bash
# 安装
pip install evo

# 绝对轨迹误差 (ATE)
evo_ape tum ground_truth.txt estimated.txt -p --plot_mode xy

# 相对位姿误差 (RPE)
evo_rpe tum ground_truth.txt estimated.txt -p --delta 1 --delta_unit m

# 多种方法对比
evo_traj tum ekf.txt ukf.txt gps_only.txt --ref ground_truth.txt -p
```

### 关键指标

| 指标 | 定义 | 典型值（室外机器人） |
|------|------|-------------------|
| ATE RMSE | 绝对轨迹误差均方根 | < 0.5 m |
| RPE（1m） | 每米相对位姿误差 | < 1% |
| 更新频率 | 融合输出频率 | > 30 Hz |
| 端到端延迟 | 传感器到输出延迟 | < 50 ms |


## 参考资料

1. Moore, T., & Stouch, D. (2016). A Generalized Extended Kalman Filter Implementation for the Robot Operating System. *Intelligent Autonomous Systems*.
2. robot_localization 文档：https://docs.ros.org/en/humble/p/robot_localization/
3. Grupp, M. (2017). EVO — Python Package for the Evaluation of Odometry and SLAM. https://github.com/MichaelGruworked/evo
4. Solà, J. (2017). Quaternion Kinematics for the Error-State Kalman Filter. arXiv:1711.02508.
5. Madgwick, S. O. (2010). An Efficient Orientation Filter for Inertial and Inertial/Magnetic Sensor Arrays. *Report*.
