# 电源与散热

!!! note "引言"
    电源系统和散热设计是机器人硬件工程中容易被低估但极其关键的环节。电源设计不当可能导致系统重启、传感器数据异常甚至硬件损坏；散热不足则会引发计算平台降频，严重影响算法实时性。本文系统介绍电池选型、电源管理、功耗预算、散热方案以及常见嵌入式平台的热管理策略。


## 电池选型

机器人常用的可充电电池类型有三种：锂聚合物（Lithium Polymer, LiPo）、锂离子（Lithium-Ion, Li-ion）和磷酸铁锂（Lithium Iron Phosphate, LiFePO4）。


### 电池类型对比

| 参数 | LiPo | Li-ion（18650/21700） | LiFePO4 |
|------|------|----------------------|---------|
| 标称电压（每节） | 3.7 V | 3.6–3.7 V | 3.2 V |
| 充电截止电压 | 4.2 V | 4.2 V | 3.65 V |
| 放电截止电压 | 3.0 V | 2.5–3.0 V | 2.5 V |
| 能量密度 | 150–250 Wh/kg | 150–270 Wh/kg | 90–160 Wh/kg |
| 最大放电倍率 | 20–100C | 1–5C（动力型 10C） | 3–10C |
| 循环寿命 | 300–500 次 | 500–1000 次 | 2000–5000 次 |
| 安全性 | 较低（易鼓包/起火） | 中等 | 高（热稳定好） |
| 典型应用 | 无人机、竞赛机器人 | 移动机器人、AGV | 大型 AGV、户外机器人 |
| 价格 | 中等 | 低–中等 | 中–高 |


### 电池选型建议

- **无人机**：首选 LiPo，放电倍率高（通常 25C 以上），重量轻，但需严格管理充放电。
- **室内移动机器人**：Li-ion 18650/21700 组合，性价比高，循环寿命好。
- **工业 AGV（自动导引车）/ 户外机器人**：LiFePO4 安全性高，循环寿命长，适合长时间连续运行。


### 电池容量估算

电池容量通常以毫安时（mAh）或瓦时（Wh）表示。估算续航时间的公式：

$$
t_{运行} = \frac{E_{电池} \times \eta_{放电}}{P_{总功耗}}
$$

其中 \(E_{电池}\) 为电池能量（Wh），\(\eta_{放电}\) 为放电效率（通常 0.85–0.95），\(P_{总功耗}\) 为系统总功耗（W）。


## 电池管理系统

电池管理系统（Battery Management System, BMS）是电池安全运行的核心保障。


### BMS 核心功能

| 功能 | 说明 |
|------|------|
| 过充保护 | 单节电压超过上限时切断充电 |
| 过放保护 | 单节电压低于下限时切断输出 |
| 过流保护 | 输出电流超过额定值时切断 |
| 短路保护 | 检测到短路立即断开 |
| 均衡充电 | 平衡各节电池电压差异（被动/主动均衡） |
| 温度监控 | NTC 热敏电阻监测电池温度 |
| SOC 估算 | 估算电池荷电状态（State of Charge） |


### BMS 选型要点

```
选型清单：
+-- 串联节数（S 数）：与电池组匹配
+-- 持续放电电流：>= 系统最大持续电流
+-- 峰值放电电流：>= 系统峰值电流（如电机堵转）
+-- 均衡方式：被动均衡（简单）/ 主动均衡（效率高）
+-- 通信接口：SMBus / I2C / UART / CAN（用于 SOC 上报）
+-- 温度保护阈值：充电 0–45°C，放电 -20–60°C
```


## 电压调节

机器人系统中通常有多个不同电压等级的子系统，需要使用 DC-DC 变换器进行电压转换。


### 降压变换器（Buck Converter）

将高电压降为低电压，效率通常 85–95%。常用芯片如 LM2596（3A）、MP1584（3A）、TPS5430（3A）等。

```
电池 24V --> [Buck 24V->12V] --> Jetson Orin Nano (12V, 15W)
         --> [Buck 24V->5V]  --> Raspberry Pi (5V, 15W)
         --> [Buck 24V->3.3V]--> MCU 及低压传感器
```


### 升压变换器（Boost Converter）

将低电压升为高电压，用于电池电压低于负载需求的场景。例如 3S LiPo（11.1V）驱动需要 24V 供电的步进电机驱动器。


### 关键设计参数

| 参数 | 说明 | 典型要求 |
|------|------|----------|
| 输入电压范围 | 需覆盖电池放电全程 | 如 3S LiPo: 9.0–12.6V |
| 输出电压精度 | 负载变化时输出波动 | ±1–2% |
| 输出纹波 | 高频噪声 | < 50 mV（传感器供电需 < 20 mV） |
| 转换效率 | 输出功率 / 输入功率 | > 90% |
| 散热能力 | 大电流时发热量 | 需计算热阻和结温 |


## 功耗预算

在系统设计初期进行功耗预算（Power Budget）分析至关重要。


### 功耗预算表示例

| 子系统 | 额定电压 | 额定功耗 | 峰值功耗 | 工作占比 |
|--------|----------|----------|----------|----------|
| 底盘电机 x4 | 24 V | 40 W | 120 W | 80% |
| Jetson AGX Orin | 12 V | 30 W | 60 W | 100% |
| 激光雷达 | 12 V | 8 W | 10 W | 100% |
| 深度相机 | 5 V | 3 W | 5 W | 100% |
| MCU + 传感器 | 3.3/5 V | 2 W | 3 W | 100% |
| Wi-Fi 模块 | 5 V | 2 W | 4 W | 100% |
| 散热风扇 | 12 V | 3 W | 5 W | 50% |
| **合计** | — | **88 W** | **207 W** | — |

加权平均功耗计算：

$$
P_{平均} = \sum_{i} P_{额定,i} \times D_i
$$

其中 \(D_i\) 为各子系统的工作占比。本例约 86.5 W。

若使用 24V / 10Ah 电池组（240 Wh），按 90% 放电效率，估算续航：

$$
t = \frac{240 \times 0.9}{86.5} \approx 2.5 \text{ 小时}
$$


## 热备份与冗余

在安全要求较高的场景（医疗、军工、户外无人设备），需要考虑电源冗余设计。


### 常见冗余方案

- **双电池热备份**：两组电池通过二极管 OR 电路并联，一组电量耗尽后自动切换到另一组，不中断供电。
- **UPS 后备电源**：小容量备用电池仅供安全系统（安全 MCU、急停逻辑），在主电源断电后维持数秒钟，足够完成安全停机。
- **热插拔设计**：支持在不断电的情况下更换电池，常见于工业 AGV。需要超级电容或小型缓冲电池在切换期间维持供电。

```c
// 电源监控示例 -- 通过 ADC 监测电池电压
#include "stm32f4xx_hal.h"

#define VBAT_DIVIDER_RATIO  11.0f   // 分压比 100k:10k
#define ADC_REF_VOLTAGE     3.3f
#define ADC_RESOLUTION      4096.0f
#define LOW_BATTERY_THRESHOLD  22.0f  // 24V 电池低电量阈值

float read_battery_voltage(ADC_HandleTypeDef *hadc) {
    HAL_ADC_Start(hadc);
    HAL_ADC_PollForConversion(hadc, 10);
    uint32_t raw = HAL_ADC_GetValue(hadc);
    float v_adc = (raw / ADC_RESOLUTION) * ADC_REF_VOLTAGE;
    return v_adc * VBAT_DIVIDER_RATIO;
}

void check_battery_status(ADC_HandleTypeDef *hadc) {
    float vbat = read_battery_voltage(hadc);
    if (vbat < LOW_BATTERY_THRESHOLD) {
        // 触发低电量警告，降低电机功率
        set_motor_power_limit(0.5f);
        send_low_battery_warning();
    }
}
```


## 散热管理

散热管理的目标是将芯片结温（Junction Temperature）控制在安全范围内，防止热节流（Thermal Throttling）导致性能下降。


### 散热基本原理

热量从芯片传递到环境的路径可以用热阻模型表示：

$$
T_j = T_a + P \times (\theta_{jc} + \theta_{cs} + \theta_{sa})
$$

其中 \(T_j\) 为结温，\(T_a\) 为环境温度，\(P\) 为功耗，\(\theta_{jc}\)、\(\theta_{cs}\)、\(\theta_{sa}\) 分别为芯片到外壳、外壳到散热器、散热器到空气的热阻（单位 °C/W）。


### 被动散热

- **散热片（Heat Sink）**：铝合金或铜材质，通过增大散热面积降低 \(\theta_{sa}\)。
- **导热垫（Thermal Pad）**：硅胶基底，厚度 0.5–3 mm，导热系数 1–6 W/(m·K)，适用于不平整的接触面。
- **导热硅脂（Thermal Paste）**：填充芯片与散热片之间的微观空隙，导热系数通常 4–12 W/(m·K)。
- **金属外壳导热**：将机器人外壳设计为散热结构，整机作为散热器。


### 主动散热

| 方案 | 散热能力 | 噪音 | 功耗 | 适用场景 |
|------|----------|------|------|----------|
| 轴流风扇 | 中–高 | 中 | 1–5 W | 通用场景 |
| 离心风扇 | 高 | 高 | 3–10 W | 受限空间 |
| 热管 + 风扇 | 高 | 中 | 2–5 W | 高功耗芯片 |
| 液冷 | 极高 | 低 | 5–20 W | 数据中心/大型机器人 |
| TEC 半导体制冷 | 中 | 低 | 高（COP < 1） | 特殊环境（军工） |


## 嵌入式平台热管理

机器人常用的嵌入式计算平台在满负荷时容易达到热极限，需要针对性的热管理方案。


### NVIDIA Jetson 系列

| 平台 | TDP | 最大结温 | 散热方案建议 |
|------|-----|----------|-------------|
| Jetson Nano | 5–10 W | 97°C | 被动散热片（<= 5W）/ 风扇（10W） |
| Jetson Orin Nano | 7–15 W | 97°C | 散热片 + 小风扇 |
| Jetson AGX Orin | 15–60 W | 105°C | 大型散热片 + 风扇 / 液冷 |

Jetson 平台提供动态功耗模式管理工具 `nvpmodel` 和性能监控工具 `jetson_clocks`：

```bash
# 查看当前功耗模式
sudo nvpmodel -q

# 设置为 15W 模式（Jetson AGX Orin）
sudo nvpmodel -m 2

# 最大化时钟频率（测试用，增加发热）
sudo jetson_clocks

# 监控温度
cat /sys/devices/virtual/thermal/thermal_zone*/temp
# 输出单位为毫摄氏度，如 45000 表示 45°C

# 持续监控温度和功耗
sudo tegrastats
```

当温度接近限值时，Jetson 会自动降低 GPU/CPU 频率（热节流），导致推理延迟增加。在封闭机器人外壳中尤其需要注意散热设计。


### Raspberry Pi 系列

Raspberry Pi 4/5 在高负荷时 CPU 温度容易超过 80°C 并触发降频：

```bash
# 查看 CPU 温度
vcgencmd measure_temp

# 查看是否发生降频
vcgencmd get_throttled
# 返回值含义：
# 0x0     -- 正常
# 0x50000 -- 曾经发生过降频
# 0x50005 -- 当前正在降频

# 在 /boot/config.txt 中设置温度阈值
# temp_limit=80         # 默认 85°C，可适当降低
# arm_freq=1800         # 限制最大频率以降低发热
```

推荐散热方案：

- **Raspberry Pi 4**：铝合金外壳散热器（如 Argon ONE 外壳）或散热片 + 小风扇
- **Raspberry Pi 5**：官方主动散热器（Active Cooler）或第三方散热外壳


## 电源监控系统

完善的电源监控系统可以提前预警问题，避免意外断电。


### 监控指标

| 监控项 | 传感器/方法 | 典型芯片 | 报警阈值 |
|--------|-------------|----------|----------|
| 电池电压 | 分压器 + ADC | 内置 ADC | < 放电截止电压 x 节数 |
| 放电电流 | 霍尔传感器 / 分流电阻 | INA219、INA226 | > 额定电流 120% |
| 电池温度 | NTC 热敏电阻 | — | > 60°C |
| 电源轨电压 | INA3221 多通道监控 | INA3221 | ±5% 偏差 |


### INA219 电流/功率监控示例

```python
# 使用 INA219 通过 I2C 监控电池电流和功率
# pip install pi-ina219

from ina219 import INA219, DeviceRangeError

SHUNT_OHMS = 0.1  # 分流电阻值（单位：欧姆）
MAX_EXPECTED_AMPS = 3.0

ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=0x40)
ina.configure(ina.RANGE_32V, ina.GAIN_AUTO)

def monitor_power():
    try:
        voltage = ina.voltage()          # 总线电压 (V)
        current = ina.current()          # 电流 (mA)
        power = ina.power()              # 功率 (mW)
        shunt_v = ina.shunt_voltage()    # 分流电压 (mV)

        print(f"电压: {voltage:.2f} V")
        print(f"电流: {current:.2f} mA")
        print(f"功率: {power:.2f} mW")

        if voltage < 22.0:
            print("[警告] 电池电压过低！")
        if current > MAX_EXPECTED_AMPS * 1000:
            print("[警告] 电流超过额定值！")

    except DeviceRangeError:
        print("[错误] 电流超出传感器量程")

if __name__ == "__main__":
    import time
    while True:
        monitor_power()
        print("---")
        time.sleep(1)
```


## 设计检查清单

在完成电源与散热设计后，建议按以下清单逐项检查：

| 检查项 | 要点 |
|--------|------|
| 功耗预算 | 是否包含所有子系统？峰值功耗是否考虑？ |
| 电池容量 | 续航时间是否满足需求？含安全余量（>= 20%）？ |
| BMS 保护 | 过充/过放/过流/短路/温度保护是否齐全？ |
| DC-DC 选型 | 输入范围是否覆盖电池全放电曲线？纹波是否满足要求？ |
| 电源隔离 | 电机电源与逻辑电源是否隔离？EMI 滤波是否到位？ |
| 接线规格 | 导线截面积是否满足最大电流要求？ |
| 散热预算 | 最坏情况环境温度下，结温是否在安全范围内？ |
| 散热测试 | 满负荷连续运行 30 分钟，温度是否稳定？ |
| 安全冗余 | 急停按钮、保险丝、TVS 保护是否到位？ |


## 参考资料

- NVIDIA Jetson Power Management: https://developer.nvidia.com/embedded/jetson-power-management
- Raspberry Pi Documentation — Configuration: https://www.raspberrypi.com/documentation/computers/config_txt.html
- Texas Instruments — Power Management Guide for Robotics: https://www.ti.com/
- INA219 Datasheet: https://www.ti.com/product/INA219
- Battery University — Lithium-ion Comparisons: https://batteryuniversity.com/
