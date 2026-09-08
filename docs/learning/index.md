# 机器人学习

!!! note "引言"
    机器学习为机器人提供了一条与传统建模方法互补的路径：当环境难以精确建模、任务难以用规则穷举、或者感知输入是图像点云这类高维数据时，从数据中学习往往比手工设计更有效。本章涵盖机器学习基础、强化学习与深度学习三条主线，并重点关注它们在机器人系统中的落地方式——包括仿真到现实的迁移、边缘设备上的部署以及与 ROS 系统的集成。


## 三条主线

| 方向 | 解决的问题 | 在机器人中的典型应用 |
|------|-----------|--------------------|
| [机器学习基础](ml.md) | 从数据中学习规律并预测 | 传感器标定、故障诊断、参数辨识、状态分类 |
| [强化学习](rl.md) | 通过试错学习序贯决策策略 | 运动控制、灵巧操作、导航、四足与人形机器人步态 |
| [深度学习](dl.md) | 从高维原始数据学习特征表示 | 目标检测、语义分割、位姿估计、端到端策略 |

三者并非互斥：现代机器人学习方法大多是它们的组合，例如深度强化学习用神经网络表示策略，模仿学习用监督学习拟合专家演示。


## 与传统方法的关系

学习方法不是要替代 [控制](../control/index.md) 与 [规划](../planning/index.md)，而是填补它们难以覆盖的部分：

| 场景 | 更适合的方法 | 原因 |
|------|-------------|------|
| 已知动力学的轨迹跟踪 | [模型预测控制](../control/mpc/mpc.md)、[LQR](../control/lqr/lqr.md) | 有稳定性保证，无需数据，可解释 |
| 结构化环境中的路径规划 | [采样规划](../planning/pathplanning.md) | 完备性保证，可验证 |
| 富接触的灵巧操作 | 强化学习、模仿学习 | 接触动力学难以建模，难以手工设计策略 |
| 从图像识别物体与位姿 | 深度学习 | 高维输入，手工特征远不如学习特征 |
| 非结构化环境的开放任务 | 视觉-语言-动作模型 | 需要常识与泛化能力 |

工程上最稳健的做法通常是**分层混合**：用学习方法处理感知与高层决策，用传统控制方法处理底层的实时闭环，两者之间通过明确的接口（如末端位姿指令或关节轨迹）解耦。这样既利用了学习的泛化能力，又保留了控制层的安全保障。


## 强化学习专题

- [强化学习](rl.md) — 马尔可夫决策过程、值函数与策略、探索与利用、核心理论框架
- [强化学习算法与实践](rl-algorithms-practice.md) — DQN、PPO、SAC、TD3 等主流算法与 Stable-Baselines3 代码实践
- [强化学习在机器人中的部署](rl-robotics-deployment.md) — Sim-to-Real 迁移、域随机化、安全约束、Jetson 部署与 ROS 2 集成
- [强化学习进阶范式](rl-advanced-paradigms.md) — 基于模型的 RL、离线 RL、多智能体 RL、分层 RL、逆强化学习
- [强化学习参考资料](rl-full-reference.md) — 教材、论文、库、仿真环境与算法选型指南


## 深度学习专题

- [深度学习](dl.md) — 神经网络基础、卷积网络与 Transformer、在机器人中的关键方法
- [基础模型](dl-foundation-models.md) — 视觉基础模型、大语言模型、视觉-语言-动作模型与具身智能
- [训练与部署](dl-training-deployment.md) — 分布式训练、混合精度、模型压缩、TensorRT 与边缘推理
- [机器人深度学习流水线](dl-robotics-pipelines.md) — 感知流水线、模仿学习、端到端方法、数据采集与持续学习
- [深度学习参考资料](dl-full-reference.md) — 论文、教材、框架、数据集与硬件选型


## 学习方法的工程约束

在机器人上部署学习模型时，有几个约束与纯软件场景显著不同：

**实时性**：控制回路通常要求 100 Hz 至 1 kHz，留给推理的时间只有毫秒级。这直接限制了模型规模，也决定了推理必须在边缘设备（见 [Jetson](../jetson/index.md)）上完成而非云端。

**安全性**：策略输出的错误动作会造成物理损坏或人员伤害。实践中通常在学习策略外部套一层安全层：限制关节速度与力矩、检查工作空间边界、监测碰撞，必要时切换到安全的备用控制器。

**数据成本**：真实机器人数据的采集成本远高于图像或文本数据——每条轨迹都需要实际运行时间，且硬件会磨损。这是[仿真](../simulation/index.md)在机器人学习中占据核心地位的原因，也催生了域随机化、Sim-to-Real 等一整套方法。

**分布偏移**：训练时的数据分布与部署环境几乎必然不同（光照、物体、磨损、温度）。模仿学习中还存在复合误差问题：策略的微小偏差会把系统带到训练数据未覆盖的状态，导致误差累积。


## 相关章节

- [视觉](../cv/index.md)：目标检测、分割、位姿估计等具体的深度学习应用
- [感知](../sensing/index.md)：传感器数据的预处理与融合，是学习模型的输入来源
- [仿真](../simulation/index.md)：[MuJoCo](../simulation/mujoco.md)、[PyBullet](../simulation/pybullet.md)、Isaac Lab 提供强化学习训练环境
- [控制](../control/nn/nn.md)：神经网络控制，学习方法在控制层的直接应用
- [数据集](../database/dataset.md)：机器人领域公开数据集汇总


## 参考资料

1. Sutton, R. S. & Barto, A. G. (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press. — [免费在线版本](http://incompleteideas.net/book/the-book.html)
2. Goodfellow, I., Bengio, Y. & Courville, A. (2016). *Deep Learning*. MIT Press. — [免费在线版本](https://www.deeplearningbook.org/)
3. Bishop, C. M. (2006). *Pattern Recognition and Machine Learning*. Springer.
4. Levine, S., Finn, C., Darrell, T. & Abbeel, P. (2016). End-to-End Training of Deep Visuomotor Policies. *Journal of Machine Learning Research*, 17(1), 1334-1373.
5. Ibarz, J., et al. (2021). How to Train Your Robot with Deep Reinforcement Learning: Lessons We Have Learned. *International Journal of Robotics Research*, 40(4-5), 698-721.
6. 周志华 (2016). 《机器学习》. 清华大学出版社.
