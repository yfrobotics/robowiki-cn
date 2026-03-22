# 通信总线

!!! note "引言"
    通信总线是连接机器人各子系统（传感器、执行器、计算单元）的数据传输通道。选择合适的总线协议直接影响系统的实时性、可靠性和可扩展性。本文详细介绍机器人中常用的通信总线协议，包括 I2C、SPI、UART、CAN、USB 和以太网/EtherCAT，并提供协议对比和选型指南。


## I2C 总线

I2C（Inter-Integrated Circuit，集成电路互连）是 Philips（现 NXP）公司开发的两线制串行总线，广泛用于连接低速外设。


### 协议特点

- **线路**：SDA（数据线）+ SCL（时钟线），仅需两根线
- **拓扑**：多主多从（实际多用单主多从）
- **寻址**：7 位地址（最多 128 个设备）或 10 位地址
- **速率**：标准模式 100 kbps、快速模式 400 kbps、高速模式 3.4 Mbps
- **传输距离**：通常 < 1 m（受总线电容限制）


### 上拉电阻

I2C 总线采用开漏（Open-Drain）输出，需要外部上拉电阻将空闲电平拉高至 VCC。上拉电阻值的选择影响通信可靠性：

| 总线速率 | 推荐上拉电阻 | 说明 |
|----------|-------------|------|
| 100 kHz | 4.7 kohm | 标准值，兼容性好 |
| 400 kHz | 2.2 kohm | 更强的驱动能力 |
| 1 MHz+ | 1 kohm | 需注意功耗增加 |

上拉电阻过大会导致上升沿变慢（信号失真），过小会增加功耗且驱动器可能无法将线拉低。


### 代码示例（Python + SMBus）

```python
# 通过 I2C 读取 MPU6050 IMU 数据
# 适用于 Raspberry Pi

import smbus2
import time

MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

bus = smbus2.SMBus(1)  # I2C 总线 1

def mpu6050_init():
    """初始化 MPU6050，唤醒传感器"""
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0x00)
    time.sleep(0.1)

def read_raw_data(addr):
    """读取 16 位有符号整数"""
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32767:
        value -= 65536
    return value

def read_accel():
    """读取三轴加速度（单位：g）"""
    ax = read_raw_data(ACCEL_XOUT_H) / 16384.0
    ay = read_raw_data(ACCEL_XOUT_H + 2) / 16384.0
    az = read_raw_data(ACCEL_XOUT_H + 4) / 16384.0
    return ax, ay, az

if __name__ == "__main__":
    mpu6050_init()
    while True:
        ax, ay, az = read_accel()
        print(f"加速度: X={ax:.3f}g  Y={ay:.3f}g  Z={az:.3f}g")
        time.sleep(0.1)
```


### I2C 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| 设备无响应 | 地址冲突或接线错误 | 用 `i2cdetect` 扫描确认 |
| 数据错误 | 上拉电阻不合适 | 调整电阻值，缩短线缆 |
| 总线挂死 | 从设备拉住 SDA | SCL 产生 9 个脉冲恢复 |
| 速率不达标 | 总线电容过大 | 减少设备数或使用总线缓冲器 |


## SPI 总线

SPI（Serial Peripheral Interface，串行外设接口）是一种高速全双工同步串行总线，由 Motorola 开发。


### 协议特点

- **线路**：MOSI（主出从入）、MISO（主入从出）、SCK（时钟）、CS（片选）
- **拓扑**：单主多从（每个从设备需要独立 CS 线）
- **速率**：通常 1–50 MHz，某些设备支持 100 MHz 以上
- **传输距离**：< 1 m（建议 < 30 cm）
- **全双工**：发送和接收同时进行


### SPI 模式

SPI 有四种工作模式，由时钟极性（CPOL）和时钟相位（CPHA）决定：

| 模式 | CPOL | CPHA | 时钟空闲电平 | 采样边沿 |
|------|------|------|-------------|----------|
| Mode 0 | 0 | 0 | 低电平 | 上升沿 |
| Mode 1 | 0 | 1 | 低电平 | 下降沿 |
| Mode 2 | 1 | 0 | 高电平 | 下降沿 |
| Mode 3 | 1 | 1 | 高电平 | 上升沿 |

大多数传感器使用 Mode 0 或 Mode 3，具体需查阅器件数据手册。


### SPI vs I2C

| 特性 | SPI | I2C |
|------|-----|-----|
| 速度 | 更快（10–100 MHz） | 较慢（100 kHz–3.4 MHz） |
| 线数 | 4 + N（N 为从设备数） | 2 |
| 全双工 | 是 | 否 |
| 多主 | 不常用 | 支持 |
| 适用场景 | 高速传感器、SD 卡、显示屏 | 低速传感器、EEPROM |


## UART / RS-232 / RS-485

UART（Universal Asynchronous Receiver-Transmitter，通用异步收发器）是最经典的串行通信方式。


### UART 基础

- **线路**：TX（发送）、RX（接收），可选 RTS/CTS 硬件流控
- **异步传输**：无时钟线，收发双方必须约定相同的波特率
- **常用波特率**：9600、115200、921600 bps
- **数据格式**：起始位（1 位）+ 数据位（7/8 位）+ 校验位（可选）+ 停止位（1/2 位）


### 物理层标准

| 标准 | 电平 | 拓扑 | 最大距离 | 最大速率 | 典型应用 |
|------|------|------|----------|----------|----------|
| TTL UART | 0/3.3V 或 0/5V | 点对点 | < 1 m | 几 Mbps | MCU 互连 |
| RS-232 | ±3–15V | 点对点 | 15 m | 115.2 kbps | 工控设备、GPS 模块 |
| RS-485 | 差分 ±1.5V | 多点总线 | 1200 m | 10 Mbps | 工业传感器、Dynamixel 舵机 |

RS-485 采用差分信号传输，抗干扰能力强，支持多点总线拓扑（最多 32 个节点，带中继可扩展至 256 个），是工业环境中的首选低速总线。


### RS-485 半双工通信示例

```python
# RS-485 半双工通信示例（Linux + USB-to-RS485 适配器）
import serial
import time

ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.1
)

def send_command(device_id, command_bytes):
    """发送指令到指定设备"""
    packet = bytes([0xFF, 0xFF, device_id, len(command_bytes) + 1])
    checksum = (~(device_id + len(command_bytes) + 1
                  + sum(command_bytes))) & 0xFF
    packet += bytes(command_bytes) + bytes([checksum])
    ser.write(packet)

def read_response(expected_length):
    """读取从设备响应"""
    response = ser.read(expected_length)
    if len(response) < expected_length:
        print("[超时] 未收到完整响应")
    return response

# 示例：读取 Dynamixel 舵机位置
send_command(0x01, [0x02, 0x24, 0x02])  # READ, 地址 0x24, 长度 2
response = read_response(8)
```


## CAN 总线

CAN（Controller Area Network，控制器局域网）最初由 Bosch 公司为汽车工业开发，现已广泛应用于机器人、工业自动化和医疗设备。


### CAN 协议要点

- **拓扑**：线性总线，两端 120 ohm 终端电阻
- **差分信号**：CAN_H 和 CAN_L 两根线，抗干扰能力强
- **速率**：经典 CAN 最高 1 Mbps，CAN FD（Flexible Data-rate）最高 8 Mbps
- **仲裁机制**：基于报文标识符（ID）的非破坏性逐位仲裁，ID 越小优先级越高
- **错误检测**：CRC 校验、位填充、帧格式检查、应答检查、错误界定


### CAN 帧格式

经典 CAN 2.0B 扩展帧结构：

```
+------+---------+----+------+-------+------+-----+------+-----+
| SOF  |  29-bit | RTR| 控制  | 数据   | CRC  | ACK | EOF  | IFS |
| 1bit |  ID     |1bit| 6bit | 0-8B  | 16bit| 2bit| 7bit | 3bit|
+------+---------+----+------+-------+------+-----+------+-----+
```

- **SOF**（Start of Frame）：帧起始位
- **ID**：标准帧 11 位，扩展帧 29 位
- **RTR**（Remote Transmission Request）：远程帧标志
- **DLC**（Data Length Code）：数据长度码（0–8 字节）
- **CRC**：循环冗余校验


### CANopen 协议

CANopen 是基于 CAN 的高层应用协议，广泛用于工业机器人和伺服驱动：

| 对象 | COB-ID 范围 | 功能 |
|------|-------------|------|
| NMT | 0x000 | 网络管理（启动/停止/复位） |
| SYNC | 0x080 | 同步信号 |
| EMCY | 0x080 + NodeID | 紧急报文 |
| TPDO1–4 | 0x180–0x480 + NodeID | 过程数据输出（传感器到主站） |
| RPDO1–4 | 0x200–0x500 + NodeID | 过程数据输入（主站到执行器） |
| SDO | 0x580/0x600 + NodeID | 服务数据（参数配置） |
| Heartbeat | 0x700 + NodeID | 心跳检测 |


### CAN 总线代码示例（Linux SocketCAN）

```python
# Linux SocketCAN + python-can 库
# pip install python-can

import can
import struct

def setup_can_bus(interface='can0', bitrate=500000):
    """初始化 CAN 总线"""
    import os
    os.system(f'sudo ip link set {interface} type can bitrate {bitrate}')
    os.system(f'sudo ip link set {interface} up')

    bus = can.interface.Bus(
        channel=interface,
        bustype='socketcan'
    )
    return bus

def send_motor_command(bus, motor_id, position, velocity):
    """发送电机位置/速度指令（CANopen RPDO 格式）"""
    data = struct.pack('<ih', position, velocity)  # 小端序
    msg = can.Message(
        arbitration_id=0x200 + motor_id,
        data=data,
        is_extended_id=False
    )
    bus.send(msg)
    print(f"发送到电机 {motor_id}: 位置={position}, 速度={velocity}")

def receive_feedback(bus, timeout=1.0):
    """接收电机反馈数据"""
    msg = bus.recv(timeout=timeout)
    if msg is not None:
        motor_id = msg.arbitration_id - 0x180
        if len(msg.data) >= 6:
            position, velocity = struct.unpack('<ih', msg.data[:6])
            print(f"电机 {motor_id} 反馈: 位置={position}, 速度={velocity}")
            return motor_id, position, velocity
    return None

if __name__ == "__main__":
    bus = setup_can_bus('can0', 1000000)
    try:
        send_motor_command(bus, 1, 10000, 500)
        receive_feedback(bus)
    finally:
        bus.shutdown()
```


## USB

USB（Universal Serial Bus，通用串行总线）是机器人系统中连接相机、激光雷达、外部存储等设备的主要接口。


### USB 版本对比

| 版本 | 速率 | 接口类型 | 供电能力 | 典型应用 |
|------|------|----------|----------|----------|
| USB 2.0 | 480 Mbps | Type-A/B/Micro | 5V / 500 mA | MCU 编程、串口适配器 |
| USB 3.0 | 5 Gbps | Type-A (蓝色) | 5V / 900 mA | 深度相机、激光雷达 |
| USB 3.1 Gen 2 | 10 Gbps | Type-C | 5V / 3A | 高分辨率相机 |
| USB 3.2 Gen 2x2 | 20 Gbps | Type-C | 5–20V / 5A (PD) | 多相机系统 |


### USB 在机器人中的注意事项

- **带宽共享**：同一 USB 控制器下的多个设备共享带宽。多个 USB 3.0 相机应分布在不同的 USB 控制器上。
- **线缆长度**：USB 2.0 最长 5 m，USB 3.0 最长 3 m。超长需使用有源延长线或 USB over Ethernet。
- **电磁干扰**：USB 3.0 信号可能干扰 2.4 GHz Wi-Fi 和 GPS 接收器，注意线缆屏蔽和布局。
- **热插拔**：USB 支持热插拔，但 Linux 下设备节点名（如 `/dev/ttyUSB0`）可能变化，建议使用 udev 规则绑定固定名称。

```bash
# 创建 udev 规则，固定 USB 串口设备名称
# /etc/udev/rules.d/99-robot-usb.rules
# 根据设备 vendor ID 和 product ID 绑定
# SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="robot_mcu"
# SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="robot_lidar"

# 查看设备信息
udevadm info --name=/dev/ttyUSB0 --attribute-walk | grep -E "idVendor|idProduct|serial"

# 重新加载规则
sudo udevadm control --reload-rules && sudo udevadm trigger
```


## Ethernet 与 EtherCAT

以太网是大型机器人系统和工业机器人的通信骨干。


### 标准以太网

- **速率**：100 Mbps（百兆）、1 Gbps（千兆）、10 Gbps
- **协议栈**：TCP/IP（可靠传输）或 UDP/IP（低延迟）
- **拓扑**：星型（通过交换机）
- **延迟**：毫秒级（标准 TCP/IP），可通过 TSN（Time-Sensitive Networking，时间敏感网络）降至微秒级

在 ROS 2 系统中，以太网是各节点间通信的首选物理层，DDS 中间件通过 UDP 多播实现话题发布/订阅。


### EtherCAT

EtherCAT（Ethernet for Control Automation Technology）是由 Beckhoff 公司开发的工业实时以太网协议，专为高精度运动控制设计：

- **工作原理**：主站发出以太网帧，帧在各从站之间逐站传递（飞行读写），每个从站在帧经过时直接读写自己的数据区
- **拓扑**：线型（daisy-chain）、支持星型和树形扩展、环形冗余
- **周期时间**：100 us 以下可达，抖动 < 1 us
- **同步精度**：分布式时钟（Distributed Clocks, DC）实现亚微秒级同步

| 特性 | 标准以太网 + TCP | EtherCAT |
|------|-----------------|----------|
| 延迟 | 1–10 ms | < 100 us |
| 抖动 | 不确定 | < 1 us |
| 实时性 | 软实时 | 硬实时 |
| 带宽利用率 | 较低 | > 90% |
| 主要用途 | 数据传输、ROS 通信 | 伺服控制、传感器同步采集 |


## 总线综合对比

| 总线 | 速率 | 距离 | 拓扑 | 线数 | 实时性 | 典型应用 |
|------|------|------|------|------|--------|----------|
| I2C | 100k–3.4M bps | < 1 m | 多点 | 2 | 无 | IMU、温度、EEPROM |
| SPI | 1–100 MHz | < 0.3 m | 点对点 | 4+N | 无 | 高速传感器、ADC |
| UART | 9.6k–1M bps | < 15 m | 点对点 | 2–4 | 无 | GPS、蓝牙模块 |
| RS-485 | 100k–10M bps | < 1200 m | 多点 | 2 | 无 | 工业传感器、舵机串联 |
| CAN | 1M bps (FD 8M) | < 500 m | 多点 | 2 | 中 | 电机控制、车载系统 |
| USB 3.0 | 5 Gbps | < 3 m | 星型 | 多 | 无 | 相机、激光雷达 |
| Ethernet | 100M–10G bps | < 100 m | 星型 | 4/8 | 软 | ROS 2 通信 |
| EtherCAT | 100 Mbps | < 100 m | 线型 | 4/8 | 硬 | 工业伺服控制 |


## 总线选型指南

### 按设备类型选型

| 设备类型 | 推荐总线 | 备选方案 | 说明 |
|----------|----------|----------|------|
| IMU（6/9 轴） | SPI | I2C | SPI 延迟低、速率高 |
| 温度/湿度传感器 | I2C | 单总线 | 低速设备，I2C 接线少 |
| GPS 模块 | UART | I2C | 串口通信最常见 |
| 激光雷达 | Ethernet / USB | UART（低端） | 高数据量需高带宽 |
| 深度相机 | USB 3.x | Ethernet (GigE) | USB 3.0 带宽足够 |
| 直流电机驱动 | PWM + 编码器 | CAN | 简单场景用 PWM |
| 伺服电机（工业） | EtherCAT | CAN (CANopen) | EtherCAT 同步性最好 |
| 舵机串联（多个） | RS-485 | UART（单个） | Dynamixel 等使用 RS-485 |
| LED 灯带 | SPI | PWM | WS2812 用单线协议 |
| 显示屏 | SPI / I2C | HDMI | 小尺寸 OLED 用 I2C/SPI |


### 按系统规模选型

| 系统规模 | MCU <-> 传感器 | MCU <-> MCU | MCU <-> SBC | SBC <-> 云端 |
|----------|---------------|-------------|-------------|-------------|
| 小型（教育） | I2C / SPI | UART | USB | Wi-Fi |
| 中型（产品） | I2C / SPI / CAN | CAN | USB / Ethernet | Wi-Fi / 4G |
| 大型（工业） | EtherCAT / CAN | CAN / EtherCAT | Ethernet | 有线网络 |


## 参考资料

- NXP Semiconductors. *I2C-bus Specification and User Manual*, UM10204.
- Bosch. *CAN Specification Version 2.0*, 1991.
- Beckhoff. *EtherCAT Technology Introduction*: https://www.ethercat.org/
- CiA (CAN in Automation). *CANopen Application Layer and Communication Profile*, CiA 301.
- USB Implementers Forum: https://www.usb.org/
- python-can Documentation: https://python-can.readthedocs.io/
- Dynamixel Protocol 2.0: https://emanual.robotis.com/docs/en/dxl/protocol2/
