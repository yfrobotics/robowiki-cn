# Atlas

!!! note "引言"
    Atlas 是由美国 Boston Dynamics 公司研发的人形机器人，是全球最具标志性的双足机器人之一。Atlas 最初于 2013 年作为液压驱动的研究平台亮相，在动态运动控制领域不断突破人类对机器人运动能力的认知。2024 年，Boston Dynamics 推出全新的全电动 Atlas，标志着该平台从研究原型向商业应用的重大转型。


## 发展历程

Atlas 的发展可以追溯到 Boston Dynamics 早期的双足行走研究。

- **2013 年**：第一代 Atlas 亮相，由美国国防高级研究计划局（Defense Advanced Research Projects Agency, DARPA）资助，用于 DARPA 机器人挑战赛（DARPA Robotics Challenge, DRC）。该版本采用液压驱动，身高约 1.8 m，体重约 150 kg。
- **2016 年**：发布新一代 Atlas（Next Generation），体型更小（身高 1.5 m，体重 80 kg），具备更强的平衡和恢复能力。其在雪地行走、被推倒后自主起身等视频引发全球关注。
- **2017-2023 年**：液压版 Atlas 不断展示后空翻、跑酷、舞蹈等高难度动作，成为机器人运动能力的标杆。
- **2024 年 4 月**：Boston Dynamics 宣布液压版 Atlas 退役，并发布全新的全电动 Atlas。电动版采用全新设计，关节具备超过 360 度的旋转范围，运动更加灵活。


## 技术规格

### 电动版 Atlas（2024）

| 参数 | 规格 |
|------|------|
| 身高 | 约 1.5 m |
| 体重 | 约 89 kg |
| 驱动方式 | 全电动（Electric Actuators） |
| 自由度（DOF） | 28+ |
| 关节特性 | 多轴旋转关节，超 360° 旋转范围 |
| 感知系统 | 多传感器融合（摄像头、LiDAR、力/力矩传感器） |
| 手部 | 多指灵巧手，可抓取不规则物体 |

### 液压版 Atlas（2016-2024）

| 参数 | 规格 |
|------|------|
| 身高 | 1.5 m |
| 体重 | 约 80 kg |
| 驱动方式 | 液压驱动（Hydraulic Actuators） |
| 自由度（DOF） | 28 |
| 行走速度 | 约 1.5 m/s |
| 感知系统 | LiDAR、立体视觉、IMU |
| 电源 | 外接电源 / 电池组 |


## 关键技术

### 动态运动控制（Dynamic Locomotion）

Atlas 的运动控制系统是其最核心的技术。Boston Dynamics 采用了基于模型预测控制（Model Predictive Control, MPC）和全身运动优化（Whole-Body Motion Optimization）的方法，使 Atlas 能够在复杂地形上保持平衡，并执行跳跃、后空翻等高动态动作。

### 感知与规划（Perception & Planning）

Atlas 配备了多种传感器用于环境感知，包括激光雷达（LiDAR）、深度摄像头和惯性测量单元（Inertial Measurement Unit, IMU）。通过实时三维地图构建和路径规划算法，Atlas 能够在非结构化环境中自主导航和避障。

### 全电动驱动（Electric Actuation）

2024 年的电动版 Atlas 放弃了传统液压系统，转向全电动关节驱动。电动驱动具有更高的能效、更低的维护成本和更精细的力控制能力，更适合与人类协作的应用场景。


## 应用方向

Atlas 目前主要面向以下场景：

- **研究与演示**：作为前沿运动控制技术的验证平台
- **工业应用**：电动版 Atlas 定位于与现代 Hyundai 汽车制造环境配合使用（Boston Dynamics 现为 Hyundai 旗下子公司）
- **危险环境作业**：核电站检修、灾难救援等人类难以到达的场景


## Boston Dynamics 与 Atlas

Boston Dynamics 成立于 1992 年，由马克·雷伯特（Marc Raibert）创立，脱胎于麻省理工学院（Massachusetts Institute of Technology, MIT）的腿足实验室（Leg Laboratory）。公司先后经历了 Google（2013 年收购）、软银（SoftBank，2017 年收购）和现代汽车集团（Hyundai Motor Group，2020 年收购）的所有权变更。Atlas 项目贯穿了公司的发展历程，是 Boston Dynamics 技术实力的集中体现。


## 参考资料

1. [Atlas](https://bostondynamics.com/atlas/), Boston Dynamics 官网
2. [Atlas (robot)](https://en.wikipedia.org/wiki/Atlas_(robot)), Wikipedia
3. [Farewell to HD Atlas](https://bostondynamics.com/blog/electric-new-satisfying-atlas/), Boston Dynamics Blog, 2024
