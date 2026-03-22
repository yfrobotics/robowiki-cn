# PyBullet 强化学习工作流

!!! note "引言"
    PyBullet 是强化学习机器人控制研究中广泛使用的仿真平台，支持 Gymnasium 接口标准，可与 Stable-Baselines3（SB3）等主流 RL 库无缝集成。本文介绍如何使用 PyBullet 构建自定义 RL 环境、设计奖励函数、进行并行训练以及应用域随机化技术。


## Gymnasium 环境接口

### PyBullet 内置环境

PyBullet 提供了一系列兼容 Gymnasium 的标准环境：

```bash
pip install pybullet gymnasium stable-baselines3
```

```python
import gymnasium as gym
import pybullet_envs  # 注册 PyBullet 环境

# 常用环境
env = gym.make("AntBulletEnv-v0")      # 四足蚂蚁
env = gym.make("HumanoidBulletEnv-v0")  # 人形机器人
env = gym.make("HalfCheetahBulletEnv-v0")  # 半猎豹
env = gym.make("KukaBulletEnv-v0")      # Kuka 机械臂
```

| 环境名 | 观测维度 | 动作维度 | 任务描述 |
|--------|---------|---------|---------|
| AntBulletEnv | 28 | 8 | 四足行走 |
| HumanoidBulletEnv | 44 | 17 | 人形行走 |
| HalfCheetahBulletEnv | 26 | 6 | 前进奔跑 |
| HopperBulletEnv | 15 | 3 | 单腿跳跃 |
| KukaBulletEnv | 9 | 3 | 物体抓取 |


## 自定义环境设计

### 环境模板

```python
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pybullet as p, pybullet_data

class RobotReachEnv(gym.Env):
    """机械臂到达目标点的自定义环境"""
    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        self.action_space = spaces.Box(-1.0, 1.0, shape=(7,), dtype=np.float32)
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(20,), dtype=np.float32)
        self.physics_client = p.connect(p.GUI if render_mode == "human" else p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -9.81)
        self.robot_id = None
        self.step_count, self.max_steps = 0, 500

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        p.resetSimulation(); p.setGravity(0, 0, -9.81)
        p.loadURDF("plane.urdf")
        self.robot_id = p.loadURDF("kuka_iiwa/model.urdf", [0,0,0], useFixedBase=True)
        self.target_pos = self.np_random.uniform([0.2,-0.3,0.2], [0.6,0.3,0.6])
        for i in range(7):
            p.resetJointState(self.robot_id, i, self.np_random.uniform(-0.5, 0.5))
        self.step_count = 0
        return self._get_obs(), {}

    def step(self, action):
        action = np.clip(action, -1.0, 1.0) * 0.05
        states = p.getJointStates(self.robot_id, range(7))
        for i in range(7):
            p.setJointMotorControl2(self.robot_id, i, p.POSITION_CONTROL,
                                    targetPosition=states[i][0] + action[i], force=240)
        for _ in range(4): p.stepSimulation()
        self.step_count += 1
        obs = self._get_obs()
        ee_pos = np.array(p.getLinkState(self.robot_id, 6)[0])
        dist = np.linalg.norm(ee_pos - self.target_pos)
        reward = -dist + (10.0 if dist < 0.05 else 0.0)
        return obs, reward, dist < 0.02, self.step_count >= self.max_steps, {}

    def _get_obs(self):
        states = p.getJointStates(self.robot_id, range(7))
        ee = list(p.getLinkState(self.robot_id, 6)[0])
        return np.array([s[0] for s in states] + [s[1] for s in states]
                        + ee + list(self.target_pos), dtype=np.float32)

    def close(self): p.disconnect()
```


## 奖励函数设计

### 常用奖励组件

| 组件 | 公式 | 作用 |
|------|------|------|
| 距离惩罚 | \(-\|x_{ee} - x_{goal}\|\) | 引导末端接近目标 |
| 到达奖励 | \(+R \cdot \mathbb{1}[d < \epsilon]\) | 鼓励精确到达 |
| 动作惩罚 | \(-\lambda \|a\|^2\) | 减少不必要运动 |
| 能量惩罚 | \(-\sum \tau_i \dot{q}_i\) | 减少能耗 |
| 速度奖励 | \(+v_x\) | 前进任务 |
| 存活奖励 | \(+c\) | 防止提前终止 |
| 平滑惩罚 | \(-\|a_t - a_{t-1}\|^2\) | 动作平滑 |

### 奖励函数示例

```python
def compute_locomotion_reward(robot_id, prev_pos, action, alive_bonus=1.0):
    """四足机器人运动奖励"""
    # 获取当前位置和速度
    pos, orn = p.getBasePositionAndOrientation(robot_id)
    vel, ang_vel = p.getBaseVelocity(robot_id)

    # 前进速度奖励
    forward_reward = vel[0]  # x 方向速度

    # 存活奖励（高度不能太低）
    height = pos[2]
    alive = alive_bonus if height > 0.2 else 0.0

    # 动作惩罚
    action_penalty = -0.01 * np.sum(np.square(action))

    # 姿态惩罚（保持直立）
    euler = p.getEulerFromQuaternion(orn)
    orientation_penalty = -0.1 * (euler[0]**2 + euler[1]**2)

    reward = forward_reward + alive + action_penalty + orientation_penalty

    # 终止条件：摔倒
    terminated = height < 0.15

    return reward, terminated
```


## 并行环境训练

### 使用 SubprocVecEnv

```python
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback

def make_env(rank):
    def _init():
        env = RobotReachEnv(render_mode=None)
        env.reset(seed=rank)
        return env
    return _init

if __name__ == "__main__":
    # 创建 8 个并行环境
    n_envs = 8
    env = SubprocVecEnv([make_env(i) for i in range(n_envs)])

    # 评估环境
    eval_env = RobotReachEnv(render_mode=None)

    # 训练 PPO
    model = PPO(
        "MlpPolicy", env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=256,
        n_epochs=10,
        gamma=0.99,
        verbose=1,
        tensorboard_log="./logs/"
    )

    eval_callback = EvalCallback(
        eval_env, eval_freq=5000,
        best_model_save_path="./best/"
    )

    model.learn(total_timesteps=1_000_000, callback=eval_callback)
```

### 完整训练流程

```python
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy

# 训练 → 保存 → 评估
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=500_000)
model.save("robot_reach_ppo")

model = PPO.load("robot_reach_ppo")
mean_reward, std = evaluate_policy(model, RobotReachEnv(), n_eval_episodes=20)
print(f"平均奖励: {mean_reward:.2f} +/- {std:.2f}")
```

SB3 提供 `BaseCallback` 可自定义训练监控，结合 TensorBoard 记录距离、成功率等自定义指标。


## 域随机化

### 物理参数随机化

在 `reset()` 中随机化物理参数即可实现域随机化：

```python
class DomainRandomizedEnv(RobotReachEnv):
    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)
        # 随机化质量、摩擦、重力
        for link in range(p.getNumJoints(self.robot_id)):
            mass = p.getDynamicsInfo(self.robot_id, link)[0]
            p.changeDynamics(self.robot_id, link,
                             mass=mass * self.np_random.uniform(0.8, 1.2))
        p.changeDynamics(self.robot_id, -1,
                         lateralFriction=self.np_random.uniform(0.3, 1.5))
        p.setGravity(0, 0, -9.81 + self.np_random.uniform(-0.5, 0.5))
        return obs, info
```

还可以在 `step()` 中添加观测噪声和动作延迟来模拟传感器和执行器的不确定性。

视觉域随机化可通过 `changeVisualShape` 随机化物体颜色。注意 PyBullet 的光照控制有限，复杂视觉随机化建议使用 Isaac Sim。


## 训练技巧总结

| 技巧 | 说明 |
|------|------|
| 观测归一化 | 使用 `VecNormalize` 包装器 |
| 奖励归一化 | 使用 `VecNormalize(norm_reward=True)` |
| 帧堆叠 | 使用 `VecFrameStack` 提供速度信息 |
| 提前终止 | 不合理状态直接终止，节省训练时间 |
| 课程学习 | 从简单目标开始，逐步增加难度 |
| 奖励裁剪 | 限制单步奖励范围，防止梯度爆炸 |
| 多种子训练 | 使用不同随机种子训练 3-5 次取平均 |

使用 `VecNormalize(env, norm_obs=True, norm_reward=True)` 包装环境即可自动归一化。


## 参考资料

- PyBullet 快速入门：<https://docs.google.com/document/d/10sXEhzFRSnvFcl3XxNGhnD4N2SedqwdAvK3dsihxVUA/>
- Stable-Baselines3 文档：<https://stable-baselines3.readthedocs.io/>
- Gymnasium 文档：<https://gymnasium.farama.org/>
- Coumans E, Bai Y. PyBullet, a Python module for physics simulation. 2016-2021.
