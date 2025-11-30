# 控制系统建模

系统可以用以下方式之一来描述：

- 微分方程 (Differential equation)
- 差分方程 (Difference Equation)
- 传递函数 (Transfer Function)
- 状态空间 (State Space)


## 微分方程 (Differential Equation)
\begin{aligned}
\ddot{x} + \dot{x} &= ax + b \\\\
y &= x
\end{aligned}


## 差分方程 (Difference Equation)
$$
x_{t} = ax_{t-1} + b
$$


## 传递函数 (Transfer Function)
- 多项式形式 (Polynomial)
$$
Y(s) = \frac{a_m s^m + ... + a_0}{b_n s^n + ... + b_0}
$$

- 零极点形式 (Poles and Zeros)
$$
Y(s) = K \frac{(s-z_m)...(s-z_0)}{(s - p_n) ... (s-p_0)}
$$


## 状态空间 (State Space)
![](assets/markdown-img-paste-2017041221520164.png)

$$
\begin{align}
\dot{x}(t) &= Ax(t) + Bu(t) \\\\
y(t) &= Cx(t) + Du(t)
\end{align}
$$


- **x** 为状态向量
- **A** 为系统矩阵（方阵，对于 N 个状态为 N x N）
- **B** 为输入矩阵（对于单输入单输出 (SISO) 系统为 N 行 x 1 列）
- **C** 为输出矩阵（对于 SISO 系统为 1 行 x N 列）
- **D** 为前馈矩阵（对于 SISO 系统为 1 x 1）

- **(*)** 传递函数的极点就是系统矩阵 **A** 的特征值


### Matlab 代码
`sys = ss(a,b,c,d)`

`sys = ss(a,b,c,d,Ts)`

`sys_ss = ss(sys)`




## Matlab 函数
### 传递函数 (Transfer Function)
`s = tf('s')`

`feedback(G(s), H(s))`

`G = zpk(sys)`

`G = zpk([1],[1],[1])`

### 零极点 (Poles and Zeros)
查找 SISO 或 MIMO 系统的极点：`pole(sys)`

`pzplot(sys)`

### 状态空间 (State Space)


### 系统分析 (System Analysis)
`linearSystemAnalyzer(G,T1,T2)`

`step(sys)`



## References
1. Control Tutorials, [Inverted Pendulum: Digital Controller Design](http://ctms.engin.umich.edu/CTMS/index.php?example=InvertedPendulum&section=ControlDigital), University of Michigan
