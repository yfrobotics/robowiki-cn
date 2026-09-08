# 控制系统

!!! note "引言"
    控制理论（Control Theory）是使机器人按照期望方式运动和行为的数学基础。无论是工业机械臂的精准定位、四旋翼无人机的姿态稳定，还是双足机器人的行走平衡，其核心都依赖控制理论。控制系统负责将传感器测量值与期望目标进行比较，并计算出驱动执行器的指令，从而不断修正系统行为。正是这一"感知—决策—执行"的闭环结构，赋予了机器人应对外部扰动和模型误差的能力。


## 控制理论概述

控制理论（Control Theory）是工程学与数学的交叉学科，研究动态系统（Dynamical System）的行为，以及如何利用反馈（Feedback）来改变和塑造这些行为。其核心目标是设计控制器（Controller），使被控对象（Plant）满足以下典型需求：

- **稳定化（Stabilization）**：使系统从任意初始状态收敛到平衡点。
- **调节（Regulation）**：在外部扰动下，将输出维持在期望值附近。
- **跟踪（Tracking）**：使输出准确跟随随时间变化的参考信号。
- **扰动抑制（Disturbance Rejection）**：削弱外部干扰对输出的影响。

### 基本反馈回路

控制系统最核心的结构是**负反馈回路（Negative Feedback Loop）**，其信号流向如下：

$$
\text{参考值} \rightarrow \bigoplus \rightarrow \text{控制器} \rightarrow \text{执行器} \rightarrow \text{被控对象} \rightarrow \text{输出}
$$

$$
\text{传感器} \leftarrow \text{输出}
$$

具体流程为：

1. **传感器（Sensor）** 测量系统的实际输出（位置、速度、力等）。
2. 将测量值与**参考信号（Reference Signal）** 相减，得到**误差（Error）** \(e = r - y\)。
3. **控制器（Controller）** 依据误差计算控制量 \(u\)。
4. **执行器（Actuator）** 根据控制量对被控对象施加作用（力、力矩、电压等）。
5. 被控对象的**输出（Output）** \(y\) 再次被传感器测量，形成闭合回路。

### 反馈的价值

开环控制（Open-loop Control）仅依赖预先建立的模型，不使用任何测量反馈。这种方式实现简单，但对模型误差和外部扰动极为敏感。反馈的引入带来了三大核心优势：

1. **鲁棒性（Robustness）**：即使模型存在误差，反馈也能通过持续修正使系统趋近期望状态。
2. **抗扰动能力**：外部扰动（如摩擦、风力）引起的偏差可被实时检测并补偿。
3. **性能提升**：合理设计的反馈控制器可以显著加快系统响应速度、减小稳态误差。

然而，反馈也引入了**稳定性（Stability）** 问题：若控制器设计不当，闭环系统可能出现振荡甚至发散。因此，稳定性分析是控制理论的核心议题之一。


## 控制系统分类

### 开环与闭环

**开环系统（Open-loop System）** 不使用输出反馈，控制量完全由参考输入决定。优点是结构简单、无稳定性风险；缺点是对模型误差和扰动无纠正能力，精度依赖模型准确性。例如，微波炉定时加热即为典型的开环控制。

**闭环系统（Closed-loop System）** 利用输出反馈持续修正控制量。优点是对扰动和参数变化具有鲁棒性；缺点是需要传感器、增加了系统复杂度，且存在稳定性设计难题。机器人控制绝大多数属于闭环系统。

### 单输入单输出与多输入多输出

**SISO（Single Input Single Output，单输入单输出）** 系统只有一个控制输入和一个被控输出，分析工具成熟（传递函数、Bode 图等），适用于独立关节控制等简单场景。

**MIMO（Multiple Input Multiple Output，多输入多输出）** 系统具有多个输入和输出，各通道之间存在耦合（Coupling）。机器人动力学通常是高度耦合的 MIMO 系统，需要采用状态空间方法或解耦控制策略。

### 连续时间与离散时间

**连续时间系统（Continuous-time System）** 以微分方程描述，信号在时间上连续变化。经典控制理论（传递函数、根轨迹）主要针对连续时间系统。

**离散时间系统（Discrete-time System）** 以差分方程描述，信号仅在采样时刻取值，适用于数字计算机实现的控制器。采样频率（Sampling Frequency）的选择需满足奈奎斯特定理（Nyquist Theorem），通常要求高于被控带宽的 5～10 倍。

### 线性与非线性

**线性系统（Linear System）** 满足叠加原理（Superposition Principle），可用传递函数或线性状态方程描述，分析工具丰富。

**非线性系统（Nonlinear System）** 不满足叠加原理，典型非线性效应包括摩擦（Friction）、死区（Dead Zone）、饱和（Saturation）及机器人关节的重力/科氏力项。非线性控制设计通常需要反步法（Backstepping）、滑模控制（Sliding Mode Control）等专门方法。

### 时不变与时变

**线性时不变系统（LTI, Linear Time-Invariant System）** 的参数不随时间变化，是经典控制理论的主要研究对象。

**线性时变系统（LTV, Linear Time-Varying System）** 的参数随时间变化，例如消耗燃料后质量减小的火箭，或随关节角度变化的机器人惯性矩阵线性化模型。


## 控制性能指标

评价控制系统优劣需要量化的性能指标，分为时域指标和频域指标两大类。

### 时域性能指标

以阶跃响应（Step Response）为基准，常用时域指标如下：

- **上升时间（Rise Time）\(t_r\)**：输出从稳态值的 10% 上升到 90% 所需的时间，反映系统响应速度。
- **峰值时间（Peak Time）\(t_p\)**：输出达到第一个峰值的时刻。
- **超调量（Overshoot）\(M_p\)**：输出超过稳态值的最大百分比：

$$
M_p = \frac{y_{\max} - y_{\infty}}{y_{\infty}} \times 100\%
$$

- **调节时间（Settling Time）\(t_s\)**：输出进入并保持在稳态值 \(\pm 2\%\)（或 \(\pm 5\%\)）误差带内所需的时间。
- **稳态误差（Steady-state Error）\(e_{ss}\)**：系统达到稳态后参考值与输出的残余偏差。

对于标准二阶系统（Second-order System），其传递函数为：

$$
G(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}
$$

其中自然频率（Natural Frequency）和阻尼比（Damping Ratio）分别为：

$$
\omega_n = \sqrt{\frac{k}{m}}, \quad \zeta = \frac{c}{2\sqrt{km}}
$$

\(m\) 为质量，\(k\) 为刚度，\(c\) 为阻尼系数。超调量与阻尼比的关系为：

$$
M_p = e^{-\pi\zeta / \sqrt{1 - \zeta^2}} \times 100\%, \quad 0 < \zeta < 1
$$

### 频域性能指标

频域指标通过 Bode 图（Bode Plot）或 Nyquist 图分析系统的稳定裕度：

- **增益裕度（Gain Margin）\(G_m\)**：在相位交叉频率（Phase Crossover Frequency）处，系统开环增益距离 0 dB 的余量。增益裕度越大，系统对增益扰动的容忍度越高，一般要求 \(G_m > 6 \text{ dB}\)。
- **相位裕度（Phase Margin）\(\phi_m\)**：在增益交叉频率（Gain Crossover Frequency）处，系统开环相位距离 \(-180°\) 的余量，反映系统对相位滞后的容忍能力，一般要求 \(\phi_m > 30°\)，推荐 \(45°\sim 60°\)。
- **带宽（Bandwidth）\(\omega_{BW}\)**：闭环幅频响应从低频值下降 3 dB 所对应的频率，表征系统能跟踪信号的最高频率上限。


## 经典控制方法

### PID 控制

PID 控制器（Proportional-Integral-Derivative Controller）是工业界最广泛使用的控制方法。其控制律为：

$$
u(t) = K_P e(t) + K_I \int_0^t e(\tau)\, d\tau + K_D \dot{e}(t)
$$

三项各有其作用：

- **比例项（Proportional）** \(K_P e\)：与当前误差成正比，提供即时纠正力，增大 \(K_P\) 可加快响应但可能引发超调和振荡。
- **积分项（Integral）** \(K_I \int e\, dt\)：累积历史误差，消除稳态误差，但积分过强会导致积分饱和（Integral Windup）和响应迟缓。
- **微分项（Derivative）** \(K_D \dot{e}\)：预测误差变化趋势，提供超前阻尼，抑制超调，但对噪声敏感。

在离散域，PID 的数字实现形式为：

$$
u[k] = K_P e[k] + K_I T_s \sum_{i=0}^{k} e[i] + K_D \frac{e[k] - e[k-1]}{T_s}
$$

其中 \(T_s\) 为采样周期。

PID 参数整定（Tuning）方法包括：Ziegler-Nichols 法、Cohen-Coon 法、自动整定（Auto-tuning）以及基于模型的优化方法。

### 根轨迹法

根轨迹法（Root Locus Method）由 Walter Evans 于 1948 年提出，通过绘制开环增益从 0 变化到无穷大时闭环极点（Closed-loop Poles）的轨迹，直观判断系统稳定性和动态特性的变化。设计者可以通过选择合适的增益或加入超前/滞后补偿器（Lead/Lag Compensator）将闭环极点移动到期望位置。

### 频率响应方法

**Bode 图分析**：将开环传递函数的幅频和相频特性分别绘制为频率的函数，直观展示增益裕度和相位裕度，便于串联补偿器的设计。

**Nyquist 判据（Nyquist Criterion）**：通过绘制开环传递函数在频域的 Nyquist 曲线，利用幅角原理判断闭环系统稳定性，特别适用于含纯时延（Pure Time Delay）的系统。


## 现代控制方法

### 状态空间表示

现代控制理论（Modern Control Theory）以状态空间（State Space）为框架描述系统。一般线性时不变系统的状态方程为：

$$
\dot{x}(t) = Ax(t) + Bu(t)
$$

$$
y(t) = Cx(t) + Du(t)
$$

其中：

- \(x \in \mathbb{R}^n\) 为状态向量（State Vector），描述系统的内部状态（如位置、速度）；
- \(u \in \mathbb{R}^m\) 为输入向量（控制量）；
- \(y \in \mathbb{R}^p\) 为输出向量（可测量量）；
- \(A\)（系统矩阵）、\(B\)（输入矩阵）、\(C\)（输出矩阵）、\(D\)（直馈矩阵）为常数矩阵。

状态空间框架自然处理 MIMO 系统，并为极点配置、最优控制等方法提供统一基础。

### 极点配置

极点配置（Pole Placement）通过设计状态反馈增益矩阵 \(K\)，使闭环系统矩阵 \(A - BK\) 的特征值（即闭环极点）恰好位于复平面上的期望位置，从而实现对瞬态响应的直接设计。

前提条件：系统必须是**完全可控的（Completely Controllable）**，即可控性矩阵（Controllability Matrix）满秩：

$$
\mathcal{C} = \begin{bmatrix} B & AB & A^2B & \cdots & A^{n-1}B \end{bmatrix}, \quad \text{rank}(\mathcal{C}) = n
$$

### 线性二次型调节器（LQR）

线性二次型调节器（LQR, Linear Quadratic Regulator）是最优控制（Optimal Control）的经典方法。其目标是寻找最优反馈增益 \(K^*\)，使以下二次型性能指标最小：

$$
J = \int_0^\infty \left( x^T Q x + u^T R u \right) dt
$$

其中 \(Q \geq 0\) 为状态权重矩阵，\(R > 0\) 为控制权重矩阵。设计者通过调整 \(Q\) 和 \(R\) 的比例，在状态偏差（跟踪精度）与控制代价（能量消耗）之间折中。

最优增益通过求解**代数黎卡提方程（Algebraic Riccati Equation, ARE）** 得到：

$$
A^T P + PA - PBR^{-1}B^T P + Q = 0
$$

最优控制律为 \(u^* = -K^* x = -R^{-1}B^T P x\)。LQR 保证闭环系统具有至少 60° 相位裕度和无穷大增益裕度，鲁棒性优良。

### 卡尔曼滤波器

在实际系统中，状态 \(x\) 往往不能被直接测量，需要通过带噪声的输出 \(y\) 进行估计。**卡尔曼滤波器（Kalman Filter, KF）** 是针对线性高斯系统的最优状态估计器，其预测-更新两步迭代为：

**预测步（Prediction）**：

$$
\hat{x}_{k|k-1} = A\hat{x}_{k-1|k-1} + Bu_{k-1}
$$

$$
P_{k|k-1} = AP_{k-1|k-1}A^T + Q_w
$$

**更新步（Update）**：

$$
K_k = P_{k|k-1}C^T\left(CP_{k|k-1}C^T + R_v\right)^{-1}
$$

$$
\hat{x}_{k|k} = \hat{x}_{k|k-1} + K_k\left(y_k - C\hat{x}_{k|k-1}\right)
$$

其中 \(Q_w\) 为过程噪声协方差，\(R_v\) 为测量噪声协方差，\(K_k\) 为卡尔曼增益（Kalman Gain）。

将 LQR 与卡尔曼滤波器结合，即构成**线性二次高斯控制（LQG, Linear Quadratic Gaussian Control）**，是现代控制中全状态最优输出反馈的标准框架。

对于非线性系统，常用**扩展卡尔曼滤波器（EKF, Extended Kalman Filter）** 或**无迹卡尔曼滤波器（UKF, Unscented Kalman Filter）** 进行状态估计。

### 模型预测控制（MPC）

模型预测控制（MPC, Model Predictive Control）也称为滚动时域控制（Receding Horizon Control），其核心思想是：在每个采样时刻，利用当前状态和系统模型，在有限预测时域 \(N\) 步内在线求解一个带约束的优化问题：

$$
\min_{u_0, \ldots, u_{N-1}} \sum_{k=0}^{N-1} \left( x_k^T Q x_k + u_k^T R u_k \right) + x_N^T P_f x_N
$$

$$
\text{subject to:} \quad x_{k+1} = Ax_k + Bu_k, \quad x_k \in \mathcal{X}, \quad u_k \in \mathcal{U}
$$

只将优化序列的第一个控制量施加到系统，然后在下一时刻重新求解（滚动策略）。

MPC 的主要优势：

- **显式处理约束（Constraint Handling）**：可直接将输入饱和、状态边界等物理约束纳入优化问题。
- **多步预测**：利用未来参考轨迹的先验信息，改善跟踪性能。
- **统一框架**：通过调整代价函数，可实现调节、跟踪、经济优化等不同控制目标。

MPC 的主要挑战是在线计算负担较重，对实时性要求高的系统（如高频机器人控制）需要高效的数值优化求解器（如 OSQP、qpOASES 等）。


## 智能控制方法

### 神经网络控制

神经网络控制（Neural Network Control）利用深度神经网络（Deep Neural Network）的强大函数逼近能力，学习复杂非线性系统的动力学或直接学习从传感器到控制量的映射（端到端控制）。主要应用方式包括：

- **神经网络逆模型（Inverse Model）**：学习系统的逆动力学，用于前馈补偿。
- **端到端学习（End-to-End Learning）**：直接从原始感知输入（如图像）学习控制策略。
- **神经网络辅助 MPC**：用神经网络拟合复杂非线性动力学模型，加速 MPC 在线求解。

### 自适应控制

自适应控制（Adaptive Control）的目标是处理系统参数未知或随时间变化的情况，其核心是在线调整控制器参数以适应变化的被控对象。典型方法包括：

- **模型参考自适应控制（MRAC, Model Reference Adaptive Control）**：使实际系统的响应跟踪参考模型的响应，自适应律保证跟踪误差收敛。
- **自校正调节器（Self-tuning Regulator, STR）**：在线辨识系统参数，并实时更新控制器。
- **鲁棒自适应控制（Robust Adaptive Control）**：在自适应律中引入鲁棒修正项，防止参数漂移。

自适应控制在机器人领域的典型应用包括：负载变化时的关节力矩补偿、接触环境刚度未知时的阻抗调节等。

### 强化学习控制

强化学习控制（Reinforcement Learning-based Control）通过让智能体（Agent）与环境交互并接收奖励信号（Reward Signal），自主学习控制策略，无需精确的系统模型。

常用算法包括：

- **策略梯度方法（Policy Gradient）**：如 PPO（Proximal Policy Optimization）、SAC（Soft Actor-Critic），适用于连续动作空间。
- **基于模型的强化学习（Model-based RL）**：学习环境模型以提高采样效率，如 Dyna、MBPO。
- **模仿学习（Imitation Learning）**：从专家示范中学习策略，如行为克隆（Behavior Cloning）和逆强化学习（Inverse Reinforcement Learning）。

强化学习在复杂机器人任务（如灵巧手操作、双足行走）上取得了突破性进展，但其训练样本效率低、真实环境部署的安全性仍是主要挑战。

### 模糊控制

模糊控制（Fuzzy Control）基于模糊逻辑（Fuzzy Logic），将人类专家的定性知识编码为"IF-THEN"规则，适用于难以建立精确数学模型的非线性系统。模糊控制的优点是设计直观、对参数变化不敏感；缺点是规则库的设计依赖经验，且理论分析较困难。


## 机器人控制的特殊挑战

### 非线性动力学

机器人（特别是多关节机械臂和腿式机器人）的动力学是高度非线性且耦合的。以 \(n\) 自由度机械臂为例，其运动方程（Newton-Euler 或 Lagrange 方程）为：

$$
M(q)\ddot{q} + C(q, \dot{q})\dot{q} + G(q) = \tau
$$

其中 \(M(q)\) 为惯性矩阵（Inertia Matrix），\(C(q, \dot{q})\dot{q}\) 为科氏力和离心力项（Coriolis and Centrifugal Terms），\(G(q)\) 为重力项（Gravity Term），\(\tau\) 为关节力矩（Joint Torque）。

由于 \(M(q)\)、\(C(q,\dot{q})\)、\(G(q)\) 均随关节角 \(q\) 变化，将 PID 等线性控制器直接应用于全工作空间时效果往往有限。**计算力矩法（Computed Torque Control）** 通过显式补偿这些非线性项，将系统线性化为双积分器形式，再施加线性控制器。

### 全身控制（Whole Body Control）

全身控制（WBC, Whole Body Control）是腿式机器人（Legged Robot）运动控制的核心框架。腿式机器人面临如下挑战：

- **欠驱动（Underactuation）**：躯干不受直接驱动，需通过腿部接触力间接控制。
- **接触约束（Contact Constraints）**：支撑腿的接触力必须满足摩擦锥（Friction Cone）约束。
- **多任务优先级（Task Hierarchy）**：同时满足平衡、运动、末端执行器目标等多个任务，并按优先级处理冲突。

WBC 通常将上述需求建模为带约束的层次化二次规划（Hierarchical QP）问题，在满足接触约束的前提下优化各级任务目标。

### 阻抗控制与力控制

在机器人与环境发生接触（如装配、抛光、外科手术）时，纯位置控制会因刚性碰撞而损坏工件或机器人。**阻抗控制（Impedance Control）** 将机器人末端执行器与环境的交互建模为弹簧-质量-阻尼系统，通过调整虚拟刚度、阻尼和惯性，在位置控制与力控制之间实现灵活过渡：

$$
M_d \ddot{e} + B_d \dot{e} + K_d e = F_{\text{ext}}
$$

其中 \(e = x - x_d\) 为位置误差，\(F_{\text{ext}}\) 为外部接触力，\(M_d\)、\(B_d\)、\(K_d\) 分别为期望的虚拟惯量、阻尼和刚度。

**导纳控制（Admittance Control）** 是阻抗控制的对偶形式：测量接触力，将其转化为位置修正量，适用于位置控制内环的机器人平台。

**力/力矩控制（Force/Torque Control）** 则直接以接触力为控制目标，需要力/力矩传感器（F/T Sensor）的闭环反馈，常用于精密装配和柔顺操作任务。


## 本章内容导览

本章涵盖机器人控制理论的核心方法，各子页面的主要内容如下：

| 页面 | 主要内容 |
|------|----------|
| [建模（Modelling）](modelling/modelling.md) | 如何建立机器人的数学模型：拉普拉斯变换、传递函数、状态空间建模、系统辨识方法 |
| [PID 控制](pid/pid.md) | 比例-积分-微分控制器的原理、参数整定方法（Ziegler-Nichols、自动整定）、抗积分饱和及实现技巧 |
| [LQR](lqr/lqr.md) | 线性二次型最优控制的推导、黎卡提方程求解、与极点配置的对比、在机械臂和倒立摆上的应用 |
| [MPC](mpc/mpc.md) | 滚动时域优化框架、约束处理、线性/非线性 MPC、实时求解器选型及在移动机器人路径跟踪中的应用 |
| [神经网络控制](nn/nn.md) | 神经网络逼近理论、端到端学习、神经网络与传统控制器的结合（学习残差动力学等） |
| [自适应控制](adaptive/adaptive.md) | MRAC 设计、Lyapunov 稳定性证明、参数投影、在负载变化机械臂上的应用 |

建模章节还包含 [建模基础](modelling/modelling-foundations.md)、[离散化与系统辨识](modelling/modelling-discrete-identification.md)、[状态空间方法](modelling/state-space.md) 与 [建模参考资料](modelling/modelling-full-reference.md) 四个专题页面。

机器人本体的几何与力学模型（正逆运动学、雅可比、动力学方程）不在本章，而在 [机构与运动学](../kinematics/index.md) 章节中讨论。计算力矩控制、阻抗控制等需要动力学模型的方法请同时参阅 [机器人动力学](../kinematics/dynamics.md)。


## 参考资料

1. Ogata, K. (2010). *Modern Control Engineering* (5th ed.). Prentice Hall. — 经典控制与现代控制理论教材。
2. Slotine, J.-J. E., & Li, W. (1991). *Applied Nonlinear Control*. Prentice Hall. — 非线性控制经典著作。
3. Åström, K. J., & Wittenmark, B. (2008). *Adaptive Control* (2nd ed.). Dover Publications. — 自适应控制权威教材。
4. Rawlings, J. B., Mayne, D. Q., & Diehl, M. (2017). *Model Predictive Control: Theory, Computation, and Design*. Nob Hill Publishing. — MPC 系统性参考书。
5. Siciliano, B., Sciavicco, L., Villani, L., & Oriolo, G. (2009). *Robotics: Modelling, Planning and Control*. Springer. — 机器人建模与控制综合教材。
6. How, J., & Frazzoli, E. (2010). [16.30 Feedback Control Systems](https://ocw.mit.edu/courses/aeronautics-and-astronautics/16-30-feedback-control-systems-fall-2010/). MIT OpenCourseWare.
7. Wikipedia. [Control Theory](https://en.wikipedia.org/wiki/Control_theory).
