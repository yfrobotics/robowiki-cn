# PID控制器

## 公式 (Formula)

$$ u(t) = K_p e(t) + K_i \int^t_0 e(\tau) d\tau + K_d \frac{de(t)}{dt} $$

拉普拉斯变换为：
$$ L(s) = U(s)/E(s) = K_p + \frac{K_i}{s} + K_d s $$


## 离散化 (Discretization)
控制系统在连续时间域中设计，但运行控制算法的计算机需要数字实现。离散化是将系统从连续时间转换为离散时间。典型方法包括：

- 前向差分 (Forward difference)：通常用于积分部分
- 后向差分 (Backward difference)：对于微分部分，通常选择后向差分以获得稳定的微分（结果离散参数通常是位置，因此没有振铃效应）
- 双线性变换 (Tustin approximation)


---

## 实现 (Implementation)
C 代码：

```c
  float k_p = 0;
  float k_i = 0;
  float k_d = 0;
  float e_i = 0;  /* integrated error */
  float e_p = 0;  /* previous error */

  void pid_init(float kp_, float ki_, float kd_) {
  	k_p = kp_;
  	k_i = ki_;
  	k_d = kd_;
  	e_i = 0;
  	e_p = 0;
  }

  void pid_controller() {
    float y = adc_input();
    float e = r - y;
    e_i += e * dt;

    float u = k_p * e + k_i * e_i + k_d * (e - e_p) / dt;

    dac_output(u);
    e_p = e;
    sleep(dt);
  }
```


---

## 参数调节 (Parameter Tuning)

PID需要良好的控制器参数（\(k_p, k_i, k_d\)）才可以正常工作。

目前PID调参的方法有：

- Ziegler-Nichols 调参法 (Ziegler-Nichols Tuning)
- 反应曲线调参法 (Reaction Curve Tuning)


---

## 改善 (Improvements)

根据 [1]，可以对所谓的"初学者 PID"进行一些改进。作者 [1] 为 Arduino 编写了 PID 库。以下是他建议的改进列表：

1. 采样时间 (Sample Time) - 如果 PID 算法在固定间隔内评估，其功能最佳。如果算法知道这个间隔，我们也可以简化一些内部数学计算。
2. 微分冲击 (Derivative Kick) - 虽然不是最大的问题，但很容易消除，所以我们要解决它。
3. 在线调参更改 (On-The-Fly Tuning Changes) - 一个好的 PID 算法应该能够在不断开内部工作的情况下更改调参参数。
4. 积分饱和抑制 (Reset Windup Mitigation) - 我们将介绍什么是积分饱和，并实现一个具有额外好处的解决方案。
5. 开关控制 (On/Off Auto/Manual) - 在大多数应用中，有时需要关闭 PID 控制器并手动调整输出，而不受控制器干扰。
6. 初始化 (Initialization) - 当控制器首次启动时，我们希望实现"无冲击切换"。也就是说，我们不希望输出突然跳转到某个新值。
7. 控制器方向 (Controller Direction) - 最后一个改进本身不是为了鲁棒性，而是为了确保用户输入具有正确符号的调参参数。

在本节中，我将遵循他的建议并重写我的代码版本来说明主要思想。

### 固定采样时间 (Fixed Sampling Time)
首先要确保的是控制器在固定的时间间隔内被调用。我们可以创建一个周期性控制任务，利用 ADC 采样中断，或者我们可以使用操作系统工具来测试指定的采样时间是否已过。使用固定采样时间，我们不需要每次都计算与 $dt$ 相关的数学，并且可以将 $dt$ 合并到系数 $K_i$ 和 $K_d$ 中：

```c
/* ... */

void pid_init(float kp_, float ki_, float kd_, float dt){
  k_p = kp_;
  k_i = ki_ * dt;
  k_d = kd_ / dt;
  /* ... */
}

void pid_controller() {
  /* ... */
  e_i += e;
  float u = k_p * e + k_i * e_i + k_d * (e - e_p);
  /* ... */
}
```

### 微分冲击 (Derivative Kick)
由于误差 = 设定值 - 输入，设定值的任何变化都会导致误差的瞬时变化，特别是对于微分项，因为这种变化会导致接近无穷大的数值。当这个数字被输入到 PID 方程中时，结果将导致输出中出现不期望的尖峰。

![](assets/markdown-img-paste-20170412223043418.png)

由于 $\dot{e} = \dot{r} - \dot{y}$，我们可以将设定点视为常数，所以 $\frac{de}{dt} = -\frac{dy}{dt}$。这导致了"基于测量的微分"方法。

```c
/* ... */
float y_p = 0;

void pid_controller() {
  /* ... */
  e_i += e;
  float u = k_p * e + k_i * e_i + k_d * (y - y_p);
  /* ... */
  y_p = y;
}
```

### 调参更改 (Tuning Changes)
在系统运行时更改 PID 参数可能会导致不期望的行为。

![](assets/markdown-img-paste-20170412223856166.png)

主要变化来自"I"项。解决方案是每次都乘以 k_i，而不是在整个总和上乘以它。这导致了一个平滑的解决方案，无需额外的计算。

```c
/* ... */
float ITerm = 0;

void pid_controller() {
  /* ... */
  ITerm += k_i * e;
  float u = k_p * e + ITerm + k_d * (y - y_p);
  /* ... */
}
```

### 积分饱和 (Reset Windup)
积分饱和问题来自于 PID 控制器可以发送的输出存在限制。例如，对于 Arduino，PWM 输出只能接受 0-255 的值。如果输出值达到此范围，控制器应停止增加其输出并停止累积积分误差。如果控制器不知道其输出不是实际输出，输出将饱和，并在设定点再次下降时引入滞后。

![](assets/markdown-img-paste-20170412224103491.png)

此步骤后的 C 代码：

```c
/* ... */
float u_limit_upp = xxx;
float u_limit_low = xxx;

void pid_controller() {
  /* ... */
  if (pid_output_saturated(u)) {
    pid_output_reset(u);
    /* roll back the I term */
    ITerm -= k_i * e;
  }
  /* ... */
}

int pid_output_saturated(float u) {
  if (u > u_limit_upp || u < u_limit_low) {
    return 1;
  }
  else {
    return 0;
  }
}

int pid_output_reset(float u) {
  if (u > u_limit_upp) {
    u = u_limit_upp;
  } else if (u < u_limit_low) {
    u = u_limit_low;
  }
}
```

### 开关控制 (Switch On/off)
（在非常罕见的情况下），我们可能想要打开/关闭 PID 控制器并手动向过程提供控制输入。此操作可能会使控制器混淆，因为它完全失去了对输出的控制。

![](assets/markdown-img-paste-20170412231026842.png)

解决方案很简单，添加一个开关控制变量来启用/禁用控制器并停止更改其内部状态变量。

```c
/* ... */
int pid_switch_on = 1;

void pid_controller() {
  if (pid_switch_on == 0) {
    return;
  }
  /* ... */
}

void pid_switch(int new_state) {
  pid_switch_on = new_state;
}
```

### 切换后的初始化 (Initialization after Switch)
使用开关控制的副作用是，当控制器从关闭切换到打开时，会出现不期望的冲击。这在以下图中说明：

![](assets/markdown-img-paste-20170413001022770.png)

为了使控制器重新打开后输出平滑，我们可以重置控制器内部变量：

- "P"：比例项不依赖于任何过去的信息，因此不需要任何初始化，所以 P = 0。
- "D"：设置 last_input = previous_input，所以 D = 0。
- "I"：设置 ITerm = previous_output，所以 P + I + D = previous_output。

结果控制器在重新打开控制器后具有平滑的响应：

![](assets/markdown-img-paste-20170413021327538.png)

### 反向控制 (Reverse Control)
对于某些系统，输入的增加会导致输出的减少。例如，冷却风扇速度的增加会导致温度下降。为了处理这些系统，我们引入一个方向变量来解决直接/反向控制之间的差异。反向控制的唯一区别是 PID 参数的符号需要为负，而不是直接情况下的正。

```c
#define DIRECT_CONTROL  (0)
#define REVERSE_CONTROL (1)
int direction = DIRECT_CONTROL;

void pid_init() {
  /* ... */
  if (direction == REVERSE_CONTROL) {
    k_p = 0 - k_p;
    k_i = 0 - k_i;
    k_d = 0 - k_d;
  }
  /* ... */
}

void pid_setdir(int d_) {
  direction = d_;
}
```

---

## 其他改进 (Other Improvements)
### 输入滤波 (Input Filtering)
为了避免微分部分中高频测量噪声的问题，添加了低通滤波器。

$$U_D(s) = \frac{K T_D s}{1 + s T_D / N}(\gamma Y_{sp}(s) - Y(s))$$

$\gamma$ 用于设定点加权，可以解释为来自设定点的前馈。

### 时序补偿 (Timing Compensation)
- I 和 D 部分依赖于两次控制操作之间的实际间隔。如果间隔不一致，我们需要对它们进行补偿。

### 前馈 (Feedforward)

### 复位反馈 (Reset Tiebacks)

### **I** 项饱和 (**I**-term Saturation)

### **D** 项滤波 (**D**-term Filtering)

### 误差死区 (Error Dead-zone)

### 输出限制 (Output Limitation)

### 死区 (Dead band)

### 抗积分饱和 (Anti Windup)

---

## 基于事件的 PID [2] (Event-based PID)
事件检测器（事件触发）-> PID 控制器（时间触发）

事件触发条件应该具有较小的复杂度，以便与时间触发控制器进行比较：

$|e(t_k) - e(t_{s}) > e_{lim}|$ 或 $h_{act} > h_{max}$

这意味着检测器以标称采样频率运行，但 PID 计算仅在检测到事件时执行。然而，由于每次都需要重新计算 PID 系数，该算法需要更多计算。

正确过滤测量噪声并设置足够大的误差限制以避免因噪声触发控制是很重要的。

---

## 参考文献 (References)
1. Improving the Beginner's PID, [网页链接](http://brettbeauregard.com/blog/2011/04/improving-the-beginners-pid-introduction/)
2. Årzén, K-E. (1999), A Simple Event-Based PID Controller, 在 14th IFAC World Congress (1999), 北京, 中国 上发表的论文。
