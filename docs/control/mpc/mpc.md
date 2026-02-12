# MPC控制器

!!! note "引言"
    模型预测控制（Model Predictive Control, MPC）是一类基于在线优化的先进控制方法。MPC在每个采样时刻利用系统的动态模型预测未来行为，并通过求解优化问题确定最优控制序列。MPC天然支持多变量系统和约束处理，是工业过程控制和自主系统领域中应用最广泛的高级控制策略之一。

![](assets/markdown-img-paste-20170413120952608.png)

## 概述 (Generals)
- MPC：使用过程变量对操纵变量变化的响应的显式动态模型进行调节控制。
- \(obj = min(\sum (y - y_{trajectory})^2)\)
- 基本版本使用线性模型。也可以是经验模型。
- 相对于 PID 的优点：
    - 长时间常数、显著的时间延迟、反向响应等
    - 多变量
    - 对过程变量有约束

- 一般特征：
    - 目标（设定点）由实时优化软件根据当前运行和经济条件选择
    - 最小化预测未来输出与特定参考轨迹到新目标之间的偏差平方
    - 处理 MIMO 控制问题
    - 可以包括对受控变量和操纵变量的等式和不等式约束
    - 在每个采样时刻求解非线性规划问题
    - 通过比较实际受控变量与模型预测来估计扰动
    - 通常实现 \(M\) 个计算移动中的第一个移动

- MPC 目标轨迹
![](assets/markdown-img-paste-20170413121028412.png)
    - 类型：
        - 漏斗轨迹 (Funnel Trajectory)
        - 纯死区 (Pure dead-band)
        - 参考轨迹 (Reference Trajectory)
    - 近期与长期目标
    - 响应目标
    - 响应速度

- 二次目标函数
  $$\sum_{i=0}^p x_i^TQx_i + \sum_{i=0}^{m-1} u_i^TRu_i$$


![](assets/markdown-img-paste-20170413121003374.png)

## 详细内容 (Details)
- 脉冲和阶跃响应模型以及预测方程
- 状态估计的使用
- 优化
- 无限时域 MPC 和稳定性
- 非线性模型的使用

![](assets/markdown-img-paste-20170413124746649.png)


### 线性MPC公式

线性MPC是最常见的MPC形式，使用线性状态空间模型进行预测。给定离散时间线性系统：

$$x_{k+1} = Ax_k + Bu_k$$
$$y_k = Cx_k$$

MPC在每个时间步求解以下优化问题：

$$\min_{u_0, u_1, \ldots, u_{m-1}} J = \sum_{i=0}^{p} \|y_{k+i|k} - r_{k+i}\|_Q^2 + \sum_{i=0}^{m-1} \|\Delta u_{k+i|k}\|_R^2$$

其中：

- \(p\) 为预测时域（Prediction Horizon），定义模型向前预测的步数。
- \(m\) 为控制时域（Control Horizon），定义优化变量的个数，通常 \(m \leq p\)。
- \(Q\) 为输出误差权重矩阵，\(R\) 为控制增量权重矩阵。
- \(r\) 为参考轨迹（Reference Trajectory）。
- \(\Delta u = u_k - u_{k-1}\) 为控制增量。

预测时域和控制时域的选择是MPC设计中的关键参数。预测时域过短可能导致闭环不稳定；控制时域过长会增加计算负担。


### 约束处理

MPC的核心优势之一是能够显式处理系统约束。常见的约束类型包括：

- **输入约束（Input Constraints）**：执行器的物理限制，如电机的最大力矩、阀门的开度范围。

$$u_{min} \leq u_k \leq u_{max}$$

- **输入增量约束（Input Rate Constraints）**：限制控制量的变化速率，防止执行器的剧烈运动。

$$\Delta u_{min} \leq \Delta u_k \leq \Delta u_{max}$$

- **输出约束（Output Constraints）**：系统输出的安全范围，如温度上限、位置边界。

$$y_{min} \leq y_k \leq y_{max}$$

在线性MPC中，这些约束使得优化问题成为一个二次规划（Quadratic Programming, QP）问题，可以使用高效的QP求解器进行求解。


### 滚动时域原理 (Receding Horizon Principle)

滚动时域（也称为移动时域，Receding Horizon）是MPC的核心工作原理：

1. 在当前时刻 \(k\)，基于当前状态测量值（或估计值），求解一个有限时域的优化问题，得到未来 \(m\) 步的最优控制序列 \(\{u_k^*, u_{k+1}^*, \ldots, u_{k+m-1}^*\}\)。
2. 仅执行该控制序列的**第一个元素** \(u_k^*\)，将其施加到系统上。
3. 在下一个采样时刻 \(k+1\)，获取新的状态测量值，重复步骤1和2。

滚动时域策略的核心思想是：通过在每个时间步重新优化并结合最新的状态反馈，补偿模型误差和外部扰动的影响，从而实现闭环反馈控制。


### 计算考量

MPC的在线计算是其工程实现中的核心挑战。每个采样周期内，控制器必须完成从状态测量到优化求解再到控制输出的全部计算。

影响计算量的关键因素：

- **预测时域和控制时域的长度**：更长的时域意味着更多的优化变量和约束，计算量增大。
- **模型复杂度**：非线性模型的预测比线性模型复杂得多。
- **约束数量**：更多的约束增加了QP问题的规模。
- **采样周期**：更高的控制频率要求更快的求解速度。

对于线性MPC，求解QP问题的典型时间在微秒到毫秒级别，适合大多数工业控制场景。对于非线性MPC（Nonlinear MPC, NMPC），需要求解非线性规划（Nonlinear Programming, NLP）问题，计算量显著增大。常用的加速策略包括：

- **实时迭代（Real-Time Iteration, RTI）**：每个采样周期仅执行一次SQP（序列二次规划）迭代，用计算精度换取求解速度。
- **显式MPC（Explicit MPC）**：对于小规模问题，预先离线计算所有可能状态下的最优控制律，在线时仅需查表。
- **并行计算**：利用GPU或FPGA加速矩阵运算和优化求解。


## 在机器人中的应用

MPC在机器人领域有广泛的应用，以下是几个典型场景：

### 自动驾驶

在自动驾驶中，MPC被广泛用于横向和纵向控制。控制器根据车辆动力学模型预测未来轨迹，在满足车道边界、舒适性和安全距离等约束的条件下跟踪参考路径。非线性MPC可以在高速和紧急避障场景中提供更准确的预测。

### 无人机控制

MPC适合多旋翼无人机的轨迹跟踪和避障控制。无人机的多输入多输出（MIMO）特性和飞行包络约束（如最大倾斜角、推力限制）都可以在MPC框架中自然处理。

### 足式机器人

MPC被用于四足和双足机器人的步态规划和运动控制。控制器在预测时域内优化足端接触力和关节力矩，同时满足摩擦锥约束和动力学约束。

### 机械臂

在工业机器人和协作机器人中，MPC可以在笛卡尔空间或关节空间进行轨迹规划和跟踪，同时处理关节限位、速度限制和碰撞避免等约束。


## 软件工具

以下是常用的MPC开发和仿真工具：

- **ACADO Toolkit**：开源的自动控制和动态优化工具包，支持快速生成嵌入式MPC代码。
- **CasADi**：开源的符号计算框架，支持自动微分，广泛用于非线性MPC的建模和求解。
- **OSQP**：高效的开源QP求解器，适合嵌入式线性MPC应用。
- **MATLAB MPC Toolbox**：MathWorks提供的商业MPC工具箱，集成了设计、仿真和代码生成功能。
- **do-mpc**：基于Python和CasADi的开源MPC框架，适合快速原型开发和学术研究。
- **FORCESPRO**：Embotech公司的商业嵌入式优化求解器，专为实时MPC设计。


## 参考资料

1. J. M. Maciejowski, *Predictive Control with Constraints*, Prentice Hall, 2002.
2. J. B. Rawlings, D. Q. Mayne, and M. M. Diehl, *Model Predictive Control: Theory, Computation, and Design*, 2nd Edition, Nob Hill Publishing, 2017.
3. L. Grüne and J. Pannek, *Nonlinear Model Predictive Control: Theory and Algorithms*, 2nd Edition, Springer, 2017.
4. [CasADi官方文档](https://web.casadi.org/)
5. [OSQP求解器](https://osqp.org/)
