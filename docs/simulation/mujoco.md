# MuJoCo
![5e430036ce538f09f700003a](assets/2beebaa320424c06ac56bc364c08511a.png)

- 官方网站：http://www.mujoco.org
- GitHub：https://github.com/google-deepmind/mujoco
- 物理引擎：MuJoCo（自研）
- 许可：Apache 2.0 开源

!!! note "引言"
    MuJoCo (Multi-Joint dynamics with Contact) 是一款专注于接触动力学仿真的高性能物理引擎。MuJoCo最初由华盛顿大学 (University of Washington) 的Emo Todorov教授开发，侧重控制与接触相关的仿真与优化。2021年，DeepMind收购了MuJoCo，并于2022年将其以Apache 2.0许可证完全开源，使其成为机器人强化学习 (Reinforcement Learning) 研究领域中最重要的仿真平台之一。

## 发展历程

MuJoCo的发展经历了几个重要阶段：

- **2012年**：Emo Todorov在华盛顿大学首次发布MuJoCo，作为商业软件提供试用和付费许可
- **2015年至2020年**：随着OpenAI Gym将MuJoCo作为标准仿真后端，MuJoCo在强化学习社区中获得广泛采用
- **2021年10月**：DeepMind宣布收购MuJoCo
- **2022年5月**：MuJoCo以Apache 2.0许可证正式开源，任何人均可免费使用和修改
- **后续版本**：开源后开发节奏加快，持续引入新功能，包括原生Python绑定 (Native Python Bindings)、MuJoCo XLA (MJX) 等

## 物理引擎特性

MuJoCo的物理引擎针对机器人控制和学习任务进行了深度优化：

- **广义坐标系 (Generalized Coordinates)**：使用最小坐标表示法描述系统状态，避免了约束求解中的冗余计算
- **高效接触求解 (Contact Solver)**：采用凸优化方法处理接触动力学，保证了求解的唯一性和稳定性
- **软接触模型 (Soft Contact Model)**：通过可配置的刚度和阻尼参数模拟柔性接触，避免了刚性接触模型中常见的数值不稳定
- **肌腱与执行器建模 (Tendon and Actuator Modeling)**：支持复杂的肌腱路由和多种执行器类型，适合生物力学仿真
- **高仿真速度**：单线程下可实现远超实时的仿真速度，适合大规模并行训练

## MJCF 模型格式

MuJoCo使用自定义的MJCF (MuJoCo XML Format) 格式描述仿真模型。MJCF文件采用XML语法，定义机器人的运动学结构、动力学参数和仿真环境：

```xml
<mujoco model="example">
  <worldbody>
    <light diffuse=".5 .5 .5" pos="0 0 3" dir="0 0 -1"/>
    <geom type="plane" size="1 1 0.1" rgba=".9 .9 .9 1"/>
    <body name="box" pos="0 0 1">
      <joint type="free"/>
      <geom type="box" size=".1 .1 .1" rgba="1 0 0 1" mass="1"/>
    </body>
  </worldbody>
</mujoco>
```

MJCF支持定义关节 (Joint)、几何体 (Geom)、执行器 (Actuator)、传感器 (Sensor)、接触排除 (Contact Exclusion) 等元素。MuJoCo同时支持导入URDF格式模型并自动转换。

## Python 绑定

MuJoCo提供多种Python绑定方式：

- **原生Python绑定**：开源后官方推出的原生绑定（`mujoco` 包），安装简单，API设计清晰，性能优异
- **mujoco-py**：由OpenAI开发的早期Python绑定，目前已不再积极维护，建议迁移至原生绑定
- **dm_control**：由DeepMind开发的控制任务套件 (Control Suite)，在MuJoCo之上构建了一系列标准化的控制基准任务

安装原生Python绑定：

```bash
pip install mujoco
```

## 在强化学习研究中的应用

MuJoCo在强化学习领域的地位举足轻重。OpenAI Gym（现为Gymnasium）中大量经典的连续控制基准任务 (Benchmark Tasks) 均基于MuJoCo构建：

- **HalfCheetah**：半猎豹奔跑控制
- **Ant**：四足蚂蚁行走
- **Humanoid**：人形机器人运动控制
- **Walker2d**：双足行走
- **Hopper**：单足跳跃

这些任务已成为评估强化学习算法（如PPO、SAC、TD3等）的标准基准。MuJoCo XLA (MJX) 进一步允许在GPU/TPU上运行批量仿真，极大加速了策略训练过程。

## 与其他物理引擎的对比

| 特性 | MuJoCo | PyBullet | PhysX |
|------|--------|----------|-------|
| 坐标系统 | 广义坐标 | 笛卡尔坐标 | 笛卡尔坐标 |
| 接触模型 | 软接触 (凸优化) | 刚性接触 | 刚性接触 |
| 仿真速度 | 极快 | 快 | 快 (GPU加速) |
| 许可证 | Apache 2.0 | zlib | 商业/免费 |
| RL集成 | 原生支持 | 良好 | 通过Isaac Sim |

## 参考资料

- [MuJoCo官方文档](https://mujoco.readthedocs.io/)
- [MuJoCo GitHub仓库](https://github.com/google-deepmind/mujoco)
- [dm_control控制任务套件](https://github.com/google-deepmind/dm_control)
- [Gymnasium MuJoCo环境](https://gymnasium.farama.org/environments/mujoco/)
- Todorov, E., Erez, T., & Tassa, Y. (2012). MuJoCo: A physics engine for model-based control. *IEEE/RSJ International Conference on Intelligent Robots and Systems*.
