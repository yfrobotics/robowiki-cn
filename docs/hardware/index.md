# 机器人硬件平台

!!! note "引言"
    硬件平台是机器人系统的物理基础，负责感知、计算和执行等核心功能。根据计算能力、实时性、功耗和成本等需求的不同，机器人开发者需要在微控制器（Microcontroller, MCU）、单板计算机（Single-Board Computer, SBC）和工控机（Industrial PC, IPC）之间做出合理选择。许多现代机器人系统采用异构架构，将不同类型的硬件平台组合使用以发挥各自的优势。

机器人开发中常用的硬件平台有：

- Arduino (AVR)
- 树莓派 (ARM Cortex-A)
- Nvidia Jetson系列 (ARM Cortex-A + GPU)
- 基于STM32/AVR/PIC32等嵌入式控制器
- 基于工控机 (Intel Atom / Intel x86 / Intel x64)


## 硬件平台分类

### 微控制器 (Microcontroller, MCU)

微控制器是将处理器、内存、I/O接口集成在单个芯片上的计算单元，适合执行实时性要求高但计算量不大的任务。在机器人系统中，MCU通常负责底层控制，如电机驱动、传感器数据采集和通信协议处理。

常见的MCU平台包括：

- **STM32系列**（ARM Cortex-M）：ST公司生产，型号丰富，从低功耗的Cortex-M0到高性能的Cortex-M7均有覆盖。广泛用于电机控制、传感器融合和通信网关。
- **Arduino**（AVR / ARM）：开源硬件平台，以易用性著称，适合原型开发和教学。
- **ESP32**（Xtensa / RISC-V）：乐鑫公司生产，内置Wi-Fi和蓝牙，适合物联网机器人应用。
- **PIC32**（MIPS）：Microchip公司生产，常用于工业控制场景。

### 单板计算机 (Single-Board Computer, SBC)

单板计算机具有完整的计算机功能，可以运行Linux等通用操作系统，适合需要复杂计算、图形界面或网络功能的场景。

常见的SBC平台包括：

- **Raspberry Pi**（ARM Cortex-A）：全球最流行的SBC，拥有丰富的社区资源和配件生态。
- **Nvidia Jetson系列**（ARM Cortex-A + GPU）：内置GPU加速能力，专为AI和视觉计算设计。
- **BeagleBone**（ARM Cortex-A）：拥有丰富的GPIO和PRU协处理器，适合实时I/O应用。
- **Orange Pi / Banana Pi**：国产SBC，性价比较高。

### 工控机 (Industrial PC, IPC)

工控机是面向工业环境设计的计算机，具有高可靠性、宽温度范围和丰富的工业接口。在大型机器人系统中，工控机通常用作中央控制计算机。

常见的工控机方案包括：

- **Intel NUC系列**：小型化x86计算平台，性能强劲。
- **研华（Advantech）工控机**：覆盖无风扇嵌入式系统到机架式服务器等多种形态。
- **倍福（Beckhoff）工业PC**：集成EtherCAT主站功能，适合运动控制应用。


## 选型指南

选择硬件平台时需要综合考虑以下因素：

| 考量因素 | MCU | SBC | IPC |
|----------|-----|-----|-----|
| 计算能力 | 低-中 | 中-高 | 高 |
| 实时性 | 优秀（硬实时） | 一般（需RTOS补丁） | 需要实时扩展 |
| 功耗 | 极低（mW-W级） | 低（W级） | 中-高（数十W） |
| 成本 | 极低 | 低-中 | 中-高 |
| I/O灵活性 | 丰富的GPIO/ADC/PWM | GPIO有限 | 依赖扩展板 |
| 操作系统 | 裸机/RTOS | Linux/Android | Linux/Windows |
| 开发难度 | 中-高 | 低-中 | 低 |


## 通信接口

机器人系统中各硬件模块之间需要通过通信接口进行数据交换。常见的通信接口包括：

- **UART（通用异步收发器）**：最简单的串行通信接口，常用于GPS模块、蓝牙模块和调试终端的连接。
- **SPI（串行外设接口）**：高速同步通信协议，支持全双工通信，常用于传感器（如IMU、ADC）和显示屏的连接。
- **I2C（集成电路总线）**：双线制同步通信协议，支持多设备共享总线，常用于低速传感器和EEPROM的连接。
- **CAN（控制器局域网）**：面向汽车和工业控制的高可靠性总线协议，支持多节点通信和错误检测，常用于多关节机器人的分布式控制。
- **Ethernet（以太网）**：高带宽网络通信，常用于机器人与上位机之间的数据传输，以及基于EtherCAT的工业实时通信。
- **USB（通用串行总线）**：通用的外设连接接口，常用于摄像头、激光雷达和外部存储设备。


## 执行器与驱动

执行器（Actuator）是机器人将控制信号转化为物理运动的关键部件。常见的执行器类型和对应的驱动方案包括：

- **直流电机（DC Motor）**：通过H桥驱动电路控制转速和方向，常用PWM信号调节占空比。驱动芯片如L298N、TB6612等。
- **步进电机（Stepper Motor）**：通过脉冲信号精确控制转角，常用于3D打印机和精密定位系统。驱动芯片如A4988、DRV8825等。
- **伺服电机（Servo Motor）**：内置位置反馈的闭环控制电机，常用于工业机器人关节。驱动器通常支持CAN或EtherCAT通信。
- **舵机（RC Servo）**：通过PWM脉冲宽度控制角度的小型执行器，常用于舵机云台和小型机器人关节。
- **直线执行器（Linear Actuator）**：提供直线运动的电动推杆，常用于升降和推拉机构。


## 参考资料

1. [Arduino官方网站](https://www.arduino.cc/)
2. [Raspberry Pi官方网站](https://www.raspberrypi.org/)
3. [Nvidia Jetson开发者中心](https://developer.nvidia.com/embedded-computing)
4. [STM32官方网站](https://www.st.com/en/microcontrollers-microprocessors/stm32-32-bit-arm-cortex-mcus.html)
