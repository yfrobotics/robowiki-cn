# 系统架构

!!! note "引言"
    机器人系统架构是指计算单元、传感器、执行器、电源和通信总线之间的组织方式与互联关系。合理的架构设计决定了系统的实时性、可扩展性和可靠性。本文从计算层级、总线拓扑、执行器接口、电源分配和典型机器人架构等方面，系统介绍机器人硬件系统架构的设计原则与工程实践。


## 计算层级

现代机器人通常采用**分层异构计算架构**，将不同延迟要求和计算负载的任务分配到最合适的处理器上。


### 三层计算模型

| 层级 | 典型硬件 | 主要职责 | 延迟要求 |
|------|----------|----------|----------|
| 底层（实时层） | MCU（STM32、ESP32、Teensy） | 电机控制、传感器采集、安全监控 | < 1 ms |
| 中层（感知/规划层） | SBC（Raspberry Pi、Jetson Orin Nano） | SLAM、路径规划、传感器融合 | 1–100 ms |
| 上层（决策/学习层） | GPU/NPU（Jetson AGX Orin、工控 PC + RTX） | 深度学习推理、语义理解、云端通信 | 10–1000 ms |

**底层微控制器（Microcontroller Unit, MCU）** 运行裸机程序或实时操作系统（Real-Time Operating System, RTOS），负责闭环控制回路，如电机 PID（比例-积分-微分）控制、IMU（惯性测量单元）数据采集以及紧急停机逻辑。

**中层单板计算机（Single Board Computer, SBC）** 运行 Linux 操作系统，承载 ROS 2（Robot Operating System 2）节点，执行激光雷达点云处理、视觉里程计、运动规划等任务。

**上层 GPU 计算平台** 用于神经网络推理（目标检测、语义分割）、大规模地图构建或与云端服务器通信。


### 实时与非实时分区

实时分区和非实时分区的划分是架构设计的核心决策之一：

- **硬实时任务**：电机伺服控制（通常 1 kHz 以上）、安全联锁逻辑、力/力矩传感器反馈。这些任务必须运行在确定性调度环境中，如 RTOS 或专用 FPGA（现场可编程门阵列）。
- **软实时任务**：路径规划（10–50 Hz）、SLAM（Simultaneous Localization and Mapping，同步定位与地图构建）更新（5–30 Hz）。允许偶尔的延迟抖动，运行在 Linux + PREEMPT_RT 补丁上即可满足。
- **非实时任务**：日志记录、用户界面、云端数据上传。对延迟无严格要求。

```
┌─────────────────────────────────────────────────┐
│              非实时层 (Linux / ROS 2)            │
│   UI、日志、云通信、深度学习推理                   │
├─────────────────────────────────────────────────┤
│            软实时层 (PREEMPT_RT / Xenomai)       │
│   SLAM、路径规划、传感器融合                      │
├─────────────────────────────────────────────────┤
│            硬实时层 (RTOS / 裸机 / FPGA)          │
│   电机控制、安全逻辑、编码器反馈                   │
└─────────────────────────────────────────────────┘
```


## 传感器总线拓扑

传感器根据数据速率和实时性要求，通过不同的总线连接到对应的计算层。


### 低速传感器

| 传感器 | 典型总线 | 数据速率 | 连接目标 |
|--------|----------|----------|----------|
| 温度传感器 | I2C | < 100 kbps | MCU |
| 气压计 | I2C / SPI | < 1 Mbps | MCU |
| 超声波测距 | GPIO / UART | 脉冲信号 | MCU |
| IMU（6/9 轴） | SPI（推荐）/ I2C | 1–10 Mbps | MCU |


### 高速传感器

| 传感器 | 典型总线 | 数据速率 | 连接目标 |
|--------|----------|----------|----------|
| 激光雷达（LiDAR） | Ethernet / USB | 100 Mbps 以上 | SBC / GPU |
| 深度相机（RealSense、ZED） | USB 3.x | 5 Gbps | SBC / GPU |
| 工业相机 | GigE Vision / Camera Link | 1–10 Gbps | GPU |
| 毫米波雷达 | CAN / Ethernet | 1–100 Mbps | SBC |

在系统设计中，低速传感器通常直接挂载在 MCU 的外设总线上，而高速传感器则需要通过 USB 或以太网连接至具有足够带宽的 SBC 或 GPU 平台。


## 执行器接口

执行器是机器人与物理世界交互的通道，其接口设计直接影响控制精度和响应速度。


### 电机驱动接口

- **PWM（脉冲宽度调制）控制**：最简单的模拟量控制方式，MCU 输出 PWM 信号到电机驱动板（如 L298N、DRV8825），适用于直流电机和步进电机。
- **方向 + 脉冲**：步进电机常用的控制方式，MCU 输出方向信号和脉冲信号到步进驱动器。
- **CAN 总线伺服**：工业级方案。电机驱动器内置编码器反馈和电流环，通过 CAN（Controller Area Network，控制器局域网）总线接收位置/速度/力矩指令。典型协议包括 CANopen 和 EtherCAT（Ethernet for Control Automation Technology）。
- **EtherCAT 伺服**：高端工业机器人标准，支持亚微秒级同步，通常用于六轴及以上的工业机械臂。


### 常见执行器接口对比

| 接口类型 | 延迟 | 同步精度 | 布线复杂度 | 适用场景 |
|----------|------|----------|------------|----------|
| PWM + 编码器 | 低 | 无同步 | 简单 | 教育/业余项目 |
| UART 串口伺服 | 中 | 无同步 | 简单 | 舵机、小型机器人 |
| CAN 总线伺服 | 低 | 中等 | 中等 | 移动机器人、协作臂 |
| EtherCAT 伺服 | 极低 | < 1 us | 较复杂 | 工业机器人 |
| RS-485 多轴 | 中 | 低 | 中等 | Dynamixel 舵机串联 |


## 电源分配架构

电源分配需要考虑不同子系统的电压要求、功耗特性和隔离需求。

```
电池/电源适配器
    |
    +-- 主电源开关 + 急停按钮
    |
    +-- 大功率支路（电机、电磁阀）
    |     +-- 电机驱动 1 (24V / 48V)
    |     +-- 电机驱动 2
    |     +-- ...
    |
    +-- 逻辑电源支路（计算/传感）
    |     +-- DC-DC 降压 -> 5V（Raspberry Pi、传感器）
    |     +-- DC-DC 降压 -> 3.3V（MCU、低压外设）
    |     +-- DC-DC 降压 -> 12V（Jetson、散热风扇）
    |
    +-- 备用电源支路（安全系统）
          +-- 独立稳压 -> 安全 MCU、急停继电器
```

关键设计原则：

1. **电源隔离**：电机驱动等大电流负载应与逻辑电源隔离，避免电磁干扰（EMI）导致计算单元重启。
2. **上电顺序**：先给安全系统和传感器上电，最后给执行器上电；断电时反向操作。
3. **浪涌保护**：电机启停会产生反向电动势（Back-EMF），需要添加续流二极管和 TVS（瞬态电压抑制器）保护。


## 通信骨干网络

不同计算层级之间需要高效的通信骨干网络进行数据交换。


### 层间通信方式

| 通信路径 | 推荐协议 | 典型数据 | 带宽 |
|----------|----------|----------|------|
| MCU <-> MCU | CAN bus | 电机指令/反馈 | 1 Mbps |
| MCU <-> SBC | UART / USB / CAN | 传感器数据、控制指令 | 115 kbps – 12 Mbps |
| SBC <-> GPU | Ethernet / PCIe | 图像帧、点云 | 1–10 Gbps |
| SBC <-> SBC | Ethernet + DDS | ROS 2 话题 | 1 Gbps |
| 机器人 <-> 云端 | Wi-Fi / 5G / Ethernet | 日志、模型更新 | 可变 |

在 ROS 2 系统中，DDS（Data Distribution Service，数据分发服务）是默认的中间件，支持多种 QoS（Quality of Service，服务质量）策略，可以在同一以太网骨干上同时传输高吞吐量的图像数据和低延迟的控制指令。


### 以太网骨干设计

对于传感器数量较多的中大型机器人，建议采用以太网交换机作为通信骨干：

```python
# ROS 2 中配置 DDS 多播（以 CycloneDDS 为例）
# cyclonedds.xml
"""
<CycloneDDS>
  <Domain>
    <General>
      <NetworkInterfaceAddress>eth0</NetworkInterfaceAddress>
    </General>
    <Internal>
      <SocketReceiveBufferSize min="10MB"/>
    </Internal>
  </Domain>
</CycloneDDS>
"""

# 设置环境变量
# export CYCLONEDDS_URI=file:///path/to/cyclonedds.xml
# export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
```


## 典型机器人架构

不同类型的机器人因其功能需求和物理约束，呈现出截然不同的系统架构特征。


### 移动机器人（Mobile Robot）

移动机器人（如自主导航小车、送餐机器人）的架构相对简单：

- **计算**：1 个 SBC（导航 + 感知）+ 1 个 MCU（底盘电机控制）
- **传感**：2D 激光雷达、IMU、轮式编码器、超声波避障
- **通信**：SBC 与 MCU 之间使用 USB 或 UART；激光雷达通过 USB/Ethernet 连接 SBC
- **电源**：12V/24V 锂电池，降压至 5V 供 SBC，12V 供电机驱动


### 工业机械臂（Manipulator）

六轴工业机械臂对实时性和同步性要求极高：

- **计算**：工控 PC（运动规划 + 视觉）+ 运动控制器（轨迹插补）+ 各轴伺服驱动（电流/速度/位置环）
- **传感**：各关节编码器（绝对值式）、六维力/力矩传感器、腕部相机
- **通信**：EtherCAT 总线串联所有伺服驱动器，周期时间 1 ms 或更短
- **电源**：380V/220V 工业供电，伺服驱动器直接使用直流母线，独立 24V 控制电源


### 人形机器人（Humanoid）

人形机器人架构最为复杂，需要协调大量自由度和多模态传感：

- **计算**：中央 GPU 服务器（感知 + AI）+ 运动控制器（全身动力学）+ 分布式 MCU（各关节驱动）
- **传感**：双目/RGB-D 相机、激光雷达、IMU（躯干 + 四肢）、力传感器（脚底 + 手指）、关节编码器（20–40 个）
- **通信**：EtherCAT 骨干连接各关节驱动器；以太网连接视觉传感器到 GPU；CAN 总线连接手部小关节
- **电源**：48V 锂电池包（背负式），分布式 DC-DC 变换器


### 无人机（Drone / UAV）

无人飞行器（Unmanned Aerial Vehicle, UAV）对重量和功耗极度敏感：

- **计算**：飞控 MCU（姿态控制 + 导航，如 STM32H7 运行 PX4/ArduPilot）+ 任务计算机（Jetson Nano/Orin Nano，可选）
- **传感**：IMU、气压计、GPS、光流传感器、可选激光雷达/相机
- **通信**：飞控内部 SPI/I2C 连接传感器；飞控与任务计算机之间 UART/MAVLink；遥控器 Sbus/CRSF
- **电源**：3S–6S LiPo 电池，BEC（Battery Eliminator Circuit）降压给飞控和接收机


## 架构设计原则

### 模块化与可扩展性

优秀的机器人架构应遵循模块化设计原则：

1. **标准化接口**：定义清晰的电气接口和通信协议，使传感器和执行器可以即插即用。
2. **功能分离**：每个 MCU/SBC 只负责一个明确的功能域，降低耦合度。
3. **抽象层**：通过 ROS 2 的硬件抽象层（如 ros2_control）隔离上层算法与底层硬件。


### 可靠性与冗余

| 冗余策略 | 应用场景 | 实现方式 |
|----------|----------|----------|
| 双 IMU | 无人机、自动驾驶 | 主/备切换或融合 |
| 双 MCU（安全监控） | 协作机器人 | 独立安全 MCU 监控主 MCU |
| 双电源 | 医疗/军工机器人 | 热备份切换 |
| 通信冗余 | 工业机器人 | EtherCAT 环形拓扑 |


### 故障检测与处理

```c
// 安全 MCU 的看门狗检测示例（STM32 HAL）
#include "stm32h7xx_hal.h"

IWDG_HandleTypeDef hiwdg;

void safety_watchdog_init(void) {
    hiwdg.Instance = IWDG1;
    hiwdg.Init.Prescaler = IWDG_PRESCALER_64;
    hiwdg.Init.Window = IWDG_WINDOW_DISABLE;
    hiwdg.Init.Reload = 500;  // 约 1 秒超时
    HAL_IWDG_Init(&hiwdg);
}

void safety_loop(void) {
    while (1) {
        // 检查主控 MCU 心跳信号
        if (check_heartbeat_timeout()) {
            trigger_emergency_stop();
        }

        // 检查传感器数据合理性
        if (!validate_sensor_ranges()) {
            trigger_safe_shutdown();
        }

        // 喂看门狗
        HAL_IWDG_Refresh(&hiwdg);
        HAL_Delay(10);
    }
}
```


## 架构选型建议

| 项目规模 | 推荐架构 | 计算平台 | 通信方式 |
|----------|----------|----------|----------|
| 教育/原型 | 单 MCU 或 MCU + SBC | Arduino + RPi | UART / USB |
| 小型产品 | MCU + SBC | STM32 + Jetson Orin Nano | USB / CAN |
| 中型产品 | 多 MCU + SBC + GPU | STM32 集群 + Jetson AGX Orin | CAN + Ethernet |
| 工业级 | 工控 PC + 运动控制器 + 伺服 | Beckhoff / 倍福 IPC | EtherCAT |
| 研究平台 | PC + 多传感器 + ROS 2 | x86 工控机 + GPU | Ethernet + DDS |


## 参考资料

- Siegwart, R., Nourbakhsh, I. R., & Scaramuzza, D. *Introduction to Autonomous Mobile Robots*, MIT Press.
- Craig, J. J. *Introduction to Robotics: Mechanics and Control*, Pearson.
- ROS 2 Design Documentation: https://design.ros2.org/
- EtherCAT Technology Group: https://www.ethercat.org/
- PX4 Autopilot Architecture: https://docs.px4.io/main/en/concept/architecture.html
- STM32 HAL Reference Manual: https://www.st.com/
