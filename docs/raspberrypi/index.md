# Raspberry Pi

!!! note "引言"
    树莓派（Raspberry Pi）是由英国树莓派基金会（Raspberry Pi Foundation）于2012年推出的低成本单板计算机（Single-Board Computer, SBC）。凭借其完整的Linux运行环境、丰富的GPIO接口和庞大的社区生态，树莓派已成为机器人开发、物联网原型设计和嵌入式教学中使用最广泛的SBC平台之一。

树莓派是英国树莓派基金设计和推广的嵌入式Linux开发板。

## 1. 树莓派型号

树莓派有以下主要型号：

- Raspberry Pi A/A+/B/B+
- Raspberry Pi 2B
- Raspberry Pi 3B/3A+/3B+
- Raspberry Pi 4B 1GB/2GB/4GB/8GB

小型化型号：

- Raspberry Pi Zero W/WH

微型主机：

- Raspberry Pi 400

模块化计算单元：

- Raspberry Pi Compute Module 3 (CM3)
- Raspberry Pi Compute Module 4 (CM4)

嵌入式型号：

- Raspberry Pi Pico: 基于RP2040 (32-bit ARM Cortex-M0+)


## 2. 芯片方案

- Raspberry Pi 4 chip: [BCM2711](https://datasheets.raspberrypi.org/bcm2711/bcm2711-peripherals.pdf)
- Raspberry Pi 3+ chip: [BCM2837B0](https://www.raspberrypi.org/documentation/hardware/raspberrypi/bcm2837b0/README.md)
- Raspberry Pi 3 chip: [BCM2837](https://www.raspberrypi.org/documentation/hardware/raspberrypi/bcm2837/README.md)
- Raspberry Pi 2 chip: [BCM2836](https://www.raspberrypi.org/documentation/hardware/raspberrypi/bcm2836/README.md)
- Raspberry Pi 1 chip: [BCM2835](https://www.raspberrypi.org/documentation/hardware/raspberrypi/bcm2835/README.md)


## 3. 操作系统

### Raspberry Pi OS（原Raspbian）

Raspberry Pi OS是官方推荐的操作系统，基于Debian Linux发行版。提供三个版本：

- **Raspberry Pi OS Lite**：无图形界面的精简版，适合无头（Headless）服务器和嵌入式应用。
- **Raspberry Pi OS with Desktop**：包含LXDE桌面环境的标准版。
- **Raspberry Pi OS with Desktop and Recommended Software**：包含完整桌面和预装常用软件的完整版。

### 其他支持的操作系统

树莓派还支持多种第三方操作系统：

- **Ubuntu**：Canonical官方提供了针对树莓派的Ubuntu Server和Ubuntu Desktop镜像。
- **Ubuntu MATE**：轻量级桌面发行版，适合日常使用。
- **Kali Linux**：安全测试专用发行版。
- **OSMC / LibreELEC**：媒体中心操作系统。
- **Windows IoT Core**：微软的物联网操作系统（仅支持Raspberry Pi 2/3）。


## 4. GPIO编程

树莓派提供40针GPIO接口（Raspberry Pi 2及以后的型号），支持数字输入/输出、PWM、I2C、SPI和UART等功能。

### Python GPIO编程

Python是树莓派上最常用的GPIO编程语言，主要使用`RPi.GPIO`或`gpiozero`库：

```python
# 使用gpiozero库控制LED
from gpiozero import LED
from time import sleep

led = LED(17)  # GPIO 17

while True:
    led.on()
    sleep(1)
    led.off()
    sleep(1)
```

```python
# 使用RPi.GPIO库读取按钮状态
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

if GPIO.input(18) == GPIO.LOW:
    print("Button pressed!")

GPIO.cleanup()
```

### C语言GPIO编程

对于需要更高性能的场景，可以使用`wiringPi`或直接操作`/dev/mem`进行GPIO编程：

```c
#include <wiringPi.h>

int main(void)
{
    wiringPiSetupGpio();  // 使用BCM编号
    pinMode(17, OUTPUT);

    while (1) {
        digitalWrite(17, HIGH);
        delay(1000);
        digitalWrite(17, LOW);
        delay(1000);
    }

    return 0;
}
```


## 5. 摄像头模块

树莓派官方提供了专用的摄像头模块，通过CSI（Camera Serial Interface）接口连接：

- **Camera Module V2**：基于Sony IMX219传感器，800万像素，支持1080p30视频录制。
- **Camera Module V3**：基于Sony IMX708传感器，1200万像素，支持HDR和自动对焦。
- **HQ Camera**：基于Sony IMX477传感器，1230万像素，支持可更换CS/C-mount镜头，适合机器视觉应用。

在机器人应用中，摄像头模块常与OpenCV配合使用进行图像处理和目标检测：

```python
import cv2

# 打开摄像头
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 显示图像
    cv2.imshow('Robot Camera', gray)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```


## 6. 机器人应用

树莓派在机器人领域的典型应用包括：

- **ROS运行平台**：树莓派可以运行ROS（Robot Operating System）和ROS 2，作为机器人的主控计算机处理传感器数据、执行导航算法和协调各子系统。
- **视觉处理**：配合摄像头和OpenCV进行目标检测、颜色追踪、二维码识别等视觉任务。
- **SLAM建图**：通过连接激光雷达（如RPLidar）和运行Cartographer或GMapping等SLAM算法，实现室内地图构建。
- **语音交互**：利用麦克风阵列和语音识别库（如CMU Sphinx、Vosk）实现语音命令控制。
- **远程监控**：通过Wi-Fi提供视频流和Web控制界面，实现机器人远程操控。
- **教育平台**：如树莓派官方的Build HAT配合LEGO Technic电机，用于STEM教育。


## 7. 网络连接

树莓派提供了多种网络连接方式：

- **有线以太网**：Raspberry Pi 3B+和4B提供千兆以太网端口（4B为真千兆，3B+受限于USB 2.0总线），适合需要稳定网络连接的应用。
- **Wi-Fi**：Raspberry Pi 3及以后的型号内置802.11ac（双频）Wi-Fi模块。
- **蓝牙**：内置蓝牙4.2/5.0（取决于型号），可连接蓝牙手柄、键盘等外设。

对于机器人联网应用，树莓派还支持：

- 通过USB 4G/LTE模块实现户外移动网络连接
- 作为Wi-Fi热点（Access Point）为其他设备提供网络
- MQTT协议进行轻量级物联网通信


## 8. 与其他SBC的对比

| 特性 | Raspberry Pi 4B | BeagleBone Black | Orange Pi 5 | Nvidia Jetson Nano |
|------|----------------|-------------------|-------------|-------------------|
| 处理器 | BCM2711 (Cortex-A72) | AM3358 (Cortex-A8) | RK3588S (Cortex-A76/A55) | Cortex-A57 |
| 主频 | 1.5 GHz 四核 | 1 GHz 单核 | 2.4 GHz 八核 | 1.43 GHz 四核 |
| RAM | 1/2/4/8 GB | 512 MB | 4/8/16 GB | 4 GB |
| GPU | VideoCore VI | PowerVR SGX530 | Mali-G610 | 128核 Maxwell |
| 价格 | 约$35-$75 | 约$55 | 约$60-$150 | 约$99 |
| 社区支持 | 极好 | 良好 | 一般 | 良好 |
| 特色 | 生态最丰富 | PRU实时协处理器 | 高性能 | AI加速 |

树莓派的最大优势是其庞大的社区和成熟的软件生态。大多数开源机器人项目都优先提供树莓派的支持，这使得开发者能够快速找到教程、驱动程序和解决方案。


## 参考资料
1. [raspberrypi.org - BCM2711](https://www.raspberrypi.org/documentation/hardware/raspberrypi/bcm2711/README.md)
2. [Raspberry Pi官方文档](https://www.raspberrypi.org/documentation/)
3. [gpiozero文档](https://gpiozero.readthedocs.io/)
4. Simon Monk, *Programming the Raspberry Pi: Getting Started with Python*, 3rd Edition, McGraw-Hill, 2021.
