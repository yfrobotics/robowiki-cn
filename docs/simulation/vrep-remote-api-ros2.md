# CoppeliaSim 远程 API 与 ROS 2

!!! note "引言"
    CoppeliaSim（原名 V-REP）提供了多种远程控制接口，使外部程序能够与仿真环境交互。自 V4.3 版本起，基于 ZeroMQ 的远程 API 取代了旧版 API，成为推荐的通信方式。同时，CoppeliaSim 提供了 ROS 2 插件，支持通过标准 ROS 2 话题和服务与仿真进行双向通信。


## 远程 API 发展历程

| 版本 | API 类型 | 协议 | 状态 |
|------|---------|------|------|
| V-REP 3.x | Legacy Remote API | 自定义 TCP | 已弃用 |
| CoppeliaSim 4.3+ | ZeroMQ Remote API | ZeroMQ + CBOR | 推荐使用 |
| CoppeliaSim 4.5+ | WebSocket API | WebSocket | 浏览器端使用 |

ZeroMQ Remote API 相比旧版的主要优势：

- 通信速度更快，延迟更低
- 支持所有 CoppeliaSim API 函数（旧版仅支持部分）
- 使用 CBOR（Concise Binary Object Representation）序列化，数据传输高效
- 支持 Python、C++、Java、MATLAB、Lua 等多种客户端


## ZeroMQ Remote API 基础

### 安装与配置

```bash
# 安装 Python 客户端
pip install coppeliasim-zmqremoteapi-client
```

确保 CoppeliaSim 启动时加载了 ZeroMQ 插件（默认启用）。仿真器默认在端口 23000 监听连接。

### 连接与基本操作

```python
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

# 建立连接
client = RemoteAPIClient()
sim = client.require('sim')

# 仿真控制
sim.setStepping(True)   # 启用步进模式
sim.startSimulation()

# 获取场景中的对象句柄
robot_handle = sim.getObject('/robot')
joint_handle = sim.getObject('/robot/joint1')

# 读取和设置关节位置
position = sim.getJointPosition(joint_handle)
sim.setJointTargetPosition(joint_handle, 1.57)  # 设置目标位置（弧度）

# 步进仿真
for i in range(1000):
    sim.step()

sim.stopSimulation()
```

### 传感器数据读取

```python
# 视觉传感器
vision_handle = sim.getObject('/vision_sensor')
img, resolution = sim.getVisionSensorImg(vision_handle)

# 将图像转换为 NumPy 数组
import numpy as np
img_array = np.frombuffer(img, dtype=np.uint8).reshape(
    resolution[1], resolution[0], 3
)

# 近距离传感器
prox_handle = sim.getObject('/proximity_sensor')
result, dist, point, handle, normal = sim.readProximitySensor(prox_handle)

# 力传感器
force_handle = sim.getObject('/force_sensor')
result, force, torque = sim.readForceSensor(force_handle)
```

### 关节控制模式

CoppeliaSim 支持多种关节控制模式：

| 控制模式 | 函数 | 适用场景 |
|---------|------|---------|
| 位置控制 | `setJointTargetPosition()` | PID 位置跟踪 |
| 速度控制 | `setJointTargetVelocity()` | 轮式机器人驱动 |
| 力/力矩控制 | `setJointTargetForce()` | 动力学仿真 |
| 混合模式 | `setJointMode()` | 自定义控制器 |

```python
# 速度控制示例（差分驱动机器人）
left_motor = sim.getObject('/left_motor')
right_motor = sim.getObject('/right_motor')

# 设置目标速度
sim.setJointTargetVelocity(left_motor, 2.0)   # 左轮 2 rad/s
sim.setJointTargetVelocity(right_motor, 2.0)  # 右轮 2 rad/s
```


## 步进模式与同步仿真

步进模式（Stepping Mode）允许外部程序精确控制仿真推进节奏：

```python
sim.setStepping(True)
sim.startSimulation()

while True:
    # 1. 读取传感器
    sensor_data = read_sensors(sim)

    # 2. 运行控制算法（可能耗时较长）
    control_output = my_controller(sensor_data)

    # 3. 发送控制指令
    apply_control(sim, control_output)

    # 4. 推进仿真一步
    sim.step()

    # 5. 检查终止条件
    if done:
        break

sim.stopSimulation()
```

同步模式确保控制算法有足够时间计算，不会因为仿真提前运行而丢失控制周期。


## ROS 2 插件集成

### 插件安装

CoppeliaSim 的 ROS 2 插件（`simROS2`）需要与 ROS 2 版本匹配编译：

```bash
# 在 ROS 2 工作空间中编译插件
cd ~/ros2_ws/src
git clone https://github.com/CoppeliaRobotics/simROS2.git
cd ~/ros2_ws
colcon build --packages-select simROS2
```

### 话题发布与订阅

在 CoppeliaSim 的 Lua 脚本中配置 ROS 2 通信：

```lua
function sysCall_init()
    -- 创建发布器：发布关节状态
    jointStatePub = simROS2.createPublisher(
        '/joint_states', 'sensor_msgs/msg/JointState'
    )

    -- 创建订阅器：接收速度指令
    cmdVelSub = simROS2.createSubscription(
        '/cmd_vel', 'geometry_msgs/msg/Twist',
        'cmdVelCallback'
    )
end

function cmdVelCallback(msg)
    -- 将 Twist 消息转换为差分驱动指令
    local linear = msg.linear.x
    local angular = msg.angular.z
    local wheel_sep = 0.3
    local v_left = linear - angular * wheel_sep / 2
    local v_right = linear + angular * wheel_sep / 2
    sim.setJointTargetVelocity(leftMotor, v_left / wheel_radius)
    sim.setJointTargetVelocity(rightMotor, v_right / wheel_radius)
end

function sysCall_actuation()
    -- 发布关节状态
    local msg = {}
    msg.header = {stamp = simROS2.getSystemTime(), frame_id = 'base_link'}
    msg.name = {'joint1', 'joint2'}
    msg.position = {
        sim.getJointPosition(joint1Handle),
        sim.getJointPosition(joint2Handle)
    }
    simROS2.publish(jointStatePub, msg)
end
```

### 传感器数据发布

```lua
function sysCall_init()
    -- 激光雷达发布器
    laserPub = simROS2.createPublisher(
        '/scan', 'sensor_msgs/msg/LaserScan'
    )
    -- 相机图像发布器
    imgPub = simROS2.createPublisher(
        '/camera/image_raw', 'sensor_msgs/msg/Image'
    )
end
```


## 协同仿真架构

### ZeroMQ + ROS 2 混合使用

推荐架构：

```
ROS 2 节点（导航/控制）
       ↕ ROS 2 话题
CoppeliaSim（ROS 2 插件）
       ↕ ZeroMQ API
Python 脚本（强化学习/数据收集）
```

- ROS 2 插件用于与 ROS 2 导航栈、控制器等标准组件集成
- ZeroMQ API 用于场景管理、批量数据采集、强化学习训练循环


### 多仿真实例

可以同时运行多个 CoppeliaSim 实例（每个使用不同端口，如 23000-23003），通过 `RemoteAPIClient(port=port)` 分别连接，结合 Python 的 `threading` 或 `multiprocessing` 实现并行仿真，适合强化学习数据收集和参数扫描。


## 常见问题与排查

| 问题 | 可能原因 | 解决方法 |
|------|---------|---------|
| 连接超时 | ZeroMQ 插件未加载 | 检查 CoppeliaSim 控制台输出 |
| API 函数不存在 | 版本不匹配 | 更新客户端库或 CoppeliaSim |
| 仿真不推进 | 步进模式未调用 `step()` | 确认调用了 `sim.step()` |
| ROS 2 话题不可见 | 插件未编译 / 版本不匹配 | 重新编译 simROS2 插件 |
| 图像数据异常 | 分辨率/格式不匹配 | 检查 `getVisionSensorImg` 参数 |


## 参考资料

- CoppeliaSim ZeroMQ Remote API 文档：<https://manual.coppeliarobotics.com/en/zmqRemoteApiOverview.htm>
- CoppeliaSim ROS 2 插件：<https://github.com/CoppeliaRobotics/simROS2>
- CoppeliaSim 用户手册：<https://manual.coppeliarobotics.com/>
- ZeroMQ 官方文档：<https://zeromq.org/languages/python/>
