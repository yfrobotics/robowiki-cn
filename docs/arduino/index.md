# Arduino

!!! note "引言"
    Arduino是一个开源的电子原型平台，由硬件（开发板）和软件（Arduino IDE）两部分组成。自2005年在意大利诞生以来，Arduino以其低门槛、低成本和丰富的社区资源，成为全球嵌入式开发教育和快速原型设计的事实标准。在机器人领域，Arduino常被用作底层控制器，负责传感器数据采集、电机驱动和通信接口管理。

Arduino是全世界使用最广泛的嵌入式计算机，被用于大量电子hacking、互动式艺术以及DIY作品中。

## 1. Arduino型号

Arduino有以下常见型号：

### 1.1 Entry Level

- Arduino Uno
- Arduino Leonardo
- Arduino Nano
- Arduino Micro
- Arduino Esplora
- Arduino Mega
- Arduino Mega 2560


### 1.2 Enhanced

- Arduino Uno WiFi Rev.2
- Arduino Yun
- Arduino Yun Rev.2
- Arduino Zero (32bit ARM Cortex-MO+ @ 48 MHz)
- Arduino MKR Zero (32bit ARM Cortex-M0+ @ 48MHz)
- Arduino MKR1000 (32bit ARM Cortex-M0+; with Wi-Fi)
- Arduino Due (32bit ARM Cortex-M3 @ 84 MHz)


## 2. Arduino IDE

Arduino IDE是Arduino官方提供的集成开发环境。其特点包括：

- **基于C/C++语言**：Arduino程序（称为Sketch）本质上是C/C++代码，但对初学者隐藏了底层复杂性。
- **跨平台**：支持Windows、macOS和Linux操作系统。
- **库管理器（Library Manager）**：内置库管理工具，可以方便地搜索、安装和更新第三方库。
- **板卡管理器（Board Manager）**：支持通过URL添加第三方开发板的支持，如ESP32、STM32等。
- **串口监视器（Serial Monitor）**：内置串口调试工具，用于查看程序输出和发送调试命令。

Arduino IDE 2.0基于Eclipse Theia框架重新开发，提供了自动补全、代码导航和集成调试器等现代IDE功能。


## 3. 编程基础

每个Arduino程序包含两个核心函数：

- **`setup()`**：在程序启动时执行一次，用于初始化配置（如引脚模式、串口波特率等）。
- **`loop()`**：在`setup()`执行完成后不断循环执行，是程序的主逻辑所在。

```cpp
void setup() {
    Serial.begin(9600);       // 初始化串口通信，波特率9600
    pinMode(LED_BUILTIN, OUTPUT);  // 设置内置LED引脚为输出模式
}

void loop() {
    digitalWrite(LED_BUILTIN, HIGH);  // 点亮LED
    delay(1000);                       // 延时1秒
    digitalWrite(LED_BUILTIN, LOW);   // 熄灭LED
    delay(1000);                       // 延时1秒
}
```


## 4. GPIO、PWM与ADC

### GPIO（通用输入输出）

Arduino的数字引脚可以配置为输入（INPUT）或输出（OUTPUT）模式。输出模式下可以驱动LED、继电器等外设；输入模式下可以读取按钮、传感器等信号。

### PWM（脉冲宽度调制）

Arduino Uno上标记有`~`符号的数字引脚（3、5、6、9、10、11）支持PWM输出。PWM通过调节方波的占空比（Duty Cycle）来模拟模拟量输出，常用于电机速度控制和LED亮度调节。

```cpp
// 使用PWM控制LED亮度（0-255）
analogWrite(9, 128);  // 50%占空比
```

### ADC（模数转换器）

Arduino Uno提供6个模拟输入引脚（A0-A5），内置10位ADC，分辨率为0到1023。常用于读取电位器、光敏电阻和各类模拟传感器。

```cpp
int sensorValue = analogRead(A0);  // 读取A0引脚的模拟值
float voltage = sensorValue * (5.0 / 1023.0);  // 转换为电压值
```


## 5. 常用库

Arduino生态拥有大量开源库，以下是机器人开发中常用的库：

| 库名称 | 功能 | 应用场景 |
|--------|------|----------|
| Servo | 舵机控制 | 机器人关节、云台 |
| Wire | I2C通信 | IMU、OLED显示屏 |
| SPI | SPI通信 | SD卡、无线模块 |
| AccelStepper | 步进电机控制 | 精密运动控制 |
| PID_v1 | PID控制算法 | 电机速度/位置控制 |
| Encoder | 编码器读取 | 电机转速测量 |
| NewPing | 超声波测距 | 避障 |
| MPU6050 | IMU数据读取 | 姿态估计 |
| rosserial | ROS通信 | 与ROS系统集成 |


## 6. 扩展板与模块

Arduino通过扩展板（Shield）和外接模块来扩展功能：

- **电机驱动扩展板（Motor Shield）**：如Adafruit Motor Shield V2，可同时驱动多个直流电机和步进电机。
- **传感器扩展板（Sensor Shield）**：提供方便的传感器接口，简化接线。
- **以太网扩展板（Ethernet Shield）**：基于W5100/W5500芯片，提供有线网络连接。
- **Wi-Fi模块**：如ESP8266、ESP32，通过串口与Arduino通信实现无线连接。
- **蓝牙模块**：如HC-05/HC-06，用于短距离无线通信和手机遥控。
- **GPS模块**：如NEO-6M，用于户外机器人的定位。
- **IMU模块**：如MPU6050（6轴）、MPU9250（9轴），用于姿态估计。


## 7. 通信方式

### 串口通信 (Serial / UART)

Arduino内置硬件串口，通过`Serial`对象进行收发。Arduino Mega拥有4个硬件串口，适合同时连接多个串口设备。

```cpp
Serial.begin(115200);
Serial.println("Hello Robot!");
```

### I2C通信

I2C是双线制通信协议（SDA和SCL），支持一主多从。Arduino通过`Wire`库实现I2C通信，常用于连接IMU、OLED显示屏和电机驱动器。

### SPI通信

SPI是高速四线制通信协议（MOSI、MISO、SCK、SS），适合需要高数据传输速率的场景。Arduino通过`SPI`库实现SPI通信，常用于SD卡读写和无线收发模块。


## 8. 电机控制示例

以下示例演示使用Arduino和L298N驱动板控制一个直流电机：

```cpp
// L298N直流电机控制
const int IN1 = 7;   // 方向控制引脚1
const int IN2 = 8;   // 方向控制引脚2
const int ENA = 9;   // 速度控制引脚（PWM）

void setup() {
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(ENA, OUTPUT);
}

// 正转
void motorForward(int speed) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, speed);  // speed: 0-255
}

// 反转
void motorBackward(int speed) {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, speed);
}

// 停止
void motorStop() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 0);
}

void loop() {
    motorForward(200);   // 正转，速度200
    delay(2000);
    motorStop();
    delay(500);
    motorBackward(150);  // 反转，速度150
    delay(2000);
    motorStop();
    delay(500);
}
```


## 9. 与其他MCU平台的对比

| 特性 | Arduino Uno | STM32 (Blue Pill) | ESP32 | Raspberry Pi Pico |
|------|-------------|-------------------|-------|--------------------|
| 处理器 | ATmega328P (AVR 8-bit) | STM32F103 (ARM Cortex-M3) | Xtensa LX6 双核 | RP2040 (ARM Cortex-M0+) |
| 主频 | 16 MHz | 72 MHz | 240 MHz | 133 MHz |
| Flash | 32 KB | 64 KB | 4 MB | 2 MB |
| RAM | 2 KB | 20 KB | 520 KB | 264 KB |
| GPIO | 14数字 + 6模拟 | 37 | 34 | 26 |
| Wi-Fi/蓝牙 | 无 | 无 | 有 | 无（Pico W有Wi-Fi） |
| 价格 | 较低 | 极低 | 低 | 极低 |
| 开发难度 | 极低 | 中 | 低-中 | 低 |
| 适用场景 | 入门学习/原型 | 工业控制 | IoT/无线 | 通用嵌入式 |

Arduino的最大优势在于极低的开发门槛和庞大的社区支持，适合快速原型验证。而当项目进入产品化阶段，通常会考虑迁移到STM32或ESP32等更专业的平台以获得更好的性能和成本优势。

(本条目需要完善，[立刻参与知识公共编辑](/how-to-contribute/))


## 参考资料

1. [Arduino官方网站](https://www.arduino.cc/)
2. [Arduino语言参考手册](https://www.arduino.cc/reference/en/)
3. [Arduino Project Hub](https://create.arduino.cc/projecthub)
