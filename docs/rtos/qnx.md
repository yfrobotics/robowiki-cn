# QNX

!!! note "引言"
    QNX是一个基于微内核架构的商用实时操作系统，以其卓越的可靠性和模块化设计著称。QNX在汽车电子领域占据主导地位，全球数亿辆汽车的信息娱乐系统和数字座舱运行QNX系统。2010年被Research In Motion（RIM，即后来的BlackBerry）收购后，QNX进一步拓展了在自动驾驶、医疗设备和工业控制等领域的应用。

是加拿大QNX公司出品的一种商用的、遵从POSIX标准规范的类UNIX实时操作系统。QNX是最成功的微内核操作系统之一，在汽车领域得到了极为广泛的应用，如保时捷跑车的音乐和媒体控制系统和美国陆军无人驾驶Crusher坦克的控制系统，还有RIM公司的blackberry playbook平板电脑。具有独一无二的微内核实时平台，实时、稳定、可靠、运行速度极快。


## 微内核架构 (Microkernel Architecture)

QNX的设计哲学是真正的微内核架构（True Microkernel Architecture）。在QNX中，内核（称为Neutrino微内核）仅负责最基本的功能：

- **进程调度（Process Scheduling）**
- **进程间通信（Inter-Process Communication, IPC）**
- **中断分发（Interrupt Dispatching）**
- **定时器服务（Timer Services）**

所有其他系统服务——包括设备驱动程序、文件系统、网络协议栈、甚至图形子系统——都以用户态进程的形式运行在内核之外。这种设计带来了显著的优势：

- **高可靠性**：任何一个用户态服务进程的崩溃不会导致整个系统宕机。内核可以检测到故障进程并自动重启它，而不影响其他服务。
- **模块化**：系统服务可以动态加载和卸载，无需重新编译内核。
- **安全性**：每个服务运行在独立的地址空间中，内存保护防止了服务之间的相互干扰。

QNX的微内核非常小，Neutrino微内核的代码量仅约100KB，这意味着其中存在潜在缺陷的可能性远低于包含数百万行代码的宏内核操作系统。


## QNX Neutrino RTOS

QNX Neutrino是QNX操作系统的现代版本，也是当前的主力产品。其主要特性包括：

### 进程模型

QNX Neutrino采用完整的进程模型，每个进程拥有独立的虚拟地址空间。进程内部可以包含多个线程（Thread），线程是调度的基本单位。这与许多嵌入式RTOS仅支持"任务"（共享地址空间）的方式不同。

### 调度策略

QNX Neutrino支持多种调度策略，可以按线程级别独立配置：

- **FIFO调度（SCHED_FIFO）**：同优先级内先到先服务，高优先级线程可以抢占低优先级线程。
- **轮转调度（SCHED_RR）**：同优先级内时间片轮转，适合需要公平共享处理器的场景。
- **散发调度（SCHED_SPORADIC）**：为散发性任务（Sporadic Task）设计的高级调度策略，可以限制线程在给定时间段内的处理器使用量。

QNX支持256个优先级等级（0-255），其中优先级0分配给空闲线程。


## POSIX兼容性

QNX是POSIX兼容性最好的嵌入式RTOS之一。它支持：

- **POSIX 1003.1**：基本操作系统接口（文件操作、进程管理等）。
- **POSIX 1003.1b**：实时扩展（信号量、共享内存、消息队列、异步I/O等）。
- **POSIX 1003.1c**：线程扩展（pthread线程、互斥锁、条件变量等）。
- **POSIX 1003.1d/1003.1j**：高级实时扩展。

POSIX兼容性使得大量为Linux或UNIX编写的应用程序可以相对容易地移植到QNX上。开发者可以使用熟悉的POSIX API进行开发，降低了学习成本。


## 消息传递IPC (Message Passing IPC)

消息传递（Message Passing）是QNX最核心的IPC机制，也是整个系统架构的基石。QNX的消息传递具有以下特点：

### 同步消息传递

QNX的消息传递是同步的（Synchronous）：发送消息的线程会被阻塞，直到接收方处理完消息并回复（Reply）。这个过程包含三个步骤：

1. **Send**：客户端线程发送消息到服务器，客户端进入SEND-blocked状态。
2. **Receive**：服务器线程接收消息并处理，客户端进入REPLY-blocked状态。
3. **Reply**：服务器线程回复结果，客户端解除阻塞。

### 脉冲 (Pulse)

对于不需要同步回复的场景，QNX提供了脉冲（Pulse）机制。脉冲是一种小型的异步通知，不会阻塞发送者。脉冲常用于中断处理程序向线程发送通知。

### 基于消息传递的资源管理器

QNX的设备驱动和文件系统都是通过资源管理器（Resource Manager）框架实现的。资源管理器是一个用户态进程，它注册一个路径名（如`/dev/ser1`），当应用程序对该路径执行`open()`、`read()`、`write()`等操作时，内核将这些操作转化为消息传递给对应的资源管理器进程处理。


## 汽车领域应用

QNX在汽车电子领域拥有最广泛的部署，主要产品线包括：

### QNX Car平台

QNX Car是面向车载信息娱乐系统（In-Vehicle Infotainment, IVI）的软件平台，提供：

- HTML5应用引擎
- 多媒体框架（音频、视频播放）
- 蓝牙、Wi-Fi连接
- 语音识别集成
- 智能手机互联（Apple CarPlay、Android Auto）

### BlackBerry QNX

被BlackBerry收购后，QNX推出了面向自动驾驶的解决方案：

- **QNX OS for Safety**：通过ISO 26262 ASIL D认证的安全操作系统，用于高级驾驶辅助系统（ADAS）和自动驾驶控制系统。
- **QNX Hypervisor**：虚拟化平台，允许在同一硬件上同时运行多个操作系统（如QNX + Linux + Android），实现安全关键功能和信息娱乐功能的整合。
- **BlackBerry IVY**：与AWS合作推出的智能汽车数据平台，实现车辆数据的边缘计算和云端分析。


## 安全认证

QNX在安全认证方面具有深厚的积累：

| 认证标准 | 适用领域 | 等级 |
|----------|----------|------|
| ISO 26262 | 汽车功能安全 | ASIL D |
| IEC 61508 | 工业功能安全 | SIL 3 |
| IEC 62304 | 医疗设备软件 | Class C |
| EN 50128 | 轨道交通 | SIL 3/4 |

QNX OS for Safety是专门为通过这些认证而设计的产品，提供了完整的安全认证包，包括源代码、测试用例、追溯矩阵和安全手册。


## 自适应分区 (Adaptive Partitioning)

自适应分区（Adaptive Partitioning）是QNX的独特功能，它允许管理员为不同的进程组分配CPU时间预算（Budget）。

自适应分区的核心特点：

- **保证最低CPU资源**：即使系统处于高负载状态，每个分区都能获得其预算的CPU时间。
- **自适应分配**：当某些分区不需要全部预算时间时，空闲的CPU时间会按比例分配给其他有需求的分区。
- **安全隔离**：防止低优先级或异常进程耗尽系统资源，确保关键任务始终获得足够的处理器时间。
- **运行时可调**：分区的CPU预算可以在运行时动态调整，无需重启系统。

这一功能在汽车和工业控制等多任务环境中尤为重要。例如，在一个汽车信息娱乐系统中，可以将导航、媒体播放和蓝牙通信分配到不同的分区，确保导航应用在播放高清视频时仍能流畅运行。


## QNX软件开发平台 (QNX SDP)

QNX SDP（Software Development Platform）是QNX的完整开发工具包，主要组件包括：

- **QNX Momentics IDE**：基于Eclipse的集成开发环境，提供代码编辑、交叉编译、远程调试和系统分析功能。
- **系统分析工具（System Analysis Toolkit）**：实时显示进程调度、CPU占用、内存使用和IPC活动，帮助开发者优化系统性能。
- **内存分析工具**：检测内存泄漏、缓冲区溢出和野指针等问题。
- **代码覆盖率工具**：用于安全认证所需的测试覆盖率分析。
- **目标文件系统构建器**：用于创建和定制QNX文件系统镜像。

QNX SDP支持在Windows和Linux主机上进行交叉开发，目标平台包括ARM、x86和MIPS等架构。


## 参考资料

1. Robert Krten, *Getting Started with QNX Neutrino*, PARSE Software Devices, 2009.
2. [QNX Neutrino RTOS官方文档](https://www.qnx.com/developers/docs/)
3. [BlackBerry QNX官方网站](https://blackberry.qnx.com/)
4. Dan Dodge, "The QNX Microkernel," *QNX Software Systems Technical Paper*.
