# 强化学习进阶范式

!!! note "引言"
    除了标准的无模型在线强化学习（Model-Free Online RL），研究者提出了多种进阶范式以应对采样效率低、安全性差、多智能体协调等挑战。本文介绍基于模型的 RL、离线 RL、多智能体 RL、分层 RL、逆强化学习以及基础模型与 RL 的结合等前沿方向。


## 基于模型的强化学习

基于模型的 RL（Model-Based RL, MBRL）学习环境的动力学模型 \(\hat{f}(s_{t+1}|s_t, a_t)\)，然后利用该模型进行规划或生成虚拟数据，显著提高采样效率。

### Dreamer

Dreamer 系列（DreamerV1/V2/V3）在学习到的世界模型中进行"想象"训练：

1. **世界模型**：使用循环状态空间模型（RSSM）学习环境动力学
2. **想象训练**：在世界模型中生成虚拟轨迹，在想象空间中训练 Actor-Critic
3. **真实数据收集**：使用当前策略与真实环境交互，收集数据更新世界模型

$$
\text{RSSM:} \quad
\begin{cases}
\text{确定性路径:} & h_t = f_\theta(h_{t-1}, z_{t-1}, a_{t-1}) \\
\text{随机路径:} & z_t \sim q_\theta(z_t | h_t, o_t) \\
\text{先验:} & \hat{z}_t \sim p_\theta(\hat{z}_t | h_t)
\end{cases}
$$

DreamerV3 可以在不调整超参数的情况下跨越多种任务类型（连续控制、Atari、Minecraft）。


### MBPO

基于模型的策略优化（Model-Based Policy Optimization, MBPO）结合了模型学习和无模型算法：

1. 用真实数据训练环境模型的集成（Ensemble）
2. 从真实状态出发，用模型生成短期虚拟轨迹
3. 将真实数据和虚拟数据混合，用 SAC 更新策略

MBPO 控制模型使用的 rollout 长度，通过不确定性估计避免模型误差积累。

| 算法 | 类型 | 采样效率 | 适用场景 |
|------|------|---------|---------|
| PPO | 无模型 | 低 | 仿真环境充足 |
| SAC | 无模型 | 中 | 连续控制 |
| MBPO | 基于模型 | 高 | 真实交互受限 |
| Dreamer | 基于模型 | 高 | 高维观测（图像） |


## 离线强化学习

离线 RL（Offline RL / Batch RL）完全从预先收集的静态数据集中学习策略，无需与环境交互。核心挑战是**分布偏移**：策略可能选择数据集中未覆盖的动作，导致 Q 值的过估计。

### CQL（保守 Q 学习）

CQL（Conservative Q-Learning）通过对未见动作的 Q 值施加惩罚来学习保守的 Q 函数：

$$
\min_Q \; \alpha \cdot \mathbb{E}_{s \sim D}\left[\log \sum_a \exp(Q(s, a)) - \mathbb{E}_{a \sim D}[Q(s, a)]\right] + \frac{1}{2} \mathbb{E}_{(s,a,r,s') \sim D}\left[(Q - \hat{\mathcal{B}}^\pi \hat{Q})^2\right]
$$

第一项使得数据集外动作的 Q 值降低，第二项是标准的 Bellman 误差。


### IQL（隐式 Q 学习）

IQL（Implicit Q-Learning）避免查询数据集外的动作，使用分位数回归估计 V 函数：

$$
L_V(\psi) = \mathbb{E}_{(s,a) \sim D}\left[L_\tau^2(Q_{\hat{\theta}}(s, a) - V_\psi(s))\right]
$$

其中 \(L_\tau^2\) 是不对称的二次损失，\(\tau\) 控制期望分位数。IQL 实现简单，训练稳定。


### Decision Transformer

Decision Transformer 将 RL 建模为序列预测问题，使用 Transformer 架构：

输入序列：\((\hat{R}_1, s_1, a_1, \hat{R}_2, s_2, a_2, \ldots)\)

其中 \(\hat{R}_t\) 是期望的回报-to-go（Returns-to-Go）。推理时通过设定高回报目标来引导生成高质量动作。

```python
# Decision Transformer 推理伪代码
def generate_action(model, states, actions, returns_to_go, timesteps):
    # 构建输入序列
    input_seq = interleave(returns_to_go, states, actions)

    # Transformer 前向传播
    predicted_action = model(input_seq, timesteps)

    return predicted_action[-1]  # 返回最新预测的动作
```


## 多智能体强化学习

多智能体 RL（Multi-Agent RL, MARL）研究多个智能体在共享环境中的学习与协调。

### 训练范式

| 范式 | 缩写 | 描述 |
|------|------|------|
| 集中式训练集中式执行 | CTCE | 全局信息训练和执行，可扩展性差 |
| 集中式训练分布式执行 | CTDE | 训练时使用全局信息，执行时仅用局部观测 |
| 独立学习 | IL | 每个智能体独立训练，简单但不稳定 |

CTDE 是目前最主流的范式。


### MAPPO

MAPPO（Multi-Agent PPO）将 PPO 扩展到多智能体场景：

- 每个智能体有独立的策略网络（基于局部观测）
- Critic 使用全局状态信息（CTDE 范式）
- 参数共享：同类智能体共享网络参数，输入智能体 ID 区分
- 在 StarCraft Multi-Agent Challenge（SMAC）等基准上表现优异


### QMIX

QMIX 用于合作型多智能体任务，将全局 Q 值分解为个体 Q 值的单调混合：

$$
Q_{tot}(s, \mathbf{a}) = f_{mix}(Q_1(o_1, a_1), Q_2(o_2, a_2), \ldots, Q_n(o_n, a_n); s)
$$

混合网络的权重由全局状态 \(s\) 通过超网络生成，并约束为非负以保证单调性。


## 分层强化学习

分层 RL（Hierarchical RL, HRL）将复杂任务分解为多层次的子任务：

### Option 框架

Option \(\langle \mathcal{I}, \pi, \beta \rangle\) 由三部分组成：

- \(\mathcal{I}\)：初始集合（在哪些状态下可以启动该 option）
- \(\pi\)：内部策略（option 执行时的行为策略）
- \(\beta\)：终止条件（option 何时结束）

### Goal-Conditioned RL

高层策略生成子目标（Goal），低层策略学习达成子目标：

1. **高层策略**：每隔 \(k\) 步选择一个子目标 \(g\)
2. **低层策略**：\(\pi_{low}(a|s, g)\) 执行原始动作以达成子目标
3. **内在奖励**：低层策略的奖励基于是否接近子目标

这种结构在长视野、稀疏奖励的导航和操作任务中效果显著。


## 逆强化学习

逆强化学习（Inverse RL, IRL）从专家演示中推断奖励函数，再据此训练策略。

### 最大熵 IRL

假设专家行为遵循最大熵分布：

$$
p(\tau) \propto \exp\left(\sum_t r_\psi(s_t, a_t)\right)
$$

通过最大化专家轨迹的对数似然来学习奖励函数 \(r_\psi\)。

### GAIL

生成对抗模仿学习（Generative Adversarial Imitation Learning, GAIL）使用 GAN 框架：

- **判别器**：区分专家轨迹和策略轨迹
- **生成器（策略）**：学习产生让判别器无法区分的行为

GAIL 无需显式恢复奖励函数，直接学习策略。


## 基础模型与强化学习

大语言模型（Large Language Model, LLM）和视觉-语言模型（Vision-Language Model, VLM）正与 RL 深度融合：

### LLM 作为奖励函数

利用 LLM 的常识知识设计奖励函数：

- 给定任务描述，LLM 生成奖励函数代码
- 人类反馈指导奖励优化
- 代表工作：Eureka（NVIDIA, 2023）

### LLM 作为高层规划器

LLM 分解自然语言指令为子任务序列，RL 策略执行底层动作：

- SayCan：LLM 提议动作，RL 评估可行性
- Inner Monologue：加入视觉和触觉反馈的闭环推理

### VLM 作为表征

视觉-语言预训练模型提供通用视觉表征：

- R3M、MVP 等使用预训练视觉编码器
- 减少视觉 RL 的训练数据需求


## 参考资料

- Hafner D, et al. Mastering Diverse Domains through World Models (DreamerV3). *arXiv:2301.04104*, 2023.
- Janner M, et al. When to Trust Your Model: Model-Based Policy Optimization. *NeurIPS*, 2019.
- Kumar A, et al. Conservative Q-Learning for Offline Reinforcement Learning. *NeurIPS*, 2020.
- Chen L, et al. Decision Transformer: Reinforcement Learning via Sequence Modeling. *NeurIPS*, 2021.
- Yu C, et al. The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games. *NeurIPS*, 2022.
- Ma Y J, et al. Eureka: Human-Level Reward Design via Coding Large Language Models. *arXiv:2310.12931*, 2023.
