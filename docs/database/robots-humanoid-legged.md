# 人形与足式机器人图鉴

!!! note "引言"
    人形与足式机器人是当前机器人产业投入最集中的方向。人形机器人以双足行走与通用操作为目标，硬件与算法难度最高，但在与人类环境的兼容性上具有天然优势；四足机器人则牺牲了手部操作能力，换取远高于双足的运动稳定性与负载能力，已在工业巡检等场景率先实现商业化。本页面汇总两类平台的代表产品及其定位。


## 人形机器人（Humanoid Robots）

人形机器人（Humanoid Robot）模仿人类外形，通常具备双足行走（Bipedal Locomotion）和双臂操作（Bimanual Manipulation）能力。其核心挑战在于动态平衡控制（Dynamic Balance Control）、全身运动规划（Whole-Body Motion Planning）与鲁棒感知，是当前机器人产业最受关注的方向之一。

驱动方式上，早期人形机器人多采用液压驱动（Hydraulic Actuation），具有功率密度高的优点，但系统复杂、噪音大、维护困难；现代人形机器人主流转向电机驱动（Electric Actuation），配合高减速比谐波减速器（Harmonic Drive）或行星减速器（Planetary Gearbox）实现力矩放大；部分机器人探索线驱动（Tendon-Driven）架构以降低腿部惯量（Leg Inertia）。

从技术路线看，Boston Dynamics 的 Atlas 长期代表液压路线的顶峰，而 2024 年发布的全电动 Atlas 则象征行业向电动方向的全面转型。中国团队在 2023–2024 年间集中爆发，宇树、傅利叶、智元、优必选等企业密集发布产品，推动了人形机器人商业化进程。

| 名称 | 公司/机构 | 国家 | 首发年份 | 身高 | 体重 | 自由度 | 驱动方式 | 主要应用 |
|------|---------|------|----------|------|------|--------|----------|----------|
| [Atlas](atlas.md) | Boston Dynamics | 美国 | 2013（液压）/ 2024（电动） | 1.5 m | ~89 kg | 28+ | 液压→电动 | 研究与演示 |
| [Optimus](optimus.md) | Tesla | 美国 | 2022 | 1.73 m | ~73 kg | 28+ | 电动 | 通用任务 |
| [Figure 02](figure.md) | Figure AI | 美国 | 2024 | 1.67 m | ~60 kg | 16+ | 电动 | 仓储物流 |
| [ASIMO](asimo.md) | Honda | 日本 | 2000 | 1.3 m | 54 kg | 57 | 电动 | 研究与展示 |
| [Digit](digit.md) | Agility Robotics | 美国 | 2019 | 1.75 m | ~65 kg | 16+ | 电动 | 物流搬运 |
| [H1](unitree-h1.md) | 宇树科技（Unitree） | 中国 | 2023 | 1.8 m | ~47 kg | 19 | 电动 | 研究与通用任务 |
| G1 | 宇树科技（Unitree） | 中国 | 2024 | 1.27 m | ~35 kg | 23 | 电动 | 研究与教育 |
| [NAO](nao.md) | SoftBank Robotics | 法国/日本 | 2008 | 0.574 m | 5.48 kg | 25 | 电动 | 教育与研究 |
| Pepper | SoftBank Robotics | 法国/日本 | 2014 | 1.2 m | 28 kg | 20 | 电动 | 商业接待 |
| Sophia | Hanson Robotics | 美国/香港 | 2016 | — | — | 头部 62+ | 电动 | 社交互动演示 |
| Phoenix | Sanctuary AI | 加拿大 | 2023 | 1.7 m | ~70 kg | 20+ | 电动 | 通用任务 |
| Apollo | Apptronik | 美国 | 2023 | 1.73 m | ~73 kg | 24+ | 电动 | 物流与制造 |
| GR-1 | 傅利叶智能（Fourier） | 中国 | 2023 | 1.65 m | ~55 kg | 40 | 电动 | 康复与研究 |
| GR-2 | 傅利叶智能（Fourier） | 中国 | 2024 | 1.75 m | ~63 kg | 53 | 电动 | 通用人形 |
| Agibot（远征 A2） | 智元机器人 | 中国 | 2024 | 1.75 m | ~65 kg | 40+ | 电动 | 通用任务 |
| Walker S | 优必选（UBTECH） | 中国 | 2023 | 1.7 m | ~77 kg | 41 | 电动 | 工业与服务 |
| CyberOne | 小米（Xiaomi） | 中国 | 2022 | 1.77 m | ~52 kg | 21 | 电动 | 展示与研究 |
| HRP-4 | 川田工业（Kawada） | 日本 | 2010 | 1.51 m | 39 kg | 34 | 电动 | 研究与演示 |
| iCub | 意大利技术研究院（IIT） | 意大利 | 2008 | 1.04 m | ~33 kg | 53 | 电动 | 认知与具身智能研究 |
| Valkyrie（R5） | NASA / JSC | 美国 | 2015 | 1.8 m | ~125 kg | 44 | 电动 | 太空探索研究 |
| TALOS | PAL Robotics | 西班牙 | 2017 | 1.75 m | ~95 kg | 32 | 电动（力控） | 学术研究平台 |
| Surena IV | 德黑兰大学 | 伊朗 | 2019 | 1.7 m | ~74 kg | 43 | 电动 | 学术研究 |


## 四足机器人（Quadruped Robots）

四足机器人（Quadruped Robot）以四条腿为支撑，具备出色的地形适应能力（Terrain Adaptability），可在不平整、泥泞或危险环境中执行巡检（Inspection）、测绘（Mapping）和搜救（Search and Rescue）等任务。

**控制方法演进**：早期四足机器人依赖预先设计的步态库（Gait Library）和零力矩点（Zero Moment Point，ZMP）准则；现代系统广泛采用模型预测控制（Model Predictive Control，MPC）和凸优化（Convex Optimization），结合接触力规划（Contact Force Planning）实现动步态（Dynamic Gait）。近年来，基于深度强化学习（Deep Reinforcement Learning，DRL）的端到端步态控制取得突破，MIT Mini Cheetah 和宇树 Go2 均展示了在仿真中训练、在真实世界部署（Sim-to-Real Transfer）的能力。

**商业化进展**：Boston Dynamics 的 Spot 是目前商业化程度最高的四足机器人，已在石油化工、电力、矿山等行业部署超过数千台，执行例行巡检任务。宇树科技凭借极具竞争力的价格策略，将四足机器人推向科研和消费市场。

| 名称 | 公司/机构 | 国家 | 首发年份 | 体重 | 最大速度 | 主要应用 |
|------|---------|------|----------|------|----------|----------|
| Spot | Boston Dynamics | 美国 | 2019 | ~32 kg | 1.6 m/s | 工业巡检与测绘 |
| LS3（骡子机器人） | Boston Dynamics / DARPA | 美国 | 2012 | ~590 kg | 3.2 m/s | 军用负载运输 |
| BigDog | Boston Dynamics / DARPA | 美国 | 2005 | ~109 kg | 1.6 m/s | 军用早期研究平台 |
| ANYmal C | ANYbotics | 瑞士 | 2020 | ~50 kg | 1.0 m/s | 工业巡检 |
| ANYmal D | ANYbotics | 瑞士 | 2023 | ~50 kg | 1.0 m/s | 工业巡检（升级版） |
| HyQ | 意大利技术研究院（IIT） | 意大利 | 2010 | ~80 kg | 2.0 m/s | 学术研究平台 |
| MIT Mini Cheetah | 麻省理工学院（MIT） | 美国 | 2019 | ~9 kg | 3.7 m/s | 学术步态与 RL 研究 |
| Go1 | 宇树科技（Unitree） | 中国 | 2021 | ~12 kg | 3.5 m/s | 消费与教育 |
| Go2 | 宇树科技（Unitree） | 中国 | 2023 | ~15 kg | 3.5 m/s | 科研与消费 |
| B1 | 宇树科技（Unitree） | 中国 | 2021 | ~50 kg | 1.6 m/s | 工业巡检 |
| B2 | 宇树科技（Unitree） | 中国 | 2023 | ~60 kg | 1.5 m/s | 工业与科研 |
| Laikago | 宇树科技（Unitree） | 中国 | 2018 | ~22 kg | 3.0 m/s | 早期研究平台 |
| A1 | 宇树科技（Unitree） | 中国 | 2020 | ~12 kg | 3.3 m/s | 学术步态研究 |
| CyberDog 1 | 小米（Xiaomi） | 中国 | 2021 | ~14 kg | 3.2 m/s | 消费与开发 |
| CyberDog 2 | 小米（Xiaomi） | 中国 | 2023 | ~8.9 kg | 3.2 m/s | 消费与开发（升级版） |
| Jueying X20 | 云深处科技 | 中国 | 2022 | ~60 kg | 1.5 m/s | 工业巡检 |
| Spot Mini（原型） | Boston Dynamics | 美国 | 2016 | ~25 kg | 1.4 m/s | Spot 的前身平台 |


## 参考资料

1. [IEEE Spectrum: Robot Database](https://robots.ieee.org/)，IEEE
2. [机器人图鉴总览](robots.md)
3. [Atlas](atlas.md)、[Optimus](optimus.md)、[Figure](figure.md)、[Digit](digit.md)、[Unitree H1](unitree-h1.md)、[Spot](spot.md)
4. [建模](../kinematics/index.md)
