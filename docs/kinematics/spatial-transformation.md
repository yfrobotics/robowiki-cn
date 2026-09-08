# 空间描述与变换

!!! note "引言"
    机器人学中几乎所有的计算都涉及"某个量在哪个坐标系下表示"的问题。相机看到的目标点在相机坐标系中，机械臂要抓取它必须转换到基座坐标系；IMU 测得的加速度在机体坐标系中，导航算法需要它在世界坐标系中的分量。本页面系统介绍刚体位姿（Pose）的各种数学表示——旋转矩阵、欧拉角、轴角、四元数——以及它们之间的转换关系和工程上的取舍。


## 位置、姿态与位姿

刚体在三维空间中的完整状态由**位姿**（Pose）描述，它包含两部分：

- **位置**（Position）：刚体上某个参考点相对于参考坐标系原点的平移，用三维向量 \(\mathbf{p} \in \mathbb{R}^3\) 表示
- **姿态**（Orientation）：刚体自身坐标系相对于参考坐标系的转动，需要 3 个独立参数描述

因此空间刚体共有 6 个自由度。位置的表示没有歧义，而姿态的表示方式众多，各有优劣，是本页面的重点。

**记号约定**：本页面采用上标表示参考坐标系，下标表示被描述的对象。例如 \({}^{A}\mathbf{p}_{B}\) 表示坐标系 \(\{B\}\) 的原点在坐标系 \(\{A\}\) 中的位置，\({}^{A}R_{B}\) 表示 \(\{B\}\) 相对于 \(\{A\}\) 的旋转矩阵。


## 旋转矩阵

### 定义与性质

旋转矩阵 \({}^{A}R_{B} \in \mathbb{R}^{3\times 3}\) 的列向量是坐标系 \(\{B\}\) 的三个单位轴在坐标系 \(\{A\}\) 中的表示：

$$ {}^{A}R_{B} = \begin{bmatrix} {}^{A}\hat{x}_B & {}^{A}\hat{y}_B & {}^{A}\hat{z}_B \end{bmatrix} $$

所有三维旋转矩阵构成特殊正交群（Special Orthogonal Group）\(SO(3)\)，满足两个约束：

$$R^T R = I, \qquad \det(R) = +1$$

第一个条件说明 \(R\) 是正交矩阵，其逆等于转置——这是旋转矩阵最有用的性质，因为求逆变换不需要做矩阵求逆运算：

$$ {}^{B}R_{A} = {}^{A}R_{B}^{-1} = {}^{A}R_{B}^{T} $$

第二个条件排除了反射变换（\(\det = -1\) 对应镜像，会改变手性）。9 个元素受到 6 个独立约束（3 个单位长度 + 3 个正交），因此只剩 3 个自由度，与直觉一致。

### 基本旋转

绕三个坐标轴的旋转矩阵是构造复杂旋转的基础：

$$R_x(\theta) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta \\ 0 & \sin\theta & \cos\theta \end{bmatrix}$$

$$R_y(\theta) = \begin{bmatrix} \cos\theta & 0 & \sin\theta \\ 0 & 1 & 0 \\ -\sin\theta & 0 & \cos\theta \end{bmatrix}$$

$$R_z(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

注意 \(R_y\) 中负号的位置与另外两个不同，这是右手坐标系下循环置换的结果，手工推导时极易出错。

### 旋转的复合

旋转矩阵相乘即可复合旋转，但**乘法顺序不可交换**，且顺序的含义取决于旋转是相对固定坐标系还是相对运动坐标系：

- **绕固定轴旋转**（Fixed Angles / 外旋）：新的旋转左乘，\(R = R_3 R_2 R_1\) 表示先执行 \(R_1\)
- **绕运动轴旋转**（Euler Angles / 内旋）：新的旋转右乘，\(R = R_1 R_2 R_3\) 表示先执行 \(R_1\)

一个重要结论：绕固定轴 X-Y-Z 依次旋转 \((\alpha, \beta, \gamma)\)，与绕运动轴 Z-Y-X 依次旋转 \((\gamma, \beta, \alpha)\) 得到完全相同的旋转矩阵。工程中的"欧拉角"歧义大多源于未说明是内旋还是外旋。


## 欧拉角

### 定义与常见约定

欧拉角用三个角度描述姿态，是最直观的表示方式。按旋转轴序列可分为两大类：

- **Proper Euler Angles**：首尾轴相同，如 Z-X-Z、Z-Y-Z，常用于经典力学与陀螺仪分析
- **Tait-Bryan Angles**：三轴各不相同，如 Z-Y-X（航空航天中的偏航-俯仰-滚转），机器人领域最常用

Z-Y-X 约定（也称 RPY，Roll-Pitch-Yaw）在机器人中最为普遍，ROS 的 tf2 即采用此约定：

$$R_{zyx}(\gamma, \beta, \alpha) = R_z(\gamma) R_y(\beta) R_x(\alpha)$$

其中 \(\alpha\) 为滚转（Roll，绕 X 轴）、\(\beta\) 为俯仰（Pitch，绕 Y 轴）、\(\gamma\) 为偏航（Yaw，绕 Z 轴）。展开后：

$$R_{zyx} = \begin{bmatrix} c_\gamma c_\beta & c_\gamma s_\beta s_\alpha - s_\gamma c_\alpha & c_\gamma s_\beta c_\alpha + s_\gamma s_\alpha \\ s_\gamma c_\beta & s_\gamma s_\beta s_\alpha + c_\gamma c_\alpha & s_\gamma s_\beta c_\alpha - c_\gamma s_\alpha \\ -s_\beta & c_\beta s_\alpha & c_\beta c_\alpha \end{bmatrix}$$

其中 \(c_\theta = \cos\theta\)，\(s_\theta = \sin\theta\)。

### 从旋转矩阵反解欧拉角

给定 \(R = [r_{ij}]\)，Z-Y-X 欧拉角的反解为：

$$\beta = \operatorname{atan2}\left(-r_{31}, \sqrt{r_{11}^2 + r_{21}^2}\right)$$

$$\gamma = \operatorname{atan2}(r_{21}/c_\beta,\ r_{11}/c_\beta), \qquad \alpha = \operatorname{atan2}(r_{32}/c_\beta,\ r_{33}/c_\beta)$$

必须使用 `atan2` 而非 `atan`，前者能根据两个参数的符号确定角度所在象限，返回 \((-\pi, \pi]\) 的完整范围。

### 万向节死锁

当 \(\beta = \pm 90°\) 时 \(c_\beta = 0\)，上述反解公式失效。此时 \(R_x\) 与 \(R_z\) 的旋转轴重合，三个自由度退化为两个，只能求出 \(\alpha \pm \gamma\) 的组合值，无法唯一确定 \(\alpha\) 和 \(\gamma\)——这就是**万向节死锁**（Gimbal Lock）。

死锁的后果不只是数学上的奇异：在死锁附近，微小的姿态变化会引起欧拉角的剧烈跳变，导致基于欧拉角的插值与控制出现抖动。这是任何三参数姿态表示的固有缺陷（拓扑学上 \(SO(3)\) 无法用三个参数全局无奇异地参数化），也是姿态插值必须使用四元数或旋转矩阵的根本原因。

**工程结论**：欧拉角适合人机交互（读数、配置文件、示教器显示），不适合作为内部计算与存储的表示。


## 轴角表示与旋转向量

### 等效轴角

Euler 旋转定理指出：任何姿态都可以通过绕某个单位轴 \(\hat{\boldsymbol{\omega}}\) 旋转某个角度 \(\theta\) 得到。这一对参数 \((\hat{\boldsymbol{\omega}}, \theta)\) 称为等效轴角（Equivalent Axis-Angle）表示。

由轴角构造旋转矩阵使用 **Rodrigues 公式**：

$$R = I + \sin\theta\, [\hat{\boldsymbol{\omega}}]_\times + (1 - \cos\theta)\, [\hat{\boldsymbol{\omega}}]_\times^2$$

其中 \([\cdot]_\times\) 是将向量映射为反对称矩阵的算子：

$$[\boldsymbol{\omega}]_\times = \begin{bmatrix} 0 & -\omega_z & \omega_y \\ \omega_z & 0 & -\omega_x \\ -\omega_y & \omega_x & 0 \end{bmatrix}$$

反对称矩阵的作用是把叉积写成矩阵乘法：\([\boldsymbol{a}]_\times \boldsymbol{b} = \boldsymbol{a} \times \boldsymbol{b}\)。

反解时，旋转角与旋转轴分别为：

$$\theta = \arccos\left(\frac{\operatorname{tr}(R) - 1}{2}\right), \qquad \hat{\boldsymbol{\omega}} = \frac{1}{2\sin\theta}\begin{bmatrix} r_{32} - r_{23} \\ r_{13} - r_{31} \\ r_{21} - r_{12} \end{bmatrix}$$

当 \(\theta \to 0\) 时旋转轴不确定（任意轴转 0 度都是恒等变换），当 \(\theta \to \pi\) 时上式分母趋于 0，需要改用其他数值稳定的公式。

### 旋转向量与李代数

把轴与角合并为一个三维向量 \(\boldsymbol{\phi} = \theta \hat{\boldsymbol{\omega}}\)，称为旋转向量（Rotation Vector）。它是 \(SO(3)\) 对应的李代数 \(\mathfrak{so}(3)\) 的元素，与旋转矩阵通过指数/对数映射关联：

$$R = \exp([\boldsymbol{\phi}]_\times), \qquad \boldsymbol{\phi} = \log(R)^\vee$$

李代数是无约束的三维向量空间，因此在优化问题中可以直接对 \(\boldsymbol{\phi}\) 求导、更新，而不必处理 \(R^TR = I\) 这样的流形约束。这正是视觉 SLAM 的后端优化（如 [SLAM](../sensing/slam.md) 中的 BA 与位姿图优化）普遍采用李代数的原因，OpenCV 的 `cv::Rodrigues` 与 Sophus、GTSAM 等库均基于此。


## 四元数

### 定义

单位四元数（Unit Quaternion）用四个参数表示旋转：

$$q = q_w + q_x i + q_y j + q_z k, \qquad q_w^2 + q_x^2 + q_y^2 + q_z^2 = 1$$

它与轴角表示的关系为：

$$q_w = \cos\frac{\theta}{2}, \qquad (q_x, q_y, q_z) = \hat{\boldsymbol{\omega}} \sin\frac{\theta}{2}$$

半角的出现使得 \(q\) 与 \(-q\) 表示同一个旋转（双重覆盖，Double Cover）。实现中通常约定 \(q_w \ge 0\) 以消除歧义，插值时也需要检查两个四元数的点积符号，必要时取反其中之一以走"短弧"。

### 运算

四元数乘法对应旋转的复合（注意不可交换）：

$$q_1 \otimes q_2 = \begin{bmatrix} w_1 w_2 - \mathbf{v}_1 \cdot \mathbf{v}_2 \\ w_1 \mathbf{v}_2 + w_2 \mathbf{v}_1 + \mathbf{v}_1 \times \mathbf{v}_2 \end{bmatrix}$$

其中 \(\mathbf{v} = (q_x, q_y, q_z)\)。单位四元数的逆等于其共轭：\(q^{-1} = q^* = (q_w, -\mathbf{v})\)。

旋转一个向量 \(\mathbf{p}\) 通过夹心积完成（\(\mathbf{p}\) 视为纯四元数 \((0, \mathbf{p})\)）：

$$\mathbf{p}' = q \otimes \mathbf{p} \otimes q^{-1}$$

转换为旋转矩阵：

$$R(q) = \begin{bmatrix} 1 - 2(q_y^2 + q_z^2) & 2(q_x q_y - q_w q_z) & 2(q_x q_z + q_w q_y) \\ 2(q_x q_y + q_w q_z) & 1 - 2(q_x^2 + q_z^2) & 2(q_y q_z - q_w q_x) \\ 2(q_x q_z - q_w q_y) & 2(q_y q_z + q_w q_x) & 1 - 2(q_x^2 + q_y^2) \end{bmatrix}$$

### 姿态插值

四元数最重要的工程价值是插值。球面线性插值（Spherical Linear Interpolation，SLERP）在两个姿态之间生成匀角速度的过渡：

$$\text{slerp}(q_0, q_1, t) = \frac{\sin((1-t)\Omega)}{\sin\Omega} q_0 + \frac{\sin(t\Omega)}{\sin\Omega} q_1, \qquad \cos\Omega = q_0 \cdot q_1$$

当 \(\Omega\) 很小时 \(\sin\Omega \to 0\)，应退化为线性插值加归一化（NLERP）以避免数值问题。

**分量顺序陷阱**：不同库对四元数的分量顺序约定不一致，混用时会产生难以排查的姿态错误。

| 库 / 格式 | 顺序 |
|-----------|------|
| ROS `geometry_msgs/Quaternion`、Eigen 的存储顺序 | \((x, y, z, w)\) |
| Eigen 构造函数 `Quaterniond(w, x, y, z)` | \((w, x, y, z)\) |
| MuJoCo、SciPy 的 `as_quat` 之外的多数数学文献 | \((w, x, y, z)\) |
| SciPy `Rotation.as_quat()`（默认） | \((x, y, z, w)\) |


## 表示方法对比

| 表示 | 参数个数 | 约束 | 奇异性 | 插值 | 复合成本 | 典型用途 |
|------|---------|------|--------|------|---------|---------|
| 旋转矩阵 | 9 | 6 个 | 无 | 需正交化 | 27 次乘法 | 内部计算、变换向量 |
| 欧拉角 | 3 | 无 | 万向节死锁 | 不可靠 | 需转矩阵 | 人机交互、参数配置 |
| 轴角 / 旋转向量 | 3 | 无 | \(\theta = 0, \pi\) | 需转四元数 | 需转矩阵 | 优化变量、标定输出 |
| 四元数 | 4 | 1 个（单位模） | 无（双重覆盖） | SLERP，优秀 | 16 次乘法 | 姿态存储、滤波、插值 |

工程实践中的常见分工：**四元数用于存储与传输，旋转矩阵用于向量变换，李代数用于优化迭代，欧拉角只用于显示给人看**。


## 齐次变换矩阵

### 定义

把旋转与平移合并到一个 \(4 \times 4\) 矩阵中，即得齐次变换矩阵（Homogeneous Transformation Matrix）：

$$ {}^{A}T_{B} = \begin{bmatrix} {}^{A}R_{B} & {}^{A}\mathbf{p}_{B} \\ \mathbf{0}^T & 1 \end{bmatrix} $$

所有这样的矩阵构成特殊欧氏群（Special Euclidean Group）\(SE(3)\)。点的变换写成统一的矩阵乘法（点用齐次坐标 \(\tilde{\mathbf{p}} = [\mathbf{p}^T, 1]^T\) 表示）：

$$ {}^{A}\tilde{\mathbf{p}} = {}^{A}T_{B} \cdot {}^{B}\tilde{\mathbf{p}} $$

齐次表示的价值在于把"先旋转再平移"这个仿射变换统一为线性变换，从而使多级坐标变换可以简单地连乘：

$$ {}^{0}T_{n} = {}^{0}T_{1} \cdot {}^{1}T_{2} \cdots {}^{n-1}T_{n} $$

这正是串联机械臂 [正运动学](forward-kinematics.md) 的计算方式。

### 逆变换

齐次变换矩阵的逆有解析形式，不需要做 \(4 \times 4\) 矩阵求逆：

$$T^{-1} = \begin{bmatrix} R^T & -R^T \mathbf{p} \\ \mathbf{0}^T & 1 \end{bmatrix}$$

注意平移部分是 \(-R^T\mathbf{p}\) 而非 \(-\mathbf{p}\)，这是实现时最常见的错误之一。

### 变换的复合与"读法"

复合变换的下标遵循"相邻抵消"规则，这是检查代码正确性的快速方法：

$$ {}^{A}T_{C} = {}^{A}T_{B} \cdot {}^{B}T_{C} $$

相邻的 \(B\) 抵消，剩下 \({}^{A}T_{C}\)。如果写出的表达式无法这样抵消，则一定存在错误。


## 在 ROS 中的实现

ROS 使用 tf2 维护整个系统的坐标变换树（Transform Tree）。变换树是一棵有向树，每个坐标系只能有一个父坐标系，避免了变换关系的冲突与环路。

```python
import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
from tf2_ros import TransformException


class TfLookupNode(Node):
    def __init__(self):
        super().__init__('tf_lookup')
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.create_timer(1.0, self.on_timer)

    def on_timer(self):
        try:
            # 查询 camera_link 在 base_link 中的位姿
            t = self.buffer.lookup_transform(
                'base_link', 'camera_link', rclpy.time.Time())
        except TransformException as ex:
            self.get_logger().warn(f'变换不可用: {ex}')
            return

        p = t.transform.translation
        q = t.transform.rotation
        self.get_logger().info(
            f'平移 ({p.x:.3f}, {p.y:.3f}, {p.z:.3f}) '
            f'四元数 ({q.x:.3f}, {q.y:.3f}, {q.z:.3f}, {q.w:.3f})')
```

调试坐标变换问题的常用命令：

```bash
# 导出当前变换树为 PDF，检查是否存在断裂或多父节点
ros2 run tf2_tools view_frames

# 打印两个坐标系之间的实时变换
ros2 run tf2_ros tf2_echo base_link camera_link

# 手动发布一个静态变换（x y z yaw pitch roll 父 子）
ros2 run tf2_ros static_transform_publisher 0.1 0 0.2 0 0 0 base_link camera_link
```

REP 105 规定了移动机器人的标准坐标系命名与层级：`map` → `odom` → `base_link` → 各传感器坐标系。其中 `odom` → `base_link` 连续但会漂移，`map` → `odom` 由定位模块发布以修正漂移，不连续但无累积误差。


## Python 计算示例

```python
import numpy as np
from scipy.spatial.transform import Rotation as R, Slerp


def hat(w):
    """向量到反对称矩阵"""
    return np.array([[0, -w[2], w[1]],
                     [w[2], 0, -w[0]],
                     [-w[1], w[0], 0]])


def rodrigues(axis, theta):
    """Rodrigues 公式：轴角 -> 旋转矩阵"""
    axis = axis / np.linalg.norm(axis)
    K = hat(axis)
    return np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * K @ K


def make_transform(rot, trans):
    """组装齐次变换矩阵"""
    T = np.eye(4)
    T[:3, :3] = rot
    T[:3, 3] = trans
    return T


def invert_transform(T):
    """齐次变换的解析逆"""
    Rm, p = T[:3, :3], T[:3, 3]
    return make_transform(Rm.T, -Rm.T @ p)


# 验证 Rodrigues 公式与 SciPy 一致
axis, theta = np.array([0.0, 0.0, 1.0]), np.pi / 4
assert np.allclose(rodrigues(axis, theta),
                   R.from_rotvec(theta * axis).as_matrix())

# 验证逆变换：T @ T^{-1} 应为单位阵
T_ab = make_transform(rodrigues([1, 1, 0], 0.6), [0.3, -0.1, 0.5])
assert np.allclose(T_ab @ invert_transform(T_ab), np.eye(4))

# 欧拉角往返转换（大写字母表示内旋，小写表示外旋）
rpy = [0.3, -0.2, 1.1]
r = R.from_euler('ZYX', rpy[::-1])          # 内旋 Z-Y-X
assert np.allclose(r.as_euler('ZYX')[::-1], rpy)

# 四元数球面插值
key_rots = R.from_euler('ZYX', [[0, 0, 0], [1.5, 0.3, -0.2]])
slerp = Slerp([0.0, 1.0], key_rots)
mid = slerp(0.5)
print('中间姿态四元数 (x,y,z,w):', np.round(mid.as_quat(), 4))
```


## 常见错误

- **左乘与右乘混淆**：\(R_{new} = R_\delta R\) 表示在固定坐标系下施加增量，\(R_{new} = R R_\delta\) 表示在物体自身坐标系下施加增量，两者结果不同。
- **齐次变换求逆时忘记 \(-R^T\mathbf{p}\)**：直接对平移取负是错误的。
- **四元数分量顺序不一致**：跨库传递时必须显式确认是 \((w,x,y,z)\) 还是 \((x,y,z,w)\)。
- **旋转矩阵累积误差**：长时间连乘后 \(R\) 会偏离正交，应定期通过 SVD 或 Gram-Schmidt 重新正交化，或改用四元数并周期性归一化。
- **欧拉角插值**：在两个欧拉角之间做线性插值不会得到匀速旋转，跨越 \(\pm\pi\) 边界时还会绕远路，应转为四元数后使用 SLERP。
- **标定外参的方向搞反**：\({}^{cam}T_{base}\) 与 \({}^{base}T_{cam}\) 互为逆，标定工具输出的是哪一个必须查阅文档确认。


## 参考资料

1. Craig, J. J. (2005). *Introduction to Robotics: Mechanics and Control* (3rd ed.). Pearson Prentice Hall. — 第 2 章系统讲解空间描述与变换。
2. Lynch, K. M. & Park, F. C. (2017). *Modern Robotics: Mechanics, Planning, and Control*. Cambridge University Press. — 第 3 章以旋量与指数坐标讲解刚体运动。
3. Solà, J., Deray, J. & Atchuthan, D. (2018). A Micro Lie Theory for State Estimation in Robotics. *arXiv:1812.01537*. — 面向机器人状态估计的李群李代数简明教程。
4. Shoemake, K. (1985). Animating Rotation with Quaternion Curves. *SIGGRAPH Computer Graphics*, 19(3), 245-254. — SLERP 的原始论文。
5. Foote, T. (2013). tf: The Transform Library. *IEEE International Conference on Technologies for Practical Robot Applications (TePRA)*.
6. [REP 105 — Coordinate Frames for Mobile Platforms](https://www.ros.org/reps/rep-0105.html)
7. 高翔, 张涛 (2017). 《视觉SLAM十四讲：从理论到实践》. 电子工业出版社. — 第 3、4 讲详述李群李代数在位姿表示中的应用。
