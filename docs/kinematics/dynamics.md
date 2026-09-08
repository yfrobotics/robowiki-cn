# 机器人动力学

!!! note "引言"
    运动学只描述"怎么动"，动力学（Dynamics）回答"为什么这样动"——它把关节力矩与运动联系起来，引入质量、惯量、重力与摩擦。低速运动时可以忽略动力学，用位置环加减速度前馈就足够；但一旦机器人高速运动、负载变化、或需要力控与柔顺交互，动力学模型就成为必需品。它同时也是强化学习仿真环境、模型预测控制与全身控制的核心。


## 动力学方程

### 标准形式

\(n\) 自由度机器人的运动方程可以写成统一的矩阵形式：

$$M(\mathbf{q}) \ddot{\mathbf{q}} + C(\mathbf{q}, \dot{\mathbf{q}}) \dot{\mathbf{q}} + \mathbf{g}(\mathbf{q}) + \mathbf{f}(\dot{\mathbf{q}}) = \boldsymbol{\tau} + J^T \mathcal{F}_{ext}$$

各项的含义：

| 项 | 维度 | 物理意义 |
|----|------|---------|
| \(M(\mathbf{q})\) | \(n \times n\) | 质量矩阵（惯量矩阵），对称正定 |
| \(C(\mathbf{q},\dot{\mathbf{q}})\dot{\mathbf{q}}\) | \(n\) | 科氏力与离心力 |
| \(\mathbf{g}(\mathbf{q})\) | \(n\) | 重力项 |
| \(\mathbf{f}(\dot{\mathbf{q}})\) | \(n\) | 摩擦力矩 |
| \(\boldsymbol{\tau}\) | \(n\) | 关节驱动力矩 |
| \(J^T\mathcal{F}_{ext}\) | \(n\) | 外部接触力折算到关节的力矩 |

其中科氏力（Coriolis Force）与离心力（Centrifugal Force）都是速度的二次项：\(C\dot{\mathbf{q}}\) 中含 \(\dot{q}_i \dot{q}_j\)（\(i \ne j\)）的是科氏力，含 \(\dot{q}_i^2\) 的是离心力。它们的存在意味着**关节之间存在耦合**：转动一个关节会对其他关节产生力矩扰动。这正是独立关节 PID 控制在高速时精度下降的原因。

### 两类问题

- **逆动力学**（Inverse Dynamics）：已知 \(\mathbf{q}, \dot{\mathbf{q}}, \ddot{\mathbf{q}}\) 求 \(\boldsymbol{\tau}\)。这是"容易"的方向，递推牛顿-欧拉法可在 \(O(n)\) 时间内完成，用于力矩前馈控制。
- **正动力学**（Forward Dynamics）：已知 \(\boldsymbol{\tau}\) 求 \(\ddot{\mathbf{q}} = M^{-1}(\boldsymbol{\tau} - C\dot{\mathbf{q}} - \mathbf{g})\)。这是"困难"的方向，朴素实现需 \(O(n^3)\)，Featherstone 的关节体算法（Articulated Body Algorithm，ABA）可降至 \(O(n)\)。仿真器需要正动力学。

### 重要性质

这些性质是控制器设计与稳定性证明的基础：

**质量矩阵对称正定**：\(M = M^T \succ 0\)，因此总是可逆，正动力学总有唯一解。\(\frac{1}{2}\dot{\mathbf{q}}^T M \dot{\mathbf{q}}\) 即系统动能。

**斜对称性**：适当选取 \(C\) 的形式（Christoffel 符号形式）后，矩阵 \(\dot{M} - 2C\) 是斜对称的：

$$\mathbf{z}^T (\dot{M}(\mathbf{q}) - 2C(\mathbf{q},\dot{\mathbf{q}})) \mathbf{z} = 0, \quad \forall \mathbf{z}$$

这条性质反映了能量守恒（科氏力不做功），是基于 Lyapunov 方法证明 PD 加重力补偿控制器与[自适应控制](../control/adaptive/adaptive.md)器稳定性的关键工具。

**参数线性性**：动力学方程关于惯性参数（质量、质心、惯量张量）是线性的：

$$M\ddot{\mathbf{q}} + C\dot{\mathbf{q}} + \mathbf{g} = Y(\mathbf{q}, \dot{\mathbf{q}}, \ddot{\mathbf{q}}) \, \boldsymbol{\pi}$$

其中 \(Y\) 是回归矩阵（Regressor），\(\boldsymbol{\pi}\) 是惯性参数向量（每个连杆 10 个参数：质量 1 个、一阶矩 3 个、惯量张量 6 个）。这使得参数辨识可以用最小二乘完成，也是自适应控制的基础。


## 拉格朗日方法

### 基本框架

拉格朗日方法（Lagrangian Formulation）从能量出发，适合符号推导与理解结构。定义拉格朗日量为动能减势能：

$$L(\mathbf{q}, \dot{\mathbf{q}}) = T(\mathbf{q}, \dot{\mathbf{q}}) - V(\mathbf{q})$$

运动方程由拉格朗日方程给出：

$$\frac{d}{dt}\left(\frac{\partial L}{\partial \dot{q}_i}\right) - \frac{\partial L}{\partial q_i} = \tau_i$$

系统动能是各连杆动能之和，每个连杆的动能包含平动与转动两部分：

$$T = \frac{1}{2}\sum_{i=1}^{n}\left( m_i \mathbf{v}_{c_i}^T \mathbf{v}_{c_i} + \boldsymbol{\omega}_i^T I_{c_i} \boldsymbol{\omega}_i \right)$$

利用连杆质心的雅可比 \(J_{v_i}, J_{\omega_i}\)（把关节速度映射为该连杆质心的线速度与角速度），可以把动能写成关节速度的二次型，从而直接读出质量矩阵：

$$M(\mathbf{q}) = \sum_{i=1}^{n} \left( m_i J_{v_i}^T J_{v_i} + J_{\omega_i}^T R_i I_{c_i} R_i^T J_{\omega_i} \right)$$

势能则为 \(V(\mathbf{q}) = -\sum_i m_i \mathbf{g}_0^T \mathbf{p}_{c_i}(\mathbf{q})\)，重力项为其梯度 \(\mathbf{g}(\mathbf{q}) = \partial V / \partial \mathbf{q}\)。

科氏与离心项由 Christoffel 符号给出：

$$C_{ij} = \sum_{k=1}^{n} \frac{1}{2}\left( \frac{\partial M_{ij}}{\partial q_k} + \frac{\partial M_{ik}}{\partial q_j} - \frac{\partial M_{jk}}{\partial q_i} \right) \dot{q}_k$$

这一形式保证了上述斜对称性成立。

### 示例：平面两连杆机械臂

设两连杆质量为 \(m_1, m_2\)，长度为 \(l_1, l_2\)，质心在连杆中点，绕质心的转动惯量为 \(I_1, I_2\)。质量矩阵为：

$$M = \begin{bmatrix} \alpha + 2\beta \cos q_2 & \delta + \beta \cos q_2 \\ \delta + \beta \cos q_2 & \delta \end{bmatrix}$$

其中

$$\alpha = I_1 + I_2 + m_1 l_{c1}^2 + m_2(l_1^2 + l_{c2}^2), \quad \beta = m_2 l_1 l_{c2}, \quad \delta = I_2 + m_2 l_{c2}^2$$

科氏与离心项为：

$$C\dot{\mathbf{q}} = \begin{bmatrix} -\beta \sin q_2 \,(2\dot{q}_1 \dot{q}_2 + \dot{q}_2^2) \\ \beta \sin q_2 \, \dot{q}_1^2 \end{bmatrix}$$

第一行中 \(2\dot{q}_1\dot{q}_2\) 是科氏项，\(\dot{q}_2^2\) 是离心项。

这个例子清楚显示了动力学的两个关键特征：**\(M\) 随位形变化**（\(\cos q_2\) 项，手臂伸展时等效惯量最大），以及**关节间存在耦合**（非对角元不为零，\(q_2\) 的运动会对关节 1 产生力矩）。

拉格朗日方法的问题是计算量随自由度增长极快（\(O(n^4)\)），六自由度以上手工推导几乎不可行，通常借助 SymPy 等符号计算工具。


## 牛顿-欧拉方法

### 递推公式

递推牛顿-欧拉法（Recursive Newton-Euler Algorithm，RNEA）对每个连杆逐一应用牛顿第二定律与欧拉方程，通过两次遍历完成逆动力学计算，复杂度仅为 \(O(n)\)。

**外推（Outward Iteration，\(i: 0 \to n-1\)）**：从基座向末端传播运动量。

$$ {}^{i+1}\boldsymbol{\omega}_{i+1} = {}^{i+1}R_i \, {}^{i}\boldsymbol{\omega}_i + \dot{\theta}_{i+1} \, {}^{i+1}\hat{z}_{i+1} $$

$$ {}^{i+1}\dot{\boldsymbol{\omega}}_{i+1} = {}^{i+1}R_i \, {}^{i}\dot{\boldsymbol{\omega}}_i + {}^{i+1}R_i \, {}^{i}\boldsymbol{\omega}_i \times \dot{\theta}_{i+1}\,{}^{i+1}\hat{z}_{i+1} + \ddot{\theta}_{i+1}\,{}^{i+1}\hat{z}_{i+1} $$

$$ {}^{i+1}\mathbf{a}_{i+1} = {}^{i+1}R_i \left( {}^{i}\dot{\boldsymbol{\omega}}_i \times {}^{i}\mathbf{p}_{i+1} + {}^{i}\boldsymbol{\omega}_i \times ({}^{i}\boldsymbol{\omega}_i \times {}^{i}\mathbf{p}_{i+1}) + {}^{i}\mathbf{a}_i \right) $$

由质心加速度得到作用在连杆上的合力与合力矩：

$$\mathbf{F}_i = m_i \mathbf{a}_{c_i}, \qquad \mathbf{N}_i = I_{c_i}\dot{\boldsymbol{\omega}}_i + \boldsymbol{\omega}_i \times I_{c_i}\boldsymbol{\omega}_i$$

**内推（Inward Iteration，\(i: n \to 1\)）**：从末端向基座传播力。

$$ {}^{i}\mathbf{f}_i = {}^{i}R_{i+1}\, {}^{i+1}\mathbf{f}_{i+1} + \mathbf{F}_i $$

$$ {}^{i}\mathbf{n}_i = \mathbf{N}_i + {}^{i}R_{i+1}\,{}^{i+1}\mathbf{n}_{i+1} + {}^{i}\mathbf{p}_{c_i} \times \mathbf{F}_i + {}^{i}\mathbf{p}_{i+1} \times {}^{i}R_{i+1}\,{}^{i+1}\mathbf{f}_{i+1} $$

关节力矩即力矩在关节轴上的投影：

$$\tau_i = {}^{i}\mathbf{n}_i^T \, {}^{i}\hat{z}_i$$

**实现技巧**：把重力加速度作为基座的初始加速度 \(\mathbf{a}_0 = -\mathbf{g}_0\) 代入，就自动包含了重力项，不需要单独计算 \(\mathbf{g}(\mathbf{q})\)。

### 用 RNEA 提取各项

RNEA 直接给出 \(\boldsymbol{\tau}\) 的数值，不显式给出 \(M, C, \mathbf{g}\)。但可以通过特定输入组合把它们提取出来：

- \(\mathbf{g}(\mathbf{q}) = \text{RNEA}(\mathbf{q}, \mathbf{0}, \mathbf{0})\)（含重力）
- \(M(\mathbf{q})\) 的第 \(i\) 列 \(= \text{RNEA}(\mathbf{q}, \mathbf{0}, \mathbf{e}_i)\)（不含重力，\(\mathbf{e}_i\) 为单位向量）
- \(C\dot{\mathbf{q}} = \text{RNEA}(\mathbf{q}, \dot{\mathbf{q}}, \mathbf{0})\)（不含重力）

调用 \(n+2\) 次 RNEA 即可得到完整的动力学各项，这是标准做法（称为 Composite Rigid Body Algorithm 的简化版本）。


## 摩擦模型

刚体动力学假设关节无摩擦，但真实机器人的摩擦力矩可占额定力矩的 10%–30%，尤其在使用谐波减速器的协作机器人上。常用的摩擦模型按复杂度递增：

**库仑加粘滞摩擦**（最常用）：

$$f(\dot{q}) = f_c \operatorname{sgn}(\dot{q}) + f_v \dot{q}$$

参数少、易辨识，缺点是在 \(\dot{q} = 0\) 处不连续，仿真中会引起数值抖振，实现时常用 \(\tanh(\dot{q}/\epsilon)\) 平滑。

**Stribeck 模型**：在低速区加入从静摩擦到库仑摩擦的过渡：

$$f(\dot{q}) = \left(f_c + (f_s - f_c) e^{-(|\dot{q}|/v_s)^2}\right)\operatorname{sgn}(\dot{q}) + f_v \dot{q}$$

能解释低速爬行（Stick-Slip）现象，是精密力控与低速跟踪必须考虑的。

**LuGre 模型**：引入鬃毛（Bristle）内部状态描述预滑移位移，能刻画摩擦滞后与静摩擦的动态特性，用于高精度力控，但参数辨识困难。

工程上还需注意摩擦随温度、润滑状态、磨损而变化——刚开机与运行数小时后的摩擦参数可能相差 20% 以上，因此纯前馈补偿总要配合反馈控制。


## 动力学参数辨识

CAD 模型给出的惯性参数往往不准确（未建模的线缆、减速器、涂层），实际项目通常需要辨识。利用参数线性性：

$$\boldsymbol{\tau} = Y(\mathbf{q},\dot{\mathbf{q}},\ddot{\mathbf{q}})\,\boldsymbol{\pi}$$

沿一条激励轨迹采集 \(N\) 组数据，堆叠成最小二乘问题：

$$\begin{bmatrix} Y_1 \\ \vdots \\ Y_N \end{bmatrix}\boldsymbol{\pi} = \begin{bmatrix} \boldsymbol{\tau}_1 \\ \vdots \\ \boldsymbol{\tau}_N \end{bmatrix} \quad \Rightarrow \quad \hat{\boldsymbol{\pi}} = (Y^TY)^{-1}Y^T\boldsymbol{\tau}$$

实施要点：

- **只有基参数可辨识**。\(10n\) 个惯性参数中有相当一部分对力矩没有影响或只以线性组合出现（如基座连杆绕固定轴的惯量）。应先通过 QR 分解或符号分析确定最小参数集（Base Parameters），否则 \(Y^TY\) 奇异。
- **激励轨迹要优化**。以回归矩阵的条件数为目标，优化有限傅里叶级数轨迹的系数，使各参数都被充分激励。随意选取的轨迹会导致某些参数的估计方差极大。
- **加速度要滤波**。\(\ddot{\mathbf{q}}\) 通常由位置二阶差分得到，噪声极大，必须使用零相位滤波（如 `filtfilt`）以避免引入相位延迟。
- **物理可行性约束**。辨识结果应满足质量为正、惯量张量正定且满足三角不等式。可以把辨识写成带线性矩阵不等式约束的半定规划，保证参数物理可实现。


## 动力学在控制中的应用

### 重力补偿

最简单也最常用的应用：在控制律中加入 \(\hat{\mathbf{g}}(\mathbf{q})\) 抵消重力，使 PD 控制器不必用稳态误差换取重力平衡：

$$\boldsymbol{\tau} = K_p(\mathbf{q}_d - \mathbf{q}) - K_d\dot{\mathbf{q}} + \hat{\mathbf{g}}(\mathbf{q})$$

可以证明（利用斜对称性构造 Lyapunov 函数），只要 \(K_p, K_d\) 正定且重力补偿准确，该控制律对定点镇定是全局渐近稳定的，且**不依赖于 \(M\) 与 \(C\) 的准确性**。这解释了为什么重力补偿是性价比最高的动力学应用——它也是协作机器人"手动拖动示教"功能的实现基础。

### 计算力矩控制

计算力矩控制（Computed Torque Control）用完整动力学模型做反馈线性化：

$$\boldsymbol{\tau} = M(\mathbf{q})\left(\ddot{\mathbf{q}}_d + K_d \dot{\mathbf{e}} + K_p \mathbf{e}\right) + C(\mathbf{q},\dot{\mathbf{q}})\dot{\mathbf{q}} + \mathbf{g}(\mathbf{q})$$

其中 \(\mathbf{e} = \mathbf{q}_d - \mathbf{q}\)。代入动力学方程后，若模型完全准确，闭环误差动力学变为解耦的线性系统：

$$\ddot{\mathbf{e}} + K_d\dot{\mathbf{e}} + K_p\mathbf{e} = \mathbf{0}$$

于是可以用极点配置直接设定每个关节的响应特性。实践中模型误差不可避免，需要配合鲁棒项或[自适应控制](../control/adaptive/adaptive.md)；且该方法要求机器人支持力矩控制接口，多数位置控制型工业机械臂无法使用。

### 操作空间控制

Khatib 的操作空间公式（Operational Space Formulation）把动力学投影到笛卡尔空间：

$$\Lambda(\mathbf{q}) = \left(J M^{-1} J^T\right)^{-1}$$

\(\Lambda\) 称为操作空间惯量矩阵，描述末端在各方向的等效惯量。控制律为：

$$\boldsymbol{\tau} = J^T\left(\Lambda \mathbf{a}_d + \boldsymbol{\mu} + \mathbf{p}\right) + \left(I - J^T\bar{J}^T\right)\boldsymbol{\tau}_0$$

其中 \(\boldsymbol{\mu}, \mathbf{p}\) 分别为操作空间的科氏项与重力项，第二项是零空间力矩，用于冗余机械臂的次要任务。这是阻抗控制与人形机器人全身控制的理论框架，详见 [雅可比矩阵与奇异性](jacobian.md) 中的静力学对偶讨论。


## 代码实现

### 用 Pinocchio 计算

Pinocchio 是目前性能最好的开源刚体动力学库，实现了 RNEA、ABA、CRBA 及其解析导数：

```python
import pinocchio as pin
import numpy as np

model = pin.buildModelFromUrdf('robot.urdf')
data = model.createData()

q = pin.randomConfiguration(model)
v = np.random.randn(model.nv) * 0.5
a = np.random.randn(model.nv) * 0.5

# 逆动力学：RNEA，O(n)
tau = pin.rnea(model, data, q, v, a)

# 质量矩阵：CRBA
M = pin.crba(model, data, q)

# 重力项
g = pin.computeGeneralizedGravity(model, data, q)

# 非线性项 C(q,v)v + g(q)
nle = pin.nonLinearEffects(model, data, q, v)

# 正动力学：ABA，O(n)
a_fd = pin.aba(model, data, q, v, tau)

print('逆动力学-正动力学一致性误差:', np.abs(a_fd - a).max())
print('分解式误差:', np.abs(M @ a + nle - tau).max())

# 验证质量矩阵对称正定
print('对称性误差:', np.abs(M - M.T).max())
print('最小特征值:', np.linalg.eigvalsh(M).min())
```

### 平面两连杆的显式动力学

```python
import numpy as np


class TwoLinkArm:
    def __init__(self, m1=1.0, m2=1.0, l1=0.5, l2=0.4,
                 I1=0.02, I2=0.015, g=9.81):
        self.lc1, self.lc2 = l1 / 2, l2 / 2
        self.m1, self.m2, self.l1, self.g = m1, m2, l1, g
        self.alpha = I1 + I2 + m1 * self.lc1 ** 2 + m2 * (l1 ** 2 + self.lc2 ** 2)
        self.beta = m2 * l1 * self.lc2
        self.delta = I2 + m2 * self.lc2 ** 2

    def mass_matrix(self, q):
        c2 = np.cos(q[1])
        return np.array([
            [self.alpha + 2 * self.beta * c2, self.delta + self.beta * c2],
            [self.delta + self.beta * c2,     self.delta],
        ])

    def coriolis(self, q, dq):
        s2 = np.sin(q[1])
        return np.array([
            -self.beta * s2 * (2 * dq[0] * dq[1] + dq[1] ** 2),
            self.beta * s2 * dq[0] ** 2,
        ])

    def gravity(self, q):
        m1, m2, l1, g = self.m1, self.m2, self.l1, self.g
        return np.array([
            (m1 * self.lc1 + m2 * l1) * g * np.cos(q[0])
            + m2 * self.lc2 * g * np.cos(q[0] + q[1]),
            m2 * self.lc2 * g * np.cos(q[0] + q[1]),
        ])

    def inverse_dynamics(self, q, dq, ddq):
        return self.mass_matrix(q) @ ddq + self.coriolis(q, dq) + self.gravity(q)

    def forward_dynamics(self, q, dq, tau):
        rhs = tau - self.coriolis(q, dq) - self.gravity(q)
        return np.linalg.solve(self.mass_matrix(q), rhs)


if __name__ == '__main__':
    arm = TwoLinkArm()
    q = np.array([0.3, 0.8])
    dq = np.array([0.5, -0.4])
    ddq = np.array([1.0, 0.7])

    tau = arm.inverse_dynamics(q, dq, ddq)
    print('所需关节力矩 (N·m):', np.round(tau, 4))
    print('往返一致性:', np.abs(arm.forward_dynamics(q, dq, tau) - ddq).max())

    # 重力补偿演示：静止时抵消重力所需力矩
    print('重力补偿力矩 (N·m):', np.round(arm.gravity(q), 4))
```


## 仿真器中的动力学

不同[仿真器](../simulation/index.md)在动力学求解上的取舍不同，直接影响 sim-to-real 的效果：

| 仿真器 | 求解器 | 接触模型 | 特点 |
|--------|--------|---------|------|
| [MuJoCo](../simulation/mujoco.md) | 广义坐标 + 凸优化 | 软接触（Soft Contact） | 接触求解稳定、可微，适合强化学习与轨迹优化 |
| [PyBullet](../simulation/pybullet.md) | 广义坐标（Featherstone） | LCP / 顺序冲量 | 开源易用，接触参数需仔细调节 |
| [Gazebo](../simulation/gazebo.md) | ODE / Bullet / DART | 刚性接触 | 与 ROS 集成最好，物理精度依赖后端 |
| Isaac Sim / Isaac Lab | PhysX（GPU） | 刚性接触 | GPU 并行数千环境，适合大规模 RL 训练 |
| Drake | 广义坐标 + 凸接触 | 水弹性（Hydroelastic） | 接触面而非接触点，物理保真度高 |

需要注意的是：**接触动力学是 sim-to-real 差距的主要来源**。刚体动力学本身（无接触时）在各仿真器中高度一致，但摩擦系数、恢复系数、接触刚度等参数难以准确标定，这也是抓取与行走任务的策略难以直接迁移到实机的原因，相关的域随机化方法见 [强化学习在机器人中的部署](../learning/rl-robotics-deployment.md)。


## 参考资料

1. Craig, J. J. (2005). *Introduction to Robotics: Mechanics and Control* (3rd ed.). Pearson Prentice Hall. — 第 6 章推导拉格朗日与牛顿-欧拉方法。
2. Featherstone, R. (2008). *Rigid Body Dynamics Algorithms*. Springer. — RNEA、ABA、CRBA 的权威论述。
3. Siciliano, B., Sciavicco, L., Villani, L. & Oriolo, G. (2010). *Robotics: Modelling, Planning and Control*. Springer. — 第 7、8 章讨论动力学与运动控制。
4. Khatib, O. (1987). A Unified Approach for Motion and Force Control of Robot Manipulators: The Operational Space Formulation. *IEEE Journal of Robotics and Automation*, 3(1), 43-53.
5. Khosla, P. K. & Kanade, T. (1985). Parameter Identification of Robot Dynamics. *IEEE Conference on Decision and Control*, 1754-1760.
6. Gautier, M. & Khalil, W. (1990). Direct Calculation of Minimum Set of Inertial Parameters of Serial Robots. *IEEE Transactions on Robotics and Automation*, 6(3), 368-373.
7. Olsson, H., Åström, K. J., Canudas de Wit, C., Gäfvert, M. & Lischinsky, P. (1998). Friction Models and Friction Compensation. *European Journal of Control*, 4(3), 176-195.
8. Carpentier, J., et al. (2019). The Pinocchio C++ Library. *IEEE/SICE International Symposium on System Integration*.
