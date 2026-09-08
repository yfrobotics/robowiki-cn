# 逆运动学

!!! note "引言"
    逆运动学（Inverse Kinematics，IK）求解的是正运动学的反问题：已知末端执行器的目标位姿，求各关节应当处于什么位置。与正运动学不同，逆运动学是非线性问题，可能无解、有有限多解、甚至有无穷多解，是机器人学中最具工程挑战性的基础问题之一。抓取、示教、轨迹跟踪、遥操作等任务都依赖逆运动学把笛卡尔空间的指令翻译成关节指令。


## 问题的困难之处

给定目标位姿 \(T_d \in SE(3)\)，求 \(\mathbf{q}\) 使得：

$$f(\mathbf{q}) = T_d$$

这个方程组的困难来自三个方面。

**可解性**：目标位姿必须落在机器人的工作空间内。工作空间之外的目标无解。即使在工作空间内，关节限位也可能使某些位姿实际不可达。

**多解性**：即使有解，解通常不唯一。以六轴工业机械臂为例，典型有 **8 组解**，对应三对二值选择：

- 肩部构型（Shoulder）：左手 / 右手
- 肘部构型（Elbow）：上肘 / 下肘
- 腕部构型（Wrist）：翻转 / 不翻转

若关节行程超过 \(2\pi\)，同一构型还会因为 \(\theta\) 与 \(\theta + 2\pi\) 而增加更多解。**选择哪一组解**是实际系统必须明确回答的工程问题：常见策略是选择与当前构型关节空间距离最近的解，以避免运动过程中出现大幅度的构型切换。

**冗余性**：当自由度大于任务维度时（如 7 轴机械臂完成 6 维位姿任务），解构成一个连续的解流形（Self-Motion Manifold），有无穷多组解。此时可以利用零空间（Null Space）实现避障、避奇异、关节限位规避等次要目标。


## 解析解法

### 可解性条件

Pieper 准则（Pieper's Criterion）给出了六自由度机械臂存在封闭解析解的充分条件：

- 连续三个关节的轴线**相交于一点**（球形手腕），或
- 连续三个关节的轴线**相互平行**

绝大多数工业机械臂（Puma、ABB IRB、KUKA KR 系列、FANUC）都设计成球形手腕，正是为了保证解析解的存在——解析解速度快（微秒级）、能穷举所有解、无收敛性问题，对工业场景至关重要。

近年的协作机器人（UR 系列、Franka Panda）有些不满足严格的球形手腕，但仍通过特殊几何设计保留了封闭解。

### 运动学解耦

对球形手腕机械臂，问题可解耦为两个三自由度子问题：

**第一步：求腕心位置。** 腕心（Wrist Center）是后三个关节轴的交点。由于末端到腕心的偏移量 \(d_6\) 沿末端 \(\hat{z}\) 轴固定，腕心位置可以直接从目标位姿算出：

$$\mathbf{p}_{wc} = \mathbf{p}_d - d_6 \, R_d \hat{z}$$

其中 \(\mathbf{p}_d\) 与 \(R_d\) 是目标位姿的平移与旋转部分。腕心位置只由前三个关节 \((\theta_1, \theta_2, \theta_3)\) 决定，因此可以独立求解。

**第二步：求姿态。** 前三个关节确定后，\({}^{0}R_{3}\) 已知，则后三个关节需要提供的旋转为：

$$ {}^{3}R_{6} = {}^{0}R_{3}^{T} R_d $$

这是一个从旋转矩阵反解三个欧拉角的问题，与 [空间描述与变换](spatial-transformation.md) 中的欧拉角反解完全相同（对球形手腕通常是 Z-Y-Z 序列）。

### 示例：平面两连杆机械臂

平面两连杆机械臂（连杆长 \(l_1, l_2\)）的逆运动学是理解多解性的最佳例子。给定末端位置 \((x, y)\)：

由余弦定理，第二关节角为：

$$\cos\theta_2 = \frac{x^2 + y^2 - l_1^2 - l_2^2}{2 l_1 l_2}$$

$$\theta_2 = \pm \arccos\left(\frac{x^2 + y^2 - l_1^2 - l_2^2}{2 l_1 l_2}\right)$$

正负号即对应"上肘"与"下肘"两组解。第一关节角为：

$$\theta_1 = \operatorname{atan2}(y, x) - \operatorname{atan2}\left(l_2 \sin\theta_2,\ l_1 + l_2 \cos\theta_2\right)$$

可解性条件是 \(|\cos\theta_2| \le 1\)，即 \(|l_1 - l_2| \le \sqrt{x^2+y^2} \le l_1 + l_2\)——正是工作空间圆环的内外半径。

数值实现时应使用 \(\theta_2 = \operatorname{atan2}(\pm\sqrt{1-c_2^2},\ c_2)\) 而非 `arccos`，因为前者在 \(c_2\) 接近 \(\pm 1\) 时数值条件更好。

### 解析解的实现要点

- 全程使用 `atan2` 而非 `atan`、`asin`、`acos`，以保证象限正确与数值稳定
- 对每组解检查关节限位，剔除不可达的解
- 因浮点误差导致 \(|\cos\theta| = 1.0000001\) 时要做钳位（clamp），否则 `arccos` 返回 NaN
- 返回全部解并由上层策略选择，不要在求解器内部硬编码选择规则


## 数值解法

对于不满足 Pieper 准则的机构、冗余机械臂、或者带有额外约束的问题，需要使用数值迭代法。数值法的通用思路是把逆运动学转化为优化问题，反复用 [雅可比矩阵](jacobian.md) 做局部线性化并迭代逼近。

### 雅可比转置法

最简单的方法，把末端位姿误差 \(\mathbf{e}\) 当作虚拟力，通过雅可比转置映射为关节力矩方向：

$$\Delta \mathbf{q} = \alpha J^T \mathbf{e}$$

优点是不需要矩阵求逆，在奇异点附近也不会发散；缺点是收敛慢，步长 \(\alpha\) 难以自动选取。可以证明该方向始终是误差范数的下降方向，因此收敛性有保证，但只是一阶方法。

### 雅可比伪逆法

用 Moore-Penrose 伪逆求最小范数解：

$$\Delta \mathbf{q} = J^{\dagger} \mathbf{e}, \qquad J^{\dagger} = J^T (J J^T)^{-1} \quad (m < n)$$

收敛速度快（接近牛顿法），但在奇异位形附近 \(J J^T\) 接近奇异，\(J^\dagger\) 的元素趋于无穷，产生极大的关节速度指令——这是伪逆法最致命的问题。

### 阻尼最小二乘法

阻尼最小二乘（Damped Least Squares，DLS），也称 Levenberg-Marquardt 法，是工程上最常用的数值 IK 方法。它在求逆时加入阻尼项：

$$\Delta \mathbf{q} = J^T (J J^T + \lambda^2 I)^{-1} \mathbf{e}$$

等价于求解带正则项的优化问题：

$$\min_{\Delta \mathbf{q}} \ \|J \Delta \mathbf{q} - \mathbf{e}\|^2 + \lambda^2 \|\Delta \mathbf{q}\|^2$$

阻尼系数 \(\lambda\) 在精度与稳定性之间做权衡：\(\lambda \to 0\) 退化为伪逆（精确但不稳定），\(\lambda\) 增大则关节速度受限但存在稳态误差。

实用做法是**自适应阻尼**：远离奇异时用小阻尼保证精度，接近奇异时按最小奇异值 \(\sigma_{\min}\) 增大阻尼：

$$\lambda^2 = \begin{cases} 0 & \sigma_{\min} \ge \epsilon \\ \left(1 - \left(\frac{\sigma_{\min}}{\epsilon}\right)^2\right)\lambda_{\max}^2 & \sigma_{\min} < \epsilon \end{cases}$$

### 冗余度与零空间投影

对冗余机械臂（\(n > m\)），通解由特解加零空间项构成：

$$\Delta \mathbf{q} = J^{\dagger} \mathbf{e} + (I - J^{\dagger} J) \, \mathbf{z}$$

第二项中 \((I - J^\dagger J)\) 是到 \(J\) 零空间的投影算子，任意选取的 \(\mathbf{z}\) 经投影后都不会影响末端位姿。因此可以令 \(\mathbf{z} = k \nabla H(\mathbf{q})\)，其中 \(H\) 是待优化的次要目标函数：

| 次要目标 | 目标函数 \(H(\mathbf{q})\) |
|---------|--------------------------|
| 远离关节限位 | \(-\sum_i \left(\frac{q_i - \bar{q}_i}{q_i^{max} - q_i^{min}}\right)^2\)，\(\bar{q}_i\) 为行程中点 |
| 远离奇异位形 | 可操作度 \(w = \sqrt{\det(JJ^T)}\) |
| 避障 | 机器人各连杆到障碍物的最小距离 |
| 最小化关节运动 | \(-\|\mathbf{q} - \mathbf{q}_{ref}\|^2\) |

这一框架可以推广为**任务优先级**（Task Priority）控制，在多个任务之间建立严格的优先级层次，是人形机器人全身控制（Whole-Body Control）的基础。

### 误差的定义

数值 IK 中位姿误差 \(\mathbf{e} \in \mathbb{R}^6\) 的构造需要小心。位置部分直接相减：

$$\mathbf{e}_p = \mathbf{p}_d - \mathbf{p}(\mathbf{q})$$

姿态部分不能直接相减矩阵，常用做法是取旋转误差的对数映射：

$$\mathbf{e}_o = \log\left(R_d R(\mathbf{q})^T\right)^\vee$$

或使用四元数误差的向量部分。位置误差（米）与姿态误差（弧度）量纲不同，需要加权：\(\mathbf{e}_w = W \mathbf{e}\)，权重矩阵 \(W\) 的选取会显著影响收敛行为，一个常见的经验做法是让姿态权重对应机器人特征长度上的等效弧长。


## 求解器与工具

| 求解器 | 类型 | 特点 |
|--------|------|------|
| [IKFast](http://openrave.org/docs/latest_stable/openravepy/ikfast/) | 解析（代码生成） | 离线用符号计算生成 C++ 解析解，微秒级速度，返回全部解；仅支持满足可解性条件的机构 |
| KDL | 数值（NR/DLS） | ROS 默认求解器，通用但在关节限位附近成功率一般 |
| [TRAC-IK](https://traclabs.com/projects/trac-ik/) | 数值（并行） | 同时运行 KDL 的 NR 求解器与 SQP 求解器，取先收敛者，成功率显著高于纯 KDL |
| [BioIK](https://github.com/PickNikRobotics/bio_ik) | 演化 + 梯度 | 支持自定义目标（朝向、视线、平衡），适合冗余机器人与复杂约束 |
| Pinocchio + CasADi | 数值优化 | 可加入任意约束，适合研究与全身控制 |
| [Drake IK](https://drake.mit.edu/) | 非线性规划 | 支持碰撞规避与多约束的全局求解 |

在 MoveIt 中切换求解器只需修改 `kinematics.yaml`：

```yaml
manipulator:
  kinematics_solver: trac_ik_kinematics_plugin/TRAC_IKKinematicsPlugin
  kinematics_solver_search_resolution: 0.005
  kinematics_solver_timeout: 0.05
  solve_type: Distance          # Speed / Distance / Manipulation1 / Manipulation2
```


## 代码实现

### 阻尼最小二乘 IK

```python
import numpy as np
from scipy.linalg import logm


def pose_error(T_cur, T_des):
    """返回 6 维位姿误差 [位置误差; 姿态误差]"""
    e_p = T_des[:3, 3] - T_cur[:3, 3]
    R_err = T_des[:3, :3] @ T_cur[:3, :3].T
    so3 = logm(R_err).real
    e_o = np.array([so3[2, 1], so3[0, 2], so3[1, 0]])
    return np.concatenate([e_p, e_o])


def ik_dls(fk, jac, T_des, q0, q_min, q_max,
           max_iter=200, tol=1e-5, lam_max=0.1, eps=1e-3):
    """阻尼最小二乘逆运动学

    fk(q)  -> 4x4 末端位姿
    jac(q) -> 6xn 几何雅可比
    """
    q = np.asarray(q0, dtype=float).copy()

    for it in range(max_iter):
        e = pose_error(fk(q), T_des)
        if np.linalg.norm(e) < tol:
            return q, True, it

        J = jac(q)
        # 自适应阻尼：接近奇异时增大 lambda
        sigma_min = np.linalg.svd(J, compute_uv=False)[-1]
        if sigma_min >= eps:
            lam2 = 0.0
        else:
            lam2 = (1.0 - (sigma_min / eps) ** 2) * lam_max ** 2

        JJt = J @ J.T + lam2 * np.eye(J.shape[0])
        dq = J.T @ np.linalg.solve(JJt, e)

        # 限制单步幅度，避免大跨步越过解
        step = np.linalg.norm(dq)
        if step > 0.2:
            dq *= 0.2 / step

        q = np.clip(q + dq, q_min, q_max)

    return q, False, max_iter
```

### 平面两连杆的解析解

```python
import numpy as np


def ik_planar_2link(x, y, l1, l2):
    """返回全部解 [(theta1, theta2), ...]，无解时返回空列表"""
    r2 = x * x + y * y
    c2 = (r2 - l1 ** 2 - l2 ** 2) / (2 * l1 * l2)

    if abs(c2) > 1.0 + 1e-9:              # 目标在工作空间外
        return []
    c2 = np.clip(c2, -1.0, 1.0)           # 钳位以吸收浮点误差

    solutions = []
    for sign in (+1.0, -1.0):             # 上肘 / 下肘
        s2 = sign * np.sqrt(max(0.0, 1.0 - c2 ** 2))
        t2 = np.arctan2(s2, c2)
        t1 = np.arctan2(y, x) - np.arctan2(l2 * s2, l1 + l2 * c2)
        solutions.append((t1, t2))
    return solutions


if __name__ == '__main__':
    l1, l2 = 0.5, 0.4
    for t1, t2 in ik_planar_2link(0.6, 0.3, l1, l2):
        # 代回正运动学验证
        x = l1 * np.cos(t1) + l2 * np.cos(t1 + t2)
        y = l1 * np.sin(t1) + l2 * np.sin(t1 + t2)
        print(f'theta = ({t1:+.4f}, {t2:+.4f})  ->  ({x:.4f}, {y:.4f})')
```

### 在 MoveIt 中调用

```python
from moveit.planning import MoveItPy
from geometry_msgs.msg import PoseStamped

moveit = MoveItPy(node_name='ik_demo')
arm = moveit.get_planning_component('manipulator')

target = PoseStamped()
target.header.frame_id = 'base_link'
target.pose.position.x = 0.4
target.pose.position.y = 0.1
target.pose.position.z = 0.5
target.pose.orientation.w = 1.0

arm.set_start_state_to_current_state()
arm.set_goal_state(pose_stamped_msg=target, pose_link='tool0')

plan = arm.plan()
if plan:
    moveit.execute(plan.trajectory, controllers=[])
else:
    print('规划失败：目标位姿可能不可达或存在碰撞')
```


## 工程实践建议

- **优先使用解析解**。如果机构满足可解性条件，用 IKFast 生成解析求解器，速度与可靠性都远优于数值法。
- **数值解需要好的初值**。在轨迹跟踪中用上一周期的关节角作为初值，收敛通常只需 2–3 次迭代；随机初值则可能收敛到不期望的构型或不收敛。
- **多起点重启**。对单次求解（如抓取位姿），失败时从若干随机初值重试，可显著提高成功率——TRAC-IK 的高成功率部分来自于此。
- **区分"无解"与"未收敛"**。求解失败时应报告失败原因：目标超出工作空间、违反关节限位、还是迭代次数耗尽。上层的处理策略完全不同。
- **考虑连续性**。轨迹跟踪中每个路径点独立求 IK 可能得到构型跳变的解序列，导致关节剧烈运动。应在解集中选择与上一构型关节距离最小者，或直接在关节空间做[轨迹生成](trajectory-generation.md)。
- **奇异位形附近降速**。即使使用 DLS，接近奇异时末端跟踪精度也会下降，应在任务层主动降低末端速度或规划绕开奇异区域，详见 [雅可比矩阵与奇异性](jacobian.md)。


## 参考资料

1. Craig, J. J. (2005). *Introduction to Robotics: Mechanics and Control* (3rd ed.). Pearson Prentice Hall. — 第 4 章讲解逆运动学与 Pieper 准则。
2. Pieper, D. L. (1968). *The Kinematics of Manipulators Under Computer Control*. PhD Thesis, Stanford University.
3. Buss, S. R. (2004). Introduction to Inverse Kinematics with Jacobian Transpose, Pseudoinverse and Damped Least Squares Methods. *Technical Report, UC San Diego*. — 数值 IK 方法的经典综述。
4. Nakamura, Y. & Hanafusa, H. (1986). Inverse Kinematic Solutions with Singularity Robustness for Robot Manipulator Control. *Journal of Dynamic Systems, Measurement, and Control*, 108(3), 163-171. — 阻尼最小二乘法的原始论文。
5. Beeson, P. & Ames, B. (2015). TRAC-IK: An Open-Source Library for Improved Solving of Generic Inverse Kinematics. *IEEE-RAS International Conference on Humanoid Robots*.
6. Siciliano, B. & Slotine, J.-J. E. (1991). A General Framework for Managing Multiple Tasks in Highly Redundant Robotic Systems. *International Conference on Advanced Robotics*.
7. Diankov, R. (2010). *Automated Construction of Robotic Manipulation Programs*. PhD Thesis, Carnegie Mellon University. — IKFast 的理论基础。
