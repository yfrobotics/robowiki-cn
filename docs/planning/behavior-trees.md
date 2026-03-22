# 行为树

!!! note "引言"
    行为树（Behavior Tree, BT）是一种用于描述智能体决策逻辑的树状结构，最早源于游戏 AI 领域，现已广泛应用于机器人任务编排。与有限状态机（Finite State Machine, FSM）相比，行为树具有更好的模块化特性和可扩展性，是 ROS 2 Navigation2 等主流框架的默认任务调度机制。


## 行为树基本概念

行为树由若干**节点**组成，每个节点在被"tick"（时钟驱动）时返回三种状态之一：

- **Success（成功）**：节点任务完成
- **Failure（失败）**：节点任务无法完成
- **Running（运行中）**：节点任务正在执行，尚未结束

根节点以固定频率向下发送 tick 信号，驱动整棵树的执行。这种统一的返回值协议使得节点之间可以自由组合。


## 节点类型

### 控制节点

控制节点决定子节点的执行顺序和逻辑：

| 节点类型 | 英文名 | 行为描述 |
|---------|--------|---------|
| 顺序节点 | Sequence | 依次执行子节点，任一失败则返回 Failure |
| 选择节点 | Fallback / Selector | 依次执行子节点，任一成功则返回 Success |
| 并行节点 | Parallel | 同时执行所有子节点，根据成功阈值返回结果 |

**顺序节点（Sequence）**类似逻辑与（AND），所有子节点都成功才算成功。

**选择节点（Fallback）**类似逻辑或（OR），只要有一个子节点成功就算成功，常用于实现"尝试方案 A，失败则尝试方案 B"的逻辑。

**并行节点（Parallel）**同时 tick 所有子节点，可设定成功阈值 \(M\)，当至少 \(M\) 个子节点成功时返回 Success。


### 装饰节点

装饰节点（Decorator）只有一个子节点，用于修改子节点的行为：

- **Inverter**：取反子节点的返回值
- **Repeat**：重复执行子节点 \(N\) 次
- **Retry**：失败时重试，最多 \(N\) 次
- **Timeout**：限制子节点执行时间
- **ForceSuccess / ForceFailure**：强制返回成功或失败


### 叶节点

叶节点是行为树的末端，分为两类：

- **动作节点（Action）**：执行具体操作，如移动到目标点、抓取物体
- **条件节点（Condition）**：检查某个条件是否满足，如电量是否充足、是否检测到障碍物


## 黑板机制

黑板（Blackboard）是行为树节点之间共享数据的全局键值存储。节点通过端口（Port）读写黑板中的数据，实现解耦通信。

```
[导航节点] --写入"目标位置"--> [黑板] --读取"目标位置"--> [路径规划节点]
```

黑板的优点在于节点之间不需要直接引用，任何节点都可以独立测试和替换。


## 行为树与有限状态机对比

| 特性 | 行为树（BT） | 有限状态机（FSM） |
|------|-------------|-----------------|
| 结构 | 树状，层次化 | 图状，状态+转移 |
| 模块化 | 高，子树可复用 | 低，状态转移耦合紧密 |
| 可扩展性 | 添加子树即可扩展 | 新增状态需处理大量转移 |
| 反应性 | 天然支持中断和恢复 | 需要额外机制 |
| 调试 | 可视化直观 | 状态爆炸时难以追踪 |
| 适用场景 | 复杂任务编排 | 简单状态切换 |

当状态数量超过 10 个时，FSM 的状态转移矩阵会迅速膨胀，此时行为树是更好的选择。


## 主流行为树库

### BehaviorTree.CPP

BehaviorTree.CPP 是 C++ 实现的高性能行为树库，也是 ROS 2 Nav2 的默认引擎。支持 XML 定义行为树：

```xml
<root main_tree_to_execute="MainTree">
  <BehaviorTree ID="MainTree">
    <Sequence>
      <Condition ID="BatteryOK"/>
      <Action ID="MoveToGoal" goal="{target_pose}"/>
      <Action ID="PickObject"/>
    </Sequence>
  </BehaviorTree>
</root>
```

C++ 中注册自定义节点：

```cpp
#include "behaviortree_cpp/bt_factory.h"

class MoveToGoal : public BT::SyncActionNode {
public:
    MoveToGoal(const std::string& name, const BT::NodeConfig& config)
        : BT::SyncActionNode(name, config) {}

    static BT::PortsList providedPorts() {
        return {BT::InputPort<geometry_msgs::msg::PoseStamped>("goal")};
    }

    BT::NodeStatus tick() override {
        // 执行导航逻辑
        auto goal = getInput<geometry_msgs::msg::PoseStamped>("goal");
        if (!goal) return BT::NodeStatus::FAILURE;
        // ... 发送导航目标
        return BT::NodeStatus::SUCCESS;
    }
};

// 注册节点
BT::BehaviorTreeFactory factory;
factory.registerNodeType<MoveToGoal>("MoveToGoal");
auto tree = factory.createTreeFromFile("my_tree.xml");
tree.tickWhileRunning();
```


### py_trees

py_trees 是 Python 行为树库，适合快速原型开发：

```python
import py_trees

# 创建行为节点
check_battery = py_trees.behaviours.CheckBlackboardVariableValue(
    name="电量检查",
    check=py_trees.common.ComparisonExpression(
        variable="battery_level",
        value=20,
        operator=operator.gt
    )
)

move_to_goal = py_trees.behaviours.Running(name="移动到目标")

# 组装行为树
root = py_trees.composites.Sequence("巡逻任务", memory=True)
root.add_children([check_battery, move_to_goal])

# 执行
tree = py_trees.trees.BehaviourTree(root=root)
tree.tick()
```


## Nav2 行为树集成

ROS 2 的 Navigation2 框架使用 BehaviorTree.CPP 编排导航流程。默认行为树包含路径规划、控制器切换、恢复行为等逻辑。

Nav2 常用内置节点：

| 节点 | 功能 |
|------|------|
| `ComputePathToPose` | 调用全局规划器计算路径 |
| `FollowPath` | 调用局部控制器跟踪路径 |
| `Spin` | 原地旋转（恢复行为） |
| `BackUp` | 后退（恢复行为） |
| `Wait` | 等待指定时间 |
| `NavigateRecovery` | 带恢复逻辑的导航子树 |

自定义 Nav2 行为树的典型方法是修改 XML 文件并通过参数加载：

```bash
ros2 launch nav2_bringup navigation_launch.py \
    default_bt_xml_filename:=/path/to/my_custom_bt.xml
```


## 设计模式与最佳实践

### 常用模式

1. **尝试-恢复模式**：Fallback 节点下依次放置正常行为和恢复行为
2. **条件守卫模式**：Sequence 节点以条件节点开头，条件不满足则跳过后续动作
3. **超时重试模式**：Retry 装饰器包裹 Timeout 装饰器
4. **子树复用模式**：将常用行为封装为子树（SubTree），在多处引用

### 设计建议

- 保持树的深度不超过 5-6 层，过深的树难以调试
- 动作节点应当是无状态的，状态通过黑板传递
- 条件节点不应有副作用，仅做判断
- 使用 Groot 等可视化工具辅助设计和调试
- 为每个自定义节点编写单元测试


## 移动机器人示例

以下是一个移动机器人巡逻任务的行为树结构：

```
[Fallback] 巡逻任务
├── [Sequence] 正常巡逻
│   ├── [Condition] 电量充足？
│   ├── [Action] 获取下一个巡逻点
│   ├── [Action] 导航到巡逻点
│   └── [Action] 执行检查
└── [Sequence] 低电量处理
    ├── [Action] 导航到充电站
    └── [Action] 充电
```

该设计利用 Fallback 节点实现了"正常巡逻优先，电量不足则自动充电"的逻辑。当电量检查条件失败时，整个 Sequence 返回 Failure，Fallback 节点自动切换到低电量处理分支。


## 参考资料

- Colledanchise M, Ogren P. *Behavior Trees in Robotics and AI*. CRC Press, 2018.
- BehaviorTree.CPP 文档：<https://www.behaviortree.dev/>
- py_trees 文档：<https://py-trees.readthedocs.io/>
- Nav2 行为树配置：<https://docs.nav2.org/behavior_trees/>
- Groot 可视化工具：<https://github.com/BehaviorTree/Groot>
