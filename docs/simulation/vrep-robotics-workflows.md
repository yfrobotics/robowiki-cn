# CoppeliaSim 机器人工作流

!!! note "引言"
    CoppeliaSim 提供了丰富的机器人仿真功能，支持移动机器人导航、机械臂抓取、多机器人协作等多种工作流。本文通过具体的应用场景，介绍如何在 CoppeliaSim 中搭建和运行常见的机器人仿真任务。


## 移动机器人导航

### 差分驱动机器人建模

差分驱动机器人是最常见的移动机器人类型，由两个独立驱动轮和若干从动轮组成。

运动学模型：

$$
\begin{bmatrix} \dot{x} \\ \dot{y} \\ \dot{\theta} \end{bmatrix} =
\begin{bmatrix} \cos\theta & 0 \\ \sin\theta & 0 \\ 0 & 1 \end{bmatrix}
\begin{bmatrix} v \\ \omega \end{bmatrix}
$$

其中 \(v = \frac{r(\omega_R + \omega_L)}{2}\)，\(\omega = \frac{r(\omega_R - \omega_L)}{L}\)，\(r\) 为轮半径，\(L\) 为轮距。

```python
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import math

client = RemoteAPIClient()
sim = client.require('sim')

# 获取对象句柄
robot = sim.getObject('/PioneerP3DX')
left_motor = sim.getObject('/PioneerP3DX/leftMotor')
right_motor = sim.getObject('/PioneerP3DX/rightMotor')

def set_velocity(v_linear, v_angular):
    """设置线速度和角速度"""
    wheel_radius = 0.0975
    wheel_separation = 0.33
    v_left = (v_linear - v_angular * wheel_separation / 2) / wheel_radius
    v_right = (v_linear + v_angular * wheel_separation / 2) / wheel_radius
    sim.setJointTargetVelocity(left_motor, v_left)
    sim.setJointTargetVelocity(right_motor, v_right)

# 简单前进并转弯
sim.startSimulation()
set_velocity(0.5, 0.0)  # 直行
```

### 激光雷达避障

通过 `sim.readProximitySensor()` 读取多个近距离传感器的距离值，根据左右传感器的最小距离决定避障策略（直行、左转、右转或原地旋转）。


## 机械臂抓取

### Pick-and-Place 流程

标准的 pick-and-place（取放）操作流程：预抓取位置接近 -> 下降抓取 -> 闭合夹爪 -> 提升 -> 移动到放置位置上方 -> 下降放置 -> 松开夹爪 -> 返回。每个步骤通过 IK 求解关节角并使用位置控制驱动关节。

### 逆运动学配置

CoppeliaSim 内置了逆运动学（Inverse Kinematics, IK）求解器：

```lua
-- Lua 脚本中配置 IK
function sysCall_init()
    -- 创建 IK 环境
    ikEnv = simIK.createEnvironment()
    ikGroup = simIK.createGroup(ikEnv)

    -- 添加 IK 元素
    simIK.addElementFromScene(
        ikEnv, ikGroup,
        sim.getObject('/UR5'), -- 基座
        sim.getObject('/UR5/tip'),  -- 末端执行器
        sim.getObject('/UR5/target'), -- IK 目标
        simIK.constraint_pose  -- 约束类型：位置+姿态
    )
end

function sysCall_actuation()
    -- 求解 IK
    simIK.handleGroup(ikEnv, ikGroup, {syncWorlds = true})
end
```


## 多机器人仿真

### 场景搭建

在 CoppeliaSim 中设置多机器人系统：

1. 导入第一个机器人模型
2. 复制模型，CoppeliaSim 自动重命名（如 `robot#0`, `robot#1`）
3. 每个机器人实例拥有独立的关节、传感器句柄

```python
# 获取多个机器人的句柄
n_robots = 4
robots = []
for i in range(n_robots):
    robot_data = {
        'base': sim.getObject(f'/robot[{i}]'),
        'left_motor': sim.getObject(f'/robot[{i}]/leftMotor'),
        'right_motor': sim.getObject(f'/robot[{i}]/rightMotor'),
    }
    robots.append(robot_data)

# 独立控制每个机器人
for i, robot in enumerate(robots):
    sim.setJointTargetVelocity(robot['left_motor'], velocities[i][0])
    sim.setJointTargetVelocity(robot['right_motor'], velocities[i][1])
```

### 通信与协调

多机器人之间可通过以下方式通信：

| 方式 | 适用场景 | 实现复杂度 |
|------|---------|-----------|
| 信号（Signal） | 简单数据交换 | 低 |
| 自定义数据包 | 结构化数据 | 中 |
| ROS 2 话题 | 与外部系统集成 | 中 |
| 共享黑板 | 集中式任务分配 | 低 |


## 视觉传感器

### 图像采集与处理

```python
import numpy as np

# 获取 RGB 图像
vision_handle = sim.getObject('/vision_sensor')
img, res = sim.getVisionSensorImg(vision_handle)
rgb = np.frombuffer(img, dtype=np.uint8).reshape(res[1], res[0], 3)
rgb = np.flip(rgb, axis=0)  # CoppeliaSim 图像需要上下翻转

# 获取深度图
depth_buffer = sim.getVisionSensorDepth(vision_handle)
depth = np.frombuffer(depth_buffer[0], dtype=np.float32).reshape(res[1], res[0])
# 转换为实际距离
near_clip = 0.01
far_clip = 5.0
depth_meters = near_clip + depth * (far_clip - near_clip)
```

### 目标检测集成

将仿真图像转换为 NumPy 数组后，可直接送入 YOLOv8、DETR 等外部目标检测模型进行推理，根据检测结果调整机器人行为（如避障、抓取目标物体）。


## 路径规划

CoppeliaSim 内置了路径规划模块，支持 OMPL（Open Motion Planning Library）：

```lua
function planPath(start_config, goal_config)
    local task = simOMPL.createTask('pathPlanning')

    -- 设置状态空间（6自由度机械臂）
    local ss = {
        simOMPL.createStateSpace('joint_space', simOMPL.StateSpaceType.joint_position,
            jointHandles, lowerLimits, upperLimits, 1)
    }
    simOMPL.setStateSpace(task, ss)

    -- 设置碰撞检测对
    simOMPL.setCollisionPairs(task, collisionPairs)

    -- 设置起点和目标
    simOMPL.setStartState(task, start_config)
    simOMPL.setGoalState(task, goal_config)

    -- 设置算法和参数
    simOMPL.setAlgorithm(task, simOMPL.Algorithm.RRTConnect)
    simOMPL.setup(task)

    -- 求解
    local solved, path = simOMPL.compute(task, 5.0, -1, 0)  -- 5秒超时
    simOMPL.destroyTask(task)
    return solved, path
end
```


## 自定义模型与 CAD 导入

### 模型创建流程

1. **几何体创建**：使用 CoppeliaSim 内置基元或导入网格
2. **关节添加**：在零件之间添加旋转或移动关节
3. **传感器配置**：添加视觉、距离、力等传感器
4. **物理属性设置**：质量、惯性矩阵、摩擦系数
5. **脚本编写**：为模型添加控制逻辑

### CAD 文件导入

CoppeliaSim 支持多种 CAD 格式：

| 格式 | 支持程度 | 注意事项 |
|------|---------|---------|
| STL | 完全支持 | 仅几何形状，无材质 |
| OBJ | 完全支持 | 支持材质和纹理 |
| URDF | 通过插件支持 | ROS 机器人标准格式 |
| STEP | 需要转换 | 先转为 STL/OBJ |
| Collada (.dae) | 完全支持 | 支持动画信息 |

通过 `sim.importShape()` 可以 API 方式导入模型，并用 `sim.setShapeMass()` 设置质量等物理属性。导入时注意单位转换（如 CAD 常用 mm，仿真使用 m）。


## 工作流最佳实践

1. **场景组织**：使用层次化命名，将机器人各部分放在同一父对象下
2. **仿真步长**：默认 50 ms，高精度需求可降至 5-10 ms
3. **碰撞检测**：仅对需要的对象对启用碰撞检测，减少计算开销
4. **模型保存**：将调试好的模型保存为 `.ttm` 文件，便于复用
5. **版本控制**：场景文件较大，建议将脚本外置并用 Git 管理


## 参考资料

- CoppeliaSim 用户手册：<https://manual.coppeliarobotics.com/>
- CoppeliaSim 模型库：<https://manual.coppeliarobotics.com/en/models.htm>
- OMPL 路径规划文档：<https://ompl.kavrakilab.org/>
- CoppeliaSim 论坛：<https://forum.coppeliarobotics.com/>
