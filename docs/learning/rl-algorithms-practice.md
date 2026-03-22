# 强化学习算法与实践

!!! note "引言"
    强化学习（Reinforcement Learning, RL）是机器学习的一个重要分支，智能体通过与环境交互、根据奖励信号调整策略来学习最优行为。本文系统介绍主流强化学习算法，并通过 Stable-Baselines3 代码示例展示实践方法。


## 强化学习基础框架

强化学习的核心要素包括：

- **状态 \(s\)**：环境的描述
- **动作 \(a\)**：智能体的决策
- **奖励 \(r\)**：环境对动作的反馈
- **策略 \(\pi(a|s)\)**：状态到动作的映射
- **价值函数 \(V^\pi(s)\)**：从状态 \(s\) 出发按策略 \(\pi\) 行动的期望累积奖励

目标是找到最优策略 \(\pi^*\) 使得累积折扣奖励最大化：

$$
\pi^* = \arg\max_\pi \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t r_t\right]
$$

其中 \(\gamma \in [0, 1)\) 为折扣因子。


## DQN 系列

### 深度 Q 网络（DQN）

DQN（Deep Q-Network）使用深度神经网络近似 Q 函数 \(Q(s, a)\)，核心创新包括：

- **经验回放（Experience Replay）**：将转移 \((s, a, r, s')\) 存入缓冲区，随机采样训练
- **目标网络（Target Network）**：使用延迟更新的网络计算目标值，提高稳定性

损失函数：

$$
L(\theta) = \mathbb{E}\left[\left(r + \gamma \max_{a'} Q(s', a'; \theta^-) - Q(s, a; \theta)\right)^2\right]
$$

### DQN 改进变体

| 变体 | 改进点 |
|------|--------|
| Double DQN | 分离动作选择和值估计，缓解过估计 |
| Dueling DQN | 分离状态价值 \(V(s)\) 和优势函数 \(A(s,a)\) |
| Prioritized Replay | 按 TD 误差优先采样重要经验 |
| Rainbow | 整合六种改进技术 |

DQN 系列适用于**离散动作空间**，在连续动作空间中需要离散化处理。


## 策略梯度方法

### REINFORCE 算法

策略梯度直接优化参数化策略 \(\pi_\theta\)，梯度公式为：

$$
\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}\left[\nabla_\theta \log \pi_\theta(a|s) \cdot G_t\right]
$$

其中 \(G_t = \sum_{k=0}^{\infty} \gamma^k r_{t+k}\) 为回报。REINFORCE 方差较大，通常引入基线函数 \(b(s)\) 来降低方差。


### Actor-Critic 框架

Actor-Critic 方法同时学习策略（Actor）和价值函数（Critic）：

- **Actor**：策略网络，输出动作或动作分布
- **Critic**：价值网络，评估当前状态的价值

优势函数 \(A(s, a) = Q(s, a) - V(s)\) 用于指导策略更新。


## 主流连续控制算法

### PPO（近端策略优化）

PPO（Proximal Policy Optimization）是目前最常用的策略梯度算法，通过裁剪目标函数限制策略更新幅度：

$$
L^{CLIP}(\theta) = \mathbb{E}\left[\min\left(r_t(\theta) \hat{A}_t, \; \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t\right)\right]
$$

其中 \(r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}\) 为概率比。

PPO 的优点：实现简单、稳定性好、适用范围广。


### SAC（软演员-评论家）

SAC（Soft Actor-Critic）在最大化奖励的同时最大化策略熵，鼓励探索：

$$
J(\pi) = \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t \left(r_t + \alpha \mathcal{H}(\pi(\cdot|s_t))\right)\right]
$$

其中 \(\alpha\) 为温度参数，\(\mathcal{H}\) 为策略熵。SAC 采样效率高于 PPO，适合机器人连续控制任务。


### TD3（双延迟深度确定性策略梯度）

TD3（Twin Delayed DDPG）是 DDPG 的改进版，三个关键技巧：

1. **双 Q 网络**：取两个 Critic 中较小的值，避免过估计
2. **延迟策略更新**：Critic 更新多次后才更新 Actor
3. **目标策略平滑**：在目标动作中添加噪声


## Stable-Baselines3 实践

### 安装与基本使用

```bash
pip install stable-baselines3[extra]
```

### PPO 训练示例

```python
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.callbacks import EvalCallback

# 创建并行环境
def make_env(env_id, seed):
    def _init():
        env = gym.make(env_id)
        env.reset(seed=seed)
        return env
    return _init

if __name__ == "__main__":
    n_envs = 8
    env = SubprocVecEnv([make_env("Ant-v4", i) for i in range(n_envs)])
    eval_env = gym.make("Ant-v4")

    # 评估回调
    eval_callback = EvalCallback(
        eval_env, eval_freq=10000,
        best_model_save_path="./best_model/",
        deterministic=True
    )

    # 训练 PPO
    model = PPO(
        "MlpPolicy", env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        verbose=1,
        tensorboard_log="./tb_logs/"
    )

    model.learn(total_timesteps=1_000_000, callback=eval_callback)
    model.save("ppo_ant")
```

### SAC 训练示例

```python
from stable_baselines3 import SAC

model = SAC(
    "MlpPolicy", "Humanoid-v4",
    learning_rate=3e-4,
    buffer_size=1_000_000,
    batch_size=256,
    tau=0.005,
    gamma=0.99,
    train_freq=1,
    gradient_steps=1,
    learning_starts=10000,
    verbose=1
)

model.learn(total_timesteps=3_000_000)
```


## 超参数调优

### 关键超参数

| 参数 | 算法 | 典型范围 | 影响 |
|------|------|---------|------|
| 学习率 | 全部 | 1e-4 ~ 3e-4 | 过大不稳定，过小收敛慢 |
| 折扣因子 \(\gamma\) | 全部 | 0.95 ~ 0.999 | 影响长期回报的权重 |
| batch_size | 全部 | 64 ~ 512 | 影响梯度估计的方差 |
| n_steps | PPO | 1024 ~ 4096 | 每次更新使用的步数 |
| buffer_size | SAC/TD3 | 1e5 ~ 1e6 | 经验回放缓冲区大小 |
| tau | SAC/TD3 | 0.005 ~ 0.02 | 目标网络软更新系数 |

### 调优工具

推荐使用 Optuna 进行自动超参数搜索。定义目标函数，在其中使用 `trial.suggest_float` / `trial.suggest_categorical` 采样超参数，训练后返回评估奖励。Optuna 会自动搜索最优组合。SB3 的 rl-zoo3 项目也提供了预配置的超参数搜索脚本。


## 奖励塑形

奖励塑形（Reward Shaping）通过设计辅助奖励信号加速学习：

### 常用技巧

- **稠密奖励**：提供持续反馈而非仅在目标达成时给奖励（如距离目标的负距离）
- **势能函数**：\(F(s, s') = \gamma \Phi(s') - \Phi(s)\)，保证最优策略不变
- **奖励缩放**：将奖励归一化到合适范围，避免梯度消失或爆炸
- **多目标分解**：将复杂任务分解为多个子奖励的加权和


## 课程学习

课程学习（Curriculum Learning）从简单任务开始，逐步增加难度：

1. **阶段式课程**：预定义难度等级，按指标切换
2. **自适应课程**：根据智能体当前能力自动调整难度
3. **自我博弈**：智能体与自身的历史版本对抗训练

在机器人任务中，常见的课程设计包括：从短距离导航到长距离、从无障碍到复杂障碍、从低速到高速运动。


## 算法选择指南

| 场景 | 推荐算法 | 原因 |
|------|---------|------|
| 离散动作空间 | DQN / Rainbow | Q 学习天然适合离散动作 |
| 连续控制（通用） | PPO | 稳定、调参容易 |
| 连续控制（高效采样） | SAC | 离策略算法，采样效率高 |
| 确定性策略需求 | TD3 | 输出确定性动作 |
| 仿真环境丰富 | PPO + 并行环境 | 在策略算法受益于大量并行采样 |
| 真实机器人 | SAC | 样本效率高，适合有限交互 |


## 参考资料

- Sutton R S, Barto A G. *Reinforcement Learning: An Introduction*. MIT Press, 2018.
- Schulman J, et al. Proximal Policy Optimization Algorithms. *arXiv:1707.06347*, 2017.
- Haarnoja T, et al. Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning. *ICML*, 2018.
- Fujimoto S, et al. Addressing Function Approximation Error in Actor-Critic Methods. *ICML*, 2018.
- Stable-Baselines3 文档：<https://stable-baselines3.readthedocs.io/>
