# 局部规划器

!!! note "引言"
    局部规划器（Local Planner，在 Nav2 中称为 Controller）位于导航栈的最末端：它接收全局路径与实时代价地图，输出直接驱动轮子的速度指令。它同时要做三件相互冲突的事——跟上全局路径、避开突然出现的障碍、生成机器人执行得了的平滑运动。这三者的权衡由一堆权重参数控制，也正因如此，局部规划器是整个导航栈中最难调、也最能决定机器人「气质」的模块。


## 共同的问题结构

不同的局部规划器差别很大，但都在回答同一个问题：**在当前状态下，接下来一小段时间该以什么速度运动？**

它们的共同要素是：

- **可行速度集合**：由机器人的运动学（差速 / 全向 / 阿克曼）与动力学限制（最大加减速度）确定
- **前向仿真**：用运动模型把候选速度推演成若干秒后的轨迹
- **代价函数**：对每条轨迹打分，通常包含到全局路径的距离、到目标的距离、障碍代价、速度大小等项
- **选择与执行**：取最优轨迹的第一段速度下发，下个周期重新计算

这本质上是一个**滚动时域优化**问题，与 [模型预测控制](../control/mpc/mpc.md) 是同一框架。各方法的差别在于：候选轨迹怎么产生（采样还是优化）、代价函数怎么设计、优化怎么求解。


## 主流方法对比

| 规划器 | 原理 | 支持倒车 | 阿克曼 | 计算量 | 特点 |
|--------|------|---------|--------|--------|------|
| DWB（DWA） | 速度空间采样 | 有限 | 否 | 低 | 成熟稳定，参数直观，Nav2 默认 |
| TEB | 时间弹性带优化 | 是 | 是 | 高 | 轨迹平滑，支持复杂运动学，参数极多 |
| MPPI | 采样式模型预测控制 | 是 | 是 | 中高（需并行） | 代价函数可任意设计，行为自然 |
| Regulated Pure Pursuit | 几何跟踪 + 限速规则 | 否 | 是 | 极低 | 极其稳定可预测，但避障能力弱 |
| Graceful Controller | 平滑控制律 | 否 | 否 | 极低 | 适合末端对接、精确停靠 |

### DWB / DWA

动态窗口法在速度空间 \((v, \omega)\) 中均匀采样，对每个采样点做前向仿真，再用一组打分插件（Critic）评价。算法本身的推导见 [运动规划](motionplanning.md)，这里关注调参。

DWB 的代价函数由若干 Critic 加权而成，最关键的四个：

```yaml
controller_server:
  ros__parameters:
    FollowPath:
      plugin: "dwb_core::DWBLocalPlanner"
      # 速度与加速度限制：必须与实际底盘能力一致
      min_vel_x: 0.0
      max_vel_x: 0.5
      max_vel_theta: 1.2
      acc_lim_x: 2.5
      acc_lim_theta: 3.2
      # 前向仿真
      sim_time: 1.7          # 仿真时长，决定"看多远"
      vx_samples: 20         # 线速度采样数
      vtheta_samples: 40     # 角速度采样数
      # 打分插件与权重
      critics: ["RotateToGoal", "Oscillation", "BaseObstacle",
                "GoalAlign", "PathAlign", "PathDist", "GoalDist"]
      PathAlign.scale: 32.0    # 朝向与路径一致
      PathDist.scale: 32.0     # 贴近全局路径
      GoalAlign.scale: 24.0    # 朝向目标
      GoalDist.scale: 24.0     # 靠近目标
      BaseObstacle.scale: 0.02 # 障碍代价
```

调参的核心是几个权重的相对大小：

- **`PathDist` 与 `GoalDist` 的比值**决定机器人是「老实沿路径走」还是「抄近道奔目标」。前者大则贴合路径，后者大则容易切内角撞墙。
- **`BaseObstacle.scale` 通常很小**（0.02 量级），因为代价地图的代价值本身就是 0–254 的大数，权重再大会压过其他所有项，机器人会为了远离障碍而完全不跟随路径。
- **`sim_time` 决定前瞻距离**。太短则机器人「近视」，来不及绕开障碍；太长则在动态环境中做无用功，且窄空间里所有轨迹都会撞上东西导致无解。1.5–2.0 s 是常见范围。

**振荡问题**是 DWA 最典型的毛病：机器人在两个同样好的选择之间反复横跳（比如绕障碍从左还是从右）。`Oscillation` critic 通过禁止短时间内反向来抑制，参数 `oscillation_reset_dist` 控制走多远后解除禁令。

### TEB

时间弹性带（Timed Elastic Band）把轨迹表示成一串带时间戳的位姿，然后用图优化同时调整位姿与时间间隔，使轨迹在「快」「远离障碍」「满足运动学约束」之间取得平衡。它的目标函数是一系列约束项的加权和，用 g2o 求解。

TEB 的优势是**原生支持复杂运动学**：通过设置最小转弯半径可以描述阿克曼底盘，通过允许负速度可以支持倒车。它还能同时维护多条拓扑不同的候选轨迹（从障碍左侧还是右侧绕），避免陷入局部最优。

代价是参数极多（数十个权重）且相互耦合，调参困难。常见起点：

```yaml
FollowPath:
  plugin: "teb_local_planner::TebLocalPlannerROS"
  min_turning_radius: 0.0        # 0 表示可原地转向；阿克曼底盘填实际值
  max_vel_x_backwards: 0.2       # 设为 0 可禁止倒车
  weight_max_vel_x: 2.0
  weight_acc_lim_x: 1.0
  weight_kinematics_nh: 1000.0   # 非完整约束权重，差速底盘应很大
  weight_optimaltime: 1.0        # 增大则更激进地追求时间最优
  weight_obstacle: 50.0
  min_obstacle_dist: 0.27        # 应与内切半径匹配
  enable_homotopy_class_planning: true
```

`min_obstacle_dist` 与代价地图的膨胀参数容易冲突：TEB 自己维护到障碍的距离约束，若同时又有很大的膨胀代价，两套机制会互相打架。使用 TEB 时通常把膨胀半径设得较小，把避障主要交给 TEB。

### MPPI

模型预测路径积分（Model Predictive Path Integral）是 Nav2 中较新的控制器。它采样大量带噪声的控制序列，对每条序列做前向仿真并按代价加权，用加权平均得到最优控制——本质上是一种无梯度的随机优化。

MPPI 的价值在于**代价函数可以任意设计**，不要求可微，因此可以直接把「远离障碍」「跟随路径」「保持朝向」「优先前进」等目标写成任意形式的惩罚项。它生成的运动通常比 DWA 更自然平滑，也支持倒车与阿克曼约束。

代价是计算量大——需要同时仿真上千条轨迹。Nav2 的实现做了向量化优化，在现代 CPU 上可以达到 20–30 Hz，但在算力有限的嵌入式平台上仍是负担。

```yaml
FollowPath:
  plugin: "nav2_mppi_controller::MPPIController"
  time_steps: 56
  model_dt: 0.05
  batch_size: 2000        # 采样轨迹数，直接决定计算量
  vx_std: 0.2             # 采样噪声标准差，越大探索越广
  wz_std: 0.4
  temperature: 0.3        # 越小越"贪心"地采纳最优轨迹
  critics: ["ConstraintCritic", "ObstaclesCritic", "GoalCritic",
            "GoalAngleCritic", "PathAlignCritic", "PathFollowCritic",
            "PathAngleCritic", "PreferForwardCritic"]
```

### Regulated Pure Pursuit

纯跟踪（Pure Pursuit）是最简单的路径跟踪律：在全局路径上取一个前视距离处的目标点，计算通过该点的圆弧，按圆弧曲率给出角速度。

$$\omega = \frac{2 v \sin\alpha}{L_d}$$

其中 \(L_d\) 为前视距离，\(\alpha\) 为目标点相对机器人朝向的角度。

Regulated Pure Pursuit（RPP）在此基础上加入了几条限速规则：曲率大时减速、接近障碍时减速、按速度动态调整前视距离。

它的特点是**极其稳定和可预测**——没有采样、没有优化，同样的输入永远给出同样的输出。这在需要行为可复现的场景（如安全认证、产线固定路线）中很有价值。代价是**几乎没有避障能力**：它只跟随全局路径，遇到路径上的新障碍只能减速停下，等待全局重规划。

因此 RPP 适合的场景是：路径由全局规划器频繁重规划、环境相对结构化、对运动平滑性和可预测性要求高于对灵活避障的要求。


## 选型建议

| 场景 | 推荐 | 理由 |
|------|------|------|
| 室内差速底盘，通用场景 | DWB | 成熟、参数直观、社区经验多 |
| 阿克曼底盘 / 需要倒车 | TEB 或 MPPI | DWB 不支持这两类运动学 |
| 狭窄空间、复杂机动 | TEB | 拓扑规划能找到 DWA 找不到的解 |
| 行人密集的动态环境 | MPPI | 代价函数可加入行人预测项 |
| 固定路线、要求可预测 | Regulated Pure Pursuit | 行为确定，易于验证 |
| 精确停靠对接 | Graceful Controller | 专为末端收敛设计 |
| 算力极其受限 | Regulated Pure Pursuit | 计算量最小 |

一条实用建议：**先用 DWB 把整条链路跑通，再考虑换控制器**。局部规划器的问题常常并不出在它自己身上——代价地图配错、定位不稳、足迹不准都会表现为「局部规划器工作不正常」。在一个已知能工作的基线上替换，才能判断换控制器是否真的带来改善。


## 调参方法

按以下顺序整定，每步只改一类参数：

1. **速度与加速度限制**。这些不是调参对象，而是机器人的物理事实，必须与实际能力一致。填得比实际大，规划器会输出执行不了的指令，导致跟踪误差与振荡；填得比实际小，机器人会不必要地慢。用手动遥控实测最大速度与加减速能力。

2. **前向仿真时长 / 前视距离**。在空旷场地上让机器人直线走，然后横向放一个障碍，观察它是否能平顺绕开。绕不开就加大，绕得过早、路径迂回就减小。

3. **路径跟踪权重**。让机器人走一条带转弯的路径，观察是否切内角。切内角就加大 `PathDist`/`PathAlign` 类权重。

4. **障碍权重**。放置障碍观察避让距离。贴得太近就加大，绕得太远、甚至为了避障放弃跟随路径就减小。

5. **目标收敛**。检查到达目标时的停止精度与朝向精度，调整 `xy_goal_tolerance` 与 `yaw_goal_tolerance`。**容差过小是机器人在终点反复微调的常见原因**——底盘的最小可执行速度决定了定位精度的下限，容差必须大于这个下限。

调参过程中把这些量画出来会快得多：

```bash
# 用 PlotJuggler 同时观察指令速度与实际速度，判断是否跟踪不上
ros2 run plotjuggler plotjuggler
# 订阅 /cmd_vel 与 /odom，对比 twist 分量

# 观察局部规划器的实际输出频率
ros2 topic hz /cmd_vel

# 查看候选轨迹（RViz 中显示 DWB 的 /marked_trajectories）
ros2 topic echo /local_plan --once
```


## 常见问题

- **速度指令抖动**：候选轨迹得分接近导致每周期选择不同。加大 `Oscillation` 类抑制，或降低采样密度使选择更稳定。
- **跟不上指令速度**：加速度限制填得过大，或底盘控制器本身响应慢。对比 `/cmd_vel` 与 `/odom` 中的速度即可确认。
- **靠近目标时反复来回**：目标容差小于底盘的最小可控运动量。放宽容差，或在最后阶段切换到专门的对接控制器。
- **转弯时切内角**：路径跟踪权重不足，或前视距离过大。
- **在障碍前完全停住不绕**：所有候选轨迹都被判为碰撞。检查足迹是否过大、膨胀是否过强；也可能是 `sim_time` 太长，导致远处的障碍污染了所有轨迹的评分。
- **倒车时撞到东西**：多数机器人后方无传感器覆盖。若非必要应禁止倒车（TEB 中设 `max_vel_x_backwards: 0`）。
- **换了控制器后行为反而更差**：新控制器的参数是默认值，而旧控制器已经调过。不要在未调参的情况下比较两个控制器。


## 参考资料

1. Fox, D., Burgard, W. & Thrun, S. (1997). The Dynamic Window Approach to Collision Avoidance. *IEEE Robotics and Automation Magazine*, 4(1), 23-33.
2. Rösmann, C., Hoffmann, F. & Bertram, T. (2017). Integrated Online Trajectory Planning and Optimization in Distinctive Topologies. *Robotics and Autonomous Systems*, 88, 142-153. — TEB 的拓扑规划。
3. Williams, G., Aldrich, A. & Theodorou, E. A. (2017). Model Predictive Path Integral Control: From Theory to Parallel Computation. *Journal of Guidance, Control, and Dynamics*, 40(2), 344-357.
4. Macenski, S., Singh, S., Martín, F. & Ginés, J. (2023). Regulated Pure Pursuit for Robot Path Tracking. *Autonomous Robots*, 47, 685-694.
5. Coulter, R. C. (1992). Implementation of the Pure Pursuit Path Tracking Algorithm. *Technical Report CMU-RI-TR-92-01*, Carnegie Mellon University.
6. [Nav2 Controller 配置文档](https://docs.nav2.org/configuration/packages/configuring-dwb-controller.html)
