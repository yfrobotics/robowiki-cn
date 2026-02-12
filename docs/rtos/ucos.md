# μC/OS

!!! note "引言"
    μC/OS（Micro-Controller Operating System）是由Jean J. Labrosse于1991年创建的实时操作系统内核，是嵌入式系统教学和工业应用中最经典的RTOS之一。μC/OS系列经历了三代演进：μC/OS、μC/OS-II和μC/OS-III，功能逐步增强。2016年，Silicon Labs收购了Micrium公司，并于2020年将μC/OS系列以Apache 2.0许可证开源。

μC/OS-II (以及μC/OS-III) 是著名的源代码公开的实时内核，是专为嵌入式应用设计的，可用于8位，16位和32位单片机或数字信号处理器（dsp）。它是在原版本μC/OS的基础上做了重大改进与升级，并有了近十年的使用实践，有许多成功应用该实时内核的实例。它的主要特点如下：

1. 公开源代码，容易就能把操作系统移植到各个不同的硬件平台上；
2. 可移植性，绝大部分源代码是用C语言写的，便于移植到其他微处理器上；
3. 可固化；
4. 可裁剪性，有选择的使用需要的系统服务，以减少斗所需的存储空间；
5. 抢占式，完全是抢占式的实时内核，即总是运行就绪条件下优先级最高的任务；
6. 多任务，可管理64个任务，任务的优先级必须是不同的，不支持时间片轮转调度法；
7. 可确定性，函数调用与服务的执行时间具有其可确定性，不依赖于任务的多少；
8. 实用性和可靠性，成功应用该实时内核的实例，是其实用性和可靠性的最好证据。

由于μC/OS一Ⅱ仅是一个实时内核，这就意味着它不像其他实时存在系统那样提供给用户的只是一些API函数接口，还有很多工作需要用户自己去完成。


## 系统架构

μC/OS-II的架构设计清晰，分为以下几个层次：

- **应用层（Application Layer）**：用户编写的应用程序代码，通过μC/OS-II提供的API调用内核服务。
- **内核层（Kernel Layer）**：实现任务管理、时间管理、事件管理（信号量、互斥锁、消息队列、事件标志组）和内存管理等核心功能。核心代码由`os_core.c`、`os_task.c`、`os_time.c`等源文件组成。
- **配置层（Configuration Layer）**：通过`os_cfg.h`头文件进行系统裁剪，用户可以选择性地启用或禁用内核功能，以最小化ROM和RAM占用。
- **处理器抽象层（Processor Abstraction Layer）**：与硬件相关的代码，包括`os_cpu.h`（处理器相关的宏定义和数据类型）、`os_cpu_a.asm`（汇编语言编写的上下文切换代码）和`os_cpu_c.c`（处理器相关的C语言代码）。

μC/OS-II的全部源代码不到6000行，结构紧凑，非常适合用于教学和学习操作系统原理。


## 任务状态 (Task States)

μC/OS-II中的任务有以下五种状态：

- **休眠态（Dormant）**：任务已存在于内存中但尚未被内核管理。调用`OSTaskCreate()`后任务进入就绪态。
- **就绪态（Ready）**：任务已经准备好运行，等待调度器分配处理器时间。
- **运行态（Running）**：任务正在使用处理器执行。在任何时刻只有一个任务处于运行态。
- **等待态（Waiting）**：任务正在等待某个事件的发生（如信号量、消息或延时到期）。
- **中断服务态（ISR Running）**：当中断发生时，正在运行的任务被挂起，处理器转而执行中断服务程序。

任务状态的转换关系是理解μC/OS-II调度机制的基础。例如，一个处于运行态的任务调用`OSTimeDly()`后会进入等待态；当延时到期后，内核将其移回就绪态；如果此时它是最高优先级的就绪任务，调度器会将其切换为运行态。


## 调度算法

μC/OS-II采用**基于优先级的抢占式调度算法（Priority-Based Preemptive Scheduling）**。其核心规则是：调度器始终选择就绪队列中优先级最高的任务执行。

### 优先级管理

在μC/OS-II中，每个任务必须拥有唯一的优先级（0为最高优先级），系统最多支持64个优先级等级（即最多64个任务）。内核使用一个优先级位图表（Priority Bitmap）来快速查找最高优先级的就绪任务，查找时间为常数O(1)，与任务数量无关。

优先级位图的核心数据结构包括：

- `OSRdyGrp`：就绪组，标记哪些优先级组中有就绪任务。
- `OSRdyTbl[]`：就绪表，标记每个优先级组中具体哪些任务就绪。

通过查表法（Lookup Table），μC/OS-II可以在3条语句内找到最高优先级的就绪任务，这保证了调度的确定性。

### 调度时机

以下情况会触发调度器进行任务切换：

- 任务调用`OSTimeDly()`或`OSTimeDlyHMSM()`进入延时等待
- 任务等待信号量、消息或事件标志
- 任务释放信号量或发送消息使更高优先级任务就绪
- 中断服务程序结束时
- 任务被删除或挂起


## 内存管理 (Memory Management)

μC/OS-II提供了固定大小内存块的分区内存管理（Partition Memory Management）机制。与动态内存分配（如malloc/free）相比，固定大小内存块管理具有以下优势：

- **确定性**：分配和释放操作的执行时间是恒定的。
- **无碎片化**：由于所有内存块大小相同，不会产生外部碎片。
- **简单可靠**：实现简单，不易出错。

使用内存分区的基本流程：

```c
/* 定义内存分区：10个内存块，每块32字节 */
OS_MEM  *pMemPartition;
INT8U    MemBuf[10][32];
INT8U    err;

/* 创建内存分区 */
pMemPartition = OSMemCreate(MemBuf, 10, 32, &err);

/* 申请一个内存块 */
void *pBlock = OSMemGet(pMemPartition, &err);

/* 使用内存块 */
/* ... */

/* 归还内存块 */
OSMemPut(pMemPartition, pBlock);
```


## 任务间通信 (Inter-Task Communication)

μC/OS-II提供了多种任务间通信和同步机制：

### 信号量 (Semaphore)

信号量是最基本的同步机制，用于实现任务之间的同步或保护共享资源。μC/OS-II支持计数信号量，其值可以从0到65535。

### 互斥信号量 (Mutual Exclusion Semaphore)

互斥信号量是μC/OS-II为解决优先级反转问题而提供的特殊信号量。当低优先级任务持有互斥信号量时，如果有高优先级任务请求该信号量，内核会暂时将低优先级任务的优先级提升到互斥信号量预设的优先级天花板（Priority Ceiling），从而避免中间优先级任务的干扰。

### 消息邮箱 (Message Mailbox)

消息邮箱允许一个任务向另一个任务发送一个指针大小的消息。邮箱一次只能容纳一条消息，适用于简单的任务间数据传递。

### 消息队列 (Message Queue)

消息队列可以看作是消息邮箱的数组形式，允许存储多条消息。任务可以向队列发送消息，也可以从队列接收消息，支持先进先出（FIFO）和后进先出（LIFO）两种方式。

### 事件标志组 (Event Flag Group)

事件标志组允许任务等待多个事件的组合（逻辑与或逻辑或）。每个事件标志组包含多个标志位，任务可以等待某些标志位被设置或清除。


## μC/OS-III的改进

μC/OS-III是μC/OS-II的重大升级版本，主要改进包括：

- **无限数量的任务**：不再限制64个任务，支持任意数量的任务（仅受RAM限制）。
- **支持相同优先级**：多个任务可以拥有相同的优先级，同优先级任务之间采用时间片轮转调度。
- **优化的调度器**：调度器的时间复杂度仍为O(1)，但内部实现更加高效。
- **时间戳功能（Timestamping）**：支持高精度时间戳，可以精确测量中断延迟和任务切换时间。
- **嵌套的任务挂起**：支持多次挂起同一个任务，需要相同次数的恢复才能使任务重新就绪。
- **更多的内核对象**：增加了任务信号量（Task Semaphore）和任务消息队列（Task Message Queue），每个任务内建一个信号量和一个消息队列，无需额外创建内核对象。
- **丰富的统计功能**：内置CPU利用率统计、栈使用量统计、每个任务的运行时间统计等。


## Micrium与Silicon Labs

Micrium是μC/OS系列的开发公司，由Jean J. Labrosse于1999年创立。除了μC/OS内核外，Micrium还开发了一系列配套的嵌入式软件组件：

- **μC/TCP-IP**：嵌入式TCP/IP协议栈
- **μC/FS**：嵌入式文件系统
- **μC/USB**：USB主机和设备协议栈
- **μC/CAN**：CAN总线协议栈
- **μC/Modbus**：Modbus通信协议栈

2016年，芯片厂商Silicon Labs收购了Micrium，将μC/OS系列与其硬件产品深度整合。2020年，Silicon Labs宣布将μC/OS-II、μC/OS-III及其全部配套组件以Apache 2.0许可证开源，极大地降低了使用门槛。


## 代码示例

以下是一个μC/OS-II的基础应用示例，演示了两个任务通过信号量进行同步：

```c
#include "ucos_ii.h"

#define TASK_STK_SIZE  512

/* 任务栈 */
OS_STK TaskStartStk[TASK_STK_SIZE];
OS_STK TaskLedStk[TASK_STK_SIZE];

/* 信号量 */
OS_EVENT *SemSignal;

/* 启动任务：周期性发送信号量 */
void TaskStart(void *pdata)
{
    (void)pdata;

    /* 初始化系统时钟节拍 */
    OS_CPU_SysTickInit();

    while (1) {
        /* 发送信号量通知LED任务 */
        OSSemPost(SemSignal);

        /* 延时500ms */
        OSTimeDlyHMSM(0, 0, 0, 500);
    }
}

/* LED任务：等待信号量后翻转LED */
void TaskLed(void *pdata)
{
    INT8U err;
    (void)pdata;

    while (1) {
        /* 等待信号量（无限等待） */
        OSSemPend(SemSignal, 0, &err);

        /* 翻转LED状态 */
        LED_Toggle();
    }
}

int main(void)
{
    /* 硬件初始化 */
    BSP_Init();

    /* 初始化μC/OS-II */
    OSInit();

    /* 创建信号量（初始值为0） */
    SemSignal = OSSemCreate(0);

    /* 创建任务 */
    OSTaskCreate(TaskStart, NULL, &TaskStartStk[TASK_STK_SIZE - 1], 10);
    OSTaskCreate(TaskLed,   NULL, &TaskLedStk[TASK_STK_SIZE - 1],   11);

    /* 启动多任务调度 */
    OSStart();

    return 0;
}
```


## 参考资料

1. Jean J. Labrosse, *MicroC/OS-II: The Real-Time Kernel*, 2nd Edition, CMP Books, 2002.
2. Jean J. Labrosse, *μC/OS-III: The Real-Time Kernel*, Micrium Press, 2011.
3. [Micrium μC/OS GitHub仓库](https://github.com/SiliconLabs/uC-OS2)
4. [Silicon Labs - Micrium RTOS](https://www.silabs.com/developers/micrium)
