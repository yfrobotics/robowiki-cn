# 运动规划

!!! note "引言"
    运动规划 (Motion Planning) 在路径规划的基础上，进一步考虑机器人的运动学 (Kinematics) 和动力学 (Dynamics) 约束，生成一条可实际执行的轨迹 (Trajectory)。与路径规划仅关注几何可行性不同，运动规划需要生成带有时间参数的状态序列，包括位置、速度、加速度等信息，使机器人能够平滑、安全地完成运动任务。

## 路径与轨迹的区别

在运动规划中，路径 (Path) 和轨迹 (Trajectory) 是两个不同的概念：

- **路径 (Path)**：构型空间中的一条几何曲线 \(\tau: [0, 1] \rightarrow \mathcal{C}\)，不包含时间信息
- **轨迹 (Trajectory)**：带有时间参数的路径 \(\sigma: [0, T] \rightarrow \mathcal{C}\)，指定了机器人在每个时刻的状态

轨迹不仅描述"走哪里"，还描述"何时到达"以及"以什么速度到达"。一条可行的轨迹需要同时满足：

$$
\sigma(0) = q_s, \quad \sigma(T) = q_g, \quad \forall t: \sigma(t) \in \mathcal{C}_{free}
$$

$$
\dot{\sigma}(t) \in \mathcal{V}_{feasible}, \quad \ddot{\sigma}(t) \in \mathcal{A}_{feasible}
$$

其中 \(\mathcal{V}_{feasible}\) 和 \(\mathcal{A}_{feasible}\) 分别是速度和加速度的可行集合。


## 构型空间 (Configuration Space)

构型空间 (Configuration Space, C-space) 是运动规划的核心概念。机器人的构型 (Configuration) 是完整描述机器人所有部件位置所需的最小参数集。

### 定义

对于一个 \(n\) 自由度 (Degrees of Freedom, DOF) 的机器人，其构型空间 \(\mathcal{C}\) 是一个 \(n\) 维空间。例如：

- **平面移动机器人**：\(\mathcal{C} = \mathbb{R}^2\)（位置 \(x, y\)），若考虑朝向则 \(\mathcal{C} = \mathbb{R}^2 \times SO(2)\)
- **六轴机械臂**：\(\mathcal{C} = \mathbb{T}^6\)（六个关节角度），其中 \(\mathbb{T}\) 表示圆环（关节角度的周期性）
- **自由飞行刚体**：\(\mathcal{C} = \mathbb{R}^3 \times SO(3)\)（位置和姿态），共 6 个自由度

### 障碍物在构型空间中的表示

工作空间中的障碍物映射到构型空间中形成 C-space 障碍物 \(\mathcal{C}_{obs}\)。自由构型空间定义为：

$$
\mathcal{C}_{free} = \mathcal{C} \setminus \mathcal{C}_{obs}
$$

计算 \(\mathcal{C}_{obs}\) 的显式表达通常非常困难，尤其在高维空间中。因此，实际中多使用碰撞检测 (Collision Detection) 来隐式判断某个构型是否在 \(\mathcal{C}_{free}\) 中。


## 基于优化的方法 (Optimization-based Methods)

基于优化的方法将运动规划表述为一个数学优化问题，在满足约束的条件下最小化某个代价函数。

### 样条曲线 (Spline Curves)

样条曲线通过分段多项式拟合一条平滑轨迹，是运动规划中最常用的轨迹表示方法。

**二次样条 (Quadratic Splines)：** 使用二次多项式拼接各段轨迹，每段的形式为：

$$
q_i(t) = a_i t^2 + b_i t + c_i, \quad t \in [t_i, t_{i+1}]
$$

二次样条保证位置和速度的连续性（\(C^1\) 连续），但加速度在节点处可能不连续。

**三次样条 (Cubic Splines)：** 使用三次多项式拼接各段，每段形式为：

$$
q_i(t) = a_i t^3 + b_i t^2 + c_i t + d_i, \quad t \in [t_i, t_{i+1}]
$$

三次样条保证位置、速度和加速度的连续性（\(C^2\) 连续），是机械臂轨迹规划中最常用的方法。

**连续性条件：** 在节点 \(t_k\) 处需要满足：

$$
q_{k-1}(t_k) = q_k(t_k), \quad \dot{q}_{k-1}(t_k) = \dot{q}_k(t_k), \quad \ddot{q}_{k-1}(t_k) = \ddot{q}_k(t_k)
$$

**五次样条 (Quintic Splines)：** 当需要控制加加速度 (Jerk) 的连续性时，使用五次多项式（\(C^4\) 连续），常用于对平滑性要求极高的场景。

### 贝塞尔曲线 (Bezier Curves)

\(n\) 阶贝塞尔曲线由 \(n+1\) 个控制点 \(P_0, P_1, \ldots, P_n\) 定义：

$$
B(t) = \sum_{i=0}^{n} \binom{n}{i} (1-t)^{n-i} t^i P_i, \quad t \in [0, 1]
$$

贝塞尔曲线的优点是曲线始终在控制点的凸包内，且起点和终点分别在 \(P_0\) 和 \(P_n\) 上，便于控制轨迹形状。

### 轨迹优化 (Trajectory Optimization)

轨迹优化将运动规划表述为一个约束优化问题：

$$
\min_{\sigma} \int_0^T L(\sigma(t), \dot{\sigma}(t), \ddot{\sigma}(t)) \, dt
$$

$$
\text{s.t.} \quad \sigma(0) = q_s, \quad \sigma(T) = q_g
$$

$$
\sigma(t) \in \mathcal{C}_{free}, \quad \dot{\sigma}(t) \in \mathcal{V}_{max}, \quad \ddot{\sigma}(t) \in \mathcal{A}_{max}
$$

其中 \(L\) 是阶段代价函数。常见的代价函数包括：

- **最小时间**：\(L = 1\)，最小化总运动时间 \(T\)
- **最小能量**：\(L = \| \ddot{\sigma}(t) \|^2\)，最小化加速度的平方积分
- **最小加加速度**：\(L = \| \dddot{\sigma}(t) \|^2\)，最小化加加速度的平方积分（更平滑）

**求解方法：**

- **直接法 (Direct Methods)**：将连续优化问题离散化为有限维非线性规划 (NLP) 问题，如直接配置法 (Direct Collocation)、直接打靶法 (Direct Shooting)
- **间接法 (Indirect Methods)**：利用庞特里亚金最大值原理 (Pontryagin's Maximum Principle) 推导最优条件，求解两点边值问题


## 基于采样的运动规划 (Sampling-based Motion Planning)

基于采样的方法通过随机采样探索构型空间，适合高维空间和复杂约束的场景。

### 运动学约束下的 RRT (Kinodynamic RRT)

标准 RRT 不考虑运动学/动力学约束。Kinodynamic RRT 在扩展树的过程中直接考虑系统的运动方程：

$$
\dot{x} = f(x, u)
$$

扩展步骤中，不是简单地向采样点直线移动，而是在控制输入空间中采样一个控制 \(u\)，然后对系统进行前向仿真：

```
Kinodynamic_RRT_Extend(tree, q_rand):
    q_near ← tree 中离 q_rand 最近的节点
    for each 候选控制输入 u:
        q_new ← 从 q_near 出发，施加 u，前向仿真 Δt
        if q_new 无碰撞 且 满足状态约束:
            选择使 q_new 最接近 q_rand 的 u
    tree.add(q_new)
```

### RRT\* 用于运动规划

RRT\* 的渐近最优性同样适用于运动规划场景。在构型空间中，RRT\* 通过重新连线操作不断优化路径，使其代价渐近收敛到最优值。

### PRM 用于运动规划

将 PRM 扩展到运动规划时，需要使用局部规划器 (Local Planner) 来连接两个构型之间的边。局部规划器需要生成满足约束的局部轨迹，而不仅是直线插值。


## 人工势场法 (Potential Field Methods)

人工势场法也可用于运动规划，生成连续的速度指令。在速度层面，机器人的速度指令由势场梯度决定：

$$
\dot{q} = -\nabla U(q)
$$

为了处理动力学约束，可以引入阻尼项和惯性项：

$$
M\ddot{q} + B\dot{q} = -\nabla U(q)
$$

其中 \(M\) 是惯性矩阵，\(B\) 是阻尼矩阵。这种方法也被称为阻抗控制 (Impedance Control) 框架下的运动生成。


## 动态窗口法 (Dynamic Window Approach, DWA)

DWA 是一种适用于差速驱动移动机器人的实时局部运动规划方法，在速度空间 (Velocity Space) 中搜索最优运动指令。

### 基本原理

DWA 在每个控制周期内执行以下步骤：

1. **确定搜索空间**：根据机器人的当前速度和加速度限制，计算下一个控制周期内可达的速度范围（动态窗口）
2. **采样候选速度**：在动态窗口内均匀采样一组候选速度 \((v, \omega)\)
3. **模拟轨迹**：对每个候选速度，预测未来短时间内的运动轨迹
4. **评估与选择**：根据评价函数选择最优速度

### 动态窗口 (Dynamic Window)

可达速度集合由以下约束确定：

$$
V_s = \{(v, \omega) \mid v \in [0, v_{max}], \, |\omega| \leq \omega_{max}\}
$$

$$
V_d = \{(v, \omega) \mid v \in [v_c - \dot{v}_{max} \Delta t, \, v_c + \dot{v}_{max} \Delta t]\}
$$

$$
V_a = \{(v, \omega) \mid v \leq \sqrt{2 \cdot dist(v, \omega) \cdot \dot{v}_{max}}\}
$$

其中 \(V_s\) 是速度限制，\(V_d\) 是动态窗口（由加速度限制决定），\(V_a\) 是安全速度（能在碰撞前停下）。最终的搜索空间为：

$$
V_{search} = V_s \cap V_d \cap V_a
$$

### 评价函数

$$
G(v, \omega) = \alpha \cdot heading(v, \omega) + \beta \cdot dist(v, \omega) + \gamma \cdot velocity(v, \omega)
$$

- \(heading\)：轨迹末端朝向与目标方向的偏差（越小越好）
- \(dist\)：轨迹上离最近障碍物的距离（越大越好）
- \(velocity\)：线速度大小（越大越快到达目标）
- \(\alpha, \beta, \gamma\)：权重系数，用于平衡各项指标


## 模型预测控制用于运动规划 (MPC for Motion Planning)

模型预测控制 (Model Predictive Control, MPC) 通过滚动优化 (Receding Horizon) 策略实时生成运动指令，天然地将规划与控制结合在一起。

### 基本公式

在每个控制时刻，MPC 求解以下有限时域优化问题：

$$
\min_{u_0, \ldots, u_{N-1}} \sum_{k=0}^{N-1} \left[ (x_k - x_{ref})^T Q (x_k - x_{ref}) + u_k^T R \, u_k \right] + (x_N - x_{ref})^T Q_f (x_N - x_{ref})
$$

$$
\text{s.t.} \quad x_{k+1} = f(x_k, u_k)
$$

$$
x_k \in \mathcal{X}, \quad u_k \in \mathcal{U}, \quad x_0 = x_{current}
$$

其中 \(N\) 是预测步数，\(Q\) 和 \(R\) 是状态和输入的权重矩阵，\(Q_f\) 是终端代价矩阵，\(\mathcal{X}\) 和 \(\mathcal{U}\) 是状态和输入的约束集合。

### MPC 用于运动规划的优势

- **显式处理约束**：速度、加速度、避障等约束直接嵌入优化问题
- **预测能力**：通过预测模型前瞻性地规划未来动作
- **反馈机制**：每个控制周期根据最新状态重新规划，天然具有鲁棒性
- **规划与控制统一**：无需将路径跟踪和运动规划分开处理

### 计算挑战

MPC 的主要挑战是计算效率。在每个控制周期内需要求解一个优化问题，对于非线性系统尤其如此。常用的加速方法包括：

- **线性化 MPC**：将非线性模型线性化，转化为二次规划 (QP) 问题
- **实时迭代 (Real-time Iteration, RTI)**：在每个控制周期只执行一步优化迭代
- **GPU 加速**：利用并行计算加速优化求解


## 时间最优路径参数化 (Time-Optimal Path Parameterization, TOPP)

TOPP 是一种将运动规划分解为两步的方法：

1. **路径规划**：首先使用任意方法（如 RRT、A\*）生成一条几何路径
2. **时间参数化**：沿给定路径求解速度曲线，使得运动时间最短，同时满足速度、加速度和力矩约束

### 问题公式

给定路径 \(q(s)\)，其中 \(s \in [0, 1]\) 是路径参数，定义 \(\dot{s}\) 为路径参数的时间导数。轨迹的速度和加速度可以表示为：

$$
\dot{q} = q'(s) \dot{s}, \quad \ddot{q} = q'(s) \ddot{s} + q''(s) \dot{s}^2
$$

TOPP 问题转化为在 \((s, \dot{s})\) 相平面上的最优控制问题，可以通过数值积分高效求解。


## 方法对比

| 方法 | 适用场景 | 最优性 | 实时性 | 约束处理 |
|------|---------|--------|--------|---------|
| 样条曲线 | 已知路径点的平滑插值 | 局部最优 | 很高 | 有限 |
| 轨迹优化 | 通用轨迹生成 | 局部最优 | 中等 | 好 |
| Kinodynamic RRT | 高维复杂约束 | 否 | 中等 | 好 |
| 人工势场 | 简单环境、实时避障 | 否 | 很高 | 有限 |
| DWA | 移动机器人局部规划 | 局部最优 | 很高 | 好 |
| MPC | 通用、需要反馈 | 局部最优 | 中等 | 很好 |
| TOPP | 已知路径的时间优化 | 全局最优 | 高 | 好 |


## 参考文献

1. LaValle, S. M. (2006). *Planning Algorithms*. Cambridge University Press. [在线版本](http://planning.cs.uiuc.edu/)
2. Choset, H., et al. (2005). *Principles of Robot Motion: Theory, Algorithms, and Implementation*. MIT Press.
3. Siciliano, B., et al. (2010). *Robotics: Modelling, Planning and Control*. Springer.
4. Fox, D., Burgard, W. & Thrun, S. (1997). The Dynamic Window Approach to Collision Avoidance. *IEEE Robotics and Automation Magazine*, 4(1), 23-33.
5. Karaman, S. & Frazzoli, E. (2011). Sampling-based Algorithms for Optimal Motion Planning. *International Journal of Robotics Research*, 30(7), 846-894.
6. Betts, J. T. (1998). Survey of Numerical Methods for Trajectory Optimization. *Journal of Guidance, Control, and Dynamics*, 21(2), 193-207.
7. Bobrow, J. E., Dubowsky, S. & Gibson, J. S. (1985). Time-Optimal Control of Robotic Manipulators Along Specified Paths. *International Journal of Robotics Research*, 4(3), 3-17.
8. Rawlings, J. B., Mayne, D. Q. & Diehl, M. (2017). *Model Predictive Control: Theory, Computation, and Design* (2nd ed.). Nob Hill Publishing.
