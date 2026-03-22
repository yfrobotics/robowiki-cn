# CoppeliaSim 参考资料

!!! note "引言"
    本文汇总 CoppeliaSim（原名 V-REP）的官方文档、社区资源、插件信息、API 概览、版本历史以及与其他仿真器的对比，为用户提供全面的参考入口。


## 官方文档与链接

| 资源 | 链接 | 说明 |
|------|------|------|
| 官方网站 | <https://www.coppeliarobotics.com/> | 下载和新闻 |
| 用户手册 | <https://manual.coppeliarobotics.com/> | 完整使用文档 |
| API 参考 | <https://manual.coppeliarobotics.com/en/apiFunctions.htm> | 所有 API 函数列表 |
| 论坛 | <https://forum.coppeliarobotics.com/> | 技术讨论和问答 |
| GitHub | <https://github.com/CoppeliaRobotics> | 源码和插件仓库 |
| YouTube | <https://www.youtube.com/@CoppeliaRobotics> | 教程视频 |


## 版本历史

| 版本 | 时间 | 重要变更 |
|------|------|---------|
| V-REP 3.6 | 2019 | 最后一个 V-REP 版本 |
| CoppeliaSim 4.0 | 2019 | 更名为 CoppeliaSim，架构重构 |
| CoppeliaSim 4.1 | 2020 | 改进 CoppeliaSim 引擎 |
| CoppeliaSim 4.2 | 2021 | 新增 Newton 物理引擎 |
| CoppeliaSim 4.3 | 2022 | ZeroMQ Remote API 取代旧版 |
| CoppeliaSim 4.5 | 2023 | WebSocket API，性能优化 |
| CoppeliaSim 4.7 | 2024 | 改进 URDF 导入，Python 脚本支持 |
| CoppeliaSim 4.8 | 2025 | 进一步性能优化 |

从 V-REP 迁移到 CoppeliaSim 时需注意 API 函数名变化（如 `simxGetObjectHandle` → `sim.getObject`）。


## API 体系概览

### API 分类

| API 类型 | 用途 | 推荐程度 |
|---------|------|---------|
| 常规 API（Lua/Python 脚本） | 场景内嵌脚本 | 高 |
| ZeroMQ Remote API | 外部程序控制 | 高（推荐） |
| Legacy Remote API | 外部程序控制（旧版） | 不推荐 |
| WebSocket API | 浏览器端控制 | 中 |
| ROS / ROS 2 接口 | ROS 生态集成 | 高 |
| BlueZero 接口 | 分布式仿真 | 中 |

### 常用 API 函数分类

**对象操作**：

| 函数 | 功能 |
|------|------|
| `sim.getObject(path)` | 获取对象句柄 |
| `sim.getObjectPosition(handle, relTo)` | 获取位置 |
| `sim.setObjectPosition(handle, relTo, pos)` | 设置位置 |
| `sim.getObjectOrientation(handle, relTo)` | 获取欧拉角 |
| `sim.getObjectQuaternion(handle, relTo)` | 获取四元数 |

**关节操作**：

| 函数 | 功能 |
|------|------|
| `sim.getJointPosition(handle)` | 获取关节位置 |
| `sim.setJointTargetPosition(handle, pos)` | 设置目标位置 |
| `sim.setJointTargetVelocity(handle, vel)` | 设置目标速度 |
| `sim.setJointTargetForce(handle, force)` | 设置目标力/力矩 |
| `sim.getJointForce(handle)` | 读取关节力 |

**传感器操作**：

| 函数 | 功能 |
|------|------|
| `sim.getVisionSensorImg(handle)` | 获取视觉传感器图像 |
| `sim.getVisionSensorDepth(handle)` | 获取深度图 |
| `sim.readProximitySensor(handle)` | 读取距离传感器 |
| `sim.readForceSensor(handle)` | 读取力传感器 |

**仿真控制**：

| 函数 | 功能 |
|------|------|
| `sim.startSimulation()` | 启动仿真 |
| `sim.stopSimulation()` | 停止仿真 |
| `sim.pauseSimulation()` | 暂停仿真 |
| `sim.setStepping(flag)` | 设置步进模式 |
| `sim.step()` | 推进一步 |
| `sim.getSimulationTime()` | 获取仿真时间 |


## 插件生态

| 插件 | 功能 | 仓库 |
|------|------|------|
| simROS2 | ROS 2 话题/服务/动作接口 | CoppeliaRobotics/simROS2 |
| simROS | ROS 1 接口 | CoppeliaRobotics/simROS |
| simOMPL | OMPL 路径规划 | CoppeliaRobotics/simOMPL |
| simIK | 逆运动学求解 | 内置 |
| simUI | 自定义 UI 界面 | CoppeliaRobotics/simUI |
| simVision | 图像处理滤波器 | 内置 |
| simConvexDecompose | 凸分解工具 | 内置 |
| simAssimp | 多格式模型导入 | CoppeliaRobotics/simAssimp |


## 内置模型库

CoppeliaSim 随附丰富的机器人模型：

### 移动机器人

- Pioneer P3-DX / P3-AT（差分驱动）
- youBot（全向移动 + 机械臂）
- Khepera / e-puck（教学用小型机器人）
- Robotino（全向轮）
- 多种线跟踪机器人

### 机械臂

- UR3 / UR5 / UR10（Universal Robots）
- KUKA LBR iiwa（轻型协作臂）
- Franka Emika Panda
- ABB IRB 系列
- Jaco / Baxter

### 人形机器人

- NAO
- Atlas（简化版）

### 传感器

- 视觉传感器（RGB / 深度）
- 激光雷达（2D / 3D）
- 近距离传感器
- 力/力矩传感器
- 惯性测量单元（IMU）


## 与其他仿真器对比

| 特性 | CoppeliaSim | Gazebo | Isaac Sim | PyBullet | MuJoCo |
|------|-------------|--------|-----------|----------|--------|
| 许可证 | 教育免费 / 商业付费 | 开源 | 免费 | 开源 | 开源 |
| GUI | 丰富 | 较好 | 优秀 | 基础 | 基础 |
| 物理引擎 | 4 种可选 | ODE/Bullet/DART | PhysX | Bullet | MuJoCo |
| ROS 集成 | 插件 | 原生 | 插件 | 无 | 无 |
| Python API | 优秀 | 中 | 优秀 | 优秀 | 优秀 |
| RL 训练 | 中 | 慢 | 快（GPU） | 中 | 快 |
| 内置模型 | 丰富 | 中 | 丰富 | 少 | 少 |
| 学习曲线 | 中 | 较陡 | 较陡 | 平缓 | 平缓 |

### 选择建议

- **教学和快速原型**：CoppeliaSim（GUI 友好，模型丰富）
- **ROS 集成项目**：CoppeliaSim 或 Gazebo
- **大规模 RL 训练**：Isaac Sim 或 MuJoCo
- **轻量级 Python 仿真**：PyBullet 或 MuJoCo


## 常见问题排查

| 问题 | 解决方案 |
|------|---------|
| 启动时插件加载失败 | 检查插件路径和依赖库，查看控制台日志 |
| URDF 导入后模型异常 | 检查 URDF 坐标系和单位，尝试简化网格 |
| 仿真不稳定/物体弹飞 | 减小仿真步长，增加物理引擎迭代次数 |
| 脚本执行报错 | 检查 API 版本兼容性，参考迁移指南 |
| 远程 API 连接失败 | 确认端口号、防火墙设置、插件是否启用 |
| 图像采集为空 | 确认视觉传感器激活且方向正确 |
| 关节控制无反应 | 检查关节控制模式是否匹配（位置/速度/力） |
| Linux 下 GUI 问题 | 安装 OpenGL 依赖，检查显卡驱动 |


## 学习路径

### 入门

1. 下载安装 CoppeliaSim Edu 版本
2. 熟悉 GUI 操作：创建场景、添加模型、运行仿真
3. 学习 Lua 内嵌脚本编写
4. 尝试内置示例场景（tutorials 目录）

### 进阶

1. 掌握 ZeroMQ Remote API（Python）
2. 学习自定义机器人模型创建
3. 集成 ROS 2 插件
4. 使用 OMPL 进行路径规划

### 高级应用

1. 多机器人仿真与协调
2. 视觉传感器数据处理
3. 无头模式批量仿真
4. 强化学习训练集成


## 参考资料

- CoppeliaSim 官方手册：<https://manual.coppeliarobotics.com/>
- CoppeliaSim GitHub 组织：<https://github.com/CoppeliaRobotics>
- Rohmer E, Singh S P N, Freese M. CoppeliaSim (formerly V-REP): a Versatile and Scalable Robot Simulation Framework. *IROS*, 2013.
- CoppeliaSim 论坛：<https://forum.coppeliarobotics.com/>
- ZeroMQ Remote API 客户端：<https://github.com/CoppeliaRobotics/zmqRemoteApi>
