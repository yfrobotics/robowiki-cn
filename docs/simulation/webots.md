# Webots
![5e430036ce538f09f700003a](assets/300c0e2b9bed4adc8d0b1fa6c047766c.png)

- 官方网站：https://cyberbotics.com/
- GitHub：https://github.com/cyberbotics/webots
- 物理引擎：基于ODE改进
- 许可：Apache 2.0 开源

!!! note "引言"
    Webots是一款功能完善的开源机器人仿真平台，最初由瑞士洛桑联邦理工学院 (EPFL, Ecole Polytechnique Federale de Lausanne) 开发，后由Cyberbotics公司进行商业化运营。2018年，Webots从商业许可转换为Apache 2.0开源模式，此后在机器人教育和研究领域获得了越来越广泛的关注。

## 发展历程

- **1996年**：Webots由EPFL的Olivier Michel在其博士研究期间首次开发，最初用于进化机器人学 (Evolutionary Robotics) 的研究
- **1998年**：Cyberbotics公司成立，开始Webots的商业化运营
- **2018年12月**：Webots R2019a版本正式以Apache 2.0许可证开源，所有功能免费提供
- **后续发展**：开源后社区贡献活跃，持续增加新的机器人模型和功能

## 核心特性

Webots提供了一个完整的机器人开发环境，核心特性包括：

- **集成开发环境 (IDE)**：内置代码编辑器、场景树 (Scene Tree) 编辑器和三维视图
- **物理仿真**：基于ODE (Open Dynamics Engine) 的改进版物理引擎，支持刚体动力学、碰撞检测和摩擦模型
- **高质量渲染**：使用WREN渲染引擎，支持阴影 (Shadow)、反射 (Reflection) 和纹理映射 (Texture Mapping)
- **流体力学**：支持水中机器人的浮力 (Buoyancy) 和阻力 (Drag) 仿真
- **天气效果**：可以模拟雾、雨等天气条件对传感器的影响

## 内置机器人模型

Webots提供了大量预置的机器人模型，涵盖多个领域：

- **移动机器人**：e-puck、Pioneer 3-DX、TIAGo、Thymio II
- **工业机械臂**：Universal Robots (UR3/UR5/UR10)、KUKA youBot、ABB IRB系列
- **人形机器人**：NAO、Darwin-OP、Robotis OP2
- **无人机**：Mavic 2 Pro、Crazyflie
- **自动驾驶车辆**：Tesla Model 3、BMW X5、Lincoln MKZ等车辆模型
- **其他**：Boston Dynamics Spot、Softbank Pepper

## 编程语言支持

Webots的控制器 (Controller) 程序支持多种编程语言：

- **C/C++**：提供原生API，性能最优
- **Python**：使用广泛，适合快速原型开发
- **Java**：面向对象的API设计
- **MATLAB**：适合控制算法的研究和验证
- **ROS/ROS 2**：通过 `webots_ros2` 包实现与ROS 2的深度集成

## 控制器编程 (Controller Programming)

Webots中每个机器人运行独立的控制器进程。控制器程序通过Webots API与仿真环境交互，读取传感器数据、发送执行器指令。以Python控制器为例：

```python
from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())

# 获取传感器和电机
ds_left = robot.getDevice('ds_left')
ds_left.enable(timestep)
motor_left = robot.getDevice('motor_left')

while robot.step(timestep) != -1:
    distance = ds_left.getValue()
    if distance < 100:
        motor_left.setVelocity(0.0)
    else:
        motor_left.setVelocity(5.0)
```

这种架构使得控制器代码与仿真引擎解耦 (Decoupled)，便于将仿真中验证的算法迁移到真实硬件上。

## 与ROS 2的集成

Webots通过 `webots_ros2` 功能包提供了与ROS 2的原生集成，支持：

- 将Webots传感器数据发布为ROS 2话题 (Topic)
- 通过ROS 2服务 (Service) 控制仿真的运行状态
- 使用标准ROS 2工具 (如RViz2、Nav2) 与Webots仿真环境交互
- 支持自定义ROS 2插件扩展接口功能

## 教育与竞赛应用

Webots在机器人教育领域具有显著优势：

- 内置丰富的教程 (Tutorial) 和示例项目
- 界面友好，学习曲线平缓，适合初学者入门
- 支持RoboCup仿真赛事，多次作为官方仿真平台
- 跨平台支持 (Windows、Linux、macOS)，便于教学部署
- 提供在线仿真版本 (Webots Cloud)，无需本地安装即可运行

## 优势与局限

**优势：**

- 完全开源免费，社区活跃
- 自带大量机器人模型和传感器，开箱即用
- 集成开发环境易用性强
- 与ROS 2集成良好

**局限：**

- 物理引擎精度在某些极端场景下不如MuJoCo
- 渲染质量与游戏引擎相比仍有差距
- 社区规模和生态资源不及Gazebo

## 参考资料

- [Webots官方文档](https://cyberbotics.com/doc/guide/index)
- [Webots GitHub仓库](https://github.com/cyberbotics/webots)
- [webots_ros2文档](https://github.com/cyberbotics/webots_ros2)
- Michel, O. (2004). Webots: Professional mobile robot simulation. *International Journal of Advanced Robotic Systems*, 1(1), 39-42.
