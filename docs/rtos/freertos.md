# FreeRTOS

!!! note "引言"
    FreeRTOS是目前全球使用最广泛的实时操作系统内核，自2003年由Richard Barry创建以来，已被移植到超过40种微控制器架构上。2017年，Amazon Web Services（AWS）收购了FreeRTOS项目，将其更名为AWS FreeRTOS，并在原有内核基础上增加了云连接、安全和设备管理等功能。FreeRTOS采用MIT开源许可证，对商业项目完全免费。

FreeRTOS是一个迷你的实时操作系统内核。作为一个轻量级的操作系统，功能包括：任务管理、时间管理、信号量、消息队列、内存管理、记录功能、软件定时器、协程等，可基本满足较小系统的需要。该操作系统由于简单和易用，在轻量级的CPU上目前很多厂商都用这个国外系统。

FreeRTOS是专为小型嵌入式系统设计的可扩展的实时内核。

亮点包括：

- 微小的封装形式。
- 免费的RTOS调度程序
- 免费嵌入式软件源代码。
- 免版税。
- 抢占式，协作式和混合配置选项，可选时间分片。
- SafeRTOS衍生产品对代码完整性提供了高度的信心。
- 包括一个为低功耗应用设计的tickless模式。
- 可以使用动态或静态分配的RAM来创建RTOS对象（任务，队列，信号量，软件定时器，互斥体和事件组）。


## 系统架构

FreeRTOS的架构可以分为三个层次：

- **硬件抽象层（Hardware Abstraction Layer, HAL）**：也称为"可移植层"（Portable Layer），封装了与具体硬件相关的代码，包括中断管理、上下文切换和时钟配置。
- **内核层（Kernel Layer）**：实现了任务调度、时间管理、队列、信号量、互斥锁等核心功能。内核代码与硬件无关，由`tasks.c`、`queue.c`、`list.c`和`timers.c`等少量源文件组成。
- **应用层（Application Layer）**：用户编写的应用代码，通过FreeRTOS提供的API与内核交互。

FreeRTOS内核源代码的核心文件数量很少，典型配置下仅需3个C源文件（`tasks.c`、`queue.c`、`list.c`），编译后的ROM占用通常在5-10 KB之间，RAM占用约1 KB起。


## 任务管理 (Task Management)

FreeRTOS中的基本执行单元是任务（Task）。每个任务拥有独立的栈空间，由调度器管理其执行。

### 任务状态

FreeRTOS中的任务有以下四种状态：

- **运行态（Running）**：任务正在使用处理器执行。单核系统中同一时刻只能有一个任务处于运行态。
- **就绪态（Ready）**：任务已经准备好执行，等待调度器分配处理器时间。
- **阻塞态（Blocked）**：任务正在等待某个事件（如延时到期、队列数据到达、信号量可用等）。阻塞态的任务不消耗处理器时间。
- **挂起态（Suspended）**：任务被显式挂起，不参与调度，直到被其他任务恢复。

### 任务创建

使用`xTaskCreate()`函数创建任务，需要指定任务函数、任务名称、栈大小、参数和优先级：

```c
BaseType_t xTaskCreate(
    TaskFunction_t pvTaskCode,       /* 任务函数指针 */
    const char * const pcName,       /* 任务名称（调试用） */
    configSTACK_DEPTH_TYPE usStackDepth, /* 栈深度（单位：字） */
    void *pvParameters,              /* 传给任务函数的参数 */
    UBaseType_t uxPriority,          /* 任务优先级 */
    TaskHandle_t *pxCreatedTask      /* 返回的任务句柄 */
);
```

FreeRTOS也支持使用`xTaskCreateStatic()`进行静态内存分配的任务创建，适用于不允许动态内存分配的安全关键系统。

### 任务调度

FreeRTOS的调度器采用基于优先级的抢占式调度（Priority-Based Preemptive Scheduling）。优先级数值越大，优先级越高（0为最低优先级，用于空闲任务）。同优先级的任务之间可以配置为时间片轮转方式调度。


## 内存管理 (Memory Management)

FreeRTOS提供了5种内存分配方案（heap_1到heap_5），分别适用于不同的应用场景：

| 方案 | 分配 | 释放 | 合并 | 适用场景 |
|------|------|------|------|----------|
| heap_1 | 支持 | 不支持 | 不适用 | 任务创建后不删除的简单系统 |
| heap_2 | 支持 | 支持 | 不支持 | 频繁创建/删除相同大小对象 |
| heap_3 | 标准malloc | 标准free | 取决于库 | 需要使用标准C库的系统 |
| heap_4 | 支持 | 支持 | 支持 | 通用方案，最常用 |
| heap_5 | 支持 | 支持 | 支持 | 内存地址不连续的系统 |

`heap_4`是最常用的方案，它使用首次适配（First Fit）算法，支持内存块的合并以减少碎片化。


## 任务间通信 (Inter-Task Communication)

### 队列 (Queue)

队列是FreeRTOS中最基本的任务间通信机制。队列采用先进先出（FIFO）的方式传递数据，支持多个任务同时读写。

```c
/* 创建一个可容纳10个int类型元素的队列 */
QueueHandle_t xQueue = xQueueCreate(10, sizeof(int));

/* 发送数据到队列（等待最多100个Tick） */
int value = 42;
xQueueSend(xQueue, &value, pdMS_TO_TICKS(100));

/* 从队列接收数据（等待最多100个Tick） */
int received;
xQueueReceive(xQueue, &received, pdMS_TO_TICKS(100));
```

### 信号量 (Semaphore)

信号量用于任务间的同步和共享资源管理。FreeRTOS支持二值信号量（Binary Semaphore）和计数信号量（Counting Semaphore）。

- **二值信号量**：适用于任务同步场景，例如中断服务程序通知任务处理数据。
- **计数信号量**：适用于资源计数场景，例如管理有限数量的硬件资源。

### 互斥锁 (Mutex)

互斥锁（Mutual Exclusion）是一种特殊的二值信号量，专用于保护共享资源的互斥访问。与普通信号量不同，互斥锁内置了优先级继承机制（Priority Inheritance），可以有效防止优先级反转问题。

```c
/* 创建互斥锁 */
SemaphoreHandle_t xMutex = xSemaphoreCreateMutex();

/* 获取互斥锁 */
if (xSemaphoreTake(xMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
    /* 访问共享资源 */
    /* ... */

    /* 释放互斥锁 */
    xSemaphoreGive(xMutex);
}
```

### 事件组 (Event Group)

事件组允许任务等待一个或多个事件的组合。每个事件组包含一组事件位（Event Bits），任务可以等待某些位被设置。这在需要任务等待多个条件同时满足的场景中非常有用。


## Tick中断与时间管理

FreeRTOS使用一个周期性定时器中断（Tick Interrupt）来驱动时间管理和任务调度。Tick频率通过`configTICK_RATE_HZ`宏定义，典型值为1000 Hz（即每毫秒一次Tick中断）。

Tick中断的主要功能：

- 更新系统时间计数器
- 检查是否有阻塞任务的延时到期
- 在时间片轮转模式下触发任务切换

对于低功耗应用，FreeRTOS提供了**无Tick模式（Tickless Mode）**，在没有任务需要执行时停止Tick中断，让处理器进入低功耗休眠状态，直到下一个任务需要被唤醒时再恢复。


## 硬件抽象层与移植

FreeRTOS的可移植性源于其清晰的硬件抽象层设计。移植FreeRTOS到新的处理器平台，通常只需要实现以下内容：

1. **`portmacro.h`**：定义与平台相关的数据类型和宏，如栈增长方向、临界区操作等。
2. **`port.c`**：实现上下文切换（Context Switch）、Tick定时器初始化和中断管理等功能。
3. **`FreeRTOSConfig.h`**：配置文件，定义系统参数如最大优先级数量、Tick频率、堆大小等。

FreeRTOS官方已经提供了针对ARM Cortex-M、Cortex-A、RISC-V、AVR、PIC、MSP430等数十种处理器架构的移植层代码，开发者通常只需选择对应的端口文件并配置`FreeRTOSConfig.h`即可。

### 移植步骤

1. 从FreeRTOS发行包中选择目标处理器的端口文件（`portable/`目录）。
2. 将内核源文件（`tasks.c`、`queue.c`、`list.c`）和端口文件添加到工程。
3. 创建`FreeRTOSConfig.h`配置文件，设置系统参数。
4. 配置处理器的Tick定时器和中断优先级。
5. 编写应用任务并调用`vTaskStartScheduler()`启动调度器。


## FreeRTOS+TCP

FreeRTOS+TCP是FreeRTOS官方提供的TCP/IP协议栈，专为嵌入式系统优化。其主要特点包括：

- 支持TCP和UDP协议
- 提供与BSD Socket兼容的API
- 支持DHCP客户端
- 支持DNS解析
- 内存占用可配置，适合资源受限的系统
- 支持多种网络接口驱动（如STM32 Ethernet、LPC Ethernet等）


## AWS IoT集成

Amazon收购FreeRTOS后，推出了AWS IoT集成方案，使嵌入式设备可以安全地连接到AWS云服务。主要组件包括：

- **coreMQTT**：轻量级MQTT客户端库，用于设备与云端的消息通信。
- **coreHTTP**：轻量级HTTP客户端库。
- **corePKCS11**：加密密钥管理接口。
- **AWS IoT Device Shadow**：设备影子服务，维护设备状态的云端副本。
- **AWS IoT OTA**：空中固件升级（Over-The-Air Update）支持。

这些库都遵循FreeRTOS的设计理念，代码量小、可移植性强，适合运行在资源受限的微控制器上。


## 代码示例

以下是一个完整的FreeRTOS应用示例，演示了两个任务通过队列进行通信：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

/* 队列句柄 */
QueueHandle_t xSensorQueue;

/* 传感器采集任务 */
void vSensorTask(void *pvParameters)
{
    int sensor_value;

    for (;;) {
        /* 模拟读取传感器数据 */
        sensor_value = read_sensor();

        /* 将传感器数据发送到队列 */
        xQueueSend(xSensorQueue, &sensor_value, portMAX_DELAY);

        /* 每100ms采集一次 */
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

/* 数据处理任务 */
void vProcessTask(void *pvParameters)
{
    int received_value;

    for (;;) {
        /* 从队列接收数据（阻塞等待） */
        if (xQueueReceive(xSensorQueue, &received_value, portMAX_DELAY) == pdTRUE) {
            /* 处理接收到的传感器数据 */
            process_data(received_value);
        }
    }
}

int main(void)
{
    /* 硬件初始化 */
    hardware_init();

    /* 创建队列（容量为10个int） */
    xSensorQueue = xQueueCreate(10, sizeof(int));

    /* 创建传感器采集任务（优先级2） */
    xTaskCreate(vSensorTask, "Sensor", 256, NULL, 2, NULL);

    /* 创建数据处理任务（优先级1） */
    xTaskCreate(vProcessTask, "Process", 256, NULL, 1, NULL);

    /* 启动调度器 */
    vTaskStartScheduler();

    /* 正常情况下不会执行到这里 */
    for (;;);
}
```


## 参考资料

1. Richard Barry, *Mastering the FreeRTOS Real Time Kernel - A Hands-On Tutorial Guide*, Real Time Engineers Ltd.
2. [FreeRTOS官方文档](https://www.freertos.org/Documentation/RTOS_book.html)
3. [FreeRTOS GitHub仓库](https://github.com/FreeRTOS/FreeRTOS)
4. [AWS FreeRTOS开发者指南](https://docs.aws.amazon.com/freertos/)
