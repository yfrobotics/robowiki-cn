# CoppeliaSim 性能与调试

!!! note "引言"
    CoppeliaSim 仿真的性能和精度取决于多种因素的配置，包括仿真步长、物理引擎选择、碰撞检测设置等。本文介绍如何调优仿真性能、选择合适的物理引擎、优化碰撞计算，以及常用的调试技巧和无头模式运行方法。


## 仿真步长调优

### 步长选择

仿真步长（Timestep）直接影响仿真精度和计算速度：

| 步长 | 精度 | 速度 | 适用场景 |
|------|------|------|---------|
| 50 ms | 低 | 快 | 粗略功能验证 |
| 20 ms | 中 | 中 | 一般机器人仿真 |
| 10 ms | 较高 | 较慢 | 精确控制仿真 |
| 5 ms | 高 | 慢 | 接触力、柔性体 |
| 1 ms | 极高 | 极慢 | 高频控制验证 |

### 配置方法

```python
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

client = RemoteAPIClient()
sim = client.require('sim')

# 设置仿真步长为 10 ms
sim.setFloatParam(sim.floatparam_simulation_time_step, 0.01)

# 查询当前步长
dt = sim.getFloatParam(sim.floatparam_simulation_time_step)
print(f"当前仿真步长: {dt * 1000:.1f} ms")
```

### 步长与控制频率的关系

控制器的更新频率应与仿真步长匹配。如果控制器以 100 Hz 运行，仿真步长应不大于 10 ms（100 Hz）。控制器频率远高于仿真步长会浪费计算资源，远低于则可能导致控制不稳定。


## 物理引擎对比

CoppeliaSim 集成了四种物理引擎，各有优劣：

| 特性 | Bullet 2.83 | ODE | Vortex | Newton |
|------|------------|-----|--------|--------|
| 许可证 | 开源 (zlib) | 开源 (BSD) | 商业 | 开源 |
| 速度 | 快 | 快 | 中 | 快 |
| 接触精度 | 中 | 中 | 高 | 中 |
| 稳定性 | 良好 | 良好 | 优秀 | 良好 |
| 关节精度 | 中 | 中 | 高 | 较高 |
| 柔性体 | 不支持 | 不支持 | 支持 | 不支持 |
| 推荐场景 | 通用仿真 | 快速原型 | 工业精度需求 | 通用仿真 |

### 引擎切换

```python
# 设置物理引擎（需在仿真启动前设置）
# 0=Bullet, 1=ODE, 2=Vortex, 3=Newton
sim.setInt32Param(sim.intparam_dynamic_engine, 0)  # 使用 Bullet
```

### 引擎选择建议

- **一般仿真**：Bullet 或 Newton，速度和精度平衡
- **需要高精度接触**：Vortex（需商业许可）
- **快速原型验证**：ODE，计算速度最快
- **强化学习训练**：Bullet，速度快且足够稳定


## 碰撞检测优化

碰撞检测是仿真中计算开销最大的模块之一。

### 碰撞对管理

只对需要检测碰撞的对象对启用碰撞检测：

```python
# 创建碰撞对
collision_handle = sim.addCollisionObject(
    sim.handle_all,    # 实体 1（所有对象）
    robot_handle       # 实体 2（机器人）
)

# 检查碰撞
in_collision = sim.checkCollision(collision_handle, sim.handle_all)
```

### 优化策略

| 策略 | 效果 | 实现方式 |
|------|------|---------|
| 减少碰撞对 | 显著提升速度 | 只对必要的对象对检测 |
| 简化碰撞体 | 减少计算量 | 用凸包或基元代替精细网格 |
| 空间划分 | 加速粗筛阶段 | 引擎内部自动处理 |
| 禁用非必要检测 | 直接跳过计算 | 设置对象属性 |

### 可视形状与碰撞形状分离

为复杂模型创建简化的碰撞形状：

1. 保留高精度网格用于可视化（Visible Layer）
2. 创建简化的凸包或基元用于碰撞检测（Collision Layer）
3. 两者绑定到同一对象

```python
# 生成凸包用于碰撞检测
convex_handle = sim.createPureShape(
    0,      # 形状类型（0=凸包）
    16,     # 选项（用于碰撞检测）
    [0.1, 0.1, 0.1],  # 尺寸
    0.1     # 质量
)
```


## 无头模式运行

无头模式（Headless Mode）无需 GUI 界面，适合服务器端批量仿真和强化学习训练。

### 启动方式

```bash
# Linux 无头模式启动
./coppeliaSim.sh -h -s5000 -q /path/to/scene.ttt

# 参数说明：
# -h: 无头模式
# -s5000: 仿真运行 5000 ms 后停止
# -q: 运行完毕后退出
# 也可以不指定 -s，通过 API 控制仿真时长
```

### 批量仿真脚本

```python
import subprocess
import multiprocessing

def run_single_sim(config):
    """运行单个仿真实例"""
    cmd = [
        './coppeliaSim.sh', '-h',
        '-GzmqRemoteApi.rpcPort=' + str(config['port']),
        config['scene']
    ]
    proc = subprocess.Popen(cmd)

    # 通过 API 连接并控制仿真
    client = RemoteAPIClient(port=config['port'])
    sim = client.require('sim')

    # 设置随机参数
    randomize_scene(sim, config['params'])

    sim.startSimulation()
    data = collect_data(sim, config['steps'])
    sim.stopSimulation()

    proc.terminate()
    return data

# 并行运行多个仿真
configs = [
    {'port': 23000 + i, 'scene': 'scene.ttt', 'steps': 1000,
     'params': random_params()}
    for i in range(8)
]

with multiprocessing.Pool(8) as pool:
    results = pool.map(run_single_sim, configs)
```


## 调试技巧

### 日志输出

```python
# 在仿真中打印调试信息
sim.addLog(sim.verbosity_scriptinfos, "机器人位置: " + str(position))

# 设置日志级别
sim.setInt32Param(sim.intparam_verbosity, sim.verbosity_debug)
```

### 可视化调试

```python
# 绘制调试线条
line_handle = sim.addDrawingObject(
    sim.drawing_lines, 2, 0, -1, 100, [1, 0, 0]  # 红色线条
)
sim.addDrawingObjectItem(line_handle, [x1, y1, z1, x2, y2, z2])

# 绘制调试点
point_handle = sim.addDrawingObject(
    sim.drawing_points, 5, 0, -1, 100, [0, 1, 0]  # 绿色点
)
sim.addDrawingObjectItem(point_handle, [x, y, z])

# 添加调试文本标签
dummy_handle = sim.createDummy(0.01)
sim.setObjectPosition(dummy_handle, -1, [x, y, z + 0.3])
sim.addLog(sim.verbosity_scriptinfos, f"标记点: ({x:.2f}, {y:.2f}, {z:.2f})")
```

### 录制仿真数据

可在仿真循环中将位置、速度、力矩等数据写入 CSV 文件，用于离线分析。使用 `sim.getSimulationTime()` 获取时间戳，`sim.getObjectPosition()` 和 `sim.getObjectVelocity()` 获取状态信息。

### 常见性能瓶颈

| 现象 | 可能原因 | 诊断方法 |
|------|---------|---------|
| 仿真极慢 | 步长过小 | 检查仿真步长设置 |
| 仿真极慢 | 碰撞检测过多 | 减少碰撞对数量 |
| 物体穿透 | 步长过大 | 减小步长或增加迭代次数 |
| 关节震荡 | PID 参数不当 | 调整关节 PID 增益 |
| 物体弹跳 | 恢复系数过高 | 调整材质属性 |
| 内存增长 | 图形对象未清理 | 清理绘图对象 |


## 性能分析工具

### 内置性能分析

CoppeliaSim 提供了内置的性能分析视图：

- **仿真时间分析**：菜单 → Tools → Simulation Time Analysis
- **显示帧率**：观察渲染帧率是否是瓶颈
- **脚本执行时间**：在控制台查看各脚本的执行时长

### Python 端性能分析

使用 `time.perf_counter()` 对仿真循环中的各阶段（传感器读取、控制计算、仿真步进）进行计时，找出性能瓶颈。也可使用 Python 的 `cProfile` 模块进行更详细的分析。


## 参考资料

- CoppeliaSim 性能优化指南：<https://manual.coppeliarobotics.com/en/simulation.htm>
- Bullet 物理引擎文档：<https://pybullet.org/wordpress/>
- ODE 物理引擎文档：<https://ode.org/>
- CoppeliaSim 命令行参数：<https://manual.coppeliarobotics.com/en/commandLine.htm>
