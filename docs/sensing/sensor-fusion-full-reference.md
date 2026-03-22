# 传感器融合参考资料

!!! note "引言"
    本页面汇集传感器融合相关的教材、论文、开源框架、基准数据集和核心公式，为研究和工程实践提供快速参考。


## 推荐教材

| 教材 | 作者 | 内容特色 |
|------|------|---------|
| *Probabilistic Robotics* | Thrun, Burgard, Fox | 贝叶斯滤波和 SLAM 经典著作 |
| *State Estimation for Robotics* | Barfoot, T. D. | 现代状态估计，含李群方法 |
| *Optimal State Estimation* | Simon, D. | 卡尔曼滤波全面参考 |
| *Handbook of Multisensor Data Fusion* | Liggins, Hall, Llinas | 多传感器融合百科 |
| 《多传感器信息融合》 | 何友等 | 中文参考书 |


## 关键论文

### 滤波理论

| 论文 | 年份 | 贡献 |
|------|------|------|
| Kalman (1960) | 1960 | 卡尔曼滤波器原始论文 |
| Julier & Uhlmann (1997) | 1997 | 无迹卡尔曼滤波器 (UKF) |
| Wan & van der Merwe (2000) | 2000 | UKF 用于非线性估计 |

### 视觉惯性融合

| 论文 | 年份 | 贡献 |
|------|------|------|
| Mourikis & Roumeliotis (MSCKF) | 2007 | 多状态约束卡尔曼滤波器 |
| Qin et al. (VINS-Mono) | 2018 | 鲁棒单目 VIO |
| Campos et al. (ORB-SLAM3) | 2021 | 视觉-惯性 SLAM |

### LiDAR 融合

| 论文 | 年份 | 贡献 |
|------|------|------|
| Zhang & Singh (LOAM) | 2014 | LiDAR 里程计与建图 |
| Shan & Englot (LeGO-LOAM) | 2018 | 轻量级地面优化 LOAM |
| Shan et al. (LIO-SAM) | 2020 | 紧耦合 LiDAR-IMU |

### 图优化

| 论文 | 年份 | 贡献 |
|------|------|------|
| Kümmerle et al. (g2o) | 2011 | 通用图优化框架 |
| Kaess et al. (iSAM2) | 2012 | 增量平滑与建图 |
| Dellaert & GTSAM | 2012 | 因子图推理库 |


## 开源框架

| 框架 | 语言 | 主要功能 | 适用场景 |
|------|------|---------|---------|
| GTSAM | C++/Python | 因子图优化 | SLAM、VIO 后端 |
| g2o | C++ | 图优化 | SLAM 后端 |
| Ceres Solver | C++ | 非线性最小二乘 | 标定、BA |
| robot_localization | C++ (ROS) | EKF/UKF 融合 | 移动机器人 |
| MSCKF_VIO | C++ (ROS) | 视觉惯性里程计 | 无人机 |
| OpenVINS | C++ (ROS) | 视觉惯性导航 | 研究平台 |

### GTSAM Python 示例

```python
import gtsam
import numpy as np

# 创建因子图
graph = gtsam.NonlinearFactorGraph()
initial = gtsam.Values()

# 先验因子
prior_noise = gtsam.noiseModel.Diagonal.Sigmas(np.array([0.3, 0.3, 0.1]))
graph.add(gtsam.PriorFactorPose2(1, gtsam.Pose2(0, 0, 0), prior_noise))
initial.insert(1, gtsam.Pose2(0.5, 0.0, 0.2))

# 里程计因子
odom_noise = gtsam.noiseModel.Diagonal.Sigmas(np.array([0.2, 0.2, 0.1]))
graph.add(gtsam.BetweenFactorPose2(1, 2, gtsam.Pose2(2, 0, 0), odom_noise))
initial.insert(2, gtsam.Pose2(2.3, 0.1, -0.2))

# 回环因子
loop_noise = gtsam.noiseModel.Diagonal.Sigmas(np.array([0.1, 0.1, 0.05]))
graph.add(gtsam.BetweenFactorPose2(2, 1, gtsam.Pose2(-2, 0, 0), loop_noise))

# 优化
params = gtsam.LevenbergMarquardtParams()
optimizer = gtsam.LevenbergMarquardtOptimizer(graph, initial, params)
result = optimizer.optimize()

print(f"优化后位姿1: {result.atPose2(1)}")
print(f"优化后位姿2: {result.atPose2(2)}")
```


## 基准数据集

| 数据集 | 传感器 | 场景 | 地面真值 |
|--------|--------|------|---------|
| KITTI | 双目 + LiDAR + GPS/IMU | 城市驾驶 | RTK GPS |
| EuRoC MAV | 双目 + IMU | 室内飞行 | 动捕系统 |
| TUM RGB-D | RGB-D | 室内桌面 | 动捕系统 |
| TUM VI | 双目 + IMU | 室内外 | 动捕 + GPS |
| nuScenes | 6相机 + LiDAR + Radar + GPS/IMU | 城市驾驶 | 高精定位 |
| Newer College | 多LiDAR + IMU | 室内外 | 激光扫描 |
| M2DGR | 多传感器 | 校园 | RTK GPS |
| SubT-MRS | 多传感器 | 地下 | 标记系统 |


## 核心公式速查

### 卡尔曼滤波（线性系统）

$$
\hat{x}_{k|k-1} = A\hat{x}_{k-1|k-1} + Bu_k
$$

$$
P_{k|k-1} = AP_{k-1|k-1}A^T + Q
$$

$$
K_k = P_{k|k-1}H^T(HP_{k|k-1}H^T + R)^{-1}
$$

$$
\hat{x}_{k|k} = \hat{x}_{k|k-1} + K_k(z_k - H\hat{x}_{k|k-1})
$$

$$
P_{k|k} = (I - K_kH)P_{k|k-1}
$$

### 四元数运算

四元数 \(q = [w, x, y, z]^T\) 表示旋转：

$$
q_1 \otimes q_2 = \begin{bmatrix} w_1w_2 - \mathbf{v}_1 \cdot \mathbf{v}_2 \\ w_1\mathbf{v}_2 + w_2\mathbf{v}_1 + \mathbf{v}_1 \times \mathbf{v}_2 \end{bmatrix}
$$

旋转向量 \(\boldsymbol{\theta}\) 到四元数：

$$
q = \begin{bmatrix} \cos(\|\boldsymbol{\theta}\|/2) \\ \frac{\boldsymbol{\theta}}{\|\boldsymbol{\theta}\|} \sin(\|\boldsymbol{\theta}\|/2) \end{bmatrix}
$$

### 马氏距离

$$
d_M = \sqrt{(\mathbf{z} - \hat{\mathbf{z}})^T S^{-1} (\mathbf{z} - \hat{\mathbf{z}})}
$$


## 参考资料

1. Thrun, S., Burgard, W., & Fox, D. (2005). *Probabilistic Robotics*. MIT Press.
2. Barfoot, T. D. (2017). *State Estimation for Robotics*. Cambridge University Press.
3. GTSAM 文档：https://gtsam.org/
4. Ceres Solver 文档：http://ceres-solver.org/
5. robot_localization 文档：https://docs.ros.org/en/humble/p/robot_localization/
6. EVO 评测工具：https://github.com/MichaelGrupp/evo
