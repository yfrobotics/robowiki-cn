# RTOS

!!! note "引言"
    实时操作系统（Real-Time Operating System, RTOS）是一类专门为满足严格时间约束而设计的操作系统。与通用操作系统（General Purpose OS, GPOS）不同，RTOS的核心目标不是吞吐量最大化，而是保证任务在确定的时间内完成。在机器人、工业控制、航空航天、医疗设备等领域，RTOS是构建可靠嵌入式系统的基础。


## 什么是实时操作系统

实时操作系统的"实时"并不意味着"快速"，而是指系统能够在可预测的、确定的时间内响应外部事件。一个RTOS必须满足以下基本要求：

- **确定性（Determinism）**：系统的响应时间是可预测的，而非统计平均意义上的快速。
- **可靠性（Reliability）**：在任何负载条件下都能保证关键任务按时完成。
- **多任务支持（Multitasking）**：支持多个任务并发执行，并通过调度算法合理分配处理器资源。
- **低中断延迟（Low Interrupt Latency）**：能够快速响应硬件中断，将控制权交给对应的中断服务程序。

RTOS与通用操作系统的根本区别在于：通用操作系统追求的是平均性能最优，而RTOS追求的是最坏情况性能可控。


## 硬实时与软实时

根据对时间约束违反的容忍程度，实时系统可分为两类：

### 硬实时系统 (Hard Real-Time)

硬实时系统要求所有任务必须在截止时间（Deadline）之前完成，否则将导致系统故障甚至灾难性后果。典型应用包括：

- 飞行控制系统（Flight Control System）
- 汽车安全气囊控制（Airbag Controller）
- 心脏起搏器（Pacemaker）
- 工业机器人运动控制（Robot Motion Control）

在硬实时系统中，错过一个截止时间可能意味着生命危险或重大财产损失。

### 软实时系统 (Soft Real-Time)

软实时系统允许偶尔错过截止时间，虽然这会导致服务质量下降，但不会造成系统崩溃。典型应用包括：

- 视频流播放（Video Streaming）
- 在线交易系统（Online Trading System）
- 网络数据包处理（Network Packet Processing）
- 人机交互界面（Human-Machine Interface）

还有一种介于两者之间的**准硬实时系统（Firm Real-Time）**，在该系统中，错过截止时间的结果虽然不会导致灾难，但该次计算结果将被视为无效而丢弃。


## 调度算法

RTOS的核心功能之一是任务调度（Task Scheduling）。调度算法决定了在多个任务就绪时，哪个任务应当获得处理器的使用权。

### 基于优先级的抢占式调度 (Priority-Based Preemptive Scheduling)

这是最常用的RTOS调度策略。每个任务被分配一个优先级，调度器总是运行当前就绪队列中优先级最高的任务。当一个更高优先级的任务就绪时，它会立即抢占（Preempt）当前正在运行的低优先级任务。

- **优点**：实现简单，响应速度快，确定性好。
- **缺点**：需要仔细设计优先级分配，否则可能出现优先级反转（Priority Inversion）问题。
- **使用该策略的RTOS**：FreeRTOS、uC/OS-II、VxWorks、QNX等绝大多数RTOS。

**优先级反转（Priority Inversion）**是指高优先级任务因等待低优先级任务持有的资源而被阻塞，同时一个中等优先级任务抢占了低优先级任务，导致高优先级任务被无限期延迟。解决方案包括优先级继承协议（Priority Inheritance Protocol）和优先级天花板协议（Priority Ceiling Protocol）。

### 时间片轮转调度 (Round-Robin Scheduling)

时间片轮转调度为每个任务分配一个固定的时间片（Time Slice / Time Quantum），任务按顺序轮流执行。当一个任务的时间片耗尽时，调度器将其放到就绪队列末尾，切换到下一个任务。

- **优点**：公平性好，每个任务都能获得处理器时间。
- **缺点**：确定性较差，不适合对响应时间要求严格的硬实时场景。
- **典型应用**：通常与优先级调度结合使用，在同优先级任务之间进行时间片轮转。

### 最早截止时间优先 (Earliest Deadline First, EDF)

EDF是一种动态优先级调度算法，它根据任务截止时间的先后动态调整优先级。截止时间最近的任务拥有最高优先级。

- **优点**：理论上是最优的动态调度算法，处理器利用率可达100%（在理想条件下）。
- **缺点**：实现复杂，运行时开销较大，在过载时行为难以预测。
- **使用该策略的RTOS**：RTEMS（部分支持）、某些学术研究系统。

### 单调速率调度 (Rate Monotonic Scheduling, RMS)

RMS是一种静态优先级分配策略，任务的优先级与其周期成反比：周期越短的任务优先级越高。Liu和Layland在1973年证明，RMS是静态优先级调度中的最优策略。

- **处理器利用率上界**：\(U = n(2^{1/n} - 1)\)，当任务数量趋于无穷时，上界约为69.3%。


## 关键性能指标

评估RTOS性能时，需要关注以下核心指标：

### 中断延迟 (Interrupt Latency)

从硬件中断信号产生到中断服务程序（ISR）开始执行之间的时间。中断延迟由以下部分组成：

- 硬件识别中断的时间
- 完成当前指令的时间
- 保存处理器上下文的时间
- 中断向量查找时间

典型的RTOS中断延迟在微秒级别。

### 任务切换时间 (Context Switch Time)

从一个任务切换到另一个任务所需的时间，包括保存当前任务上下文和恢复目标任务上下文。任务切换时间是衡量RTOS效率的重要指标。

### 抖动 (Jitter)

任务执行周期的波动程度。理想情况下，周期性任务应当严格按照固定间隔执行。抖动的存在意味着实际执行间隔会偏离理论值。对于伺服控制（Servo Control）等应用，抖动必须控制在极小范围内。

### 最坏情况执行时间 (Worst-Case Execution Time, WCET)

一个任务在最不利条件下完成执行所需的最长时间。WCET分析是硬实时系统设计中最关键的步骤之一。只有当所有任务的WCET之和满足调度可行性条件时，系统才是可靠的。


## 常见的RTOS

目前市场上常见的商用实时操作系统有：

- uCosII / uCosIII | Micrium
- FreeRTOS
- Nucleus RTOS | Mentor Graphics
- RTLinux (需要MMU支持)
- QNX (需要MMU支持)
- VxWorks | WindRiver
- eCos
- RTEMS

国产的另有：

- RT-Thread
- 华为Lite-OS
- 阿里AliOS things
- DJYOS
- 天脉


## RTOS选型指南

选择RTOS时需要综合考虑以下因素：

- **实时性要求**：硬实时场景需要选择确定性更强的RTOS，如VxWorks或QNX；软实时场景可以考虑RTLinux或FreeRTOS。
- **硬件资源**：资源受限的微控制器（如Cortex-M系列）适合FreeRTOS、uC/OS等轻量级RTOS；拥有MMU的处理器可以使用QNX、VxWorks等功能完善的RTOS。
- **生态系统与社区支持**：FreeRTOS拥有最活跃的开源社区和最广泛的硬件支持；VxWorks和QNX则提供商业级技术支持。
- **安全认证需求**：如果系统需要通过DO-178C（航空）、IEC 61508（工业）、ISO 26262（汽车）等安全认证，VxWorks和QNX是较成熟的选择。
- **成本预算**：FreeRTOS和RTEMS是免费的开源方案；商业RTOS的授权费用从数千到数十万元不等。
- **开发工具**：良好的IDE、调试器、分析工具可以显著提高开发效率。VxWorks配套的Wind River Workbench和QNX的Momentics IDE都提供了完善的开发环境。


## 主要RTOS对比

| 特性 | FreeRTOS | uC/OS-III | VxWorks | QNX | RT-Thread | RTLinux |
|------|----------|-----------|---------|-----|-----------|---------|
| 许可类型 | MIT开源 | Apache 2.0 | 商业 | 商业 | Apache 2.0 | GPL |
| 最小ROM | ~5 KB | ~6 KB | ~200 KB | ~100 KB | ~3 KB | 较大 |
| 最小RAM | ~1 KB | ~1 KB | ~20 KB | ~32 KB | ~1 KB | 较大 |
| 内核类型 | 微内核 | 微内核 | 微内核 | 微内核 | 混合内核 | 宏内核补丁 |
| 支持MMU | 否 | 否 | 是 | 是 | 可选 | 是 |
| POSIX兼容 | 部分 | 否 | 是 | 完全 | 部分 | 完全 |
| 安全认证 | IEC 61508 | 医疗/工业 | DO-178C等 | ISO 26262等 | 无 | 无 |
| 典型应用 | IoT/嵌入式 | 工业控制 | 航空航天 | 汽车/医疗 | IoT/嵌入式 | 工业控制 |
| 调度算法 | 优先级抢占 | 优先级抢占 | 优先级抢占 | 优先级抢占 | 优先级抢占+RR | FIFO/RR |
| 商业支持 | AWS | Silicon Labs | Wind River | BlackBerry | RT-Thread社区 | 社区 |


其中除了FreeRTOS, RTEMS和RTLinux是免费的之外，其余RTOS都是需要商业授权的。uCos II和FreeRTOS是平时接触比较多的RTOS，相关资料比较多。而VxWorks是安全性公认最佳的，用于航空航天、轨道交通和卫星的应用。如果系统中需要使用复杂的文件、数据库、网络等功能，那么以Linux为基础的RTLinux是比较好的选择；但是如果系统对实时性和确定性的要求非常高，那么可以使用较为简单的RTOS（如 uCosII），再根据需要开发通信协议或者软件包。总体上来说，操作系统的复杂性是与应用软件的复杂性一致的。同时，功能上更复杂的RTOS对硬件系统资源的需求也会更高。


## 参考资料
1. 戴晓天, [RTOS操作系统杂谈](https://www.yfworld.com/?p=2911)，云飞机器人实验室
2. C. L. Liu and J. W. Layland, "Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment," *Journal of the ACM*, vol. 20, no. 1, pp. 46-61, 1973.
3. J. W. S. Liu, *Real-Time Systems*, Prentice Hall, 2000.
4. A. S. Tanenbaum, *Modern Operating Systems*, 4th Edition, Pearson, 2014.
