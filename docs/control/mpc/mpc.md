# MPC控制器

![](assets/markdown-img-paste-20170413120952608.png)

## 概述 (Generals)
- MPC：使用过程变量对操纵变量变化的响应的显式动态模型进行调节控制。
- \(obj = min(\sum (y - y_{trajectory})^2)\)
- 基本版本使用线性模型。也可以是经验模型。
- 相对于 PID 的优点：
    - 长时间常数、显著的时间延迟、反向响应等
    - 多变量
    - 对过程变量有约束

- 一般特征：
    - 目标（设定点）由实时优化软件根据当前运行和经济条件选择
    - 最小化预测未来输出与特定参考轨迹到新目标之间的偏差平方
    - 处理 MIMO 控制问题
    - 可以包括对受控变量和操纵变量的等式和不等式约束
    - 在每个采样时刻求解非线性规划问题
    - 通过比较实际受控变量与模型预测来估计扰动
    - 通常实现 \(M\) 个计算移动中的第一个移动

- MPC 目标轨迹
![](assets/markdown-img-paste-20170413121028412.png)
    - 类型：
        - 漏斗轨迹 (Funnel Trajectory)
        - 纯死区 (Pure dead-band)
        - 参考轨迹 (Reference Trajectory)
    - 近期与长期目标
    - 响应目标
    - 响应速度

- 二次目标函数
  $$\sum_{i=0}^p x_i^TQx_i + \sum_{i=0}^{m-1} u_i^TRu_i$$


![](assets/markdown-img-paste-20170413121003374.png)

## 详细内容 (Details)
- 脉冲和阶跃响应模型以及预测方程
- 状态估计的使用
- 优化
- 无限时域 MPC 和稳定性
- 非线性模型的使用

![](assets/markdown-img-paste-20170413124746649.png)
