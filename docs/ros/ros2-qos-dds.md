# ROS 2 QoS 与 DDS

!!! note "引言"
    DDS (Data Distribution Service，数据分发服务) 是 ROS 2 的底层通信中间件，其 QoS (Quality of Service，服务质量) 策略为机器人系统提供了细粒度的通信质量控制能力。理解 DDS 架构和 QoS 配置，是构建可靠、高性能 ROS 2 系统的关键。


## DDS 架构概述

DDS 是由 OMG (Object Management Group，对象管理组织) 制定的分布式实时通信标准。ROS 2 通过 RMW (ROS Middleware，ROS 中间件) 抽象层与 DDS 实现交互，应用层代码无需直接操作 DDS API。

```
┌─────────────────────────────┐
│  ROS 2 应用层 (rclcpp/rclpy) │
├─────────────────────────────┤
│  RCL (ROS Client Library)    │
├─────────────────────────────┤
│  RMW (ROS Middleware 抽象层)  │
├─────────────────────────────┤
│  DDS 实现 (Fast DDS, Cyclone │
│  DDS, Connext DDS 等)        │
├─────────────────────────────┤
│  UDP / Shared Memory         │
└─────────────────────────────┘
```

DDS 相比 ROS 1 通信架构的核心优势：

- **去中心化**：无需 Master 节点，通过发现协议自动互联
- **标准化**：基于工业标准，有多种商业和开源实现
- **QoS 策略**：提供丰富的通信质量配置
- **多传输**：支持 UDP 组播、单播和共享内存


## QoS 策略详解

QoS 策略定义了数据通信的行为和约束。ROS 2 提供以下核心 QoS 参数：


### 可靠性 (Reliability)

控制消息是否保证送达。

| 值 | 行为 | 适用场景 |
|---|------|----------|
| `RELIABLE` | 重传丢失的消息，确保所有数据送达 | 控制命令、配置参数 |
| `BEST_EFFORT` | 不重传，可能丢失数据但延迟更低 | 传感器数据流、视频流 |


### 持久性 (Durability)

控制后加入的订阅者能否收到历史消息。

| 值 | 行为 | 适用场景 |
|---|------|----------|
| `VOLATILE` | 只收到订阅后发布的新消息 | 实时传感器数据 |
| `TRANSIENT_LOCAL` | 可收到订阅前发布的最新消息 | 地图数据、静态配置 |


### 历史 (History)

控制消息缓冲策略。

| 值 | 行为 | 适用场景 |
|---|------|----------|
| `KEEP_LAST(N)` | 只保留最近 N 条消息 | 大多数场景 |
| `KEEP_ALL` | 保留所有消息直到被消费 | 日志记录、可靠传输 |


### 截止时间 (Deadline)

指定发布者必须在规定时间内发布下一条消息。如果超时，系统会触发回调通知。

```python
from rclpy.qos import QoSProfile
from rclpy.duration import Duration

qos = QoSProfile(
    depth=10,
    deadline=Duration(seconds=0, nanoseconds=100_000_000)  # 100 ms
)
```


### 存活性 (Liveliness)

检测发布者是否仍然活跃。

| 值 | 行为 |
|---|------|
| `AUTOMATIC` | 由 DDS 自动管理，通过心跳检测 |
| `MANUAL_BY_TOPIC` | 发布者需要手动声明存活 |

```python
from rclpy.qos import QoSProfile, LivelinessPolicy
from rclpy.duration import Duration

qos = QoSProfile(
    depth=10,
    liveliness=LivelinessPolicy.AUTOMATIC,
    liveliness_lease_duration=Duration(seconds=1)
)
```


### 生命周期 (Lifespan)

指定消息的有效期，超过有效期的消息会被丢弃，不会传递给订阅者。适合对时效性要求高的数据。


## QoS 兼容性规则

发布者和订阅者的 QoS 设置必须兼容，否则无法建立通信连接。兼容性规则如下：

| 发布者 | 订阅者 | 兼容性 |
|--------|--------|--------|
| `RELIABLE` | `RELIABLE` | 兼容 |
| `RELIABLE` | `BEST_EFFORT` | 兼容 |
| `BEST_EFFORT` | `BEST_EFFORT` | 兼容 |
| `BEST_EFFORT` | `RELIABLE` | **不兼容** |
| `TRANSIENT_LOCAL` | `TRANSIENT_LOCAL` | 兼容 |
| `TRANSIENT_LOCAL` | `VOLATILE` | 兼容 |
| `VOLATILE` | `VOLATILE` | 兼容 |
| `VOLATILE` | `TRANSIENT_LOCAL` | **不兼容** |

核心原则：**订阅者的要求不能高于发布者的承诺**。例如，订阅者要求 `RELIABLE`，但发布者只提供 `BEST_EFFORT`，则无法通信。

诊断不兼容问题：

```bash
# 查看话题的 QoS 信息
ros2 topic info /scan --verbose
```


## QoS 预设配置

ROS 2 提供了几种常用的预设 QoS 配置：

```python
from rclpy.qos import (
    QoSProfile,
    QoSReliabilityPolicy,
    QoSDurabilityPolicy,
    QoSHistoryPolicy,
    qos_profile_sensor_data,
    qos_profile_system_default,
    qos_profile_services_default,
    qos_profile_parameters,
)
```

| 预设名称 | Reliability | Durability | History | 典型用途 |
|----------|-------------|------------|---------|----------|
| `sensor_data` | BEST_EFFORT | VOLATILE | KEEP_LAST(5) | 传感器数据（激光、IMU） |
| `system_default` | RELIABLE | VOLATILE | KEEP_LAST(10) | 一般话题通信 |
| `services_default` | RELIABLE | VOLATILE | KEEP_LAST(10) | 服务调用 |
| `parameters` | RELIABLE | VOLATILE | KEEP_LAST(1000) | 参数事件 |


### 代码示例：自定义 QoS

```python
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from sensor_msgs.msg import LaserScan

class ScanSubscriber(Node):
    def __init__(self):
        super().__init__('scan_subscriber')

        # 自定义 QoS 配置
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=5
        )

        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos
        )

    def scan_callback(self, msg):
        min_range = min(msg.ranges)
        self.get_logger().info(f'最近障碍物距离: {min_range:.2f} m')

def main():
    rclpy.init()
    node = ScanSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

```cpp
// C++ 示例
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>

class ScanSubscriber : public rclcpp::Node
{
public:
    ScanSubscriber() : Node("scan_subscriber")
    {
        // 使用传感器数据预设
        auto qos = rclcpp::SensorDataQoS();

        sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
            "/scan", qos,
            [this](const sensor_msgs::msg::LaserScan::SharedPtr msg) {
                auto min_it = std::min_element(
                    msg->ranges.begin(), msg->ranges.end());
                RCLCPP_INFO(this->get_logger(),
                    "最近障碍物距离: %.2f m", *min_it);
            });
    }
private:
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr sub_;
};
```


## DDS 实现选择

ROS 2 支持多种 DDS 实现，可通过环境变量切换：

```bash
# 使用 Fast DDS（默认）
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

# 使用 Cyclone DDS
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# 使用 Connext DDS
export RMW_IMPLEMENTATION=rmw_connextdds
```

| DDS 实现 | 维护方 | 许可 | 特点 |
|----------|--------|------|------|
| Fast DDS | eProsima | Apache 2.0 | ROS 2 默认实现，功能全面，文档丰富 |
| Cyclone DDS | Eclipse | Eclipse Public License | 轻量高效，延迟低，API 简洁 |
| Connext DDS | RTI | 商业许可 | 工业级，高可靠性，提供高级安全和监控功能 |

选择建议：

- **一般开发**：Fast DDS 或 Cyclone DDS 均可，开箱即用
- **对延迟敏感**：Cyclone DDS 通常表现更好
- **工业部署**：Connext DDS 提供商业支持和认证
- **嵌入式场景**：Cyclone DDS 占用资源更少


### DDS 配置文件

各 DDS 实现支持通过 XML 配置文件进行高级调优。以 Fast DDS 为例：

```xml
<!-- fastdds_profile.xml -->
<?xml version="1.0" encoding="UTF-8" ?>
<dds xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
    <profiles>
        <transport_descriptors>
            <transport_descriptor>
                <transport_id>udp_transport</transport_id>
                <type>UDPv4</type>
                <sendBufferSize>1048576</sendBufferSize>
                <receiveBufferSize>4194304</receiveBufferSize>
            </transport_descriptor>
        </transport_descriptors>

        <participant profile_name="participant_profile"
                     is_default_profile="true">
            <rtps>
                <userTransports>
                    <transport_id>udp_transport</transport_id>
                </userTransports>
                <useBuiltinTransports>false</useBuiltinTransports>
            </rtps>
        </participant>
    </profiles>
</dds>
```

```bash
# 加载配置文件
export FASTRTPS_DEFAULT_PROFILES_FILE=/path/to/fastdds_profile.xml
```


## DDS 发现机制

DDS 使用 SPDP (Simple Participant Discovery Protocol，简单参与者发现协议) 和 SEDP (Simple Endpoint Discovery Protocol，简单端点发现协议) 实现节点之间的自动发现。


### 发现流程

1. **参与者发现 (SPDP)**：节点启动后，通过 UDP 组播周期性广播自身存在
2. **端点发现 (SEDP)**：发现对方后，交换发布者和订阅者的元信息
3. **QoS 匹配**：检查 QoS 兼容性，兼容则建立通信链路
4. **数据传输**：通过 UDP 单播或共享内存传输实际数据


### 发现服务器模式

对于大型系统，组播发现可能导致网络风暴。Fast DDS 提供发现服务器 (Discovery Server) 模式：

```bash
# 启动发现服务器
fastdds discovery --server-id 0 --port 11811

# 客户端节点配置
export ROS_DISCOVERY_SERVER=192.168.1.100:11811
```


## 多机通信配置

### ROS_DOMAIN_ID

ROS_DOMAIN_ID 用于隔离同一网络中不同 ROS 2 系统的通信。不同 Domain ID 的节点之间互不通信。

```bash
# 设置 Domain ID（范围 0-232，默认为 0）
export ROS_DOMAIN_ID=42
```

注意事项：

- 同一团队的机器人应使用相同的 Domain ID
- 不同团队或项目使用不同的 Domain ID 以避免干扰
- Domain ID 会映射到特定的 UDP 端口，避免使用过大的值


### 多机通信配置步骤

```bash
# 1. 确保所有机器在同一网络段
# 2. 设置相同的 ROS_DOMAIN_ID
export ROS_DOMAIN_ID=10

# 3. 如果组播不可用，配置单播对等节点
# Cyclone DDS 配置示例
export CYCLONEDDS_URI='<CycloneDDS>
  <Domain>
    <General>
      <Interfaces>
        <NetworkInterface name="eth0"/>
      </Interfaces>
    </General>
    <Discovery>
      <Peers>
        <Peer address="192.168.1.101"/>
        <Peer address="192.168.1.102"/>
      </Peers>
    </Discovery>
  </Domain>
</CycloneDDS>'
```


### 防火墙配置

DDS 使用 UDP 端口进行通信，防火墙需要放行相关端口：

```bash
# 放行 DDS 端口范围（根据 Domain ID 计算）
# 基础端口 = 7400 + 250 * DOMAIN_ID
# 示例：DOMAIN_ID=0 时，端口范围 7400-7500
sudo ufw allow 7400:7500/udp

# 放行组播地址
sudo ufw allow from 239.255.0.0/16
```


### 共享内存传输

对于同一主机上的节点通信，使用共享内存可以显著降低延迟和 CPU 开销：

```xml
<!-- Fast DDS 共享内存配置 -->
<dds xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
    <profiles>
        <transport_descriptors>
            <transport_descriptor>
                <transport_id>shm_transport</transport_id>
                <type>SHM</type>
                <segment_size>1048576</segment_size>
            </transport_descriptor>
        </transport_descriptors>

        <participant profile_name="shm_participant"
                     is_default_profile="true">
            <rtps>
                <userTransports>
                    <transport_id>shm_transport</transport_id>
                </userTransports>
                <useBuiltinTransports>false</useBuiltinTransports>
            </rtps>
        </participant>
    </profiles>
</dds>
```


## QoS 调优实践

### 传感器数据管线

```python
# 典型的激光雷达/IMU 数据 QoS
sensor_qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    depth=1  # 只关心最新数据
)
```


### 控制命令

```python
# 速度控制命令需要可靠传输
control_qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    depth=10,
    deadline=Duration(seconds=0, nanoseconds=50_000_000)  # 50 ms
)
```


### 地图数据

```python
# 地图需要持久性，确保后加入的节点能收到
map_qos = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
    depth=1
)
```


## 参考资料

- [ROS 2 QoS 概念](https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Quality-of-Service-Settings.html)
- [OMG DDS 标准](https://www.omg.org/spec/DDS/)
- [eProsima Fast DDS 文档](https://fast-dds.docs.eprosima.com/)
- [Eclipse Cyclone DDS 文档](https://cyclonedds.io/docs/)
- [ROS 2 RMW 实现](https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Different-Middleware-Vendors.html)
- [ROS 2 Discovery Server](https://fast-dds.docs.eprosima.com/en/latest/fastdds/ros2/discovery_server/ros2_discovery_server.html)
