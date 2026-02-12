# Digit

!!! note "引言"
    Digit 是由美国 Agility Robotics 公司研发的人形双足机器人，专为物流搬运等商业任务而设计。Digit 是全球首个获得商业化部署的人形机器人，2023 年开始为亚马逊（Amazon）等客户执行仓储物流任务，标志着人形机器人从实验室正式走向工业现场。


## 发展历程

Agility Robotics 源自俄勒冈州立大学（Oregon State University）的机器人实验室，创始人乔纳森·赫斯特（Jonathan Hurst）是弹簧质量模型（Spring-Loaded Inverted Pendulum, SLIP）步态控制领域的知名研究者。

- **2017 年**：Agility Robotics 发布 Cassie，一款没有上半身的双足机器人，以其稳健的动态步行能力闻名。Cassie 后来在 2022 年完成了 5 公里户外跑步，刷新了双足机器人的跑步记录。
- **2019 年**：Digit V1 发布，在 Cassie 的双足底盘基础上增加了躯干和双臂，首次展示了搬运箱体的能力。
- **2020 年**：福特汽车（Ford Motor Company）成为 Digit 的首个商业客户，探索使用 Digit 进行"最后一公里"送货。
- **2023 年**：Digit 进行了重大升级，发布了面向商业部署的量产版本。亚马逊宣布开始在其仓储设施中测试 Digit。
- **2023 年**：Agility Robotics 在俄勒冈州塞勒姆（Salem, Oregon）开设了全球首个人形机器人工厂 RoboFab，年产能目标为 10,000 台。
- **2024 年**：Digit 持续在多个客户现场进行商业化试点部署，执行货物搬运和码垛等任务。


## 技术规格

| 参数 | 规格 |
|------|------|
| 身高 | 约 1.75 m |
| 体重 | 约 65 kg |
| 负载能力 | 约 16 kg |
| 行走速度 | 约 1.5 m/s |
| 自由度（DOF） | 16+（双腿各 4、双臂各 4） |
| 驱动方式 | 全电动 |
| 电池续航 | 约 2-4 小时（任务依赖） |
| 感知系统 | 头部 LiDAR + 深度摄像头 |
| 通信 | Wi-Fi、4G/5G |
| 末端执行器 | 可更换末端工具（抓手/托盘等） |


## 关键技术

### 弹性腿部设计（Compliant Leg Design）

Digit 的腿部设计继承了 Cassie 的核心理念，采用了受鸟类腿部启发的反关节（Reverse-Knee）结构。腿部关节中集成了弹性元件（Compliant Elements），可以像弹簧一样储存和释放能量，使步行更加高效和自然。这种设计参考了弹簧质量模型（SLIP Model），是 Digit 能够在平坦和不平整地面上稳健行走的关键。

### 行为编排（Behavior Orchestration）

Digit 的软件系统采用行为编排架构，将复杂任务分解为一系列可组合的基本行为模块（如导航到目标位置、拾取箱体、放置到目标架位等）。操作人员可以通过 Agility Arc 软件平台为 Digit 编排任务序列，无需深入了解底层机器人控制技术。

### 多机器人协调（Multi-Robot Coordination）

在仓储场景中，多台 Digit 需要同时作业而不相互干扰。Agility Robotics 开发了基于云端的多机器人调度系统，负责任务分配、路径协调和冲突避免，使多台 Digit 能够在共享空间中高效协作。


## 商业化与应用

Digit 的商业化进展在人形机器人行业中处于领先地位：

- **亚马逊仓储**：Digit 在亚马逊的配送中心执行空箱搬运和回收任务，帮助解放人类工人从事更有价值的工作
- **RoboFab 工厂**：全球首个专门生产人形机器人的工厂，展示了人形机器人规模化生产的可行性
- **Agility Arc 平台**：为客户提供机器人即服务（Robot-as-a-Service, RaaS）的部署和管理工具


## 与其他人形机器人的差异

Digit 在设计哲学上与 Atlas、Optimus 等人形机器人有显著差异：

| 对比项 | Digit | Atlas / Optimus |
|--------|-------|-----------------|
| 设计目标 | 物流搬运专用 | 通用任务 |
| 手部设计 | 简化末端工具 | 多指灵巧手 |
| 商业化阶段 | 已部署（2023） | 试点/原型 |
| 步态特点 | 鸟类仿生反关节 | 传统人类关节 |
| 外形设计 | 功能优先 | 拟人化优先 |

Digit 的设计体现了"够用即好"的实用主义理念：不追求最高的自由度或最拟人的外形，而是聚焦于在特定商业场景中可靠、高效地完成任务。


## 参考资料

1. [Digit](https://agilityrobotics.com/digit), Agility Robotics 官网
2. [Agility Robotics](https://en.wikipedia.org/wiki/Agility_Robotics), Wikipedia
3. [Amazon tests Digit robots](https://www.aboutamazon.com/news/operations/amazon-agility-robotics-digit), About Amazon, 2023
4. [RoboFab: World's first humanoid robot factory](https://agilityrobotics.com/robofab), Agility Robotics
