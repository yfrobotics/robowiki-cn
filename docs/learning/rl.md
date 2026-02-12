# 强化学习

!!! note "引言"
    强化学习 (Reinforcement Learning, RL) 是机器学习的一个重要分支，研究智能体 (Agent) 如何在与环境的交互中通过试错学习最优行为策略。它是机器人自主决策和技能学习的核心方法之一。


## 基本原理

强化学习是通过奖励函数的一种探索式学习方法。其原理如下图所示：

![rl](assets/rl.png)

在每个时间步 \(t\)，智能体观察当前状态 \(s_t\)，根据策略 \(\pi\) 选择动作 \(a_t\)，环境返回奖励 \(r_t\) 并转移到新状态 \(s_{t+1}\)。智能体的目标是学习一个策略，使得累积奖励最大化。


## 马尔可夫决策过程 (MDP)

强化学习问题通常被形式化为马尔可夫决策过程 (Markov Decision Process, MDP)，由一个五元组定义：

$$
\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, P, R, \gamma \rangle
$$

其中：

- \(\mathcal{S}\) 是状态空间 (State Space)
- \(\mathcal{A}\) 是动作空间 (Action Space)
- \(P(s'|s, a)\) 是状态转移概率 (Transition Probability)：在状态 \(s\) 执行动作 \(a\) 后转移到状态 \(s'\) 的概率
- \(R(s, a)\) 是奖励函数 (Reward Function)：执行动作后获得的即时奖励
- \(\gamma \in [0, 1]\) 是折扣因子 (Discount Factor)：平衡即时奖励与长期收益

MDP 的核心假设是马尔可夫性 (Markov Property)：下一个状态只依赖于当前状态和动作，与历史无关。


## 价值函数 (Value Functions)

价值函数衡量在特定状态（或状态-动作对）下，按照某策略行动所能获得的期望累积奖励。

**状态价值函数 (State Value Function)**：

$$
V^\pi(s) = \mathbb{E}_\pi \left[ \sum_{t=0}^{\infty} \gamma^t r_t \mid s_0 = s \right]
$$

**动作价值函数 (Action Value Function, Q-Function)**：

$$
Q^\pi(s, a) = \mathbb{E}_\pi \left[ \sum_{t=0}^{\infty} \gamma^t r_t \mid s_0 = s, a_0 = a \right]
$$

最优价值函数满足贝尔曼最优方程 (Bellman Optimality Equation)：

$$
V^*(s) = \max_a \left[ R(s, a) + \gamma \sum_{s'} P(s'|s, a) V^*(s') \right]
$$

$$
Q^*(s, a) = R(s, a) + \gamma \sum_{s'} P(s'|s, a) \max_{a'} Q^*(s', a')
$$


## 算法分类

强化学习算法可以从多个维度进行分类：

### 基于模型 vs 无模型 (Model-based vs Model-free)

- **基于模型的方法 (Model-based)**：学习或利用环境的动力学模型 \(P(s'|s, a)\)，通过模型进行规划。样本效率高，但模型不准确时可能导致性能下降。代表算法有 Dyna-Q、MBPO、Dreamer。
- **无模型的方法 (Model-free)**：直接从经验中学习策略或价值函数，不需要环境模型。样本效率较低但更加通用。大多数主流算法属于此类。

### 在线策略 vs 离线策略 (On-policy vs Off-policy)

- **在线策略 (On-policy)**：使用当前策略生成的数据来更新策略。数据不能重复利用，样本效率较低。代表算法有 SARSA、A3C、PPO。
- **离线策略 (Off-policy)**：可以使用由其他策略生成的历史数据来更新当前策略。通过经验回放 (Experience Replay) 机制提高样本效率。代表算法有 Q-learning、DQN、DDPG、SAC。

### 基于价值 vs 基于策略 vs 演员-评论家 (Value-based vs Policy-based vs Actor-Critic)

- **基于价值的方法 (Value-based)**：学习价值函数，策略由价值函数隐式导出（如选择最大 Q 值的动作）。适合离散动作空间。代表算法有 Q-learning、DQN。
- **基于策略的方法 (Policy-based)**：直接参数化策略并通过梯度上升优化。适合连续动作空间。代表算法有 REINFORCE。
- **演员-评论家方法 (Actor-Critic)**：结合价值方法和策略方法的优势。演员 (Actor) 学习策略，评论家 (Critic) 学习价值函数。代表算法有 A3C、PPO、SAC、TD3。


## 策略梯度方法 (Policy Gradient)

策略梯度方法直接优化参数化策略 \(\pi_\theta(a|s)\)，使得期望累积奖励最大化。策略梯度定理 (Policy Gradient Theorem) 给出了梯度的表达式：

$$
\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta} \left[ \nabla_\theta \log \pi_\theta(a|s) \cdot Q^{\pi_\theta}(s, a) \right]
$$

为了降低梯度估计的方差，通常引入基线函数 (Baseline)，将 \(Q^{\pi_\theta}(s, a)\) 替换为优势函数 (Advantage Function)：

$$
A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)
$$

近端策略优化 (Proximal Policy Optimization, PPO) 是目前最流行的策略梯度算法之一，通过限制策略更新幅度来保证训练稳定性。


## 常见强化学习算法

常见的强化学习方法有 [1]：

|    **Algorithm**    |                      **Description**                     | **Policy** | **Action Space** | **State Space** | **Operator** |
|:-------------------:|:--------------------------------------------------------:|:----------:|:----------------:|:---------------:|:------------:|
| Monte Carlo         | Every visit to Monte Carlo                               | Either     | Discrete         | Discrete        | Sample-means |
| Q-learning          | State–action–reward–state                                | Off-policy | Discrete         | Discrete        | Q-value      |
| SARSA               | State–action–reward–state–action                         | On-policy  | Discrete         | Discrete        | Q-value      |
| Q-learning - Lambda | State–action–reward–state with eligibility traces        | Off-policy | Discrete         | Discrete        | Q-value      |
| SARSA - Lambda      | State–action–reward–state–action with eligibility traces | On-policy  | Discrete         | Discrete        | Q-value      |
| DQN                 | Deep Q Network                                           | Off-policy | Discrete         | Continuous      | Q-value      |
| DDPG                | Deep Deterministic Policy Gradient                       | Off-policy | Continuous       | Continuous      | Q-value      |
| A3C                 | Asynchronous Advantage Actor-Critic Algorithm            | On-policy  | Continuous       | Continuous      | Advantage    |
| NAF                 | Q-Learning with Normalized Advantage Functions           | Off-policy | Continuous       | Continuous      | Advantage    |
| TRPO                | Trust Region Policy Optimization                         | On-policy  | Continuous       | Continuous      | Advantage    |
| PPO                 | Proximal Policy Optimization                             | On-policy  | Continuous       | Continuous      | Advantage    |
| TD3                 | Twin Delayed Deep Deterministic Policy Gradient          | Off-policy | Continuous       | Continuous      | Q-value      |
| SAC                 | Soft Actor-Critic                                        | Off-policy | Continuous       | Continuous      | Advantage    |


## 深度强化学习 (Deep Reinforcement Learning)

深度强化学习将深度神经网络与强化学习结合，使其能够处理高维状态和动作空间。

### DQN (Deep Q-Network)

DQN 使用深度神经网络近似 Q 值函数，引入了两个关键技术：

- **经验回放 (Experience Replay)**：将交互数据存储在缓冲区中，随机采样进行训练，打破数据之间的时序相关性
- **目标网络 (Target Network)**：使用参数延迟更新的目标网络计算 TD 目标，提高训练稳定性

### PPO (Proximal Policy Optimization)

PPO 通过裁剪 (Clipping) 策略比率来限制每次更新的幅度，避免策略剧变：

$$
L^{CLIP}(\theta) = \mathbb{E}_t \left[ \min \left( r_t(\theta) A_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) A_t \right) \right]
$$

其中 \(r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}\) 是策略比率，\(\epsilon\) 是裁剪范围。PPO 实现简单、性能稳定，是目前应用最广泛的深度强化学习算法之一。

### SAC (Soft Actor-Critic)

SAC 在最大化累积奖励的同时，还最大化策略的熵 (Entropy)，鼓励探索：

$$
J(\pi) = \sum_{t=0}^{T} \mathbb{E}_{(s_t, a_t) \sim \rho_\pi} \left[ r(s_t, a_t) + \alpha \mathcal{H}(\pi(\cdot|s_t)) \right]
$$

其中 \(\alpha\) 是温度参数，\(\mathcal{H}\) 是熵。SAC 在连续控制任务中表现出色，训练稳定性好。


## 强化学习在机器人中的应用

强化学习为机器人提供了从经验中学习复杂技能的能力，主要应用领域包括：

### 灵巧操作 (Dexterous Manipulation)

训练机械臂和灵巧手完成抓取、插入、装配等操作任务。典型工作包括 OpenAI 训练灵巧手旋转魔方。关键挑战在于高维动作空间和精确的力控制。

### 运动控制 (Locomotion)

训练腿足机器人（如四足机器人、双足机器人）在各种地形上行走、跑步和跳跃。通过仿真到现实迁移 (Sim-to-Real Transfer)，在仿真环境中训练策略并部署到真实机器人。

### 自主导航 (Autonomous Navigation)

训练移动机器人在未知或动态环境中避障和寻路。强化学习可以学习端到端 (End-to-End) 的导航策略，直接从传感器输入映射到运动指令。

### Sim-to-Real 迁移

由于在真实机器人上训练成本高且存在安全风险，通常先在仿真环境中训练，再将策略迁移到真实世界。常用的技术包括：

- **域随机化 (Domain Randomization)**：在仿真中随机化物理参数、视觉外观等，使策略对环境变化更鲁棒
- **域适应 (Domain Adaptation)**：显式减小仿真与真实之间的分布差异
- **系统辨识 (System Identification)**：提高仿真模型的准确度


## 常用框架与工具

| 框架/工具 | 特点 |
|-----------|------|
| Stable Baselines3 | 基于 PyTorch 的高质量 RL 算法实现（PPO、SAC、TD3 等），接口统一 |
| RLlib (Ray) | 分布式强化学习库，支持大规模并行训练 |
| Gymnasium (原 OpenAI Gym) | 标准化的 RL 环境接口，大量预置环境 |
| Isaac Gym / Isaac Lab | NVIDIA 推出的 GPU 加速物理仿真环境，适合大规模机器人 RL 训练 |
| MuJoCo | 高精度物理仿真引擎，常用于连续控制任务的基准测试 |
| dm_control | DeepMind 基于 MuJoCo 的控制任务套件 |


## 参考资料

1. Reinforcement learning. Wikipedia. <https://en.wikipedia.org/wiki/Reinforcement_learning>
2. Sutton, R. S. & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press. [在线版本](http://incompleteideas.net/book/the-book-2nd.html)
3. Schulman, J., et al. (2017). Proximal Policy Optimization Algorithms. *arXiv:1707.06347*.
4. Haarnoja, T., et al. (2018). Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor. *ICML 2018*.
5. Zhao, W., et al. (2020). Sim-to-Real Transfer in Deep Reinforcement Learning for Robotics: a Survey. *arXiv:2009.13303*.
