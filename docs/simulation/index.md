# <机器人仿真工具>
机器人系统设计离不开仿真工具的支持。机器人仿真让我们在没有物理硬件的情况下也可以快速对算法进行验证；或者提高安全性，避免实验损伤我们的设备（比如在增强学习中，就需要大量random的exploration）。这篇文章我想介绍一下当前主流的可视化仿真工具。一般来说这些仿真工具在物理引擎之上进行包装，如基于ODE、 Bullet等。有些情况下我们只需要使用物理引擎就可以满足需要，但一般情况下我们也想通过可视化平台观察机器人运行的正确性。仿真一般只在系统前期使用，因为真实物理平台与仿真环境存在差异，后期还是要转换到实际硬件平台上进行调试。当然目前也有sim-to-real的研究可以加速移植的过程，甚至可以直接将仿真结果用于实际机器人平台。

这些机器人仿真工具有：

- Gazebo
- V-Rep
- MuJoCo
- PyBullet
- Webots
- MATLAB Robotics Toolbox
- Stage

---
 
**参考资料：**

1. 胡春旭, [ROS探索总结（五十八）—— Gazebo物理仿真平台]( https://www.guyuehome.com/2256), 古月居
2. 胡春旭, [ROS史话36篇 | 25. ROS之皆大欢喜（Player与Stage）](https://zhuanlan.zhihu.com/p/74552944), 知乎
3. 任赜宇, [为什么要机器人仿真 ](https://www.zhihu.com/question/356929288/answer/913298986), 知乎
4. OpenAI, [OpenAI Gym Documentation](https://gym.openai.com/docs/)
5. 幻生如梦, [PyBullet快速上手教程](https://blog.csdn.net/yingyue20141003/article/details/89044438), CSDN
6. 戴晓天，[机器人常用可视化仿真工具 - 云飞机器人实验室](https://www.yfworld.com/?p=5453)
