# 状态空间法

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


## 能控性 (Controllability)

（待补充）

## 能观性 (Observability)

（待补充）

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
