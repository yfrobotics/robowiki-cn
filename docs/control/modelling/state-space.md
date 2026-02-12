# 状态空间法

!!! note "引言"
    状态空间法（State-Space Method）是现代控制理论的核心框架，通过引入状态变量（State Variables）来描述系统的内部行为。与传递函数方法仅关注输入输出关系不同，状态空间法能够揭示系统的全部内部特性，并自然地扩展到多输入多输出（MIMO）系统。状态空间法为控制器设计提供了系统化的工具，包括极点配置、LQR最优控制和状态观测器设计等。

状态空间模型在时域中，可以描述 SISO 和 MIMO 系统。

一些优点：

- 数值简单，易于计算机处理
- 传递函数只处理输入/输出行为，而状态空间可以评估系统的内部特征
- MIMO 和系统耦合

控制器设计：

- 全状态反馈（极点配置）
- 观测器/估计器设计：从可用测量值估计系统状态
- 动态输出反馈：将这两者结合起来，对稳定性和性能提供可证明的保证

总的来说，状态空间设计过程比经典控制设计更系统化。

连续时间线性时不变（Linear Time-Invariant, LTI）系统的状态空间模型为：

$$\dot{x}(t) = Ax(t) + Bu(t)$$
$$y(t) = Cx(t) + Du(t)$$

其中：

- \(x(t) \in \mathbb{R}^n\) 为状态向量（State Vector），包含描述系统当前状态所需的最少变量。
- \(u(t) \in \mathbb{R}^m\) 为输入向量（Input Vector）。
- \(y(t) \in \mathbb{R}^p\) 为输出向量（Output Vector）。
- \(A \in \mathbb{R}^{n \times n}\) 为系统矩阵（System Matrix），决定了系统的自由响应特性。
- \(B \in \mathbb{R}^{n \times m}\) 为输入矩阵（Input Matrix），描述输入对状态的影响。
- \(C \in \mathbb{R}^{p \times n}\) 为输出矩阵（Output Matrix），描述状态到输出的映射。
- \(D \in \mathbb{R}^{p \times m}\) 为直接传输矩阵（Feedthrough Matrix），在许多物理系统中为零矩阵。


## 能控性 (Controllability)

能控性是状态空间理论中的基本概念。一个系统是**完全能控的（Completely Controllable）**，当且仅当对于任意初始状态 \(x(0)\) 和任意目标状态 \(x_f\)，都存在有限时间内的控制输入 \(u(t)\) 能够将系统从 \(x(0)\) 转移到 \(x_f\)。

### 能控性矩阵 (Controllability Matrix)

对于线性时不变系统 \(\dot{x} = Ax + Bu\)，能控性可以通过能控性矩阵（Controllability Matrix）来判定：

$$\mathcal{C} = \begin{bmatrix} B & AB & A^2B & \cdots & A^{n-1}B \end{bmatrix}$$

其中 \(n\) 为系统的状态维数。

**判定条件（秩条件）**：系统完全能控的充要条件是能控性矩阵 \(\mathcal{C}\) 的秩等于 \(n\)，即：

$$\text{rank}(\mathcal{C}) = n$$

如果 \(\text{rank}(\mathcal{C}) < n\)，则系统不完全能控，存在某些状态方向无法通过输入来影响。

在MATLAB中可以使用以下命令检查能控性：

```matlab
Co = ctrb(A, B);        % 计算能控性矩阵
rank_Co = rank(Co);      % 计算秩
if rank_Co == size(A, 1)
    disp('系统完全能控');
else
    disp('系统不完全能控');
end
```

### 能控性的物理意义

能控性回答了一个根本性的问题：通过施加适当的输入，我们能否将系统的状态驱动到任意期望位置？如果系统不完全能控，则存在某些"不可达"的状态子空间，无论施加什么样的输入都无法到达。

在实际的机器人系统设计中，能控性分析用于验证：

- 执行器（电机、推进器等）的配置是否足以控制系统的所有自由度。
- 欠驱动系统（Underactuated System）中哪些状态是可控的，哪些不是。


## 能观性 (Observability)

能观性描述了从系统的输出测量值中推断内部状态的能力。一个系统是**完全能观的（Completely Observable）**，当且仅当对于任意初始状态 \(x(0)\)，通过有限时间内的输出 \(y(t)\) 和输入 \(u(t)\) 的测量值，可以唯一确定 \(x(0)\)。

### 能观性矩阵 (Observability Matrix)

对于系统 \(\dot{x} = Ax + Bu\)，\(y = Cx + Du\)，能观性矩阵为：

$$\mathcal{O} = \begin{bmatrix} C \\\\ CA \\\\ CA^2 \\\\ \vdots \\\\ CA^{n-1} \end{bmatrix}$$

**判定条件**：系统完全能观的充要条件是能观性矩阵的秩等于 \(n\)：

$$\text{rank}(\mathcal{O}) = n$$

在MATLAB中：

```matlab
Ob = obsv(A, C);         % 计算能观性矩阵
rank_Ob = rank(Ob);       % 计算秩
if rank_Ob == size(A, 1)
    disp('系统完全能观');
else
    disp('系统不完全能观');
end
```

### 能观性的物理意义

能观性回答了另一个根本性问题：仅通过传感器测量的输出信号，我们能否推断出系统所有内部状态的值？如果系统不完全能观，则存在某些内部状态对输出没有影响，无法通过输出测量来估计。

在机器人系统中，能观性分析帮助确定：

- 传感器的数量和位置是否足以重建系统的完整状态。
- 哪些状态需要通过状态观测器来估计。

### 能控性与能观性的对偶关系

能控性和能观性之间存在优美的对偶关系（Duality）：系统 \((A, B, C)\) 的能控性等价于对偶系统 \((A^T, C^T, B^T)\) 的能观性，反之亦然。这一对偶性使得能控性和能观性的分析方法和结论可以相互转换。


## Kalman分解

如果一个系统既不是完全能控的也不是完全能观的，可以使用Kalman分解（Kalman Decomposition）将其分解为四个子空间：

1. **能控且能观的子空间**：构成系统的传递函数部分，可以完全通过输入输出来控制和观测。
2. **能控但不能观的子空间**：可以通过输入影响，但无法通过输出观测到。
3. **不能控但能观的子空间**：对输出有影响，但无法通过输入改变。
4. **既不能控也不能观的子空间**：对输入和输出均无影响。

Kalman分解通过坐标变换将系统的状态空间分解为这四个正交子空间，帮助设计者理解系统的内在结构。


## 状态观测器 (State Observer)

在实际系统中，并非所有状态变量都可以直接测量。状态观测器（State Observer）通过利用系统模型和可测输出信号来估计不可测的状态变量。

### Luenberger观测器

Luenberger观测器是最基本的状态观测器，其结构为：

$$\dot{\hat{x}}(t) = A\hat{x}(t) + Bu(t) + L(y(t) - C\hat{x}(t))$$

其中 \(\hat{x}(t)\) 为状态估计值，\(L\) 为观测器增益矩阵。

定义估计误差 \(e(t) = x(t) - \hat{x}(t)\)，则误差的动态方程为：

$$\dot{e}(t) = (A - LC)e(t)$$

通过选择适当的观测器增益 \(L\)，使 \((A - LC)\) 的所有特征值具有负实部，即可保证估计误差渐近收敛到零。观测器增益 \(L\) 的设计本质上是一个极点配置问题。

观测器的收敛速度由 \((A - LC)\) 的特征值决定。一般原则是观测器的特征值应比闭环控制器的特征值快2到10倍，以确保状态估计能够快速收敛。

在MATLAB中设计Luenberger观测器：

```matlab
% 期望的观测器极点（比控制器极点快3-5倍）
observer_poles = [-10, -12, -14, -16];
L = place(A', C', observer_poles)';  % 利用对偶性计算观测器增益
```


## 分离原理 (Separation Principle)

分离原理（Separation Principle）是状态空间控制设计中最重要的理论结果之一。它指出：

**对于线性时不变系统，状态反馈控制器和状态观测器可以独立设计，组合后的闭环系统仍然是稳定的。**

具体而言：

- 首先，假设所有状态可测，设计状态反馈增益 \(K\)，使闭环系统 \(\dot{x} = (A-BK)x\) 具有期望的极点。
- 然后，独立设计观测器增益 \(L\)，使观测器误差动态 \(\dot{e} = (A-LC)e\) 快速收敛。
- 最后，将观测器估计的状态代替真实状态输入到控制器中：\(u = -K\hat{x}\)。

组合后的闭环系统特征值恰好是 \((A-BK)\) 的特征值和 \((A-LC)\) 的特征值的并集。这意味着控制器设计和观测器设计不会相互影响，可以分别独立完成，大大简化了设计过程。

分离原理仅对线性系统严格成立。对于非线性系统，控制器和观测器的联合设计通常需要额外的稳定性分析。


## 控制增益计算
![](assets/markdown-img-paste-20170412215404210.png)

对于 SISO 系统，传递函数可以表示为：\(H(s) = [C(sI-A)^{-1}B + D]\) 和 \(H(z) = [C(zI-A)^{-1}B + D]\)。

新输入可以计算为：
$$
u(t) = r(t) - KX = r(t) - \begin{pmatrix}k_1 & k_2 & k_3\end{pmatrix}
\begin{pmatrix} x_1 \\\\ x_2 \\\\ x_3 \end{pmatrix}
$$

这导致了闭环系统的新状态方程：
$$
\frac{dx}{dt} = [A - BK]x - Br(t)
$$



## LQR 控制器的 MATLAB 代码

```matlab
A = sys_d.a;
B = sys_d.b;
C = sys_d.c;
D = sys_d.d;
Q = C'*C            % state-cost matrix
R = 1;              % control-cost
[K] = dlqr(A,B,Q,R) % control gain matrix

Ac = [(A-B*K)];
Bc = [B];
Cc = [C];
Dc = [D];

states = {'x' 'x_dot' 'phi' 'phi_dot'};
inputs = {'r'};
outputs = {'x'; 'phi'};

sys_cl = ss(Ac,Bc,Cc,Dc,Ts,'statename',states,'inputname',inputs,'outputname',outputs);

t = 0:0.01:5;
r =0.2*ones(size(t));
[y,t,x]=lsim(sys_cl,r,t);
[AX,H1,H2] = plotyy(t,y(:,1),t,y(:,2),'plot');
set(get(AX(1),'Ylabel'),'String','cart position (m)')
set(get(AX(2),'Ylabel'),'String','pendulum angle (radians)')
title('Step Response with Digital LQR Control')
```


## 参考资料

1. K. Ogata, *Modern Control Engineering*, 5th Edition, Prentice Hall, 2010.
2. G. F. Franklin, J. D. Powell, and A. Emami-Naeini, *Feedback Control of Dynamic Systems*, 8th Edition, Pearson, 2019.
3. B. Friedland, *Control System Design: An Introduction to State-Space Methods*, Dover Publications, 2005.
4. R. E. Kalman, "A New Approach to Linear Filtering and Prediction Problems," *Transactions of the ASME - Journal of Basic Engineering*, vol. 82, pp. 35-45, 1960.
