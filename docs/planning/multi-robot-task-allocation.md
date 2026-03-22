# 多机器人任务分配

!!! note "引言"
    多机器人任务分配（Multi-Robot Task Allocation, MRTA）是多机器人系统中的核心问题之一，研究如何将一组任务有效地分配给多个机器人，使得整体性能最优。随着仓储物流、搜救、农业等领域对多机器人协作的需求日益增长，MRTA 已成为机器人学的重要研究方向。


## MRTA 分类体系

Gerkey 和 Matarić 于 2004 年提出了经典的 MRTA 分类框架，根据三个维度进行划分：

### 分类维度

| 维度 | 选项 | 说明 |
|------|------|------|
| 机器人能力 | SR（Single-Robot）/ MR（Multi-Robot） | 任务需要单个还是多个机器人协作完成 |
| 任务分配 | ST（Single-Task）/ MT（Multi-Task） | 每个机器人同时执行单个还是多个任务 |
| 时间约束 | IA（Instantaneous）/ TA（Time-extended） | 即时分配还是需考虑时序依赖 |

### 常见问题类型

| 类型 | 典型场景 | 求解难度 |
|------|---------|---------|
| SR-ST-IA | 仓库取货、多点巡逻 | 多项式可解（匹配问题） |
| SR-ST-TA | 带时间窗的配送 | NP-hard（类 VRP 问题） |
| MR-ST-IA | 多机器人搬运大型物体 | 需考虑联盟形成 |
| MR-MT-TA | 灾害搜救多任务协作 | 高复杂度，通常用启发式求解 |


## 基于拍卖的方法

拍卖机制（Auction-based Method）是 MRTA 中最常用的分布式方法，核心思想是将任务作为"商品"，机器人作为"竞拍者"。

### 基本流程

1. **任务发布**：拍卖者（中央节点或某个机器人）广播待分配任务
2. **投标**：每个机器人根据自身状态和能力计算对每个任务的投标值（bid）
3. **中标决定**：拍卖者选择投标值最优的机器人执行任务
4. **任务执行**：中标机器人执行任务，完成后报告结果

### 投标值计算

投标值通常综合考虑多个因素：

$$
b_i(t_j) = w_1 \cdot d(r_i, t_j) + w_2 \cdot E_i + w_3 \cdot C_i(t_j)
$$

其中 \(d(r_i, t_j)\) 是机器人 \(r_i\) 到任务 \(t_j\) 的距离，\(E_i\) 是剩余能量，\(C_i(t_j)\) 是机器人执行该任务的能力评估，\(w_1, w_2, w_3\) 为权重。

### 常见拍卖变体

- **单物品拍卖**：每轮分配一个任务，简单但可能导致次优解
- **组合拍卖**：机器人对任务组合进行投标，可获得更好的全局解，但计算复杂度高
- **顺序拍卖**：多轮拍卖，每轮分配一个任务，支持动态调整


## 匈牙利算法

匈牙利算法（Hungarian Algorithm）适用于 SR-ST-IA 类型的任务分配，即求解最优二部图匹配问题。给定 \(n\) 个机器人和 \(n\) 个任务，找到总代价最小的一对一分配方案。

算法时间复杂度为 \(O(n^3)\)，适用于中小规模问题。

```python
import numpy as np
from scipy.optimize import linear_sum_assignment

# 代价矩阵：cost[i][j] 表示机器人 i 执行任务 j 的代价
cost_matrix = np.array([
    [10, 5, 13],   # 机器人 0
    [3, 7, 9],     # 机器人 1
    [8, 12, 6],    # 机器人 2
])

# 求解最优分配
row_ind, col_ind = linear_sum_assignment(cost_matrix)

print("最优分配方案：")
for r, c in zip(row_ind, col_ind):
    print(f"  机器人 {r} -> 任务 {c}（代价: {cost_matrix[r, c]}）")
print(f"总代价: {cost_matrix[row_ind, col_ind].sum()}")
```


## 基于市场的协调

市场机制（Market-based Coordination）是拍卖方法的推广，引入了持续的"交易"过程：

### 任务交换

机器人之间可以通过任务交换（Task Swap）来改善全局分配质量：

1. 机器人 A 发现自己执行任务 X 的代价高于机器人 B
2. A 向 B 提出交换或转让提议
3. 如果双方总代价降低，则达成交换

### 共识算法 CBBA

共识拍卖算法（Consensus-Based Bundle Algorithm, CBBA）是一种分布式多任务分配算法：

1. **打包阶段**：每个机器人贪心地将任务加入自己的任务包
2. **共识阶段**：机器人之间交换分配信息，解决冲突
3. 重复迭代直到所有机器人达成共识

CBBA 无需中央协调器，适合通信受限的场景。


## 联盟形成

当任务需要多个机器人协作完成（MR 类型）时，需要形成联盟（Coalition）：

### 联盟价值函数

联盟 \(S\) 执行任务 \(t\) 的价值定义为：

$$
V(S, t) = R(t) - \sum_{i \in S} c_i(t)
$$

其中 \(R(t)\) 是完成任务的收益，\(c_i(t)\) 是机器人 \(i\) 的参与成本。

### 联盟形成策略

- **贪心策略**：逐步加入边际贡献最大的机器人
- **合同网协议**：任务管理者发布合同，机器人投标并形成执行团队
- **博弈论方法**：通过 Shapley 值等公平分配机制确定收益分配


## ROS 2 多机器人系统考量

### 命名空间隔离

ROS 2 通过命名空间区分不同机器人的话题和服务：

```bash
# 启动多个机器人，各自使用独立命名空间
ros2 launch my_robot robot_launch.py namespace:=robot_1
ros2 launch my_robot robot_launch.py namespace:=robot_2
```

### 任务分配节点示例

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String
import json

class TaskAllocator(Node):
    def __init__(self):
        super().__init__('task_allocator')
        self.robots = ['robot_1', 'robot_2', 'robot_3']
        self.task_pub = {}
        for robot in self.robots:
            self.task_pub[robot] = self.create_publisher(
                PoseStamped, f'/{robot}/goal_pose', 10
            )
        self.task_sub = self.create_subscription(
            String, '/new_tasks', self.allocate_callback, 10
        )

    def allocate_callback(self, msg):
        tasks = json.loads(msg.data)
        # 简单的最近距离分配策略
        assignment = self.greedy_assign(tasks)
        for robot, task in assignment.items():
            goal = PoseStamped()
            goal.pose.position.x = task['x']
            goal.pose.position.y = task['y']
            self.task_pub[robot].publish(goal)
            self.get_logger().info(f'{robot} 被分配到任务: {task}')
```

### 通信与协调架构

| 架构 | 特点 | 适用场景 |
|------|------|---------|
| 中心式 | 全局信息，最优解 | 通信可靠、机器人数量少 |
| 分布式 | 无单点故障，可扩展 | 大规模、通信受限 |
| 混合式 | 层次化分组协调 | 中等规模、区域化部署 |


## 性能评估指标

评估 MRTA 算法时常用以下指标：

- **总完成时间（Makespan）**：所有任务完成的最晚时间
- **总代价**：所有机器人的路径长度或能耗之和
- **负载均衡度**：各机器人工作量的标准差
- **通信开销**：协调过程中的消息数量
- **鲁棒性**：机器人故障时的任务重分配能力


## 参考资料

- Gerkey B P, Matarić M J. A Formal Analysis and Taxonomy of Task Allocation in Multi-Robot Systems. *IJRR*, 2004.
- Koenig S, et al. The Power of Sequential Single-Item Auctions for Agent Coordination. *AAAI*, 2006.
- Choi H L, et al. Consensus-Based Decentralized Auctions for Robust Task Allocation. *IEEE TRO*, 2009.
- ROS 2 多机器人设计文档：<https://docs.ros.org/en/rolling/Concepts.html>
- Kuhn H W. The Hungarian Method for the Assignment Problem. *Naval Research Logistics*, 1955.
