# 强化学习参考资料

!!! note "引言"
    本文汇总强化学习（Reinforcement Learning, RL）领域的核心参考资料，包括教科书、重要论文、主流库和工具、仿真环境、算法选择指南以及符号约定，为读者提供系统化的学习和查阅入口。


## 经典教科书

| 书名 | 作者 | 出版年 | 特点 |
|------|------|--------|------|
| *Reinforcement Learning: An Introduction* | Sutton, Barto | 2018 (2nd) | RL 圣经，理论全面 |
| *Algorithms for Reinforcement Learning* | Szepesvári | 2010 | 精炼数学推导 |
| *Deep Reinforcement Learning Hands-On* | Lapan | 2020 (2nd) | 实践导向，PyTorch 代码 |
| *Spinning Up in Deep RL* | OpenAI | 在线 | 入门友好，有配套代码 |
| *动手学强化学习* | 张伟楠等 | 2023 | 中文教材，适合国内读者 |
| *Decision Making Under Uncertainty* | Kochenderfer | 2015 | 偏规划与决策理论 |


## 里程碑论文

### 值函数方法

| 论文 | 年份 | 贡献 |
|------|------|------|
| Playing Atari with Deep RL (DQN) | 2013 | 深度 RL 开山之作 |
| Human-level Control (Nature DQN) | 2015 | 经验回放 + 目标网络 |
| Double DQN | 2016 | 解决 Q 值过估计 |
| Dueling DQN | 2016 | V/A 分离架构 |
| Rainbow | 2018 | 六种 DQN 改进集成 |

### 策略优化方法

| 论文 | 年份 | 贡献 |
|------|------|------|
| TRPO | 2015 | 信任域策略优化 |
| PPO | 2017 | 简化 TRPO，裁剪目标 |
| SAC | 2018 | 最大熵框架，自动温度调节 |
| TD3 | 2018 | 双 Critic + 延迟更新 |
| DDPG | 2016 | 连续控制 Actor-Critic |

### 进阶方向

| 论文 | 年份 | 贡献 |
|------|------|------|
| DreamerV3 | 2023 | 通用世界模型 |
| Decision Transformer | 2021 | 序列建模视角的 RL |
| CQL | 2020 | 保守离线 Q 学习 |
| GAIL | 2016 | 生成对抗模仿学习 |
| Eureka | 2023 | LLM 自动设计奖励函数 |


## 主流 RL 库对比

| 库名 | 语言 | 特点 | 适用场景 |
|------|------|------|---------|
| Stable-Baselines3 (SB3) | Python/PyTorch | 接口简洁，文档完善，单机训练 | 研究原型、教学 |
| RLlib (Ray) | Python/PyTorch | 分布式训练，多智能体支持 | 大规模训练、工业部署 |
| CleanRL | Python/PyTorch | 单文件实现，代码透明 | 学习算法细节、快速实验 |
| TorchRL | Python/PyTorch | PyTorch 官方，模块化设计 | 自定义算法开发 |
| Tianshou | Python/PyTorch | 中文社区活跃，API 现代化 | 中文用户、研究 |
| Sample Factory | Python/PyTorch | 极高吞吐量，异步采样 | 大规模仿真训练 |

### 安装示例

```bash
# Stable-Baselines3
pip install stable-baselines3[extra]

# CleanRL
pip install cleanrl

# RLlib
pip install "ray[rllib]"
```


## 仿真环境

### 通用 RL 环境

| 环境 | 类型 | 动作空间 | 特点 |
|------|------|---------|------|
| Gymnasium (Atari) | 像素游戏 | 离散 | 经典基准 |
| Gymnasium (MuJoCo) | 连续控制 | 连续 | 标准运动控制基准 |
| DMControl Suite | 连续控制 | 连续 | DeepMind 维护 |
| Minigrid | 网格世界 | 离散 | 轻量级测试 |
| Procgen | 程序生成游戏 | 离散 | 泛化能力测试 |

### 机器人 RL 环境

| 环境 | 模拟器 | 适用任务 |
|------|--------|---------|
| Isaac Gym / Isaac Lab | PhysX | 高并行机器人训练 |
| MuJoCo Menagerie | MuJoCo | 真实机器人模型集合 |
| PyBullet Envs | Bullet | 运动控制、操作 |
| Robosuite | MuJoCo | 机械臂操作 |
| SAPIEN / ManiSkill | PhysX | 灵巧操作、物体交互 |
| Gymnasium-Robotics | MuJoCo | Fetch、Shadow Hand 任务 |

### 多智能体环境

| 环境 | 类型 | 智能体数 |
|------|------|---------|
| PettingZoo | 通用接口 | 可变 |
| SMAC | StarCraft 微操 | 2-27 |
| MPE | 粒子环境 | 2-10 |
| Google Research Football | 足球 | 2-22 |


## 算法选择指南

```
任务类型判断
├── 离散动作空间
│   ├── 在线学习 → DQN / Rainbow
│   └── 离线数据 → CQL (离散版)
├── 连续动作空间
│   ├── 在线学习
│   │   ├── 仿真采样充裕 → PPO
│   │   ├── 采样受限 → SAC / TD3
│   │   └── 需要世界模型 → Dreamer / MBPO
│   └── 离线数据
│       ├── 数据量大 → CQL / IQL
│       └── 序列决策 → Decision Transformer
├── 多智能体合作
│   ├── 值分解 → QMIX / MAPPO
│   └── 通信学习 → CommNet / TarMAC
└── 模仿学习
    ├── 有奖励信号 → GAIL
    └── 纯行为克隆 → BC / DAgger
```


## 符号约定

本系列文章采用如下统一符号：

| 符号 | 含义 |
|------|------|
| \(s, s'\) | 当前状态、下一状态 |
| \(a\) | 动作 |
| \(r\) | 即时奖励 |
| \(\gamma\) | 折扣因子 |
| \(\pi(a \mid s)\) | 策略（给定状态的动作分布） |
| \(V^\pi(s)\) | 状态价值函数 |
| \(Q^\pi(s, a)\) | 动作价值函数 |
| \(A^\pi(s, a)\) | 优势函数 \(Q^\pi - V^\pi\) |
| \(\theta\) | 策略网络参数 |
| \(\phi\) | 价值网络参数 |
| \(\tau\) | 轨迹 \((s_0, a_0, r_0, s_1, \ldots)\) |
| \(\mathcal{D}\) | 经验回放缓冲区 / 数据集 |
| \(\alpha\) | 温度参数（SAC） |
| \(\epsilon\) | 裁剪范围（PPO）或探索率 |


## 学习路径推荐

### 初学者

1. 阅读 *Spinning Up in Deep RL* 在线教程
2. 使用 CleanRL 理解单文件算法实现
3. 在 CartPole、LunarLander 等简单环境上实验
4. 用 SB3 快速验证各算法效果

### 进阶研究者

1. 精读 Sutton & Barto 教材的数学推导
2. 复现 PPO / SAC 论文，对比 CleanRL 实现
3. 尝试 MuJoCo / Isaac Gym 机器人任务
4. 探索离线 RL、MARL 等进阶方向

### 工程部署

1. 学习 SB3 的 callback 和日志系统
2. 掌握 ONNX 导出和 TensorRT 优化
3. 熟悉 ROS 2 集成方案
4. 了解安全约束和域随机化技术


## 常用在线资源

| 资源 | 链接 | 说明 |
|------|------|------|
| Spinning Up | <https://spinningup.openai.com/> | OpenAI 入门教程 |
| Lil'Log RL 系列 | <https://lilianweng.github.io/> | 优质博客总结 |
| RL Course (Levine) | <https://rail.eecs.berkeley.edu/deeprlcourse/> | UC Berkeley 课程 |
| Hugging Face RL | <https://huggingface.co/learn/deep-rl-course> | 交互式课程 |
| CleanRL 文档 | <https://docs.cleanrl.dev/> | 算法实现详解 |
| PaperWithCode RL | <https://paperswithcode.com/area/reinforcement-learning> | 最新论文和基准 |


## 参考资料

- Sutton R S, Barto A G. *Reinforcement Learning: An Introduction* (2nd ed). MIT Press, 2018.
- OpenAI Spinning Up: <https://spinningup.openai.com/>
- Stable-Baselines3: <https://stable-baselines3.readthedocs.io/>
- CleanRL: <https://docs.cleanrl.dev/>
- Gymnasium: <https://gymnasium.farama.org/>
