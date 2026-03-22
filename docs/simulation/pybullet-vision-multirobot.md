# PyBullet 视觉与多机器人

!!! note "引言"
    PyBullet 除了物理仿真外，还提供了合成图像渲染功能，支持 RGB、深度图和语义分割图的生成。这些功能可用于训练视觉策略、生成合成数据集以及构建多机器人仿真系统。本文介绍 PyBullet 的视觉传感器接口、合成数据生成方法、多机器人场景搭建以及性能优化技巧。


## 相机图像采集

### getCameraImage 接口

PyBullet 通过 `getCameraImage` 函数渲染图像，返回 RGB、深度和分割掩码：

```python
import pybullet as p
import numpy as np

# 设置相机参数
width, height = 640, 480
fov = 60
aspect = width / height
near = 0.01
far = 10.0

# 计算视图矩阵和投影矩阵
view_matrix = p.computeViewMatrix(
    cameraEyePosition=[1.0, 0.5, 0.8],
    cameraTargetPosition=[0.0, 0.0, 0.3],
    cameraUpVector=[0, 0, 1]
)
projection_matrix = p.computeProjectionMatrixFOV(
    fov=fov, aspect=aspect, nearVal=near, farVal=far
)

# 渲染图像
_, _, rgb, depth, segmentation = p.getCameraImage(
    width=width,
    height=height,
    viewMatrix=view_matrix,
    projectionMatrix=projection_matrix,
    renderer=p.ER_BULLET_HARDWARE_OPENGL  # 使用 GPU 渲染
)

# 转换为 NumPy 数组
rgb_array = np.array(rgb, dtype=np.uint8).reshape(height, width, 4)[:, :, :3]
depth_array = np.array(depth, dtype=np.float32).reshape(height, width)
seg_array = np.array(segmentation, dtype=np.int32).reshape(height, width)
```

### 渲染器选择

| 渲染器 | 常量 | 特点 |
|--------|------|------|
| TinyRenderer | `ER_TINY_RENDERER` | CPU 渲染，无需 GPU，速度慢 |
| EGL | `ER_BULLET_HARDWARE_OPENGL` | GPU 渲染，速度快，Linux 推荐 |

```python
# Linux 下使用 EGL 无头渲染
import os
os.environ["MESA_GL_VERSION_OVERRIDE"] = "3.3"
p.connect(p.DIRECT)  # 无头模式
# EGL 渲染器在 DIRECT 模式下自动使用（如果可用）
```


## 深度图处理

### 深度值转换

`getCameraImage` 返回的深度值是归一化的非线性值，需要转换为真实距离：

$$
z_{real} = \frac{far \times near}{far - (far - near) \times z_{buffer}}
$$

```python
def depth_buffer_to_meters(depth_buffer, near, far):
    """将 PyBullet 深度缓冲转换为真实距离（米）"""
    depth = far * near / (far - (far - near) * depth_buffer)
    return depth

depth_meters = depth_buffer_to_meters(depth_array, near=0.01, far=10.0)
```

### 深度图转点云

```python
def depth_to_pointcloud(depth, fov, width, height):
    """深度图转换为 3D 点云"""
    fx = width / (2.0 * np.tan(np.radians(fov / 2.0)))
    fy = fx  # 假设正方形像素

    # 生成像素网格
    u = np.arange(width)
    v = np.arange(height)
    u, v = np.meshgrid(u, v)

    # 反投影到 3D
    z = depth
    x = (u - width / 2.0) * z / fx
    y = (v - height / 2.0) * z / fy

    points = np.stack([x, y, z], axis=-1).reshape(-1, 3)

    # 过滤无效点
    valid = (z.flatten() > 0.01) & (z.flatten() < 10.0)
    return points[valid]
```


## 语义分割

### 分割掩码使用

`getCameraImage` 返回的分割图中，每个像素值对应物体的 `bodyUniqueId` 和 `linkIndex`：

```python
def parse_segmentation(seg_array):
    """解析分割掩码，提取物体 ID 和链接 ID"""
    obj_ids = seg_array & 0xFFFF          # 低 16 位为物体 ID
    link_ids = (seg_array >> 16) - 1      # 高 16 位为链接 ID + 1
    return obj_ids, link_ids

obj_ids, link_ids = parse_segmentation(seg_array)

# 为每个物体生成不同颜色的掩码
unique_ids = np.unique(obj_ids)
color_mask = np.zeros((*obj_ids.shape, 3), dtype=np.uint8)
for uid in unique_ids:
    if uid < 0:
        continue
    color = np.random.randint(50, 255, size=3)
    color_mask[obj_ids == uid] = color
```

### 合成数据生成流程

利用分割掩码可以自动生成目标检测和实例分割训练数据。基本流程：

1. 使用 `createCollisionShape` 和 `createVisualShape` 随机生成不同形状、颜色的物体
2. 通过 `createMultiBody` 将物体放置到场景中的随机位置
3. 调用 `getCameraImage` 获取 RGB、深度和分割图
4. 根据分割掩码中的物体 ID 自动生成标注（边界框或掩码）
5. 使用 `removeBody` 清理场景后重复上述步骤


## 多机器人仿真

### 基本设置

```python
import pybullet as p, pybullet_data, numpy as np

class MultiRobotSim:
    def __init__(self, n_robots=4, gui=True):
        p.connect(p.GUI if gui else p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        p.loadURDF("plane.urdf")
        # 在圆形上均匀分布初始位置
        self.robots = []
        for i in range(n_robots):
            angle = 2 * np.pi * i / n_robots
            pos = [2.0 * np.cos(angle), 2.0 * np.sin(angle), 0.2]
            self.robots.append(p.loadURDF("husky/husky.urdf", pos))

    def step(self, actions):
        for robot_id, (vl, vr) in zip(self.robots, actions):
            p.setJointMotorControl2(robot_id, 2, p.VELOCITY_CONTROL,
                                    targetVelocity=vl, force=50)
            p.setJointMotorControl2(robot_id, 3, p.VELOCITY_CONTROL,
                                    targetVelocity=vr, force=50)
        p.stepSimulation()

    def get_states(self):
        states = []
        for rid in self.robots:
            pos, orn = p.getBasePositionAndOrientation(rid)
            vel, _ = p.getBaseVelocity(rid)
            states.append({'position': pos,
                           'orientation': p.getEulerFromQuaternion(orn),
                           'velocity': vel})
        return states
```

### 集群行为模拟

```python
class SwarmBehavior:
    """简单的群体行为算法"""

    def __init__(self, n_robots):
        self.n_robots = n_robots

    def reynolds_rules(self, states, sep_dist=0.5):
        """Reynolds 群集规则：分离、对齐、聚合"""
        actions = []
        positions = np.array([s['position'][:2] for s in states])
        for i in range(self.n_robots):
            separation, alignment, cohesion, count = np.zeros(2), np.zeros(2), np.zeros(2), 0
            for j in range(self.n_robots):
                if i == j: continue
                diff = positions[i] - positions[j]
                dist = np.linalg.norm(diff)
                if dist < sep_dist * 3:
                    count += 1
                    if dist < sep_dist and dist > 0:
                        separation += diff / dist
                    alignment += np.array(states[j]['velocity'][:2])
                    cohesion += positions[j]
            if count > 0:
                alignment /= count
                cohesion = cohesion / count - positions[i]
            desired = separation + 0.3 * alignment + 0.2 * cohesion
            heading = states[i]['orientation'][2]
            forward = np.dot(desired, [np.cos(heading), np.sin(heading)])
            lateral = np.dot(desired, [-np.sin(heading), np.cos(heading)])
            turn = np.arctan2(lateral, max(forward, 0.1))
            v = min(np.linalg.norm(desired), 5.0)
            actions.append((v - turn * 2, v + turn * 2))
        return actions
```


## 机器人间碰撞检测

使用 `getContactPoints(bodyA, bodyB)` 检查两个机器人之间是否接触，`getClosestPoints(bodyA, bodyB, distance)` 获取最近距离。遍历所有机器人对即可构建完整的碰撞/距离矩阵。


## 性能优化技巧

### 仿真加速

| 技巧 | 效果 | 实现方式 |
|------|------|---------|
| DIRECT 模式 | 无渲染开销 | `p.connect(p.DIRECT)` |
| 减少碰撞体 | 显著加速 | 使用简化形状 |
| 增大步长 | 更少的迭代次数 | `p.setTimeStep(1/60)` |
| 减少求解器迭代 | 牺牲精度换速度 | `p.setPhysicsEngineParameter(numSolverIterations=10)` |
| 批量 API | 减少函数调用 | 使用 `Array` 版本的函数 |

通过 `setPhysicsEngineParameter` 调整求解器迭代次数和碰撞检测子步数。使用 `getJointStates`（批量版本）代替逐个调用 `getJointState`。

### 多实例并行

PyBullet 的 DIRECT 模式在每个进程中独立运行，可通过 `multiprocessing.Pool` 并行启动多个仿真实例。每个进程独立调用 `p.connect(p.DIRECT)` 创建隔离的物理世界，适合并行数据收集和参数扫描。


## 参考资料

- PyBullet 快速入门：<https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/>
- PyBullet GitHub：<https://github.com/bulletphysics/bullet3>
- Reynolds C W. Flocks, Herds and Schools: A Distributed Behavioral Model. *SIGGRAPH*, 1987.
- Coumans E, Bai Y. PyBullet, a Python module for physics simulation for games, robotics and machine learning. 2016-2021.
