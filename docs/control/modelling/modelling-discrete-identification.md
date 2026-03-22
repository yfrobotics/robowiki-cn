# 离散系统与系统辨识

!!! note "引言"
    本页面是[控制系统建模](modelling.md)专题的离散系统与系统辨识部分。连续系统模型需要通过离散化才能在数字计算机上实现控制器，而系统辨识则是从实验数据中提取系统模型的实用技术。本文介绍 z 变换基础、常用离散化方法、以及参数辨识和频率响应辨识的完整工作流程。


## z 变换基础

### 定义

z 变换（z-Transform）是离散时间信号和系统分析的数学工具，类似于连续时间系统中的拉普拉斯变换。对离散序列 \(x[k]\)，z 变换定义为：

$$
X(z) = \sum_{k=0}^{\infty} x[k] z^{-k}
$$

z 变换将差分方程转化为代数方程，使离散系统的分析与设计系统化。

### s 域与 z 域的映射关系

连续域的复频率变量 \(s\) 与离散域的 \(z\) 之间的精确映射关系为：

$$
z = e^{sT}
$$

其中 \(T\) 为采样周期。这意味着：

- s 平面的虚轴 \(s = j\omega\) 映射到 z 平面的单位圆 \(|z| = 1\)
- s 平面的左半平面映射到 z 平面单位圆内部
- 稳定系统的极点在 s 平面左半平面，对应 z 平面单位圆内部

### 常用 z 变换对

| 连续信号 | z 变换 |
|---------|--------|
| 单位阶跃 \(u(t)\) | \(\frac{z}{z-1}\) |
| \(e^{-aT}\) 指数 | \(\frac{z}{z-e^{-aT}}\) |
| 单位斜坡 \(t\) | \(\frac{Tz}{(z-1)^2}\) |

### 采样定理

奈奎斯特-香农采样定理（Nyquist-Shannon Sampling Theorem）要求采样频率至少是信号最高频率的两倍：

$$
f_s \geq 2 f_{max}
$$

在控制系统中，经验法则是采样频率取闭环带宽的 10–20 倍，以保证足够的相位裕度和控制性能。


## 离散化方法

### 零阶保持（Zero-Order Hold, ZOH）

ZOH 是最常用的离散化方法，对应实际数模转换器（DAC）的工作方式——在采样间隔内保持输出恒定。

对于连续状态空间模型 \(\dot{x} = Ax + Bu\)，ZOH 离散化结果为：

$$
x[k+1] = \Phi x[k] + \Gamma u[k]
$$

其中：

$$
\Phi = e^{AT}, \quad \Gamma = \left(\int_0^T e^{A\tau} d\tau\right) B
$$

```python
import control
import numpy as np

# 连续系统（直流电机）
A = np.array([[0, 1], [0, -10]])
B = np.array([[0], [20]])
C = np.array([[1, 0]])
D = np.array([[0]])

sys_c = control.ss(A, B, C, D)

# ZOH 离散化，采样周期 0.01s
Ts = 0.01
sys_d = control.c2d(sys_c, Ts, method='zoh')
print(f"离散状态矩阵 Φ:\n{sys_d.A}")
print(f"离散输入矩阵 Γ:\n{sys_d.B}")
```

### 前向欧拉法（Forward Euler）

用前向差分近似微分：\(s \approx \frac{z-1}{T}\)

简单但可能引入不稳定性，仅适用于采样率远高于系统动态的场景。

### 后向欧拉法（Backward Euler）

用后向差分近似微分：\(s \approx \frac{z-1}{Tz}\)

无条件稳定（连续系统稳定则离散化后一定稳定），但精度较低。

### Tustin 变换（双线性变换）

$$
s = \frac{2}{T} \cdot \frac{z-1}{z+1}
$$

Tustin 变换保持频率响应的形状，将 s 平面的虚轴精确映射到 z 平面的单位圆，是 PID 控制器离散化的首选方法。

### 方法对比

| 方法 | 映射公式 | 稳定性保持 | 精度 | 适用场景 |
|------|---------|-----------|------|---------|
| ZOH | 精确计算 | 是 | 高 | 状态空间模型 |
| 前向欧拉 | \(s = \frac{z-1}{T}\) | 否 | 低 | 快速原型验证 |
| 后向欧拉 | \(s = \frac{z-1}{Tz}\) | 是 | 低 | 刚性系统 |
| Tustin | \(s = \frac{2(z-1)}{T(z+1)}\) | 是 | 中高 | PID、滤波器 |

```python
# 不同方法离散化对比
methods = ['zoh', 'foh', 'tustin', 'euler', 'backward_diff']
sys_c = control.tf([20], [1, 10])  # G(s) = 20/(s+10)

for method in ['zoh', 'tustin', 'euler', 'backward_diff']:
    try:
        sys_d = control.c2d(sys_c, 0.01, method=method)
        print(f"{method}: {sys_d}")
    except Exception as e:
        print(f"{method}: {e}")
```


## 系统辨识概述

### 什么是系统辨识

系统辨识（System Identification）是从输入输出实验数据中估计系统数学模型参数的过程。当基于物理定律的第一性原理建模（First-Principles Modeling）困难或不够精确时，系统辨识提供了一种数据驱动的替代方法。

### 辨识流程

```
实验设计 → 数据采集 → 模型结构选择 → 参数估计 → 模型验证
    ↑                                              |
    └──────────── 不满足要求时迭代 ←────────────────┘
```

### 激励信号设计

好的激励信号应覆盖系统的频率范围：

| 信号类型 | 特点 | 适用场景 |
|---------|------|---------|
| 阶跃信号 | 简单，激励有限频率范围 | 快速初步辨识 |
| 伪随机二进制序列（PRBS） | 近似白噪声，频谱平坦 | 线性系统辨识 |
| 扫频信号（Chirp） | 可控频率范围 | 频率响应辨识 |
| 多正弦信号 | 精确控制激励频率 | 频域辨识 |


## 参数辨识方法

### ARX 模型

ARX（Auto-Regressive with eXogenous input）模型是最简单的线性离散时间模型：

$$
y[k] = -a_1 y[k-1] - \cdots - a_{n_a} y[k-n_a] + b_1 u[k-1] + \cdots + b_{n_b} u[k-n_b] + e[k]
$$

写成矩阵形式：\(y[k] = \boldsymbol{\varphi}^T[k] \boldsymbol{\theta} + e[k]\)

其中回归向量 \(\boldsymbol{\varphi}[k] = [-y[k-1], \ldots, -y[k-n_a], u[k-1], \ldots, u[k-n_b]]^T\)，参数向量 \(\boldsymbol{\theta} = [a_1, \ldots, a_{n_a}, b_1, \ldots, b_{n_b}]^T\)。

### 最小二乘法

最小二乘法（Least Squares, LS）估计通过最小化预测误差的平方和求解参数：

$$
\hat{\boldsymbol{\theta}} = (\Phi^T \Phi)^{-1} \Phi^T \mathbf{Y}
$$

其中 \(\Phi\) 是由所有回归向量组成的矩阵，\(\mathbf{Y}\) 是输出向量。

### ARMAX 模型

ARMAX（Auto-Regressive Moving Average with eXogenous input）模型在 ARX 基础上增加了噪声模型：

$$
A(z^{-1})y[k] = B(z^{-1})u[k] + C(z^{-1})e[k]
$$

ARMAX 能更好地处理有色噪声，但参数估计需要迭代优化（如预测误差法）。

### 子空间辨识

子空间辨识（Subspace Identification）方法（如 N4SID、MOESP）直接从数据中估计状态空间模型，不需要预先指定模型阶次。它通过对 Hankel 矩阵进行奇异值分解（SVD）来确定系统阶次并估计状态空间矩阵。


## Python 辨识实战

### 完整辨识工作流

```python
import numpy as np
from scipy import signal
from scipy.optimize import least_squares

# 1. 生成 PRBS 激励信号
def generate_prbs(n_samples, amplitude=1.0, min_period=5):
    """生成伪随机二进制序列"""
    prbs = np.zeros(n_samples)
    val = amplitude
    i = 0
    while i < n_samples:
        duration = np.random.randint(min_period, min_period * 4)
        prbs[i:i+duration] = val
        val = -val
        i += duration
    return prbs[:n_samples]

# 2. 仿真"真实"系统（未知的被辨识对象）
dt = 0.01  # 采样周期 10ms
N = 2000   # 数据点数
t = np.arange(N) * dt
u = generate_prbs(N, amplitude=1.0)

# 真实系统：二阶系统 G(s) = 25 / (s^2 + 4s + 25)
sys_true = signal.cont2discrete(
    ([25], [1, 4, 25]), dt, method='zoh'
)
_, y_clean, _ = signal.dlsim(sys_true, u)
y_clean = y_clean.flatten()

# 添加测量噪声
noise = np.random.normal(0, 0.02, N)
y = y_clean + noise

# 3. ARX 模型辨识（最小二乘法）
def identify_arx(y, u, na, nb):
    """ARX 模型辨识"""
    n = max(na, nb)
    N = len(y)

    # 构建回归矩阵
    Phi = np.zeros((N - n, na + nb))
    Y = y[n:]

    for i in range(N - n):
        for j in range(na):
            Phi[i, j] = -y[n + i - 1 - j]
        for j in range(nb):
            Phi[i, na + j] = u[n + i - 1 - j]

    # 最小二乘求解
    theta = np.linalg.lstsq(Phi, Y, rcond=None)[0]
    y_pred = Phi @ theta

    # 拟合度 (NRMSE)
    fit = 1 - np.linalg.norm(Y - y_pred) / np.linalg.norm(Y - np.mean(Y))
    return theta, fit

# 尝试不同阶次
for na in [1, 2, 3]:
    for nb in [1, 2, 3]:
        theta, fit = identify_arx(y, u, na, nb)
        print(f"ARX({na},{nb}): 拟合度 = {fit:.4f}")

# 4. 选择最佳模型并验证
theta_best, fit_best = identify_arx(y, u, na=2, nb=2)
print(f"\n最佳模型 ARX(2,2): {theta_best}")
print(f"拟合度: {fit_best:.4f}")
```

### 频率响应辨识

```python
from scipy import signal as sig
import numpy as np

def frequency_response_id(u, y, dt, nperseg=256):
    """基于交叉功率谱密度的频率响应辨识"""
    # 计算交叉功率谱和自功率谱
    f, Puu = sig.welch(u, fs=1/dt, nperseg=nperseg)
    f, Pyu = sig.csd(y, u, fs=1/dt, nperseg=nperseg)

    # 频率响应 = 交叉谱 / 自谱
    H = Pyu / Puu

    # 相干函数（衡量线性相关性）
    _, Pyy = sig.welch(y, fs=1/dt, nperseg=nperseg)
    coherence = np.abs(Pyu)**2 / (Puu * Pyy)

    return f, H, coherence

# 使用示例
f, H, coh = frequency_response_id(u, y, dt)

# 仅信任相干性 > 0.8 的频率点
valid = coh > 0.8
print(f"有效频率范围: {f[valid][0]:.1f} - {f[valid][-1]:.1f} Hz")
```


## 模型验证

辨识完成后必须对模型进行验证，常用方法包括：

1. **交叉验证**：使用独立数据集（非辨识数据）评估模型预测精度
2. **残差分析**：检查预测残差是否为白噪声（均值为零、自相关函数在零延迟外接近零）
3. **频域对比**：比较辨识模型和实测数据的波德图
4. **阶跃响应对比**：比较模型和实际系统对阶跃输入的响应

模型拟合度通常用归一化均方根误差（Normalized Root Mean Square Error, NRMSE）衡量：

$$
\text{NRMSE} = 1 - \frac{\|\mathbf{y} - \hat{\mathbf{y}}\|}{\|\mathbf{y} - \bar{y}\|}
$$

拟合度大于 0.8 通常被认为是可接受的。


## 参考资料

1. Ljung, L. (1999). *System Identification: Theory for the User* (2nd ed.). Prentice Hall.
2. Söderström, T., & Stoica, P. (1989). *System Identification*. Prentice Hall.
3. Van Overschee, P., & De Moor, B. (1996). *Subspace Identification for Linear Systems*. Kluwer.
4. Franklin, G. F., Powell, J. D., & Workman, M. L. (1998). *Digital Control of Dynamic Systems* (3rd ed.). Addison-Wesley.
5. SIPPY — Python 系统辨识库：https://github.com/CPCLAB-UNIPI/SIPPY
6. python-control 库文档：https://python-control.readthedocs.io/
