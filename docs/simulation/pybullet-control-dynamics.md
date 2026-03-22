# PyBullet 控制与动力学

!!! note "引言"
    PyBullet 基于 Bullet 物理引擎，提供了丰富的关节控制和动力学仿真功能。本文介绍 PyBullet 中的关节控制模式、PD 控制、逆运动学（Inverse Kinematics, IK）、逆动力学（Inverse Dynamics）、接触力与约束等核心功能，并给出机械臂和四足机器人的控制示例。


## 关节控制模式

PyBullet 提供三种基本的关节控制模式：

| 控制模式 | 函数 | 说明 |
|---------|------|------|
| 位置控制 | `setJointMotorControl2(POSITION_CONTROL)` | 内置 PD 控制器跟踪目标位置 |
| 速度控制 | `setJointMotorControl2(VELOCITY_CONTROL)` | 控制关节速度 |
| 力矩控制 | `setJointMotorControl2(TORQUE_CONTROL)` | 直接施加力矩 |

### 基本用法

```python
import pybullet as p
import pybullet_data

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
p.loadURDF("plane.urdf")
robot_id = p.loadURDF("kuka_iiwa/model.urdf", [0, 0, 0], useFixedBase=True)

# 位置控制：内置 PD 控制器跟踪目标位置
p.setJointMotorControl2(robot_id, 0, p.POSITION_CONTROL,
                        targetPosition=0.5, force=240,
                        positionGain=0.3, velocityGain=1.0)

# 速度控制：适合轮式机器人
p.setJointMotorControl2(robot_id, 0, p.VELOCITY_CONTROL,
                        targetVelocity=5.0, force=10.0)

# 力矩控制：需先禁用默认控制器
for i in range(7):
    p.setJointMotorControl2(robot_id, i, p.VELOCITY_CONTROL, force=0)
p.setJointMotorControlArray(robot_id, range(7), p.TORQUE_CONTROL,
                            forces=[10, -5, 3, -2, 1, -0.5, 0.2])
```


## PD 控制

### 自定义 PD 控制器

当内置 PD 控制器不满足需求时，可以在力矩模式下实现自定义控制器：

```python
import numpy as np

kp = np.array([100, 100, 80, 80, 50, 50, 30])
kd = np.array([10, 10, 8, 8, 5, 5, 3])

for step in range(10000):
    joint_states = p.getJointStates(robot_id, range(7))
    q = np.array([s[0] for s in joint_states])
    dq = np.array([s[1] for s in joint_states])
    torques = np.clip(kp * (q_desired - q) - kd * dq, -240, 240)
    p.setJointMotorControlArray(
        robot_id, range(7), p.TORQUE_CONTROL, forces=torques.tolist()
    )
    p.stepSimulation()
```

### 计算力矩控制

利用逆动力学实现更精确的控制，补偿重力和科里奥利力：

$$
\tau = M(q)\ddot{q}_{des} + C(q, \dot{q})\dot{q} + g(q) + K_p(q_{des} - q) + K_d(\dot{q}_{des} - \dot{q})
$$

```python
def computed_torque_control(robot_id, q_des, dq_des, ddq_des, kp, kd):
    joint_states = p.getJointStates(robot_id, range(7))
    q = [s[0] for s in joint_states]
    dq = [s[1] for s in joint_states]
    tau_id = p.calculateInverseDynamics(robot_id, q, dq, ddq_des)
    tau = np.array(tau_id) + kp * (np.array(q_des) - np.array(q)) \
          + kd * (np.array(dq_des) - np.array(dq))
    return tau
```


## 逆运动学

PyBullet 内置了基于阻尼最小二乘法的 IK 求解器：

```python
# 计算 IK：给定末端目标位置，求关节角度
target_pos = [0.4, 0.2, 0.3]
target_orn = p.getQuaternionFromEuler([0, -3.14, 0])
end_effector_link = 6

joint_positions = p.calculateInverseKinematics(
    robot_id,
    end_effector_link,
    target_pos,
    targetOrientation=target_orn,
    maxNumIterations=100,
    residualThreshold=1e-5
)

# 应用 IK 结果
for i, pos in enumerate(joint_positions):
    p.setJointMotorControl2(
        robot_id, i, p.POSITION_CONTROL, targetPosition=pos
    )
```

### IK 带关节限制

```python
# 指定关节角度范围
lower_limits = [-2.96, -2.09, -2.96, -2.09, -2.96, -2.09, -3.05]
upper_limits = [2.96, 2.09, 2.96, 2.09, 2.96, 2.09, 3.05]
joint_ranges = [u - l for l, u in zip(lower_limits, upper_limits)]
rest_poses = [0.0, 0.0, 0.0, -1.57, 0.0, 1.57, 0.0]

joint_positions = p.calculateInverseKinematics(
    robot_id, end_effector_link, target_pos,
    targetOrientation=target_orn,
    lowerLimits=lower_limits,
    upperLimits=upper_limits,
    jointRanges=joint_ranges,
    restPoses=rest_poses
)
```


## 逆动力学

逆动力学计算给定期望加速度时所需的关节力矩：

$$
\tau = M(q)\ddot{q} + C(q, \dot{q})\dot{q} + g(q)
$$

```python
# 获取当前状态
joint_states = p.getJointStates(robot_id, range(7))
q = [s[0] for s in joint_states]
dq = [s[1] for s in joint_states]
ddq_desired = [0.0] * 7  # 期望加速度

# 计算所需力矩
torques = p.calculateInverseDynamics(robot_id, q, dq, ddq_desired)

# 获取质量矩阵
mass_matrix = p.calculateMassMatrix(robot_id, q)
```


## 接触力与碰撞

```python
# 获取接触点：返回法线(contact[7])、法向力(contact[9])、摩擦力(contact[10/12])
contacts = p.getContactPoints(bodyA=robot_id, bodyB=plane_id)

# 最近点查询（无需仿真步进，可用于碰撞预检测）
closest = p.getClosestPoints(bodyA=robot_id, bodyB=obstacle_id, distance=0.1)
# closest[i][8] 为距离，负值表示穿透
```


## 约束

PyBullet 通过 `createConstraint` 创建约束连接物体，`changeConstraint` 修改参数，`removeConstraint` 移除。

### 约束类型

| 类型 | 常量 | 用途 |
|------|------|------|
| 固定关节 | `JOINT_FIXED` | 刚性连接，模拟抓取 |
| 点到点 | `JOINT_POINT2POINT` | 球铰 |
| 齿轮 | `JOINT_GEAR` | 齿轮传动关系 |
| 棱柱 | `JOINT_PRISMATIC` | 滑动约束 |


## 应用示例

### 机械臂圆形轨迹跟踪

```python
import pybullet as p, pybullet_data, numpy as np, time

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
p.loadURDF("plane.urdf")
robot = p.loadURDF("kuka_iiwa/model.urdf", useFixedBase=True)

center, radius, ee_link = [0.4, 0.0, 0.4], 0.15, 6
for t in range(5000):
    angle = t * 0.01
    target = [center[0] + radius * np.cos(angle),
              center[1] + radius * np.sin(angle), center[2]]
    ik = p.calculateInverseKinematics(robot, ee_link, target)
    for i, pos in enumerate(ik):
        p.setJointMotorControl2(robot, i, p.POSITION_CONTROL,
                                targetPosition=pos, force=240)
    p.stepSimulation()
```

### 四足机器人对角步态

四足机器人步态的核心是为 12 个关节（每条腿 3 个：髋、膝、踝）生成周期性目标轨迹。对角步态中，对角线上的两条腿同相位运动：

```python
def trot_gait(phase, speed=1.0):
    """生成对角步态的 12 个关节目标位置"""
    targets = np.zeros(12)
    for leg in range(4):
        offset = 0.0 if leg in [0, 3] else np.pi
        p = phase + offset
        targets[leg*3+0] = 0.3 * np.sin(p)                    # 髋关节
        targets[leg*3+1] = -0.6 + 0.3 * max(0, np.sin(p))     # 膝关节
        targets[leg*3+2] = 0.8 - 0.2 * max(0, np.sin(p))      # 踝关节
    return targets
```


## 动力学参数设置

通过 `changeDynamics` 可设置摩擦系数（`lateralFriction`）、质量（`mass`）、惯性（`localInertiaDiagonal`）、接触刚度（`contactStiffness`）、阻尼（`contactDamping`）和恢复系数（`restitution`）。使用 `getDynamicsInfo` 查询当前参数。


## 参考资料

- PyBullet 快速入门指南：<https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/>
- Bullet 物理引擎：<https://pybullet.org/>
- PyBullet GitHub：<https://github.com/bulletphysics/bullet3>
- Featherstone R. *Rigid Body Dynamics Algorithms*. Springer, 2008.
