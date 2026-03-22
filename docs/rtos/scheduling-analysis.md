# 调度分析

!!! note "引言"
    实时操作系统（Real-Time Operating System, RTOS）的核心职责是保证任务在截止时限（Deadline）之前完成执行。调度分析（Schedulability Analysis）是验证一组实时任务能否在给定硬件和调度策略下满足所有时间约束的数学方法。对于机器人控制系统，调度分析直接决定了控制回路的稳定性和安全性——一个错过截止时限的姿态控制任务可能导致机器人失稳甚至损坏。


## 实时任务模型

### 周期任务模型

经典的周期任务模型（Periodic Task Model）由 Liu 和 Layland 于 1973 年提出，每个任务 \(\tau_i\) 由三个参数描述：

- \(C_i\)：最坏情况执行时间（Worst-Case Execution Time, WCET）
- \(T_i\)：周期（Period），即两次连续释放之间的时间间隔
- \(D_i\)：相对截止时限（Relative Deadline）

当 \(D_i = T_i\) 时称为隐式截止时限（Implicit Deadline）任务，这是最常见的模型。

### 机器人控制中的典型任务集

| 任务 | 周期 | 典型 WCET | 说明 |
|------|------|----------|------|
| IMU 数据采集 | 1 ms | 0.05 ms | 最高频率，硬实时 |
| 电机伺服控制 | 1 ms | 0.2 ms | 电流/力矩环 |
| 姿态控制 | 5 ms | 1.0 ms | PID/LQR 控制器 |
| 路径跟踪 | 20 ms | 5.0 ms | 运动控制 |
| 传感器融合 | 10 ms | 3.0 ms | 卡尔曼滤波 |
| 通信任务 | 50 ms | 2.0 ms | CAN/以太网收发 |
| 状态监控 | 100 ms | 1.0 ms | 温度、电压检测 |

任务的利用率（Utilization）定义为：

$$
U_i = \frac{C_i}{T_i}
$$

系统总利用率为所有任务利用率之和：

$$
U = \sum_{i=1}^{n} \frac{C_i}{T_i}
$$


## 固定优先级调度

### 速率单调调度（Rate Monotonic Scheduling, RMS）

RMS 是最经典的固定优先级调度算法，其规则极其简单：**周期越短的任务优先级越高**。Liu 和 Layland 证明了 RMS 在所有固定优先级调度算法中是最优的——如果一组任务在任何固定优先级分配下可调度，则在 RMS 下也一定可调度。

**Liu-Layland 利用率上界**

对于 \(n\) 个隐式截止时限的周期任务，RMS 的充分可调度条件为：

$$
U = \sum_{i=1}^{n} \frac{C_i}{T_i} \leq n(2^{1/n} - 1)
$$

当 \(n \to \infty\) 时，上界收敛到 \(\ln 2 \approx 0.693\)。具体数值：

| 任务数 \(n\) | 利用率上界 |
|-------------|----------|
| 1 | 1.000 |
| 2 | 0.828 |
| 3 | 0.780 |
| 4 | 0.757 |
| 5 | 0.743 |
| 10 | 0.718 |
| ∞ | 0.693 |

注意这是**充分条件**而非必要条件：即使利用率超过上界，任务集仍可能可调度。

### 响应时间分析（Response Time Analysis, RTA）

RTA 提供了固定优先级调度的**充分必要条件**。任务 \(\tau_i\) 的最坏情况响应时间 \(R_i\) 通过以下迭代公式计算：

$$
R_i^{(k+1)} = C_i + \sum_{j \in hp(i)} \left\lceil \frac{R_i^{(k)}}{T_j} \right\rceil C_j
$$

其中 \(hp(i)\) 是比 \(\tau_i\) 优先级更高的所有任务的集合。迭代从 \(R_i^{(0)} = C_i\) 开始，直到收敛（\(R_i^{(k+1)} = R_i^{(k)}\)）或 \(R_i > D_i\)（不可调度）。

**Python 实现**：

```python
import math

def response_time_analysis(tasks):
    """
    tasks: [(C, T, D), ...] 按优先级从高到低排列
    返回每个任务的最坏响应时间，None 表示不可调度
    """
    n = len(tasks)
    response_times = []

    for i in range(n):
        C_i, T_i, D_i = tasks[i]
        R = C_i  # 初始值

        while True:
            R_new = C_i
            for j in range(i):  # 高优先级任务的干扰
                C_j, T_j, _ = tasks[j]
                R_new += math.ceil(R / T_j) * C_j

            if R_new == R:
                break  # 收敛
            if R_new > D_i:
                response_times.append(None)  # 不可调度
                break
            R = R_new
        else:
            response_times.append(R)

    return response_times

# 示例：三个控制任务
tasks = [
    (0.2, 1.0, 1.0),   # 电机伺服，周期 1ms
    (1.0, 5.0, 5.0),   # 姿态控制，周期 5ms
    (5.0, 20.0, 20.0),  # 路径跟踪，周期 20ms
]

results = response_time_analysis(tasks)
for i, (task, rt) in enumerate(zip(tasks, results)):
    C, T, D = task
    status = f"R={rt:.1f}ms" if rt else "不可调度"
    print(f"任务{i+1}: C={C}, T={T}, D={D} → {status}")
```


## 动态优先级调度

### 最早截止时限优先（Earliest Deadline First, EDF）

EDF 是最优的动态优先级调度算法：在每个调度决策点，选择绝对截止时限最近的就绪任务执行。

**EDF 的可调度性判定**极其简洁——对于隐式截止时限的周期任务：

$$
U = \sum_{i=1}^{n} \frac{C_i}{T_i} \leq 1
$$

即只要总利用率不超过 100%，EDF 就能保证所有任务满足截止时限。这比 RMS 的 69.3% 上界宽松得多。

### RMS 与 EDF 的对比

| 特性 | RMS | EDF |
|------|-----|-----|
| 优先级类型 | 静态（编译时确定） | 动态（运行时变化） |
| 利用率上界 | \(n(2^{1/n}-1) \approx 0.69\) | 1.0 |
| 实现复杂度 | 低 | 中等 |
| 过载行为 | 可预测（低优先级任务先失败） | 不可预测（多米诺效应） |
| RTOS 支持 | FreeRTOS, VxWorks, QNX | 较少原生支持 |
| 适用场景 | 工业控制、安全关键系统 | 多媒体、高利用率系统 |


## 优先级反转

### 问题描述

优先级反转（Priority Inversion）是实时系统中一个经典的调度异常：高优先级任务被低优先级任务间接阻塞。最著名的案例是 1997 年火星探路者号（Mars Pathfinder）的系统重启事件。

典型场景：任务 H（高优先级）、M（中优先级）、L（低优先级）共享一个互斥锁。

1. L 获取锁并开始执行临界区
2. H 被释放，抢占 L，尝试获取锁但被阻塞
3. M 被释放，抢占 L（因为 M 优先级高于 L）
4. M 执行完毕后 L 才能继续，释放锁后 H 才能运行

结果：H 被 M 间接阻塞，且阻塞时间不可预测。

### 优先级继承协议（Priority Inheritance Protocol, PIP）

当低优先级任务持有高优先级任务所需的锁时，低优先级任务**临时继承**高优先级任务的优先级，直到释放锁。

FreeRTOS 中使用优先级继承互斥锁：

```c
#include "FreeRTOS.h"
#include "semphr.h"

SemaphoreHandle_t xMutex;

void vHighPriorityTask(void *pvParameters) {
    for (;;) {
        // 获取互斥锁（自动触发优先级继承）
        if (xSemaphoreTake(xMutex, portMAX_DELAY) == pdTRUE) {
            // 访问共享资源
            update_motor_command();
            xSemaphoreGive(xMutex);
        }
        vTaskDelay(pdMS_TO_TICKS(1));
    }
}

void vLowPriorityTask(void *pvParameters) {
    for (;;) {
        if (xSemaphoreTake(xMutex, portMAX_DELAY) == pdTRUE) {
            // 访问共享资源
            read_sensor_data();
            xSemaphoreGive(xMutex);
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void setup_tasks(void) {
    // 创建支持优先级继承的互斥锁
    xMutex = xSemaphoreCreateMutex();

    xTaskCreate(vHighPriorityTask, "High", 256, NULL, 3, NULL);
    xTaskCreate(vLowPriorityTask, "Low", 256, NULL, 1, NULL);
}
```

### 优先级天花板协议（Priority Ceiling Protocol, PCP）

PCP 为每个互斥锁分配一个天花板优先级（等于可能使用该锁的最高优先级任务的优先级）。任务获取锁时立即提升到天花板优先级。PCP 的优势在于：

- 完全消除死锁
- 阻塞时间有严格上界：每个任务最多被阻塞一次


## 最坏情况执行时间分析

### WCET 分析方法

WCET 分析分为静态分析和测量方法：

| 方法 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| 静态分析 | 分析程序控制流和硬件时序模型 | 提供安全上界 | 工具复杂，可能过于保守 |
| 测量法 | 运行程序并记录最大执行时间 | 简单直接 | 无法保证覆盖最坏情况 |
| 混合法 | 静态分析 + 测量校准 | 平衡安全性和精确度 | 需要硬件知识 |

### 实践建议

对于机器人控制系统中的 WCET 估算：

1. **测量法**：在目标硬件上反复运行任务，记录最大执行时间，乘以安全系数（通常 1.2–1.5）
2. **避免不确定性来源**：禁用缓存随机替换、避免动态内存分配、最小化分支预测依赖
3. **隔离干扰**：在测量期间禁用中断或使用独立的 CPU 核心


## 机器人控制任务设计示例

以四足机器人为例，设计一个多速率控制任务集：

```c
// FreeRTOS 多速率控制任务示例

// 任务1：关节电流环 (1kHz, 最高优先级)
void vCurrentLoopTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    for (;;) {
        read_current_sensors();
        compute_current_pid();
        set_pwm_output();
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(1));
    }
}

// 任务2：姿态控制环 (200Hz)
void vAttitudeTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    for (;;) {
        read_imu();
        compute_attitude_controller();  // LQR 或 MPC
        set_joint_torque_commands();
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(5));
    }
}

// 任务3：步态规划 (50Hz)
void vGaitPlannerTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    for (;;) {
        update_foot_trajectory();
        compute_inverse_kinematics();
        send_to_attitude_controller();
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(20));
    }
}

// 任务4：状态估计与通信 (10Hz)
void vTelemetryTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    for (;;) {
        send_telemetry_data();
        check_battery_voltage();
        update_state_machine();
        vTaskDelayUntil(&xLastWakeTime, pdMS_TO_TICKS(100));
    }
}

void create_control_tasks(void) {
    // 按 RMS 原则：周期越短优先级越高
    xTaskCreate(vCurrentLoopTask, "Current", 512, NULL, 4, NULL);
    xTaskCreate(vAttitudeTask,    "Attitude", 1024, NULL, 3, NULL);
    xTaskCreate(vGaitPlannerTask, "Gait",     2048, NULL, 2, NULL);
    xTaskCreate(vTelemetryTask,   "Telemetry", 512, NULL, 1, NULL);
}
```


## 参考资料

1. Liu, C. L., & Layland, J. W. (1973). Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment. *Journal of the ACM*, 20(1), 46–61.
2. Audsley, N. C., et al. (1993). Applying New Scheduling Theory to Static Priority Pre-emptive Scheduling. *Software Engineering Journal*, 8(5), 284–292.
3. Sha, L., Rajkumar, R., & Lehoczky, J. P. (1990). Priority Inheritance Protocols: An Approach to Real-Time Synchronization. *IEEE Transactions on Computers*, 39(9), 1175–1185.
4. Burns, A., & Wellings, A. J. (2009). *Real-Time Systems and Programming Languages* (4th ed.). Addison-Wesley.
5. Buttazzo, G. C. (2011). *Hard Real-Time Computing Systems: Predictable Scheduling Algorithms and Applications* (3rd ed.). Springer.
6. Jones, M. B. (1997). What Really Happened on Mars? — Mars Pathfinder Priority Inversion Incident.
