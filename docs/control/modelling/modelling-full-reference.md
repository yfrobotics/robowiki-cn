# 建模参考资料

!!! note "引言"
    本页面汇集控制系统建模相关的教材、在线课程、软件工具、常用公式及最佳实践，为机器人系统建模提供快速参考。


## 推荐教材

| 教材 | 作者 | 特点 | 适用层次 |
|------|------|------|---------|
| *Modern Control Engineering* | Ogata, K. | 经典教材，理论与实例并重 | 本科 |
| *Control Systems Engineering* | Nise, N. S. | MATLAB 集成度高，实例丰富 | 本科 |
| *Feedback Control of Dynamic Systems* | Franklin, G. F. et al. | 工程导向，数字控制章节出色 | 本科/研究生 |
| *System Dynamics* | Palm, W. J. | 多域建模（电气、机械、流体、热） | 本科 |
| *System Identification: Theory for the User* | Ljung, L. | 系统辨识权威著作 | 研究生 |
| *Modeling, Identification and Control of Robots* | Khalil, W. & Dombre, E. | 机器人建模专著 | 研究生 |
| 《自动控制原理》 | 胡寿松 | 国内经典中文教材 | 本科 |


## 在线课程

| 课程名称 | 平台/机构 | 内容特色 |
|---------|----------|---------|
| Control of Mobile Robots | Coursera / Georgia Tech | 移动机器人建模与控制 |
| Control Bootcamp | YouTube / Steve Brunton | 直观讲解 + MATLAB 演示 |
| Underactuated Robotics | MIT OCW / Russ Tedrake | 欠驱动系统建模与非线性控制 |
| Linear Systems Theory | edX / 清华大学 | 状态空间方法 |
| System Identification | YouTube / Magnus Nilsson | 实用辨识方法 |


## 软件工具对比

| 工具 | 语言 | 优势 | 局限性 | 许可 |
|------|------|------|--------|------|
| MATLAB/Simulink | MATLAB | 工业标准，System Identification Toolbox 功能完整 | 商业授权费用高 | 商业 |
| python-control | Python | 与 MATLAB Control Toolbox 接口相似，免费 | 功能不如 MATLAB 完整 | BSD |
| SciPy (signal) | Python | 信号处理和基础系统分析 | 无专用控制设计工具 | BSD |
| Modelica/OpenModelica | Modelica | 多域物理建模，组件化 | 学习曲线较陡 | 开源 |
| Simscape (MATLAB) | MATLAB | 可视化多域物理建模 | 依赖 MATLAB 生态 | 商业 |
| Drake | C++/Python | 机器人动力学建模与优化控制 | 文档相对较少 | BSD |
| CasADi | C++/Python/MATLAB | 符号计算 + 自动微分 + 非线性优化 | 偏向优化，非通用控制 | LGPL |


## 建模最佳实践

### 建模流程清单

1. **明确建模目的**：控制器设计、仿真验证还是系统分析？目的决定模型精度要求
2. **确定系统边界**：明确输入（执行器）、输出（传感器）和外部扰动
3. **选择建模方法**：第一性原理建模 vs 数据驱动辨识 vs 混合方法
4. **建立物理方程**：应用牛顿定律、基尔霍夫定律等基本物理定律
5. **合理简化**：忽略对控制目标影响小的动态（如电机电感、高阶振动模态）
6. **选择表示形式**：传递函数（SISO）or 状态空间（MIMO），连续 or 离散
7. **参数确定**：从数据手册、物理测量或系统辨识获取参数
8. **模型验证**：与实验数据对比阶跃响应、频率响应
9. **迭代改进**：根据验证结果增减模型复杂度

### 常见错误

| 错误 | 后果 | 建议 |
|------|------|------|
| 忽略执行器动态 | 控制器在实际系统上性能远不如仿真 | 至少建模一阶延迟 |
| 忽略传感器噪声 | 控制器对噪声过于敏感 | 在仿真中添加实际噪声水平 |
| 采样率选择不当 | 离散化误差导致控制性能下降 | 采样率 ≥ 10× 闭环带宽 |
| 过度简化非线性 | 线性模型在工作范围边缘失效 | 验证线性化有效范围 |
| 单位不一致 | 参数值错误数个量级 | 全程使用国际单位制（SI） |
| 忽略时延 | 相位裕度不足导致不稳定 | 建模通信和计算延迟 |


## 标准系统快速参考

### 直流电机

$$
G(s) = \frac{\Omega(s)}{V(s)} = \frac{K_t}{(Ls + R)(Js + b) + K_t K_e}
$$

参数：\(R\)（电阻）、\(L\)（电感）、\(J\)（转动惯量）、\(b\)（粘滞摩擦）、\(K_t\)（力矩常数）、\(K_e\)（反电动势常数）。

### 倒立摆

状态向量 \(\mathbf{x} = [x, \dot{x}, \theta, \dot{\theta}]^T\)，上平衡点 \(\theta = 0\) 处线性化：

$$
A = \begin{bmatrix} 0 & 1 & 0 & 0 \\ 0 & 0 & -mg/M & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & (M+m)g/(Ml) & 0 \end{bmatrix}
$$

参数：\(M\)（小车质量）、\(m\)（摆杆质量）、\(l\)（摆杆半长）、\(g\)（重力加速度）。

### 四旋翼无人机（悬停点线性化）

姿态动力学（小角度近似）：

$$
\ddot{\phi} = \frac{l}{I_{xx}} U_2, \quad \ddot{\theta} = \frac{l}{I_{yy}} U_3, \quad \ddot{\psi} = \frac{1}{I_{zz}} U_4
$$

高度动力学：

$$
\ddot{z} = -g + \frac{U_1}{m}
$$

参数：\(I_{xx}, I_{yy}, I_{zz}\)（转动惯量）、\(l\)（臂长）、\(m\)（总质量）。

### 机械臂单关节

$$
J\ddot{q} + b\dot{q} + mgl\sin(q) = \tau
$$

线性化后（\(q_0 = 0\)）：

$$
G(s) = \frac{Q(s)}{\tau(s)} = \frac{1}{Js^2 + bs + mgl}
$$

参数：\(J\)（等效转动惯量）、\(b\)（粘滞摩擦）、\(m\)（连杆质量）、\(l\)（质心到关节距离）。


## 参考资料

1. Ogata, K. (2010). *Modern Control Engineering* (5th ed.). Prentice Hall.
2. Ljung, L. (1999). *System Identification: Theory for the User* (2nd ed.). Prentice Hall.
3. Brunton, S. L., & Kutz, J. N. (2019). *Data-Driven Science and Engineering*. Cambridge University Press.
4. python-control 库：https://python-control.readthedocs.io/
5. OpenModelica 项目：https://openmodelica.org/
6. Drake 项目：https://drake.mit.edu/
