# 重规划与安全性

!!! note "引言"
    在真实环境中，机器人面临动态障碍物、地图不确定性和传感器噪声等挑战，仅凭初始规划往往不足以完成任务。重规划（Replanning）技术使机器人能够在线修正路径，而安全性保障机制则确保机器人在运动过程中不会与障碍物碰撞或违反物理约束。本文介绍常用的重规划算法和安全性验证方法。


## 增量式重规划

### D* Lite 算法

D* Lite 是 Koenig 和 Likhachev（2002）提出的增量式路径搜索算法，当环境发生局部变化时，无需从头搜索，而是复用之前的计算结果进行高效更新。

核心思想：

- 维护从目标到起点的反向搜索
- 当检测到地图变化（如新发现障碍物）时，仅更新受影响的节点
- 使用优先级队列管理待更新节点，通过 rhs 值和 g 值的不一致性触发更新

关键公式：

$$
rhs(s) = \begin{cases} 0 & \text{if } s = s_{goal} \\ \min_{s' \in Succ(s)} (c(s, s') + g(s')) & \text{otherwise} \end{cases}
$$

当 \(g(s) \neq rhs(s)\) 时，节点 \(s\) 被认为不一致，需要更新。

与 A* 相比，D* Lite 在环境频繁变化时效率提升显著，适用于移动机器人在未知环境中的导航。


### 场割规划（Field D*）

Field D* 是 D* Lite 的扩展，允许在栅格节点之间进行插值，生成任意角度的路径，避免了栅格路径的锯齿形问题。


## 任意时间规划

### ARA* 算法

任意时间重加权 A*（Anytime Repairing A*, ARA*）在时间充裕时逐步优化解的质量：

1. 使用较大的膨胀因子 \(\epsilon\)（如 \(\epsilon = 3.0\)）快速获得初始次优解
2. 逐步减小 \(\epsilon\)，复用之前的搜索信息改进路径
3. 当 \(\epsilon = 1.0\) 时，解达到最优

$$
f(s) = g(s) + \epsilon \cdot h(s), \quad \epsilon \geq 1.0
$$

ARA* 的优点在于可以在任意时刻被打断并返回当前最优解，满足实时性要求。


### 任意时间 RRT

Anytime RRT 和 RRT* 也支持渐进优化。RRT* 通过重连（rewire）操作使路径逐步趋近最优：

```python
# RRT* 重连伪代码
def rewire(tree, new_node, near_nodes, cost_fn):
    for node in near_nodes:
        new_cost = cost_fn(new_node) + distance(new_node, node)
        if new_cost < cost_fn(node):
            if collision_free(new_node, node):
                node.parent = new_node
                update_costs(node)  # 递归更新子树代价
```


## 控制屏障函数

控制屏障函数（Control Barrier Function, CBF）是一种基于 Lyapunov 理论的安全性保障工具，可在连续控制层面确保系统不进入不安全区域。

### 基本定义

对于仿射控制系统 \(\dot{x} = f(x) + g(x)u\)，定义安全集合 \(\mathcal{C} = \{x : h(x) \geq 0\}\)。函数 \(h(x)\) 是控制屏障函数，当满足以下条件时系统保持在安全集合内：

$$
\sup_{u \in U} \left[ L_f h(x) + L_g h(x) \cdot u + \alpha(h(x)) \right] \geq 0
$$

其中 \(L_f h\) 和 \(L_g h\) 是 Lie 导数，\(\alpha\) 是扩展类 K 函数。

### CBF-QP 安全滤波器

将 CBF 约束嵌入二次规划（Quadratic Programming, QP）中，可以对名义控制器的输出进行最小修正以保证安全：

$$
\begin{aligned}
u^* = \arg\min_{u} \quad & \|u - u_{nom}\|^2 \\
\text{s.t.} \quad & L_f h(x) + L_g h(x) \cdot u + \alpha(h(x)) \geq 0
\end{aligned}
$$

```python
import numpy as np
from scipy.optimize import minimize

def cbf_safety_filter(u_nom, x, obstacle_pos, safe_dist):
    """CBF 安全滤波器示例"""
    # 定义屏障函数 h(x) = ||x - x_obs||^2 - d_safe^2
    diff = x[:2] - obstacle_pos
    h = np.dot(diff, diff) - safe_dist**2

    # Lie 导数计算（简化的单积分器模型）
    Lf_h = 0.0
    Lg_h = 2 * diff  # dh/dx * g(x)

    # CBF 约束: Lf_h + Lg_h @ u + alpha * h >= 0
    alpha = 1.0
    from scipy.optimize import minimize
    def objective(u):
        return np.sum((u - u_nom)**2)

    def cbf_constraint(u):
        return Lf_h + Lg_h @ u + alpha * h

    result = minimize(objective, u_nom,
                      constraints={'type': 'ineq', 'fun': cbf_constraint})
    return result.x
```


## 速度障碍

### 速度障碍法（Velocity Obstacle, VO）

速度障碍法用于多智能体动态避障。对于机器人 A 和障碍物 B，速度障碍定义为所有会导致碰撞的相对速度集合：

$$
VO_{A|B} = \{v_A : \exists t > 0, \; \|p_A + v_A t - p_B - v_B t\| \leq r_A + r_B\}
$$

机器人选择速度障碍之外的速度即可避免碰撞。


### 最优互惠碰撞避免（ORCA）

ORCA（Optimal Reciprocal Collision Avoidance）是 VO 的改进版，假设每个智能体各承担一半的避障责任：

- 计算两个智能体之间的速度障碍
- 将避障责任对半分配，每个智能体只需调整自身速度的一半
- 使用线性规划求解满足所有 ORCA 约束的最优速度

ORCA 的优势在于去中心化、无需通信，每个智能体独立计算即可保证无碰撞（在理想条件下）。

| 方法 | 智能体数量 | 是否需要通信 | 振荡问题 |
|------|-----------|-------------|---------|
| VO | 少量 | 否 | 严重 |
| RVO | 中等 | 否 | 缓解 |
| ORCA | 大量 | 否 | 基本消除 |


## 轨迹安全验证

### 可达集分析

可达集（Reachable Set）计算系统在给定时间内所有可能到达的状态集合。若可达集与障碍物区域无交集，则轨迹安全。

工具链：

- **CORA**（MATLAB）：计算多面体和缩放带的可达集
- **Flow***: 连续和混合系统的可达性分析


### 时空走廊

时空走廊（Safe Flight Corridor）在规划空间中构建一系列凸多面体，轨迹被约束在这些凸区域内从而保证安全：

1. 沿初始路径采样参考点
2. 在每个参考点周围构建无碰撞的凸多面体
3. 在凸区域内优化光滑轨迹


## 故障安全规划

### 紧急停车轨迹

每条规划轨迹末端应附带一条紧急停车轨迹（Braking Trajectory），使机器人能在任意时刻安全停止：

$$
v(t) = v_0 \cdot \left(1 - \frac{t}{t_{brake}}\right), \quad 0 \leq t \leq t_{brake}
$$

### 防御性规划策略

1. **保守速度限制**：根据传感器可视范围限制最大速度，确保能在可见范围内停下
2. **安全间隔**：在障碍物周围设置安全缓冲区
3. **回退方案**：当主规划失败时，执行预设的安全行为（如原地停止、返回起点）
4. **超时检测**：规划超时未完成时触发安全行为


## 各方法适用场景总结

| 方法 | 适用场景 | 实时性 | 安全保障 |
|------|---------|--------|---------|
| D* Lite | 未知环境导航 | 高 | 路径级 |
| ARA* | 有时间约束的规划 | 可调 | 路径级 |
| CBF | 连续控制安全约束 | 高 | 控制级 |
| ORCA | 密集多智能体场景 | 高 | 速度级 |
| 可达集 | 安全验证 | 离线 | 形式化保证 |
| 故障安全规划 | 所有场景 | 高 | 系统级 |


## 参考资料

- Koenig S, Likhachev M. D* Lite. *AAAI*, 2002.
- Likhachev M, et al. Anytime Dynamic A*. *AAAI*, 2005.
- Ames A D, et al. Control Barrier Functions: Theory and Applications. *ECC*, 2019.
- van den Berg J, et al. Reciprocal n-Body Collision Avoidance. *ISRR*, 2011.
- LaValle S M. *Planning Algorithms*. Cambridge University Press, 2006.
