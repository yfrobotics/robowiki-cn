# 建模基础

!!! note "引言"
    本页面是[控制系统建模](modelling.md)专题的数学基础部分，涵盖拉普拉斯变换、传递函数推导、方框图代数、信号流图与梅森公式、非线性系统的线性化方法等核心数学工具。这些工具将物理系统的微分方程转化为代数运算，是控制系统分析与设计的基石。


## 拉普拉斯变换

### 定义与性质

拉普拉斯变换（Laplace Transform）将时域中的微分方程转化为复频域中的代数方程，极大简化了线性时不变（Linear Time-Invariant, LTI）系统的分析。

对于因果信号 \(f(t)\)（\(t \geq 0\)），其单边拉普拉斯变换定义为：

$$
F(s) = \mathcal{L}\{f(t)\} = \int_0^{\infty} f(t) e^{-st} \, dt
$$

其中 \(s = \sigma + j\omega\) 是复频率变量。

### 常用变换对

| 时域信号 \(f(t)\) | 拉普拉斯变换 \(F(s)\) |
|-------------------|----------------------|
| 单位冲激 \(\delta(t)\) | \(1\) |
| 单位阶跃 \(u(t)\) | \(1/s\) |
| \(t \cdot u(t)\) | \(1/s^2\) |
| \(e^{-at} u(t)\) | \(1/(s+a)\) |
| \(\sin(\omega t) \cdot u(t)\) | \(\omega/(s^2+\omega^2)\) |
| \(\cos(\omega t) \cdot u(t)\) | \(s/(s^2+\omega^2)\) |
| \(t^n e^{-at} u(t)\) | \(n!/(s+a)^{n+1}\) |

### 关键性质

拉普拉斯变换最重要的性质是**微分性质**——将微分运算转化为乘法：

$$
\mathcal{L}\left\{\frac{df}{dt}\right\} = sF(s) - f(0^-)
$$

$$
\mathcal{L}\left\{\frac{d^2f}{dt^2}\right\} = s^2F(s) - sf(0^-) - f'(0^-)
$$

当初始条件为零时，微分简化为乘以 \(s\)，积分简化为除以 \(s\)。


## 传递函数

### 从微分方程到传递函数

传递函数（Transfer Function）定义为零初始条件下，输出的拉普拉斯变换与输入的拉普拉斯变换之比。

以弹簧-质量-阻尼系统为例：

$$
m\ddot{x} + c\dot{x} + kx = F(t)
$$

对两边取拉普拉斯变换（零初始条件）：

$$
ms^2X(s) + csX(s) + kX(s) = F(s)
$$

传递函数为：

$$
G(s) = \frac{X(s)}{F(s)} = \frac{1}{ms^2 + cs + k}
$$

### 直流电机传递函数推导

直流电机的电气方程和机械方程（零初始条件下的拉普拉斯域）：

$$
(Ls + R)I(s) = V(s) - K_e \Omega(s)
$$

$$
(Js + b)\Omega(s) = K_t I(s)
$$

消去电流 \(I(s)\)，得到从输入电压到输出转速的传递函数：

$$
G(s) = \frac{\Omega(s)}{V(s)} = \frac{K_t}{(Ls + R)(Js + b) + K_t K_e}
$$

当电枢电感 \(L\) 很小可忽略时，简化为一阶系统：

$$
G(s) \approx \frac{K_t / (Rb + K_t K_e)}{(RJ/(Rb + K_t K_e))s + 1} = \frac{K_m}{\tau_m s + 1}
$$

其中 \(K_m\) 为电机增益常数，\(\tau_m\) 为电机时间常数。

### Python 中的传递函数操作

```python
import control
import numpy as np

# 直流电机参数
R = 1.0    # 电枢电阻 (Ω)
L = 0.5    # 电枢电感 (H)
J = 0.01   # 转动惯量 (kg·m²)
b = 0.1    # 粘滞摩擦系数 (N·m·s/rad)
Kt = 0.01  # 力矩常数 (N·m/A)
Ke = 0.01  # 反电动势常数 (V·s/rad)

# 构建传递函数
num = [Kt]
den = [L*J, R*J + L*b, R*b + Kt*Ke]
G = control.tf(num, den)
print(f"传递函数: {G}")

# 极点和零点
poles = control.poles(G)
zeros = control.zeros(G)
print(f"极点: {poles}")
print(f"零点: {zeros}")

# 阶跃响应
t, y = control.step_response(G)
```


## 方框图代数

### 基本连接规则

方框图（Block Diagram）是控制系统中最常用的图形化表示方法。三种基本连接的等效规则：

**串联（级联）**：

$$
G_{eq}(s) = G_1(s) \cdot G_2(s)
$$

**并联**：

$$
G_{eq}(s) = G_1(s) + G_2(s)
$$

**反馈连接**（负反馈）：

$$
G_{eq}(s) = \frac{G(s)}{1 + G(s)H(s)}
$$

其中 \(G(s)\) 为前向通道传递函数，\(H(s)\) 为反馈通道传递函数。当 \(H(s) = 1\) 时为单位反馈系统。

### 方框图化简技巧

| 操作 | 规则 |
|------|------|
| 求和点前移过方框 \(G\) | 在移动支路中插入 \(1/G\) |
| 求和点后移过方框 \(G\) | 在移动支路中插入 \(G\) |
| 引出点前移过方框 \(G\) | 在移动支路中插入 \(G\) |
| 引出点后移过方框 \(G\) | 在移动支路中插入 \(1/G\) |
| 交换相邻求和点 | 直接交换（加法交换律） |


## 信号流图与梅森公式

### 信号流图

信号流图（Signal Flow Graph, SFG）是方框图的替代表示方法，由节点和有向分支组成。每个分支上标注增益（传递函数），信号沿分支方向单向流动。

### 梅森增益公式

梅森公式（Mason's Gain Formula）可直接从信号流图计算系统传递函数，无需逐步化简：

$$
G(s) = \frac{1}{\Delta} \sum_{k=1}^{N} P_k \Delta_k
$$

其中：

- \(P_k\)：第 \(k\) 条前向通路的增益
- \(\Delta\)：图的行列式，\(\Delta = 1 - \sum L_i + \sum L_i L_j - \sum L_i L_j L_k + \cdots\)
- \(L_i\)：第 \(i\) 个独立回路的增益
- \(L_i L_j\)：第 \(i\) 和第 \(j\) 个互不接触回路的增益之积
- \(\Delta_k\)：去掉与第 \(k\) 条前向通路接触的所有回路后的行列式

### 应用示例

考虑一个典型的 PID 控制系统，信号流图有：

- 前向通路：\(P_1 = G_c(s) \cdot G_p(s)\)
- 回路：\(L_1 = -G_c(s) \cdot G_p(s) \cdot H(s)\)
- 行列式：\(\Delta = 1 - L_1 = 1 + G_c(s) G_p(s) H(s)\)
- \(\Delta_1 = 1\)（前向通路与唯一回路接触）

传递函数：

$$
G(s) = \frac{P_1 \Delta_1}{\Delta} = \frac{G_c(s) G_p(s)}{1 + G_c(s) G_p(s) H(s)}
$$

与反馈公式一致。梅森公式的优势在于处理复杂多回路系统时无需化简方框图。


## 非线性系统线性化

### 为什么需要线性化

大多数机器人系统本质上是非线性的（关节动力学、空气动力学、接触力等），但线性控制理论提供了成熟的分析和设计工具。线性化（Linearization）在平衡点附近用线性模型近似非线性系统，使得线性控制方法可以应用。

### 雅可比线性化

对于非线性状态方程：

$$
\dot{\mathbf{x}} = \mathbf{f}(\mathbf{x}, \mathbf{u})
$$

在平衡点 \((\mathbf{x}_0, \mathbf{u}_0)\) 处（满足 \(\mathbf{f}(\mathbf{x}_0, \mathbf{u}_0) = \mathbf{0}\)），通过泰勒展开取一阶项得到线性化模型：

$$
\delta\dot{\mathbf{x}} = A \, \delta\mathbf{x} + B \, \delta\mathbf{u}
$$

其中偏差变量 \(\delta\mathbf{x} = \mathbf{x} - \mathbf{x}_0\)，\(\delta\mathbf{u} = \mathbf{u} - \mathbf{u}_0\)，系统矩阵和输入矩阵为雅可比矩阵：

$$
A = \frac{\partial \mathbf{f}}{\partial \mathbf{x}}\bigg|_{(\mathbf{x}_0, \mathbf{u}_0)}, \quad B = \frac{\partial \mathbf{f}}{\partial \mathbf{u}}\bigg|_{(\mathbf{x}_0, \mathbf{u}_0)}
$$

### 倒立摆线性化示例

倒立摆的非线性运动方程（忽略摩擦）：

$$
(M + m)\ddot{x} + ml\ddot{\theta}\cos\theta - ml\dot{\theta}^2\sin\theta = F
$$

$$
l\ddot{\theta} + \ddot{x}\cos\theta - g\sin\theta = 0
$$

选择状态向量 \(\mathbf{x} = [x, \dot{x}, \theta, \dot{\theta}]^T\)，在上平衡点 \(\theta_0 = 0\) 处线性化（\(\sin\theta \approx \theta\)，\(\cos\theta \approx 1\)，\(\dot{\theta}^2 \approx 0\)）：

$$
A = \begin{bmatrix} 0 & 1 & 0 & 0 \\ 0 & 0 & -mg/M & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & (M+m)g/(Ml) & 0 \end{bmatrix}, \quad B = \begin{bmatrix} 0 \\ 1/M \\ 0 \\ -1/(Ml) \end{bmatrix}
$$

```python
import numpy as np
import control

# 倒立摆参数
M = 0.5   # 小车质量 (kg)
m = 0.2   # 摆杆质量 (kg)
l = 0.3   # 摆杆半长 (m)
g = 9.81  # 重力加速度 (m/s²)

# 上平衡点处的线性化状态空间矩阵
A = np.array([
    [0, 1, 0, 0],
    [0, 0, -m*g/M, 0],
    [0, 0, 0, 1],
    [0, 0, (M+m)*g/(M*l), 0]
])

B = np.array([[0], [1/M], [0], [-1/(M*l)]])
C = np.array([[1, 0, 0, 0],
              [0, 0, 1, 0]])
D = np.zeros((2, 1))

sys = control.ss(A, B, C, D)
print(f"极点: {np.linalg.eigvals(A)}")

# 检查能控性
Wc = control.ctrb(A, B)
rank = np.linalg.matrix_rank(Wc)
print(f"能控性矩阵秩: {rank} (需要 {A.shape[0]} 才完全能控)")
```

### 线性化的局限性

- 仅在平衡点附近有效，偏离过大时精度迅速下降
- 不能捕获极限环、混沌等本质非线性现象
- 对于大范围运动（如机械臂摆动）需要增益调度（Gain Scheduling）或非线性控制方法


## 标准系统传递函数速查

| 系统 | 传递函数 | 阶数 |
|------|---------|------|
| 弹簧-质量-阻尼 | \(\frac{1}{ms^2 + cs + k}\) | 2 |
| 直流电机（电压→转速） | \(\frac{K_t}{(Ls+R)(Js+b)+K_tK_e}\) | 2 |
| 直流电机（简化） | \(\frac{K_m}{\tau_m s + 1}\) | 1 |
| RC 低通滤波器 | \(\frac{1}{RCs + 1}\) | 1 |
| 二阶振荡系统 | \(\frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}\) | 2 |
| 积分环节 | \(\frac{K}{s}\) | — |
| 纯延迟 | \(e^{-\tau s}\) | — |


## 参考资料

1. Ogata, K. (2010). *Modern Control Engineering* (5th ed.). Prentice Hall.
2. Nise, N. S. (2019). *Control Systems Engineering* (8th ed.). Wiley.
3. Franklin, G. F., Powell, J. D., & Emami-Naeini, A. (2019). *Feedback Control of Dynamic Systems* (8th ed.). Pearson.
4. Mason, S. J. (1956). Feedback Theory — Further Properties of Signal Flow Graphs. *Proceedings of the IRE*, 44(7), 920–926.
5. python-control 库文档：https://python-control.readthedocs.io/
