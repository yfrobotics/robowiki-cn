# 机构与运动学

!!! note "引言"
    运动学（Kinematics）与动力学（Dynamics）是机器人学的力学基础。运动学研究机器人各连杆之间的几何关系，回答"关节转到某个角度时末端在哪里"以及它的反问题；动力学则引入质量、惯量与力，回答"要产生某个运动需要多大的关节力矩"。控制、规划、仿真三大方向都建立在这套模型之上——没有正确的运动学模型，路径规划得到的轨迹无法转换为关节指令；没有动力学模型，高速运动下的轨迹跟踪精度会迅速恶化。


## 为什么单独成章

本维基的 [控制](../control/index.md) 章节讨论的是控制系统建模（传递函数、状态空间、系统辨识），处理的是"从输入信号到输出信号"的映射关系；而本章讨论的是机器人本体的几何与力学模型，处理的是"从关节空间到笛卡尔空间"的映射关系。两者是不同层次的模型，共同构成完整的机器人控制体系：

```
任务描述（抓取杯子）
      ↓  逆运动学 / 运动规划
关节轨迹 q(t), q̇(t), q̈(t)
      ↓  逆动力学 / 反馈控制
关节力矩 τ(t)
      ↓  电机驱动
机器人运动
```


## 核心问题

机器人运动学与动力学围绕以下几个基本问题展开：

| 问题 | 输入 | 输出 | 对应页面 |
|------|------|------|---------|
| 位姿描述 | 坐标系定义 | 旋转与平移的数学表示 | [空间描述与变换](spatial-transformation.md) |
| 正运动学（Forward Kinematics） | 关节变量 \(\mathbf{q}\) | 末端位姿 \(T\) | [正运动学](forward-kinematics.md) |
| 逆运动学（Inverse Kinematics） | 末端位姿 \(T\) | 关节变量 \(\mathbf{q}\) | [逆运动学](inverse-kinematics.md) |
| 速度与静力映射 | 关节速度 \(\dot{\mathbf{q}}\) | 末端速度 \(\mathbf{v}\) | [雅可比矩阵与奇异性](jacobian.md) |
| 正动力学（Forward Dynamics） | 关节力矩 \(\boldsymbol{\tau}\) | 关节加速度 \(\ddot{\mathbf{q}}\) | [机器人动力学](dynamics.md) |
| 逆动力学（Inverse Dynamics） | 关节加速度 \(\ddot{\mathbf{q}}\) | 关节力矩 \(\boldsymbol{\tau}\) | [机器人动力学](dynamics.md) |
| 轨迹生成 | 路径点与时间约束 | 光滑的时间函数 \(\mathbf{q}(t)\) | [轨迹生成](trajectory-generation.md) |

其中正运动学与逆动力学是"容易"的方向：正运动学只需矩阵连乘，逆动力学有 \(O(n)\) 的递推算法。逆运动学与正动力学是"困难"的方向：逆运动学可能无解、多解或需要迭代求解，正动力学需要求解质量矩阵的逆。


## 自由度与机构类型

自由度（Degrees of Freedom，DOF）是描述机构位形所需的独立变量个数。对于空间机构，Grübler 公式给出：

$$\text{DOF} = 6(N - 1 - J) + \sum_{i=1}^{J} f_i$$

其中 \(N\) 为连杆数（含基座），\(J\) 为关节数，\(f_i\) 为第 \(i\) 个关节的自由度。平面机构中系数 6 替换为 3。

以此可以快速判断常见机构：

- **六轴串联机械臂**：\(N = 7\)，\(J = 6\)，均为转动副（\(f_i = 1\)），DOF \(= 6(7-1-6) + 6 = 6\)。恰好能实现空间任意位姿，是工业机械臂的主流构型。
- **七轴协作机械臂**：DOF \(= 7\)，多出一个冗余自由度（Redundancy），可以在末端位姿不变的前提下调整肘部姿态以避障或规避奇异位形。
- **Delta 并联机器人**：三条支链的闭链机构，DOF \(= 3\)（纯平移），刚度高、运动惯量小，用于高速分拣。
- **差速驱动移动底盘**：位形为 \((x, y, \theta)\) 共 3 维，但只有 2 个控制输入，属于非完整约束（Nonholonomic Constraint）系统，其规划问题在 [运动规划](../planning/motionplanning.md) 中讨论。

按拓扑结构分类：

| 类型 | 结构 | 优点 | 缺点 | 典型代表 |
|------|------|------|------|---------|
| 串联（Serial） | 开链 | 工作空间大、正运动学简单 | 刚度低、误差累积 | UR5、Franka Panda |
| 并联（Parallel） | 闭链 | 刚度高、精度高、动态性能好 | 工作空间小、正运动学困难 | Delta、Stewart 平台 |
| 混联（Hybrid） | 串并结合 | 兼顾工作空间与刚度 | 建模复杂 | 部分人形机器人腿部 |
| 移动（Mobile） | 带浮动基座 | 工作空间无界 | 存在非完整约束 | AGV、四足机器人 |


## 与其他章节的关系

- [控制](../control/index.md)：动力学模型是计算力矩控制（Computed Torque Control）、阻抗控制与 [模型预测控制](../control/mpc/mpc.md) 的前提。
- [规划](../planning/index.md)：[运动规划](../planning/motionplanning.md) 在构型空间中搜索，构型空间的维度即由机构自由度决定；碰撞检测需要正运动学计算各连杆的位姿。
- [三维视觉](../cv/3d-vision.md) 与 [SLAM](../sensing/slam.md)：手眼标定、相机位姿估计使用与本章相同的 \(SE(3)\) 表示与李群工具。
- [仿真](../simulation/index.md)：[PyBullet](../simulation/pybullet.md)、[MuJoCo](../simulation/mujoco.md)、[Robotics Toolbox](../simulation/robotics-toolbox.md) 均提供运动学与动力学求解接口，是验证本章公式的便捷工具。
- [ROS](../ros/index.md)：URDF 描述文件承载运动学参数，tf2 维护坐标变换树，MoveIt 封装了逆运动学与运动规划。


## 常用软件工具

| 工具 | 语言 | 特点 |
|------|------|------|
| [Pinocchio](https://stack-of-tasks.github.io/pinocchio/) | C++/Python | 高效刚体动力学库，支持解析导数，广泛用于全身控制与最优控制 |
| [KDL](https://www.orocos.org/kdl.html) | C++ | Orocos 运动学动力学库，ROS 生态默认求解器之一 |
| [Robotics Toolbox for Python](https://petercorke.github.io/robotics-toolbox-python/) | Python | Peter Corke 教材配套工具箱，适合教学与快速验证 |
| [RBDL](https://rbdl.github.io/) | C++ | 刚体动力学库，实现 ABA、RNEA 等经典算法 |
| [Drake](https://drake.mit.edu/) | C++/Python | MIT 开发，多体动力学 + 轨迹优化 + 系统框架 |
| [SymPy](https://www.sympy.org/) | Python | 符号推导运动学与动力学方程，便于验证手工推导 |


## 参考资料

1. Craig, J. J. (2005). *Introduction to Robotics: Mechanics and Control* (3rd ed.). Pearson Prentice Hall. — 运动学与动力学的经典入门教材。
2. Lynch, K. M. & Park, F. C. (2017). *Modern Robotics: Mechanics, Planning, and Control*. Cambridge University Press. — 采用旋量与指数积体系，[配套网站](http://modernrobotics.org/) 提供免费电子版与代码。
3. Siciliano, B., Sciavicco, L., Villani, L. & Oriolo, G. (2010). *Robotics: Modelling, Planning and Control*. Springer.
4. Murray, R. M., Li, Z. & Sastry, S. S. (1994). *A Mathematical Introduction to Robotic Manipulation*. CRC Press.
5. Featherstone, R. (2008). *Rigid Body Dynamics Algorithms*. Springer. — 空间向量代数与高效动力学算法的权威著作。
