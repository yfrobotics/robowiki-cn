# 路径规划

!!! note "引言"
    路径规划 (Path Planning) 是机器人规划中的核心问题之一，其目标是在已知或部分已知的环境中，找到一条从起点到终点的无碰撞路径。路径规划主要关注几何可行性，即路径不与障碍物相交，通常不考虑机器人的动力学约束。本页面介绍路径规划的主要方法及其算法原理。

## 问题定义

路径规划问题可以形式化为：给定工作空间 \(\mathcal{W}\)（通常为 \(\mathbb{R}^2\) 或 \(\mathbb{R}^3\)）、障碍物区域 \(\mathcal{O} \subset \mathcal{W}\)、自由空间 \(\mathcal{F} = \mathcal{W} \setminus \mathcal{O}\)、起点 \(q_s \in \mathcal{F}\) 和终点 \(q_g \in \mathcal{F}\)，求一条连续路径 \(\tau: [0, 1] \rightarrow \mathcal{F}\)，使得：

$$
\tau(0) = q_s, \quad \tau(1) = q_g, \quad \forall t \in [0, 1]: \tau(t) \in \mathcal{F}
$$

对于最优路径规划，还需要最小化某个代价函数（如路径长度）：

$$
\tau^* = \arg\min_{\tau} \int_0^1 \| \dot{\tau}(t) \| \, dt
$$


## 图搜索算法 (Graph Search Algorithms)

图搜索算法将环境离散化为图结构，然后在图上搜索从起点到终点的最优路径。

### 广度优先搜索 (Breadth-First Search, BFS)

BFS 从起点开始，逐层向外扩展，保证找到的路径跳数最少（在无权图中即为最短路径）。

**伪代码：**

```
BFS(start, goal):
    queue ← {start}
    visited ← {start}
    parent ← {}

    while queue 非空:
        node ← queue.dequeue()
        if node == goal:
            return 通过 parent 回溯路径

        for neighbor in node.neighbors():
            if neighbor 不在 visited 中:
                visited.add(neighbor)
                parent[neighbor] ← node
                queue.enqueue(neighbor)

    return 无解
```

- **时间复杂度**：\(O(V + E)\)，其中 \(V\) 是节点数，\(E\) 是边数
- **空间复杂度**：\(O(V)\)
- **特点**：保证最短路径（无权图），但不适合大规模搜索空间

### 深度优先搜索 (Depth-First Search, DFS)

DFS 沿着一个分支尽可能深入搜索，到达死胡同后回溯。DFS 不保证找到最短路径，但内存开销较小。

- **时间复杂度**：\(O(V + E)\)
- **空间复杂度**：\(O(V)\)（最坏情况），实际中通常远小于 BFS
- **特点**：不保证最短路径；可能陷入无限深分支（需要深度限制）

### Dijkstra 算法

Dijkstra 算法是经典的单源最短路径算法，适用于边权为非负值的加权图。它通过贪心策略，每次扩展当前距离最小的节点。

**伪代码：**

```
Dijkstra(start, goal):
    dist[start] ← 0
    对所有其他节点 v: dist[v] ← ∞
    priority_queue ← {(0, start)}
    parent ← {}

    while priority_queue 非空:
        (d, node) ← priority_queue.extract_min()
        if node == goal:
            return 通过 parent 回溯路径

        for (neighbor, weight) in node.neighbors():
            new_dist ← d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] ← new_dist
                parent[neighbor] ← node
                priority_queue.insert((new_dist, neighbor))

    return 无解
```

- **时间复杂度**：\(O((V + E) \log V)\)（使用优先队列）
- **空间复杂度**：\(O(V)\)
- **特点**：保证最短路径；向所有方向均匀扩展，效率不如 A\*

### A\* 算法

A\* 算法是路径规划中最广泛使用的算法。它在 Dijkstra 的基础上引入启发式函数 (Heuristic Function) 来引导搜索方向，大幅提高搜索效率。

**核心思想：** 对每个节点 \(n\)，A\* 维护一个评估函数：

$$
f(n) = g(n) + h(n)
$$

- \(g(n)\)：从起点到节点 \(n\) 的实际代价
- \(h(n)\)：从节点 \(n\) 到终点的启发式估计代价

**伪代码：**

```
A_star(start, goal):
    g[start] ← 0
    f[start] ← h(start)
    open_set ← {(f[start], start)}
    closed_set ← {}
    parent ← {}

    while open_set 非空:
        (_, node) ← open_set.extract_min()
        if node == goal:
            return 通过 parent 回溯路径

        closed_set.add(node)

        for (neighbor, weight) in node.neighbors():
            if neighbor 在 closed_set 中:
                continue
            tentative_g ← g[node] + weight
            if tentative_g < g[neighbor]:
                g[neighbor] ← tentative_g
                f[neighbor] ← tentative_g + h(neighbor)
                parent[neighbor] ← node
                open_set.insert((f[neighbor], neighbor))

    return 无解
```

**启发式函数的要求：** 为保证 A\* 找到最优路径，启发式函数必须满足可采纳性 (Admissibility)，即永不高估实际代价：

$$
\forall n: h(n) \leq h^*(n)
$$

其中 \(h^*(n)\) 是从 \(n\) 到终点的真实最短代价。常用的启发式函数包括：

- **欧几里得距离 (Euclidean Distance)**：\(h(n) = \sqrt{(x_n - x_g)^2 + (y_n - y_g)^2}\)
- **曼哈顿距离 (Manhattan Distance)**：\(h(n) = |x_n - x_g| + |y_n - y_g|\)（适用于四方向网格）
- **切比雪夫距离 (Chebyshev Distance)**：\(h(n) = \max(|x_n - x_g|, |y_n - y_g|)\)（适用于八方向网格）

- **时间复杂度**：\(O(b^d)\)（最坏情况），其中 \(b\) 是分支因子，\(d\) 是解的深度；好的启发式函数可以极大减少扩展节点数
- **特点**：在启发式函数可采纳时保证最优；是 Dijkstra 算法的推广（当 \(h(n) = 0\) 时退化为 Dijkstra）

### D\* 算法

D\* (Dynamic A\*) 算法及其变体 D\* Lite 专为动态环境设计，能够在环境发生变化时高效地重新规划路径，而不需要从头搜索。

**核心思想：** D\* 从终点向起点反向搜索。当机器人在移动过程中发现新的障碍物时，只需要局部更新受影响的节点，而不必重新搜索整个图。

**适用场景：**

- 未知或部分已知环境中的在线规划
- 传感器范围有限的移动机器人
- 环境频繁变化的场景（如动态障碍物）

### 算法对比

| 算法 | 最优性 | 完备性 | 动态环境 | 启发式 |
|------|--------|--------|---------|--------|
| BFS | 是（无权图） | 是 | 否 | 否 |
| DFS | 否 | 是（有限图） | 否 | 否 |
| Dijkstra | 是 | 是 | 否 | 否 |
| A\* | 是（可采纳启发式） | 是 | 否 | 是 |
| D\* / D\* Lite | 是 | 是 | 是 | 是 |


## 基于采样的方法 (Sampling-based Methods)

基于采样的方法不显式构建环境的完整表示，而是通过随机采样来探索自由空间，特别适合高维构型空间。

### 概率路线图 (Probabilistic Roadmap, PRM)

PRM 是一种多查询 (Multi-query) 方法，分为两个阶段：

**学习阶段 (Learning Phase)：**

1. 在自由空间 \(\mathcal{F}\) 中随机采样 \(N\) 个点
2. 对每个采样点，尝试与其 \(k\) 个最近邻点连接
3. 通过碰撞检测验证连接的有效性
4. 构建一个路线图（无向图）

**查询阶段 (Query Phase)：**

1. 将起点和终点连接到路线图中
2. 在路线图上使用 A\* 或 Dijkstra 搜索路径

**伪代码（学习阶段）：**

```
PRM_Learn(N, k):
    V ← {}
    E ← {}

    for i = 1 to N:
        q ← 在自由空间中随机采样
        if q ∈ 自由空间:
            V.add(q)

    for each q ∈ V:
        neighbors ← q 的 k 个最近邻
        for each q_n ∈ neighbors:
            if 路径(q, q_n)无碰撞:
                E.add((q, q_n))

    return Graph(V, E)
```

- **特点**：概率完备 (Probabilistically Complete)；适合多次查询同一环境；不适合窄通道 (Narrow Passages)

### 快速探索随机树 (Rapidly-exploring Random Tree, RRT)

RRT 是一种单查询 (Single-query) 方法，从起点开始增量式地构建一棵随机树来探索空间。

**伪代码：**

```
RRT(start, goal, max_iter):
    tree ← {start}

    for i = 1 to max_iter:
        q_rand ← 随机采样一个点
        q_near ← tree 中离 q_rand 最近的节点
        q_new ← 从 q_near 向 q_rand 方向延伸步长 δ

        if 路径(q_near, q_new)无碰撞:
            tree.add_node(q_new)
            tree.add_edge(q_near, q_new)

            if distance(q_new, goal) < 阈值:
                return 从 start 到 q_new 的路径

    return 无解
```

- **特点**：概率完备；天然倾向于探索未访问区域（Voronoi 偏置）；找到的路径通常不是最优的

### RRT\* 算法

RRT\* 是 RRT 的渐近最优 (Asymptotically Optimal) 版本。它在 RRT 的基础上增加了两个关键操作：

1. **选择最优父节点 (Choose Best Parent)**：在 \(q_{new}\) 附近搜索半径 \(r\) 内的节点，选择使路径代价最小的节点作为父节点
2. **重新连线 (Rewire)**：检查是否通过 \(q_{new}\) 可以降低附近节点的路径代价，如果可以则更新连接

搜索半径通常取：

$$
r = \gamma \left( \frac{\log n}{n} \right)^{1/d}
$$

其中 \(n\) 是当前节点数量，\(d\) 是空间维度，\(\gamma\) 是与自由空间体积相关的常数。

- **特点**：渐近最优，即随着采样数增加，路径代价收敛到最优值；计算开销比 RRT 更大


## 人工势场法 (Artificial Potential Field)

人工势场法将路径规划问题转化为一个虚拟力场中的运动问题，是一种简单而直观的局部规划方法。

### 基本原理

定义一个势场函数 \(U(q)\)，由引力场和斥力场叠加而成：

$$
U(q) = U_{att}(q) + U_{rep}(q)
$$

**引力场 (Attractive Potential)：** 将机器人拉向目标点

$$
U_{att}(q) = \frac{1}{2} \xi \| q - q_g \|^2
$$

**斥力场 (Repulsive Potential)：** 将机器人推离障碍物

$$
U_{rep}(q) =
\begin{cases}
\frac{1}{2} \eta \left( \frac{1}{\rho(q)} - \frac{1}{\rho_0} \right)^2, & \text{if } \rho(q) \leq \rho_0 \\
0, & \text{if } \rho(q) > \rho_0
\end{cases}
$$

其中 \(\xi\) 和 \(\eta\) 是增益系数，\(\rho(q)\) 是机器人到最近障碍物的距离，\(\rho_0\) 是障碍物的影响范围。

机器人沿着势场的负梯度方向运动：

$$
F(q) = -\nabla U(q) = F_{att}(q) + F_{rep}(q)
$$

### 局部极小值问题 (Local Minima)

人工势场法的主要缺点是可能陷入局部极小值（即引力和斥力平衡的非目标点）。常见的解决方案包括：

- **随机扰动 (Random Walk)**：在检测到局部极小值时添加随机扰动
- **模拟退火 (Simulated Annealing)**：以一定概率接受势场增大的方向
- **导航函数 (Navigation Functions)**：设计没有局部极小值的特殊势场函数
- **与全局规划器结合**：将势场法作为局部避障方法，配合全局路径规划器使用


## 基于栅格的方法 (Grid-based Methods)

基于栅格的方法将连续环境离散化为规则的网格（通常是二维栅格地图），每个栅格单元标记为自由或占据。

### 占据栅格地图 (Occupancy Grid Map)

将环境划分为等间距的栅格。每个栅格 \(c_{ij}\) 的值表示该区域被障碍物占据的概率：

- \(P(c_{ij}) = 0\)：完全自由
- \(P(c_{ij}) = 1\)：完全占据
- \(P(c_{ij}) = 0.5\)：未知

### 栅格分辨率的权衡

- **高分辨率**：路径更精确，但计算和存储开销大
- **低分辨率**：计算快速，但可能遗漏窄通道或产生次优路径

### 四叉树 / 八叉树 (Quadtree / Octree)

为平衡精度和效率，可以使用自适应分辨率的空间分解方法：

- **四叉树**：用于二维空间，递归将区域分为四个象限
- **八叉树**：用于三维空间，递归将体素分为八个子体素
- 只在障碍物边界附近使用高分辨率，在自由空间使用低分辨率


## Bug 算法 (Bug Algorithms)

Bug 算法是一类简单的反应式路径规划方法，仅需要机器人能够检测障碍物边界并知道目标方向，不需要完整的环境地图。

### Bug0 算法

1. 向目标方向直线前进
2. 遇到障碍物后，沿障碍物边界绕行
3. 当可以再次向目标前进时，离开障碍物边界

Bug0 不保证能到达目标（可能陷入循环）。

### Bug1 算法

1. 向目标方向直线前进
2. 遇到障碍物后，完整绕行障碍物一周，记录离目标最近的点
3. 回到该最近点，离开障碍物向目标前进

Bug1 保证到达目标（如果路径存在），但路径长度上界为：

$$
L_{Bug1} \leq d(s, g) + \frac{3}{2} \sum_{i} p_i
$$

其中 \(d(s, g)\) 是起点到终点的直线距离，\(p_i\) 是第 \(i\) 个障碍物的周长。

### Bug2 算法

1. 沿起点到终点的连线（M-line）前进
2. 遇到障碍物后，沿边界绕行
3. 当回到 M-line 且此处比遇到障碍物时更靠近目标时，离开障碍物沿 M-line 前进

Bug2 通常比 Bug1 效率更高，路径长度上界为：

$$
L_{Bug2} \leq d(s, g) + \frac{1}{2} \sum_{i} n_i \cdot p_i
$$

其中 \(n_i\) 是 M-line 与第 \(i\) 个障碍物的交点数。

### 切线 Bug 算法 (Tangent Bug)

切线 Bug 算法是 Bug 算法的改进版，利用距离传感器的信息提前检测障碍物并计算切线方向，从而缩短绕行距离。


## 方法总结与对比

| 方法 | 完备性 | 最优性 | 适用维度 | 环境要求 | 计算效率 |
|------|--------|--------|---------|---------|---------|
| BFS / Dijkstra | 完备 | 最优 | 低维 | 已知离散图 | 中 |
| A\* | 完备 | 最优 | 低维 | 已知离散图 | 高（有启发式） |
| D\* / D\* Lite | 完备 | 最优 | 低维 | 动态环境 | 高（增量更新） |
| PRM | 概率完备 | 渐近最优 | 高维 | 已知静态 | 高（多查询） |
| RRT | 概率完备 | 否 | 高维 | 已知/未知 | 高（单查询） |
| RRT\* | 概率完备 | 渐近最优 | 高维 | 已知/未知 | 中 |
| 人工势场 | 不完备 | 否 | 低维 | 局部感知 | 很高 |
| Bug 算法 | 完备 | 否 | 二维 | 局部感知 | 很高 |


## 参考文献

1. LaValle, S. M. (2006). *Planning Algorithms*. Cambridge University Press. [在线版本](http://planning.cs.uiuc.edu/)
2. Hart, P. E., Nilsson, N. J. & Raphael, B. (1968). A Formal Basis for the Heuristic Determination of Minimum Cost Paths. *IEEE Transactions on Systems Science and Cybernetics*, 4(2), 100-107.
3. Koenig, S. & Likhachev, M. (2002). D\* Lite. *Proceedings of the AAAI Conference on Artificial Intelligence*, 476-483.
4. Kavraki, L. E., Svestka, P., Latombe, J. C. & Overmars, M. H. (1996). Probabilistic Roadmaps for Path Planning in High-Dimensional Configuration Spaces. *IEEE Transactions on Robotics and Automation*, 12(4), 566-580.
5. LaValle, S. M. (1998). Rapidly-exploring Random Trees: A New Tool for Path Planning. *Technical Report*, Computer Science Department, Iowa State University.
6. Karaman, S. & Frazzoli, E. (2011). Sampling-based Algorithms for Optimal Motion Planning. *International Journal of Robotics Research*, 30(7), 846-894.
7. Khatib, O. (1986). Real-time Obstacle Avoidance for Manipulators and Mobile Robots. *International Journal of Robotics Research*, 5(1), 90-98.
8. Lumelsky, V. & Stepanov, A. (1987). Path Planning Strategies for a Point Mobile Automaton Moving Amidst Unknown Obstacles of Arbitrary Shape. *Algorithmica*, 2, 403-430.
