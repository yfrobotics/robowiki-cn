# 机器人规划

!!! note "引言"
    规划 (Planning) 是机器人自主行为的核心能力之一。它使机器人能够根据当前状态、环境信息和任务目标，自动生成一系列动作序列以完成指定任务。本页面概述了机器人规划的体系结构、核心概念及各子领域之间的关系。

## 什么是机器人规划

机器人规划是指在给定环境模型、初始状态和目标条件下，自动计算出一条从初始状态到目标状态的可行动作序列的过程。规划问题的核心可以形式化为一个元组：

$$
\mathcal{P} = \langle \mathcal{S}, s_0, \mathcal{G}, \mathcal{A}, T \rangle
$$

其中 \(\mathcal{S}\) 是状态空间，\(s_0\) 是初始状态，\(\mathcal{G} \subseteq \mathcal{S}\) 是目标状态集合，\(\mathcal{A}\) 是动作集合，\(T: \mathcal{S} \times \mathcal{A} \rightarrow \mathcal{S}\) 是状态转移函数。

规划的目标是找到一个动作序列 \(a_1, a_2, \ldots, a_n \in \mathcal{A}\)，使得：

$$
T(\ldots T(T(s_0, a_1), a_2) \ldots, a_n) \in \mathcal{G}
$$


## 规划层次结构

机器人的规划行为自顶向下可以分为以下三个层次，每个层次处理不同抽象程度的问题：

```
┌─────────────────────────────────────────────┐
│           决策规划 (Decision Making)           │
│   "做什么？" — 任务级别的目标选择与行为决策        │
│   时间尺度：秒 ~ 分钟                           │
├─────────────────────────────────────────────┤
│           路径规划 (Path Planning)              │
│   "走哪里？" — 几何空间中的无碰撞路径搜索         │
│   时间尺度：毫秒 ~ 秒                           │
├─────────────────────────────────────────────┤
│           运动规划 (Motion Planning)            │
│   "怎么走？" — 满足动力学约束的轨迹生成           │
│   时间尺度：毫秒                                │
└─────────────────────────────────────────────┘
```

这三个层次形成了一个自顶向下的分解结构：

1. **决策规划** 确定机器人应该执行哪个任务（例如"前往充电站"）
2. **路径规划** 为该任务计算一条几何上可行的路径（例如"经过走廊到达充电站的路径"）
3. **运动规划** 生成具体的关节角度或速度指令，使机器人沿路径平滑运动


## 决策规划 (Decision Making)

决策规划处于规划层次的最顶层，负责回答"做什么"的问题。它根据机器人的当前状态、环境感知和任务目标，选择下一步应该执行的行为或子任务。

常见的决策方法包括：

- **基于规则的系统 (Rule-based Systems)**：使用 if-then 规则做出决策
- **有限状态机 (Finite State Machines, FSMs)**：通过状态和转移建模行为
- **行为树 (Behavior Trees)**：以树形结构组织复杂行为逻辑
- **马尔可夫决策过程 (Markov Decision Processes, MDPs)**：基于概率模型的最优决策
- **贝叶斯推理 (Bayesian Inference)**：在不确定性环境中进行推理和决策

详见 [决策规划](decisionmaking.md) 页面。


## 路径规划 (Path Planning)

路径规划负责在已知或部分已知的环境中，找到一条从起点到终点的无碰撞路径。它主要关注几何可行性，不考虑机器人的动力学约束。

路径规划方法按照策略的不同可以分为以下几类：

- **图搜索算法 (Graph Search)**：A\*、Dijkstra、D\* 等在离散图上搜索最短路径
- **基于采样的方法 (Sampling-based)**：RRT、PRM 等在连续空间中通过随机采样构建路径
- **人工势场法 (Potential Field)**：利用引力和斥力场引导机器人运动
- **Bug 算法 (Bug Algorithms)**：基于简单规则的反应式路径跟踪

详见 [路径规划](pathplanning.md) 页面。


## 运动规划 (Motion Planning)

运动规划在路径规划的基础上，进一步考虑机器人的运动学 (Kinematics) 和动力学 (Dynamics) 约束，生成可执行的轨迹（即带有时间信息的路径）。

运动规划方法按照求解策略可以分为：

- **基于优化的方法 (Optimization-based)**：样条曲线、轨迹优化等
- **基于采样的方法 (Sampling-based)**：RRT、RRT\*、PRM 等
- **动态窗口法 (Dynamic Window Approach, DWA)**：在速度空间中搜索最优指令
- **模型预测控制 (Model Predictive Control, MPC)**：基于预测模型的滚动优化

详见 [运动规划](motionplanning.md) 页面。


## 规划与其他模块的关系

机器人规划不是一个孤立的模块，它与感知、控制等其他子系统紧密耦合：

```
  感知 (Perception)            规划 (Planning)              控制 (Control)
┌──────────────────┐     ┌──────────────────────┐     ┌──────────────────┐
│  传感器数据处理    │     │  决策 → 路径 → 运动   │     │  PID / MPC 等    │
│  环境建模         │ ──→ │  生成动作序列          │ ──→ │  执行器指令生成   │
│  定位与建图       │     │  碰撞检测与规避        │     │  实时跟踪控制     │
└──────────────────┘     └──────────────────────┘     └──────────────────┘
```

- **感知为规划提供输入**：环境地图、障碍物位置、机器人自身定位等
- **规划为控制提供参考**：期望轨迹、速度/加速度曲线等
- **控制为规划提供反馈**：实际执行状态，用于重规划 (Replanning)


## 规划问题的关键挑战

机器人规划面临诸多挑战，以下是几个核心难题：

### 维度灾难 (Curse of Dimensionality)

随着机器人自由度的增加，构型空间 (Configuration Space) 的维度呈指数增长。对于一个 \(n\) 自由度的机器人，其构型空间是 \(n\) 维的，搜索空间的大小为 \(O(r^n)\)，其中 \(r\) 是每个维度的分辨率。

### 动态环境 (Dynamic Environments)

在实际应用中，环境中的障碍物可能是运动的（如行人、其他车辆），这要求规划算法能够快速重新规划，或者预测障碍物的未来轨迹。

### 不确定性 (Uncertainty)

传感器噪声、执行误差和环境变化等因素引入了不确定性，规划算法需要在不完整和不精确的信息下做出鲁棒的决策。

### 实时性 (Real-time Constraints)

许多机器人应用（如自动驾驶、无人机）要求规划算法在极短时间内给出结果，这对算法的计算效率提出了严格要求。


## 经典应用场景

| 应用场景 | 决策规划 | 路径规划 | 运动规划 |
|---------|---------|---------|---------|
| 自动驾驶 (Autonomous Driving) | 行为决策（换道、跟车、停车） | 全局路径搜索 | 轨迹生成与跟踪 |
| 无人机 (UAV) | 任务分配 | 航路规划 | 飞行轨迹优化 |
| 机械臂 (Manipulator) | 抓取策略选择 | 关节空间路径 | 平滑轨迹生成 |
| 移动机器人 (Mobile Robot) | 探索策略 | 导航路径 | 速度与转向控制 |
| 多机器人系统 (Multi-robot) | 任务分配与协调 | 无冲突路径 | 编队控制 |


## 参考文献

1. LaValle, S. M. (2006). *Planning Algorithms*. Cambridge University Press. [在线版本](http://planning.cs.uiuc.edu/)
2. Choset, H., et al. (2005). *Principles of Robot Motion: Theory, Algorithms, and Implementation*. MIT Press.
3. Siciliano, B., et al. (2010). *Robotics: Modelling, Planning and Control*. Springer.
4. Latombe, J. C. (1991). *Robot Motion Planning*. Kluwer Academic Publishers.
5. Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
