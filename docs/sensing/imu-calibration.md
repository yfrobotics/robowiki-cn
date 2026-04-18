# IMU 标定与噪声建模

!!! note "引言"
    惯性测量单元（Inertial Measurement Unit, IMU）是移动机器人和无人系统中最重要的自体感知传感器之一。由于 IMU 的输出存在偏置（Bias）、尺度因子误差（Scale Factor）、轴间非正交（Misalignment）以及随机游走（Random Walk）等多种误差，直接使用原始数据进行积分会在短时间内产生显著漂移。因此，在将 IMU 接入 SLAM、视觉惯性里程计（Visual-Inertial Odometry, VIO）或姿态估计算法前，必须完成标定并建立可信的噪声模型。本文梳理 IMU 的误差来源、标定流程、噪声建模方法以及常用工具链。


## 1. IMU 误差来源

一个 MEMS IMU 的角速度 / 加速度原始输出可以表示为：

$$
\tilde{\omega} = (I + S_g)\,R_g\,\omega + b_g(t) + n_g
$$

$$
\tilde{a} = (I + S_a)\,R_a\,a + b_a(t) + n_a
$$

其中：

- \(\omega, a\)：真实角速度 / 比力
- \(S_g, S_a\)：尺度因子误差（对角矩阵）
- \(R_g, R_a\)：轴间非正交与安装误差旋转
- \(b_g(t), b_a(t)\)：随时间变化的偏置
- \(n_g, n_a\)：白噪声

按照误差的时变特性，IMU 误差可分为两大类：

### 1.1 确定性误差（Deterministic）

- **静态偏置（Bias）**：上电时存在的固定偏差，主要来自器件结构与温度。
- **尺度因子误差**：输出与输入之间的比例失真。
- **非正交误差**：三个敏感轴理论上应相互垂直，但制造误差导致实际存在角度偏差。
- **安装误差**：IMU 的机体坐标系与机器人本体坐标系之间的旋转不一致。
- **温度漂移**：偏置和尺度因子随温度变化而变化。

### 1.2 随机误差（Stochastic）

- **角速度 / 加速度白噪声（White Noise）**：对应功率谱密度（PSD）为常数的高斯噪声。
- **偏置随机游走（Bias Random Walk）**：偏置自身按布朗运动方式缓慢漂移。
- **量化噪声**：ADC 采样引入的离散化误差，在高端 IMU 中影响较小。


## 2. 六面静态标定（确定性误差）

六面法是入门级 IMU 标定的经典手段，可以同时标定加速度计的偏置、尺度因子和非正交。将 IMU 依次静置于六个正交面（+X/−X/+Y/−Y/+Z/−Z 对准重力方向），每个姿态采集数分钟数据取均值，得到 6 组测量值：

$$
\tilde{a}_i = T_a\,a_i + b_a, \quad i = 1,\dots,6
$$

其中 \(T_a\) 是包含尺度与非正交的 3×3 矩阵。通过最小二乘求解：

$$
\min_{T_a, b_a} \sum_i \big\| \tilde{a}_i - (T_a\,a_i + b_a) \big\|^2
$$

陀螺仪的偏置可在 IMU 完全静止时（姿态任意）通过长时间平均获得：

$$
b_g \approx \frac{1}{N}\sum_{k=1}^{N} \tilde{\omega}_k
$$

实际操作中应注意：

- 采样时间建议不少于 30 秒 / 面，以压低白噪声的平均值
- 静置平面必须水平（用水平仪校准），否则 \(a_i\) 并非纯重力
- 对温度敏感的 IMU 应在恒温环境中标定，或建立温度 – 偏置查找表


## 3. Allan 方差分析（随机误差）

Allan 方差（Allan Variance, AVAR）是评估 IMU 长时间噪声特性的标准方法。它将连续测量序列划分为长度为 \(\tau\) 的相邻段，计算相邻段均值差的方差：

$$
\sigma^2_A(\tau) = \frac{1}{2(M-1)} \sum_{k=1}^{M-1} (\bar{\Omega}_{k+1} - \bar{\Omega}_k)^2
$$

在 Allan 双对数曲线（\(\log\tau\) 对 \(\log\sigma_A\)）上，不同斜率对应不同噪声源：

| 斜率 | 噪声类型 | 对应参数 |
|------|---------|---------|
| −1/2 | 角度随机游走（ARW）/ 速度随机游走（VRW） | 白噪声 PSD |
| 0 | 偏置不稳定性（Bias Instability） | 最小值对应 \(\sigma_{BI}\) |
| +1/2 | 速率随机游走（RRW） | 偏置随机游走 PSD |

典型 MEMS IMU 的 ARW 在 0.1–0.5 °/√h，工业级光纤陀螺可低至 0.001 °/√h。采集数据建议：

- 静置时长：≥ 3 小时（更长时间能更准确提取 RRW）
- 采样频率：保留原始频率（通常 100–1000 Hz），不做下采样


## 4. 典型工具链

### 4.1 imu_utils（ROS 1 / 2）

开源工具 [imu_utils](https://github.com/gaowenliang/imu_utils) 可以读取 ROS bag 中的 IMU 话题，自动计算 Allan 方差并输出白噪声与随机游走参数。

```bash
# 1. 录制静置 3 小时以上的 IMU 数据
ros2 bag record /imu/data -o imu_static

# 2. 运行 imu_utils
roslaunch imu_utils my_imu.launch
# 输出：YAML 文件，包含 accelerometer_noise_density,
#       accelerometer_random_walk, gyroscope_noise_density,
#       gyroscope_random_walk 等字段
```

### 4.2 Kalibr（IMU–相机联合标定）

[Kalibr](https://github.com/ethz-asl/kalibr) 是视觉惯性系统中最流行的联合标定工具，能够同时求解：

- 相机内参与畸变
- 相机间外参（立体相机）
- IMU–相机外参 \(T_{ic}\)
- IMU–相机时间偏移 \(t_d\)

标定流程要点：

- 先用 imu_utils 获得 IMU 噪声参数，作为 Kalibr 的输入 `imu.yaml`
- 使用 Aprilgrid 标定板，在保证棋盘始终在画面内的前提下做足够激烈的六自由度运动
- 录制长度建议 2–5 分钟，运动覆盖三轴平动与三轴转动

```bash
kalibr_calibrate_imu_camera \
    --bag imu_cam.bag \
    --cam camchain.yaml \
    --imu imu.yaml \
    --target aprilgrid.yaml \
    --time-calibration
```

### 4.3 其他常用工具

| 工具 | 用途 | 适用场景 |
|------|------|---------|
| `allan_variance_ros` | Allan 方差可视化 | 快速评估 IMU 质量 |
| `imu_tools`（ROS 2） | 复合滤波器（Madgwick / Mahony） | 低算力姿态解算 |
| `mscnav` | 车载组合导航 | GNSS/INS 紧耦合仿真 |
| MATLAB `imuSensor` | 仿真 IMU 噪声注入 | 算法调试 |


## 5. 与姿态估计的衔接

完成标定后，需要将噪声参数写入上层估计器。以下是常见算法对噪声输入的约定：

### 5.1 互补滤波与 Madgwick

仅使用白噪声强度，不显式建模偏置随机游走。

- 加速度计权重 \(\beta \propto 1/\sigma_a\)
- 陀螺仪积分作为主要姿态来源

### 5.2 扩展卡尔曼滤波（EKF）

过程噪声 \(Q\) 矩阵的对角元素通常由：

$$
Q_{gg} = \sigma^2_{g,\text{white}}\,\Delta t, \quad
Q_{bg} = \sigma^2_{g,\text{rw}}\,\Delta t
$$

直接从 imu_utils 输出填入。注意：imu_utils 输出的是连续时间 PSD，需要乘以 \(\Delta t\) 后再平方取方差。

### 5.3 视觉惯性 SLAM（VINS-Mono / ORB-SLAM3）

这些系统的配置文件包含如下四个关键量：

```yaml
acc_n: 0.08      # 加速度计白噪声 (m/s^2/√Hz)
gyr_n: 0.004     # 陀螺仪白噪声 (rad/s/√Hz)
acc_w: 0.00004   # 加速度计随机游走 (m/s^3/√Hz)
gyr_w: 0.000002  # 陀螺仪随机游走 (rad/s^2/√Hz)
```

对大多数 MEMS IMU，应将标定值乘以 3–10 倍后再填入——真实硬件中存在温度、振动等未建模噪声，低估噪声会导致后端优化过度信任 IMU，出现姿态跳变。


## 6. 常见陷阱

- **没有对齐时间戳**：IMU 与相机 / 激光雷达的硬件触发或软件时间戳偏差超过 1 ms 会严重影响 VIO，使用 Kalibr 的 `--time-calibration` 选项估计 \(t_d\)。
- **在运动中标定**：六面法与 Allan 方差都要求严格静止，运动中的数据会被误认为偏置或随机游走。
- **忽视温度**：上电 1–5 分钟内 IMU 温度漂移最剧烈，应先预热再开始标定或记录。
- **直接使用厂商规格**：厂商数据手册给出的噪声值通常是典型值，单颗器件差异可达 2–3 倍，建议个体标定。
- **将输出直接积分**：对未经偏置补偿的陀螺仪积分姿态，短短 10 秒内就会偏差数度。


## 参考资料

1. IEEE Std 952-1997, *IEEE Standard Specification Format Guide and Test Procedure for Single-Axis Interferometric Fiber Optic Gyros*
2. Tedaldi D, Pretto A, Menegatti E. "A robust and easy to implement method for IMU calibration without external equipments". ICRA 2014.
3. Furgale P, Rehder J, Siegwart R. "Unified temporal and spatial calibration for multi-sensor systems". IROS 2013.
4. [imu_utils GitHub 仓库](https://github.com/gaowenliang/imu_utils)
5. [Kalibr GitHub 仓库](https://github.com/ethz-asl/kalibr)
6. [VINS-Mono 论文与代码](https://github.com/HKUST-Aerial-Robotics/VINS-Mono)
