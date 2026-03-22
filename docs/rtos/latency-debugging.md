# 延迟调试

!!! note "引言"
    实时系统中的延迟（Latency）是指从事件发生到系统响应完成之间的时间间隔。对于机器人控制系统，过高的延迟或不可预测的延迟抖动（Jitter）会导致控制性能下降甚至系统失稳。本文介绍实时系统中延迟的分类、测量方法、常用调试工具以及优化技术。


## 延迟分类

### 中断延迟（Interrupt Latency）

中断延迟是从硬件中断信号触发到中断服务程序（Interrupt Service Routine, ISR）开始执行的时间。它由以下部分组成：

$$
T_{interrupt} = T_{recognition} + T_{pipeline} + T_{context}
$$

- \(T_{recognition}\)：中断控制器识别并仲裁中断的时间
- \(T_{pipeline}\)：CPU 流水线刷新时间
- \(T_{context}\)：保存当前上下文（寄存器）的时间

典型值：

| 平台 | 典型中断延迟 |
|------|------------|
| ARM Cortex-M4 (STM32F4) | 12 个时钟周期（~70 ns @ 168 MHz） |
| ARM Cortex-A53 (RPi 4) | 1–10 μs（取决于缓存状态） |
| x86_64 (PREEMPT_RT) | 5–50 μs |

### 调度延迟（Scheduling Latency）

调度延迟是从任务变为就绪状态到实际开始执行的时间，包括：

- 中断处理时间
- 调度器决策时间
- 上下文切换时间

### 端到端延迟（End-to-End Latency）

在机器人系统中，端到端延迟通常指从传感器采样到执行器响应的完整链路：

```
传感器采样 → ADC 转换 → 数据读取 → 滤波/融合 → 控制计算 → DAC/PWM 输出 → 执行器响应
```

每个环节都贡献延迟，总延迟为各环节之和。典型的控制回路端到端延迟目标：

| 应用 | 目标端到端延迟 | 允许抖动 |
|------|-------------|---------|
| 电机电流环 | < 100 μs | < 10 μs |
| 姿态稳定 | < 2 ms | < 200 μs |
| 视觉伺服 | < 30 ms | < 5 ms |
| 导航规划 | < 100 ms | < 20 ms |


## 测量方法

### GPIO 翻转法

最直接的延迟测量方法是使用 GPIO 引脚配合示波器：

```c
// 在 ISR 入口翻转 GPIO（用示波器测量中断源到 GPIO 翻转的时间差）
void EXTI0_IRQHandler(void) {
    HAL_GPIO_WritePin(DEBUG_GPIO_Port, DEBUG_Pin, GPIO_PIN_SET);

    // 实际中断处理
    process_sensor_data();

    HAL_GPIO_WritePin(DEBUG_GPIO_Port, DEBUG_Pin, GPIO_PIN_RESET);
    HAL_EXTI_IRQHandler(&hexti0);
}
```

用示波器观察中断源信号与 GPIO 信号之间的时间差即为中断延迟。GPIO 翻转本身的开销仅几十纳秒，可以忽略。

### DWT 周期计数器（ARM Cortex-M）

ARM Cortex-M 系列提供数据观察点与跟踪单元（Data Watchpoint and Trace, DWT），可精确测量代码段执行时间：

```c
// 启用 DWT 周期计数器
CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
DWT->CYCCNT = 0;
DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

void measure_task_execution(void) {
    uint32_t start = DWT->CYCCNT;

    // 被测代码
    compute_control_output();

    uint32_t cycles = DWT->CYCCNT - start;
    float time_us = (float)cycles / (SystemCoreClock / 1000000);

    // 更新统计
    if (time_us > max_execution_time) {
        max_execution_time = time_us;
    }
}
```

### 软件时间戳

在 RTOS 环境中，可使用高精度定时器记录时间戳：

```c
// FreeRTOS 中使用硬件定时器获取微秒级时间戳
static volatile uint32_t latency_samples[1000];
static volatile uint32_t sample_index = 0;

void vControlTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();

    for (;;) {
        uint32_t expected_time = xLastWakeTime * portTICK_PERIOD_MS * 1000;
        uint32_t actual_time = get_microsecond_timer();
        uint32_t jitter = abs((int32_t)(actual_time - expected_time));

        if (sample_index < 1000) {
            latency_samples[sample_index++] = jitter;
        }

        // 控制计算
        compute_control();

        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(5));
    }
}
```


## Linux 调试工具

### cyclictest

`cyclictest` 是 Linux 实时性测试的标准工具，测量调度延迟的分布：

```bash
# 安装 rt-tests 工具包
sudo apt install rt-tests

# 基本测试：运行 10000 次循环，线程优先级 99
sudo cyclictest -t1 -p 99 -n -i 1000 -l 10000

# 多核测试（每个核一个线程）
sudo cyclictest -t4 -p 99 -n -i 1000 -l 100000 -m

# 输出示例：
# T: 0 ( 1234) P:99 I:1000 C: 100000 Min:    2 Act:    5 Avg:    4 Max:   23
```

输出解读：

| 字段 | 含义 |
|------|------|
| Min | 最小延迟（μs） |
| Avg | 平均延迟（μs） |
| Max | 最大延迟（μs） |

对于实时控制系统，关键指标是 **Max** 值。典型目标：

- PREEMPT_RT 内核：Max < 100 μs
- 标准 Linux 内核：Max 可达数毫秒甚至更高

### ftrace

ftrace 是 Linux 内核内置的跟踪框架，可定位延迟来源：

```bash
# 启用函数跟踪
echo function_graph > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on

# 跟踪特定函数
echo schedule > /sys/kernel/debug/tracing/set_ftrace_filter

# 使用 irqsoff 追踪器找到最长中断禁用时间段
echo irqsoff > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on
# ... 运行负载 ...
cat /sys/kernel/debug/tracing/trace

# 使用 preemptoff 追踪器找到最长抢占禁用时间段
echo preemptoff > /sys/kernel/debug/tracing/current_tracer

# 查看跟踪结果
cat /sys/kernel/debug/tracing/trace
```

### LTTng

LTTng（Linux Trace Toolkit next generation）提供低开销的内核和用户空间跟踪：

```bash
# 安装
sudo apt install lttng-tools lttng-modules-dkms

# 创建会话并添加跟踪事件
lttng create my-session
lttng enable-event -k sched_switch,sched_wakeup,irq_handler_entry,irq_handler_exit
lttng start

# 运行被测应用
./my_robot_controller &
sleep 10

# 停止并查看
lttng stop
lttng destroy
babeltrace ~/lttng-traces/my-session-* | head -50
```

### Tracealyzer

Percepio Tracealyzer 是一款商业可视化工具，支持 FreeRTOS、Zephyr、ThreadX 等 RTOS 的任务执行时序可视化。它通过在 RTOS 中插桩记录事件流，然后在 PC 上以甘特图、CPU 负载图、响应时间直方图等形式展示，非常适合诊断复杂的多任务交互问题。


## PREEMPT_RT 补丁

### 概述

PREEMPT_RT 补丁将标准 Linux 内核改造为完全可抢占的实时内核。主要改动包括：

- 将几乎所有中断处理程序转换为内核线程（可被调度和抢占）
- 将自旋锁（Spinlock）替换为可睡眠的互斥锁
- 实现优先级继承的 rt_mutex
- 高精度定时器（hrtimer）支持

### 安装与配置

```bash
# 下载并应用 PREEMPT_RT 补丁（以 6.1 内核为例）
wget https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/6.1/patch-6.1.38-rt13.patch.xz
xz -d patch-6.1.38-rt13.patch.xz

cd linux-6.1.38
patch -p1 < ../patch-6.1.38-rt13.patch

# 配置内核
make menuconfig
# General setup → Preemption Model → Fully Preemptible Kernel (Real-Time)
# 启用 CONFIG_PREEMPT_RT=y

make -j$(nproc)
sudo make modules_install install
```

### 实时应用编写

```c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>

void *realtime_control_loop(void *arg) {
    struct timespec next;
    clock_gettime(CLOCK_MONOTONIC, &next);

    while (1) {
        // 控制计算
        read_sensors();
        compute_control();
        write_actuators();

        // 等待到下一个周期
        next.tv_nsec += 1000000;  // 1 ms 周期
        if (next.tv_nsec >= 1000000000) {
            next.tv_nsec -= 1000000000;
            next.tv_sec++;
        }
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
    }
    return NULL;
}

int main(void) {
    // 锁定内存，防止页面换出导致延迟
    mlockall(MCL_CURRENT | MCL_FUTURE);

    pthread_t thread;
    pthread_attr_t attr;
    struct sched_param param;

    pthread_attr_init(&attr);
    pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
    param.sched_priority = 80;
    pthread_attr_setschedparam(&attr, &param);
    pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);

    pthread_create(&thread, &attr, realtime_control_loop, NULL);
    pthread_join(thread, NULL);

    return 0;
}
```


## 常见延迟问题与对策

| 问题 | 现象 | 原因 | 对策 |
|------|------|------|------|
| 缓存未命中 | 执行时间偶发性增大 | 任务切换导致缓存失效 | CPU 亲和性绑定，缓存预热 |
| 页面错误 | 偶发数百微秒延迟 | 内存页被换出到磁盘 | `mlockall()` 锁定内存 |
| 中断风暴 | 系统响应变慢 | 外设产生大量中断 | 中断合并、轮询模式 |
| 优先级反转 | 高优先级任务长时间阻塞 | 共享资源锁竞争 | 优先级继承/天花板协议 |
| SMI 中断 | 不可屏蔽的延迟尖峰 | BIOS 系统管理中断 | 禁用不必要的 SMI |
| 电源管理 | CPU 唤醒延迟 | C-state 深度休眠 | 禁用深度 C-state |
| USB 轮询 | 周期性延迟干扰 | USB 控制器 DMA 占用总线 | 使用独立 USB 控制器或改用串口 |


## 优化技术

### CPU 亲和性

将实时任务绑定到专用 CPU 核心，避免核心迁移和缓存失效：

```bash
# 将核心 2 和 3 从通用调度中隔离
# 编辑 GRUB 启动参数
GRUB_CMDLINE_LINUX="isolcpus=2,3 nohz_full=2,3 rcu_nocbs=2,3"

# 将实时进程绑定到核心 2
taskset -c 2 ./my_robot_controller

# 或在代码中设置
cpu_set_t cpuset;
CPU_ZERO(&cpuset);
CPU_SET(2, &cpuset);
pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
```

### 内存锁定

防止页面换出导致的延迟尖峰：

```c
#include <sys/mman.h>

// 锁定当前和未来所有内存页
mlockall(MCL_CURRENT | MCL_FUTURE);

// 预分配和预触碰堆栈
void prefault_stack(void) {
    unsigned char dummy[8192];
    memset(dummy, 0, sizeof(dummy));
}
```

### 禁用不必要的系统服务

```bash
# 禁用可能产生延迟干扰的服务
sudo systemctl disable irqbalance   # 中断负载均衡
sudo systemctl disable ondemand     # CPU 频率调节
sudo systemctl disable thermald     # 温度管理守护进程

# 设置 CPU 频率为固定最大值（禁用动态调频）
echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```


## 基准测试方法

系统化的延迟基准测试应包含以下步骤：

1. **基线测量**：空闲系统上运行 cyclictest 获取基准延迟
2. **压力测试**：使用 `stress-ng` 或实际负载并行运行，观察延迟变化
3. **长时间测试**：运行 24 小时以上，捕获罕见的延迟尖峰
4. **统计分析**：记录最小值、平均值、99 百分位、99.9 百分位和最大值

```bash
# 在压力负载下测量延迟
stress-ng --cpu 4 --io 2 --vm 2 --vm-bytes 256M &
sudo cyclictest -t1 -p 99 -n -i 1000 -l 1000000 -h 200 -q > cyclictest_output.txt

# 分析延迟分布
awk '/^#/{next} {print $0}' cyclictest_output.txt | \
  sort -n | awk '{a[NR]=$1} END {
    print "Min:", a[1];
    print "Median:", a[int(NR/2)];
    print "P99:", a[int(NR*0.99)];
    print "P99.9:", a[int(NR*0.999)];
    print "Max:", a[NR]
  }'
```


## 参考资料

1. Reghenzani, F., et al. (2019). The Real-Time Linux Kernel: A Survey on PREEMPT_RT. *ACM Computing Surveys*, 52(1), 1–36.
2. Rostedt, S. (2009). ftrace — Function Tracer. Linux 内核文档.
3. Desnoyers, M., & Dagenais, M. R. (2006). The LTTng Tracer: A Low Impact Performance and Behavior Analysis Tool for GNU/Linux. *Ottawa Linux Symposium*.
4. Percepio. Tracealyzer for FreeRTOS 用户手册.
5. Brown, J. H., & Martin, B. (2010). How Fast is Fast Enough? Choosing between Xenomai and Linux for Real-Time Applications. *Real-Time Linux Workshop*.
6. rt-tests 项目：https://git.kernel.org/pub/scm/utils/rt-tests/rt-tests.git
