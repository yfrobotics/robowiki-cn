# PyBullet 参考资料

!!! note "引言"
    本文汇总 PyBullet 的 API 分类、官方资源、常用 URDF 模型、与强化学习库的集成方式、基准测试环境以及常见问题排查，为用户提供全面的参考入口。


## API 分类速查

### 仿真控制

| 函数 | 功能 |
|------|------|
| `connect(mode)` | 连接仿真（GUI / DIRECT / SHARED_MEMORY） |
| `disconnect()` | 断开连接 |
| `setGravity(x, y, z)` | 设置重力 |
| `setTimeStep(dt)` | 设置仿真步长 |
| `stepSimulation()` | 推进一步 |
| `setRealTimeSimulation(flag)` | 启用/禁用实时仿真 |
| `resetSimulation()` | 重置仿真 |
| `setPhysicsEngineParameter(...)` | 设置物理引擎参数 |

### 模型加载

| 函数 | 功能 |
|------|------|
| `loadURDF(path, pos, orn)` | 加载 URDF 模型 |
| `loadSDF(path)` | 加载 SDF 模型 |
| `loadMJCF(path)` | 加载 MuJoCo MJCF 模型 |
| `createCollisionShape(...)` | 创建碰撞形状 |
| `createVisualShape(...)` | 创建可视形状 |
| `createMultiBody(...)` | 创建复合体 |
| `removeBody(id)` | 删除物体 |

### 关节操作

| 函数 | 功能 |
|------|------|
| `getNumJoints(id)` | 获取关节数量 |
| `getJointInfo(id, idx)` | 获取关节信息 |
| `getJointState(id, idx)` | 获取关节状态 |
| `getJointStates(id, indices)` | 批量获取状态 |
| `resetJointState(id, idx, pos)` | 重置关节状态 |
| `setJointMotorControl2(...)` | 设置关节控制 |
| `setJointMotorControlArray(...)` | 批量设置控制 |

### 位姿查询

| 函数 | 功能 |
|------|------|
| `getBasePositionAndOrientation(id)` | 获取基座位姿 |
| `resetBasePositionAndOrientation(...)` | 重置基座位姿 |
| `getBaseVelocity(id)` | 获取基座速度 |
| `resetBaseVelocity(...)` | 重置基座速度 |
| `getLinkState(id, idx)` | 获取链接状态 |

### 动力学

| 函数 | 功能 |
|------|------|
| `calculateInverseKinematics(...)` | 逆运动学 |
| `calculateInverseDynamics(...)` | 逆动力学 |
| `calculateMassMatrix(id, q)` | 计算质量矩阵 |
| `calculateJacobian(...)` | 计算雅可比矩阵 |
| `getDynamicsInfo(id, idx)` | 获取动力学参数 |
| `changeDynamics(...)` | 修改动力学参数 |

### 碰撞与接触

| 函数 | 功能 |
|------|------|
| `getContactPoints(...)` | 获取接触点 |
| `getClosestPoints(...)` | 获取最近点 |
| `rayTest(from, to)` | 射线检测 |
| `rayTestBatch(froms, tos)` | 批量射线检测 |
| `getOverlappingObjects(aabb)` | AABB 重叠查询 |

### 渲染与视觉

| 函数 | 功能 |
|------|------|
| `getCameraImage(...)` | 渲染图像 |
| `computeViewMatrix(...)` | 计算视图矩阵 |
| `computeProjectionMatrixFOV(...)` | 计算投影矩阵 |
| `changeVisualShape(...)` | 修改视觉属性 |
| `getVisualShapeData(id)` | 获取视觉形状信息 |


## 官方资源

| 资源 | 链接 | 说明 |
|------|------|------|
| PyBullet 快速入门 | <https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/> | 官方入门文档 |
| GitHub 仓库 | <https://github.com/bulletphysics/bullet3> | 源码和示例 |
| PyPI | <https://pypi.org/project/pybullet/> | Python 包 |
| Bullet 论坛 | <https://pybullet.org/Bullet/phpBB3/> | 社区讨论 |
| 示例代码 | `bullet3/examples/pybullet/` | 丰富的示例脚本 |


## 常用 URDF 模型

### pybullet_data 内置模型

安装 PyBullet 后自带的模型：

| 模型 | 路径 | 类型 |
|------|------|------|
| 地面 | `plane.urdf` | 环境 |
| Kuka iiwa | `kuka_iiwa/model.urdf` | 7-DOF 机械臂 |
| Kuka + 夹爪 | `kuka_iiwa/kuka_with_gripper.sdf` | 带夹爪的机械臂 |
| Franka Panda | `franka_panda/panda.urdf` | 7-DOF 协作臂 |
| Husky | `husky/husky.urdf` | 四轮移动机器人 |
| R2D2 | `r2d2.urdf` | 教学用简单模型 |
| 桌子 | `table/table.urdf` | 环境道具 |
| 托盘 | `tray/tray.urdf` | 环境道具 |

```python
import pybullet_data
p.setAdditionalSearchPath(pybullet_data.getDataPath())
robot = p.loadURDF("kuka_iiwa/model.urdf")
```

### 外部模型资源

| 资源 | 链接 | 说明 |
|------|------|------|
| URDF 模型库 | <https://github.com/ros-industrial> | ROS Industrial 机械臂模型 |
| MuJoCo Menagerie | <https://github.com/google-deepmind/mujoco_menagerie> | 可转换为 URDF |
| Awesome URDF | <https://github.com/ami-iit/awesome-urdf> | URDF 资源汇总 |
| NVIDIA Assets | Isaac Sim 模型库 | 高质量机器人模型 |


## RL 库集成

### Stable-Baselines3

```python
from stable_baselines3 import PPO, SAC, TD3

# PPO（在策略算法）
model = PPO("MlpPolicy", "AntBulletEnv-v0", verbose=1)
model.learn(total_timesteps=1_000_000)

# SAC（离策略算法）
model = SAC("MlpPolicy", "HalfCheetahBulletEnv-v0", verbose=1)
model.learn(total_timesteps=1_000_000)
```

### RLlib

```python
from ray import tune
from ray.rllib.algorithms.ppo import PPOConfig

config = (
    PPOConfig()
    .environment("AntBulletEnv-v0")
    .framework("torch")
    .training(lr=3e-4, train_batch_size=4000)
    .resources(num_gpus=1)
)

tune.run("PPO", config=config.to_dict(), stop={"timesteps_total": 1000000})
```

### 库对比

| 库 | 优点 | 缺点 | PyBullet 兼容性 |
|----|------|------|----------------|
| SB3 | 简洁、稳定 | 单机训练 | 优秀 |
| RLlib | 分布式、多智能体 | 配置复杂 | 良好 |
| CleanRL | 代码透明 | 功能较少 | 良好 |
| TorchRL | 模块化 | 较新，生态待完善 | 良好 |


## 基准测试环境

### 运动控制基准

| 环境 | 动作维度 | 观测维度 | 参考成绩（PPO） |
|------|---------|---------|---------------|
| AntBulletEnv-v0 | 8 | 28 | ~2500 |
| HumanoidBulletEnv-v0 | 17 | 44 | ~2000 |
| HalfCheetahBulletEnv-v0 | 6 | 26 | ~2500 |
| HopperBulletEnv-v0 | 3 | 15 | ~2000 |
| Walker2DBulletEnv-v0 | 6 | 22 | ~2000 |

### 操作任务基准

| 环境 | 任务 | 特点 |
|------|------|------|
| KukaBulletEnv-v0 | 物体抓取 | 稀疏奖励 |
| KukaDiverseObjectEnv | 多样物体抓取 | 域随机化 |
| PandaReachEnv | 到达目标 | 简单入门 |

### 自定义基准建议

使用 PyBullet 构建自定义基准环境时建议：

1. 继承 `gymnasium.Env`，实现标准接口
2. 提供确定性种子控制（通过 `reset(seed=...)` ）
3. 同时提供稠密和稀疏奖励版本
4. 记录关键指标（成功率、完成时间、能耗等）


## 常见问题排查

### 安装问题

| 问题 | 解决方案 |
|------|---------|
| `pip install pybullet` 编译失败 | 安装 C++ 编译器：`sudo apt install build-essential` |
| GUI 模式报 OpenGL 错误 | 安装显卡驱动和 OpenGL 库 |
| WSL 下无 GUI | 安装 VcXsrv 或使用 WSLg |
| Mac M1/M2 安装问题 | 使用 `pip install pybullet --no-cache-dir` |

### 仿真问题

| 问题 | 可能原因 | 解决方案 |
|------|---------|---------|
| 物体穿透地面 | 步长过大 | 减小 `setTimeStep` |
| 关节震荡 | PD 增益过高 | 降低 `positionGain` |
| 物体弹飞 | 初始穿透 | 调整初始位置避免碰撞 |
| 仿真变慢 | 物体过多 | 减少场景中的物体数量 |
| URDF 加载失败 | 路径或格式错误 | 检查文件路径和 URDF 语法 |
| 图像全黑 | 相机参数错误 | 检查 viewMatrix 和 projectionMatrix |
| 关节控制无效 | 控制模式冲突 | 确保模式正确，力矩控制先禁用默认控制器 |

### 性能问题

| 问题 | 解决方案 |
|------|---------|
| 仿真帧率低 | 使用 DIRECT 模式，减少渲染 |
| 图像渲染慢 | 使用 EGL 硬件渲染器 |
| 多机器人仿真慢 | 简化碰撞形状，减少关节数 |
| 内存泄漏 | 确保 `removeBody` 和 `disconnect` |


## URDF 编写要点

- 每个 link 必须有 `inertial` 标签（含 `mass` 和 `inertia`），否则 PyBullet 视为静态物体
- 惯性矩阵必须物理合理（正定），否则仿真不稳定
- 碰撞形状（`collision`）应尽量简单，视觉形状（`visual`）可以复杂
- `useFixedBase=True` 可固定基座不受重力影响
- 关节需指定 `type`（revolute/prismatic/fixed）、`axis`、`limit`（力矩和速度上限）


## 参考资料

- PyBullet 快速入门指南：<https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/>
- Bullet Physics SDK：<https://github.com/bulletphysics/bullet3>
- URDF 规范：<http://wiki.ros.org/urdf/XML>
- Coumans E, Bai Y. PyBullet, a Python module for physics simulation. 2016-2021.
- Stable-Baselines3：<https://stable-baselines3.readthedocs.io/>
