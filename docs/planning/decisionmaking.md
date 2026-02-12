# 决策规划

!!! note "引言"
    决策规划 (Decision Making) 是机器人规划体系中最高层次的模块，负责在给定环境状态和任务目标下，选择机器人应当执行的行为或子任务。决策规划需要处理不确定性、多目标权衡以及复杂的环境交互，是实现机器人自主行为的关键。

## 概述

决策规划回答的核心问题是"做什么"。在一个典型的机器人系统中，决策模块接收来自感知系统的环境信息，结合任务目标和内部状态，输出一个高层行为指令（如"前往 A 点"、"抓取物体"、"避让行人"），再由下游的路径规划和运动规划模块执行。

决策方法可以按照是否依赖环境模型进行分类：

- **基于模型的方法 (Model-based)**：如 MDP、POMDP，需要环境的状态转移模型
- **无模型的方法 (Model-free)**：如基于规则的系统、行为树，直接映射感知到动作
- **基于学习的方法 (Learning-based)**：如强化学习，通过与环境交互学习策略


## 基于规则的系统 (Rule-based Systems)

基于规则的系统是最直观的决策方法，使用一组 if-then 规则将感知条件映射到动作输出。

### 基本结构

规则库由一系列产生式规则 (Production Rules) 组成：

```
如果 <条件1> 且 <条件2>  则 <动作A>
如果 <条件3>             则 <动作B>
如果 <条件4> 或 <条件5>  则 <动作C>
```

系统的推理引擎 (Inference Engine) 按照优先级或顺序匹配规则，找到满足条件的规则后执行对应动作。

### 示例：简单避障规则

```
规则1: 如果 前方距离 < 0.5m      则 停止并后退
规则2: 如果 左侧距离 < 右侧距离  则 右转
规则3: 如果 右侧距离 < 左侧距离  则 左转
规则4: 如果 前方无障碍物          则 前进
```

### 优缺点

- **优点**：实现简单、可解释性强、响应速度快
- **缺点**：规则数量随场景复杂度急剧增长；规则之间可能产生冲突；难以处理连续状态空间


## 决策树 (Decision Trees)

决策树 (Decision Tree) 是一种树形结构的决策模型，通过一系列条件判断逐步缩小决策范围，最终到达叶节点得到决策结果。

### 结构

决策树由以下元素组成：

- **根节点 (Root Node)**：起始判断条件
- **内部节点 (Internal Nodes)**：中间判断条件
- **分支 (Branches)**：条件判断的结果
- **叶节点 (Leaf Nodes)**：最终的决策或动作

```
              [电量是否充足？]
              /             \
           是                否
          /                    \
  [是否有任务？]           [前往充电站]
   /          \
 是            否
 /              \
[执行任务]    [待机巡逻]
```

### 信息增益 (Information Gain)

在自动构建决策树时，通常使用信息增益来选择最优分裂属性。对于属性 \(A\)，其信息增益定义为：

$$
IG(S, A) = H(S) - \sum_{v \in \text{Values}(A)} \frac{|S_v|}{|S|} H(S_v)
$$

其中 \(H(S)\) 是数据集 \(S\) 的熵 (Entropy)：

$$
H(S) = -\sum_{i=1}^{c} p_i \log_2 p_i
$$

\(c\) 是类别数量，\(p_i\) 是第 \(i\) 类的概率。

### 优缺点

- **优点**：直观易理解、可以从数据中自动学习、支持多类别决策
- **缺点**：容易过拟合；对连续特征的处理需要离散化；不善于处理时序依赖


## 有限状态机 (Finite State Machines, FSMs)

有限状态机是机器人决策中最广泛使用的方法之一。它将机器人的行为建模为一组离散状态和状态之间的转移。

### 形式化定义

一个有限状态机可以表示为五元组：

$$
\mathcal{M} = \langle Q, \Sigma, \delta, q_0, F \rangle
$$

其中 \(Q\) 是有限状态集合，\(\Sigma\) 是输入字母表（事件集合），\(\delta: Q \times \Sigma \rightarrow Q\) 是状态转移函数，\(q_0 \in Q\) 是初始状态，\(F \subseteq Q\) 是终止状态集合。

### 示例：移动机器人巡逻 FSM

```
          电量低
  [巡逻] ──────→ [前往充电站]
    ↑                  │
    │    充电完成       │ 到达充电站
    │ ←──────── [充电中] ←──┘
    │
    │  发现目标
    └──────→ [跟踪目标]
                  │
                  │ 目标丢失
                  └──→ [巡逻]
```

### 分层有限状态机 (Hierarchical FSM, HFSM)

为了解决状态爆炸问题，分层有限状态机允许将一个状态展开为一个子状态机：

- 高层状态机处理宏观行为（如"执行任务"、"充电"、"待机"）
- 每个高层状态内部包含一个子状态机处理具体行为细节

### 优缺点

- **优点**：概念简单、执行效率高、行为可预测
- **缺点**：状态和转移数量随复杂度急剧增加（状态爆炸）；修改和扩展困难；缺乏模块化


## 行为树 (Behavior Trees)

行为树 (Behavior Tree, BT) 是近年来在机器人和游戏 AI 中广泛采用的决策结构，它克服了 FSM 难以扩展和维护的缺点。

### 节点类型

行为树由以下几种核心节点类型组成：

| 节点类型 | 符号 | 功能描述 |
|---------|------|---------|
| 顺序节点 (Sequence) | → | 依次执行子节点，全部成功则成功，任一失败则失败 |
| 选择节点 (Selector/Fallback) | ? | 依次尝试子节点，任一成功则成功，全部失败则失败 |
| 条件节点 (Condition) | ○ | 检查条件是否满足，返回成功或失败 |
| 动作节点 (Action) | □ | 执行具体动作，返回成功、失败或运行中 |
| 装饰节点 (Decorator) | ◇ | 修改子节点的行为（如重复、取反等） |

### 执行机制

每个节点在每个 Tick 周期返回三种状态之一：

- **成功 (Success)**：节点任务完成
- **失败 (Failure)**：节点任务未能完成
- **运行中 (Running)**：节点任务正在执行

### 示例：巡逻与充电行为树

```
            [?] 根选择节点
           / | \
         /   |   \
       /     |     \
  [→]充电  [→]跟踪  [→]巡逻
  / \       / \       |
 ○   □     ○   □     □
电量  前往  发现  跟踪  巡逻
低?  充电  目标? 目标  路线
```

### 与 FSM 的对比

- **模块化**：行为树的子树可以独立开发和复用
- **可扩展性**：添加新行为只需插入新的子树
- **可读性**：树形结构比状态转移图更易于理解
- **反应性**：每个 Tick 从根节点重新评估，天然支持优先级中断


## 贝叶斯推理 (Bayesian Inference)

贝叶斯推理利用贝叶斯定理在不确定性环境中更新信念 (Belief) 并做出决策。

### 贝叶斯定理 (Bayes' Theorem)

$$
P(H | E) = \frac{P(E | H) \cdot P(H)}{P(E)}
$$

其中 \(P(H|E)\) 是后验概率 (Posterior)，\(P(E|H)\) 是似然 (Likelihood)，\(P(H)\) 是先验概率 (Prior)，\(P(E)\) 是证据 (Evidence)。

### 贝叶斯网络 (Bayesian Networks)

贝叶斯网络是一种有向无环图 (Directed Acyclic Graph, DAG)，用于表示随机变量之间的条件依赖关系。联合概率分布可以分解为：

$$
P(X_1, X_2, \ldots, X_n) = \prod_{i=1}^{n} P(X_i | \text{Parents}(X_i))
$$

### 机器人中的应用

- **目标识别**：根据传感器观测更新对目标类别的信念
- **故障诊断**：根据症状推断故障原因
- **环境分类**：根据多种传感器数据推断环境类型


## 马尔可夫决策过程 (Markov Decision Processes, MDPs)

MDP 是处理序贯决策 (Sequential Decision Making) 问题的标准数学框架，适用于环境完全可观测的情况。

### 形式化定义

一个 MDP 由四元组定义：

$$
\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, T, R \rangle
$$

- \(\mathcal{S}\)：状态空间 (State Space)
- \(\mathcal{A}\)：动作空间 (Action Space)
- \(T(s' | s, a)\)：状态转移概率，即在状态 \(s\) 执行动作 \(a\) 后转移到状态 \(s'\) 的概率
- \(R(s, a)\)：奖励函数 (Reward Function)，执行动作 \(a\) 在状态 \(s\) 获得的即时奖励

### 最优策略

MDP 的目标是找到一个策略 \(\pi: \mathcal{S} \rightarrow \mathcal{A}\)，使得累积折扣奖励最大化：

$$
V^{\pi}(s) = E\left[\sum_{t=0}^{\infty} \gamma^t R(s_t, \pi(s_t)) \mid s_0 = s\right]
$$

其中 \(\gamma \in [0, 1)\) 是折扣因子 (Discount Factor)。最优值函数 \(V^*(s)\) 满足贝尔曼最优方程 (Bellman Optimality Equation)：

$$
V^*(s) = \max_{a \in \mathcal{A}} \left[ R(s, a) + \gamma \sum_{s' \in \mathcal{S}} T(s' | s, a) V^*(s') \right]
$$

### 求解方法

- **值迭代 (Value Iteration)**：迭代更新值函数直到收敛
- **策略迭代 (Policy Iteration)**：交替进行策略评估和策略改进
- **线性规划 (Linear Programming)**：将 MDP 转化为线性规划问题求解


## 部分可观测马尔可夫决策过程 (POMDPs)

在实际机器人系统中，机器人通常无法完全观测环境状态，此时需要使用 POMDP 框架。

### 形式化定义

POMDP 在 MDP 的基础上增加了观测模型：

$$
\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, T, R, \Omega, O \rangle
$$

- \(\Omega\)：观测空间 (Observation Space)
- \(O(o | s', a)\)：观测函数，即执行动作 \(a\) 到达状态 \(s'\) 后获得观测 \(o\) 的概率

### 信念状态 (Belief State)

由于状态不可直接观测，POMDP 维护一个关于当前状态的概率分布，称为信念状态 \(b(s)\)。信念更新公式为：

$$
b'(s') = \eta \cdot O(o | s', a) \sum_{s \in \mathcal{S}} T(s' | s, a) \cdot b(s)
$$

其中 \(\eta\) 是归一化常数。POMDP 在信念空间上等价于一个连续状态的 MDP，可以使用值迭代的变体求解，但计算复杂度远高于标准 MDP。

### 近似求解方法

由于精确求解 POMDP 是 PSPACE-hard 问题，实际应用中常采用近似方法：

- **基于点的值迭代 (Point-based Value Iteration, PBVI)**
- **蒙特卡罗树搜索 (Monte Carlo Tree Search, MCTS)**
- **在线规划 (Online Planning)**：仅在当前信念状态附近求解


## 效用理论 (Utility Theory)

效用理论提供了一个理性决策的数学框架，用于在多个可能的行动方案之间做出选择。

### 期望效用 (Expected Utility)

对于一个动作 \(a\)，其期望效用定义为：

$$
EU(a) = \sum_{s} P(s | a) \cdot U(s)
$$

其中 \(P(s|a)\) 是执行动作 \(a\) 后到达状态 \(s\) 的概率，\(U(s)\) 是状态 \(s\) 的效用值。

### 最大期望效用原则 (Maximum Expected Utility, MEU)

理性决策者应选择期望效用最大的动作：

$$
a^* = \arg\max_{a \in \mathcal{A}} EU(a)
$$

### 多属性效用 (Multi-attribute Utility)

在机器人决策中，通常需要同时考虑多个目标（如安全性、效率、能耗）。多属性效用函数将多个属性组合为一个综合效用值：

$$
U(s) = \sum_{i=1}^{n} w_i \cdot u_i(s)
$$

其中 \(w_i\) 是第 \(i\) 个属性的权重，\(u_i(s)\) 是状态 \(s\) 在第 \(i\) 个属性上的效用。


## 方法对比

| 方法 | 不确定性处理 | 计算复杂度 | 可扩展性 | 典型应用场景 |
|------|------------|-----------|---------|------------|
| 规则系统 | 差 | 低 | 差 | 简单避障 |
| 决策树 | 一般 | 低 | 一般 | 目标分类 |
| FSM | 差 | 低 | 差 | 简单任务切换 |
| 行为树 | 一般 | 低 | 好 | 游戏 AI、服务机器人 |
| 贝叶斯推理 | 好 | 中 | 一般 | 目标识别、故障诊断 |
| MDP | 好 | 高 | 一般 | 导航、资源分配 |
| POMDP | 很好 | 很高 | 差 | 部分可观测任务 |
| 效用理论 | 好 | 中 | 好 | 多目标决策 |


## 参考文献

1. Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
2. Thrun, S., Burgard, W. & Fox, D. (2005). *Probabilistic Robotics*. MIT Press.
3. Colledanchise, M. & Ogren, P. (2018). *Behavior Trees in Robotics and AI: An Introduction*. CRC Press.
4. Kaelbling, L. P., Littman, M. L. & Cassandra, A. R. (1998). Planning and Acting in Partially Observable Stochastic Domains. *Artificial Intelligence*, 101(1-2), 99-134.
5. Puterman, M. L. (1994). *Markov Decision Processes: Discrete Stochastic Dynamic Programming*. Wiley.
6. Koenig, S. & Simmons, R. G. (1998). Xavier: A Robot Navigation Architecture Based on Partially Observable Markov Decision Process Models. *Artificial Intelligence and Mobile Robots*, MIT Press.
