# MoveIt 实践

!!! note "引言"
    MoveIt 是 ROS 生态中最主流的机械臂运动规划框架，把逆运动学求解、碰撞检测、运动规划、轨迹时间参数化与执行控制整合在一套接口之下。它的价值在于让开发者不必自己拼装这些组件，代价是配置项繁多、失败信息晦涩。本页面按实际使用顺序梳理配置流程、核心概念与常见问题的排查方法，重点放在文档里不容易找到的工程细节上。


## 系统组成

MoveIt 的核心是 `move_group` 节点，它把各个功能模块组织在一起：

| 组件 | 职责 | 可替换实现 |
|------|------|-----------|
| 运动学求解器 | 求解逆运动学 | KDL、TRAC-IK、IKFast、BioIK |
| 规划器 | 在构型空间中搜索无碰撞路径 | OMPL、CHOMP、STOMP、Pilz |
| 碰撞检测 | 判断构型是否碰撞 | FCL、Bullet |
| 规划场景 | 维护环境与物体的几何 | PlanningSceneMonitor |
| 轨迹处理 | 时间参数化与平滑 | TOTG、Ruckig |
| 控制器接口 | 把轨迹下发给硬件 | ros2_control 的 JointTrajectoryController |

各组件的选型直接影响成败率与规划时间，后文逐一说明。

MoveIt 2 是 ROS 2 版本，API 与 MoveIt 1 差别较大（`moveit_cpp` / `MoveItPy` 取代了 `move_group_interface` 的部分用法）。新项目应直接使用 MoveIt 2。


## 配置流程

### 从 URDF 到 SRDF

MoveIt 的配置以 [URDF](../kinematics/forward-kinematics.md) 为输入，通过 Setup Assistant 生成 SRDF（Semantic Robot Description Format）及一组配置文件：

```bash
ros2 launch moveit_setup_assistant setup_assistant.launch.py
```

SRDF 补充了 URDF 中没有的语义信息：

- **规划组（Planning Group）**：哪些关节构成一条运动链，如 `manipulator`（6 个臂关节）、`gripper`（夹爪关节）
- **末端执行器（End Effector）**：夹爪与父链接的关联关系
- **预定义位姿（Named Pose）**：`home`、`ready` 等常用构型
- **自碰撞矩阵（ACM）**：哪些连杆对之间无需检测碰撞

**自碰撞矩阵是最值得关注的一项**。Setup Assistant 通过随机采样大量构型，统计哪些连杆对从不碰撞（Never）、总是碰撞（Always，通常是相邻连杆）、默认碰撞（Default，零位时就接触），把它们标记为禁用检测。这能把碰撞检测的计算量减少一个数量级。

采样数量默认 10000，对自由度多或结构复杂的机器人应提高到 50000 以上——采样不足会遗漏某些位形下的碰撞对，导致规划出的轨迹在实机上撞到自己。反过来，过度禁用同样危险：如果把一对实际可能碰撞的连杆标为 Never，MoveIt 就永远不会阻止它们相撞。

### 关键配置文件

```
config/
├── robot.srdf                    # 规划组、末端、ACM、预定义位姿
├── kinematics.yaml               # 每个规划组的 IK 求解器与参数
├── joint_limits.yaml             # 速度/加速度限制（覆盖 URDF 中的值）
├── ompl_planning.yaml            # OMPL 各规划器的参数
├── moveit_controllers.yaml       # 控制器名称与关节映射
└── pilz_cartesian_limits.yaml    # Pilz 规划器的笛卡尔限制
```

`joint_limits.yaml` 中的 `max_acceleration` 必须显式设置——URDF 的 `<limit>` 标签只有 `velocity` 和 `effort`，没有加速度。缺失时 MoveIt 会用默认值，常常导致轨迹过于保守或过于激进：

```yaml
joint_limits:
  joint1:
    has_velocity_limits: true
    max_velocity: 2.0
    has_acceleration_limits: true
    max_acceleration: 3.0
```

### 运动学求解器选型

`kinematics.yaml` 中的求解器选择对成功率影响显著：

```yaml
manipulator:
  # 默认的 KDL：通用但在关节限位附近成功率一般
  # kinematics_solver: kdl_kinematics_plugin/KDLKinematicsPlugin

  # TRAC-IK：并行运行两种求解器取先收敛者，推荐作为默认
  kinematics_solver: trac_ik_kinematics_plugin/TRAC_IKKinematicsPlugin
  kinematics_solver_timeout: 0.05
  kinematics_solver_attempts: 3
  solve_type: Distance          # Speed 最快 / Distance 解最接近当前构型
                                # Manipulation1/2 兼顾可操作度
```

`solve_type: Distance` 在轨迹跟踪中尤其重要：它返回与当前构型关节距离最小的解，避免了 [逆运动学](../kinematics/inverse-kinematics.md) 中提到的构型跳变问题。

若机构满足解析解条件，用 IKFast 生成的求解器速度可再快一到两个数量级，且能返回全部解，适合需要遍历大量候选抓取位姿的场景。

### 规划器选型

| 规划器 | 类型 | 特点 | 适用场景 |
|--------|------|------|---------|
| OMPL / RRTConnect | 采样 | 默认选择，速度快，路径不平滑 | 通用自由空间规划 |
| OMPL / RRT* | 采样 | 渐近最优，需要更长时间 | 对路径质量有要求时 |
| OMPL / BiTRRT | 采样 | 处理代价空间 | 带软约束的规划 |
| CHOMP | 优化 | 输出平滑轨迹，需要好的初值 | 对轨迹平滑度要求高 |
| STOMP | 优化 | 随机优化，可处理不可微代价 | 含复杂代价函数 |
| Pilz Industrial Motion | 解析 | 生成标准的 PTP/LIN/CIRC 运动 | 工业场景的确定性运动 |

**Pilz 规划器值得特别注意**：它不做采样搜索，而是直接生成点到点、直线、圆弧三种标准运动，行为完全可预测可重复。这正是工业应用需要的——采样规划器每次运行可能给出不同的路径，在产线上是不可接受的。

RRTConnect 输出的路径通常包含冗余的绕行，必须经过路径简化（MoveIt 默认启用）。即使简化后，采样路径在关节空间中仍可能有不必要的大幅摆动，这是采样方法的固有特性。


## 规划场景与碰撞检测

规划场景（Planning Scene）维护机器人周围的世界模型，是碰撞检测的依据。

### 添加环境物体

```python
from moveit.planning import MoveItPy, PlanningSceneMonitor
from geometry_msgs.msg import Pose
from shape_msgs.msg import SolidPrimitive
from moveit_msgs.msg import CollisionObject


def add_table(scene_monitor, frame_id='base_link'):
    """向规划场景加入一张桌子"""
    obj = CollisionObject()
    obj.header.frame_id = frame_id
    obj.id = 'table'

    box = SolidPrimitive()
    box.type = SolidPrimitive.BOX
    box.dimensions = [1.2, 0.8, 0.04]

    pose = Pose()
    pose.position.x = 0.5
    pose.position.z = -0.02          # 桌面略低于机器人基座
    pose.orientation.w = 1.0

    obj.primitives = [box]
    obj.primitive_poses = [pose]
    obj.operation = CollisionObject.ADD

    with scene_monitor.read_write() as scene:
        scene.apply_collision_object(obj)
        scene.current_state.update()
```

场景更新是异步的：`apply_collision_object` 返回后，`move_group` 不一定已经处理完。紧接着调用规划有可能用的还是旧场景。可靠做法是更新后确认场景版本已变化，或在关键操作前加短暂等待。

### 附着与分离物体

抓取物体后必须把它**附着**（Attach）到夹爪上，否则 MoveIt 会认为它还在原地，进而认为夹爪与它发生了碰撞：

```python
def attach_object(scene_monitor, obj_id, link='tool0',
                  touch_links=('left_finger', 'right_finger', 'tool0')):
    """抓取后把物体附着到末端，并允许它与夹爪接触"""
    with scene_monitor.read_write() as scene:
        scene.current_state.attach_body(
            obj_id, link, list(touch_links))
        scene.current_state.update()
```

`touch_links` 是关键参数：它列出允许与该物体接触的连杆。不设置的话，夹爪一夹住物体，碰撞检测立即报警，后续所有规划都会失败。

附着之后，物体随夹爪一起参与碰撞检测——这正是我们想要的，因为搬运途中物体本身也可能撞到环境。放置完成后要及时 `detach`，否则物体会一直跟着机器人移动。

### 从传感器构建场景

MoveIt 可以订阅点云或深度图，自动构建八叉树（OctoMap）表示的环境：

```yaml
# sensors_3d.yaml
sensors:
  - sensor_plugin: occupancy_map_monitor/PointCloudOctomapUpdater
    point_cloud_topic: /camera/depth/color/points
    max_range: 2.0
    point_subsample: 1
    padding_offset: 0.02          # 障碍物膨胀，留出安全裕度
    padding_scale: 1.0
    filtered_cloud_topic: /filtered_cloud
```

必须同时配置**自过滤**（Self-Filter），否则机器人自身会被点云识别为障碍物，导致规划永远失败。这是新手最常踩的坑之一：机器人手臂进入相机视野，点云中出现"障碍物"，MoveIt 认为无处可去。


## 笛卡尔路径

许多操作任务需要末端走直线（趋近抓取位姿、退出料箱），这要用笛卡尔路径而非普通规划：

```python
from moveit.core.robot_state import RobotState

def compute_cartesian_path(robot_model, robot_state, group_name,
                           waypoints, eef_step=0.005, jump_threshold=5.0):
    """沿路径点做笛卡尔插补，返回完成比例与轨迹"""
    fraction, trajectory = robot_state.compute_cartesian_path(
        group_name=group_name,
        waypoints=waypoints,
        max_step=eef_step,
        jump_threshold=jump_threshold)
    return fraction, trajectory
```

三个要点：

**`fraction` 必须检查**。它表示成功插补的路径比例，小于 1.0 意味着中途遇到碰撞、超出工作空间或逆运动学无解。直接执行一条 `fraction = 0.6` 的轨迹会让机器人停在半路。生产代码应要求 `fraction > 0.99`，否则视为失败。

**`jump_threshold` 不能设为 0**。设为 0 会禁用跳变检查，此时若相邻路径点的逆运动学解落在不同的构型分支上，机器人会以最大速度做一次剧烈的构型翻转——这是极危险的失败模式，可能损坏机器人或伤人。合理值在 5–10 之间（表示允许的关节位移相对于平均值的倍数）。

**`eef_step` 影响精度与耗时**。取 5 mm 是常见折中；过大会导致路径偏离直线，过小会显著增加计算时间与轨迹点数量。

笛卡尔路径不做避障搜索——它只沿指定直线插补，遇到障碍就停下。需要绕障时必须用普通规划。


## 抓取流水线

把[抓取](grasping.md)与 MoveIt 结合的完整流程：

```python
import numpy as np
from geometry_msgs.msg import PoseStamped


def pick(moveit, scene_monitor, arm, gripper, grasp_poses, object_id,
         approach_dist=0.10, retreat_dist=0.15):
    """依次尝试候选抓取位姿，返回是否成功

    grasp_poses 应已按质量排序；逐个尝试是提高成功率的关键——
    质量最高的抓取常常因为不可达或碰撞而无法执行
    """
    for idx, T_grasp in enumerate(grasp_poses):
        # 1) 预抓取位姿：沿趋近轴后退
        T_pre = T_grasp.copy()
        T_pre[:3, 3] -= T_grasp[:3, 2] * approach_dist

        arm.set_start_state_to_current_state()
        arm.set_goal_state(pose_stamped_msg=to_msg(T_pre), pose_link='tool0')
        plan = arm.plan()
        if not plan:
            continue                      # 不可达，试下一个候选

        moveit.execute(plan.trajectory, controllers=[])
        gripper.open()

        # 2) 直线趋近；此时须允许夹爪与目标物体接触
        allow_collision(scene_monitor, object_id,
                        ['left_finger', 'right_finger'], True)
        fraction, traj = cartesian_path(arm, [to_msg(T_grasp)])
        if fraction < 0.99:
            allow_collision(scene_monitor, object_id,
                            ['left_finger', 'right_finger'], False)
            continue

        moveit.execute(traj, controllers=[])

        # 3) 闭合并附着
        gripper.close()
        if gripper.width() < 0.002:       # 抓空
            gripper.open()
            continue
        attach_object(scene_monitor, object_id)

        # 4) 直线撤离
        T_retreat = T_grasp.copy()
        T_retreat[2, 3] += retreat_dist
        fraction, traj = cartesian_path(arm, [to_msg(T_retreat)])
        if fraction < 0.99:
            return False, f'撤离路径受阻（候选 {idx}）'
        moveit.execute(traj, controllers=[])

        return True, f'使用候选 {idx} 抓取成功'

    return False, '所有候选抓取均不可行'
```

**逐个尝试候选是提高成功率最有效的一招**。抓取质量评分最高的位姿常常因为机械臂够不到、或趋近路径被料箱壁挡住而无法执行。一个能返回 50 个候选并逐一验证的流水线，成功率远高于只用最优候选的方案。

MoveIt 也提供内置的 `pick`/`place` 接口与 `Grasp` 消息类型，但它的抽象层次较高、可控性差、失败时难以定位原因。多数生产项目选择自己组织上述流程。


## 轨迹时间参数化

规划器输出的路径没有时间信息，需要单独做时间参数化：

```yaml
request_adapters: >-
    default_planner_request_adapters/AddTimeOptimalParameterization
    default_planner_request_adapters/ResolveConstraintFrames
    default_planner_request_adapters/FixWorkspaceBounds
    default_planner_request_adapters/FixStartStateBounds
    default_planner_request_adapters/FixStartStateCollision
    default_planner_request_adapters/FixStartStatePathConstraints
```

- `AddTimeOptimalParameterization`：TOTG 算法，在速度与加速度限制下求时间最优参数化
- `AddRuckigTrajectorySmoothing`：额外施加加加速度限制，消除启停冲击

两者可以串联，先 TOTG 再 Ruckig。详见 [轨迹生成](../kinematics/trajectory-generation.md)。

全局降速可以通过缩放因子实现，调试新程序时应从 0.1 开始：

```python
arm.set_max_velocity_scaling_factor(0.3)
arm.set_max_acceleration_scaling_factor(0.3)
```

`FixStartStateCollision` 适配器解决一个常见困扰：机器人当前就处于碰撞状态（比如刚碰到东西），此时任何规划都会立即失败。该适配器会先把起始状态微调出碰撞区再规划。


## 常见问题排查

| 现象 | 常见原因 | 排查方法 |
|------|---------|---------|
| 规划总是失败，无具体报错 | 起始状态处于碰撞中 | RViz 中打开 Planning Scene 显示，碰撞连杆会高亮为红色 |
| 目标位姿规划失败 | 逆运动学无解或目标在碰撞中 | 单独调用 IK 接口验证目标可达，再检查碰撞 |
| 抓取时报夹爪与物体碰撞 | 未设置 `touch_links` 或未附着物体 | 抓取前允许接触，抓取后立即 attach |
| 点云把机器人当成障碍物 | 未配置自过滤 | 检查 `sensors_3d.yaml` 与机器人模型的 padding 设置 |
| 轨迹执行中途中止 | 控制器容差被触发 | 查看 `FOLLOW_JOINT_TRAJECTORY` 的错误码，放宽 `goal_time_tolerance` 或降速 |
| 笛卡尔路径只完成一部分 | 中途碰撞或 IK 无解 | 检查 `fraction`，缩短路径分段执行 |
| 机器人突然剧烈翻转 | `jump_threshold` 设为 0 | 设为 5–10 |
| 规划耗时过长 | 场景中八叉树体素过多 | 提高 `point_subsample`，限制 `max_range` |
| 实机与仿真行为不一致 | 关节限位或控制器参数不同 | 对比 `joint_limits.yaml` 与实机控制器的实际限制 |

调试时最有用的两个工具：

```bash
# RViz 中的 MotionPlanning 插件：可视化规划场景、碰撞、规划结果
ros2 launch moveit_ros_visualization moveit_rviz.launch.py

# 打印当前规划场景中的所有碰撞对
ros2 service call /get_planning_scene moveit_msgs/srv/GetPlanningScene \
  "{components: {components: 1023}}"
```

在 RViz 中把 Planning Scene 的 `Show Robot Collision` 打开，能直接看到碰撞几何（通常是简化的凸包，与视觉网格不同）——很多"不该发生"的碰撞其实是因为碰撞几何比视觉模型胖了一圈。


## 参考资料

1. [MoveIt 2 官方文档](https://moveit.picknik.ai/) — 教程、API 参考与迁移指南
2. Coleman, D., Sucan, I., Chitta, S. & Correll, N. (2014). Reducing the Barrier to Entry of Complex Robotic Software: a MoveIt! Case Study. *Journal of Software Engineering for Robotics*, 5(1), 3-16.
3. Şucan, I. A., Moll, M. & Kavraki, L. E. (2012). The Open Motion Planning Library. *IEEE Robotics and Automation Magazine*, 19(4), 72-82.
4. Kunz, T. & Stilman, M. (2012). Time-Optimal Trajectory Generation for Path Following with Bounded Acceleration and Velocity. *Robotics: Science and Systems (RSS)*. — MoveIt 中 TOTG 的算法来源。
5. Beeson, P. & Ames, B. (2015). TRAC-IK: An Open-Source Library for Improved Solving of Generic Inverse Kinematics. *IEEE-RAS International Conference on Humanoid Robots*.
6. [Pilz Industrial Motion Planner](https://moveit.picknik.ai/main/doc/how_to_guides/pilz_industrial_motion_planner/pilz_industrial_motion_planner.html) — 工业标准运动指令的实现
