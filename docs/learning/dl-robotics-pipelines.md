# 深度学习机器人流水线

!!! note "引言"
    现代机器人系统中，深度学习被广泛应用于从感知到决策的完整流水线。本文介绍机器人领域中典型的深度学习流水线架构，包括感知流水线（检测→跟踪→预测）、模仿学习、端到端自动驾驶、操作（Manipulation）流水线、数据采集策略以及持续学习机制。


## 感知流水线

### 检测-跟踪-预测（Detection-Tracking-Prediction）

自动驾驶和移动机器人中最常见的感知流水线由三个级联阶段组成：

```
相机/LiDAR 输入
    ↓
3D 目标检测 (PointPillars / BEVFusion)
    ↓
多目标跟踪 (ByteTrack / OC-SORT)
    ↓
轨迹预测 (HiVT / MTR)
    ↓
规划模块
```

**检测阶段**：从传感器原始数据中识别物体的类别、位置和朝向。3D 检测方法包括基于点云的（PointPillars、CenterPoint）、基于图像的（BEVDet）和融合的（BEVFusion）。

**跟踪阶段**：将连续帧中的检测结果关联为持续的轨迹（Track）。常用指标包括 MOTA（多目标跟踪精度）和 IDF1（身份保持率）。

**预测阶段**：基于历史轨迹预测其他交通参与者未来的运动轨迹，通常预测 3–8 秒内的多条可能路径及其概率。

### 鸟瞰图（BEV）感知

BEV（Bird's Eye View）感知将多个相机视角的图像统一投影到俯视图空间，便于后续的检测和规划：

```python
# BEV 感知伪代码
class BEVPerception(nn.Module):
    def __init__(self):
        self.backbone = ResNet50()          # 图像特征提取
        self.neck = FPN()                   # 多尺度特征融合
        self.view_transform = LSS()         # 透视图 → BEV 变换
        self.bev_encoder = BEVEncoder()     # BEV 特征编码
        self.det_head = CenterPointHead()   # 检测头
        self.seg_head = MapSegHead()        # 地图分割头

    def forward(self, multi_view_images, camera_params):
        # 提取每个相机视角的特征
        features = [self.neck(self.backbone(img)) for img in multi_view_images]
        # 投影到 BEV 空间
        bev_features = self.view_transform(features, camera_params)
        bev_features = self.bev_encoder(bev_features)
        # 多任务输出
        detections = self.det_head(bev_features)
        map_seg = self.seg_head(bev_features)
        return detections, map_seg
```


## 模仿学习

### 行为克隆（Behavior Cloning, BC）

行为克隆是最简单的模仿学习方法，将专家演示数据视为监督学习问题：

$$
\pi^* = \arg\min_\pi \mathbb{E}_{(s,a) \sim \mathcal{D}} [\mathcal{L}(\pi(s), a)]
$$

```python
import torch
import torch.nn as nn

class BCPolicy(nn.Module):
    def __init__(self, obs_dim, act_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, act_dim),
        )

    def forward(self, obs):
        return self.net(obs)

# 训练
policy = BCPolicy(obs_dim=48, act_dim=7)
optimizer = torch.optim.Adam(policy.parameters(), lr=1e-3)

for batch in expert_dataloader:
    pred_action = policy(batch['observation'])
    loss = nn.functional.mse_loss(pred_action, batch['action'])
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

行为克隆的核心问题是**分布偏移**（Distribution Shift）：策略执行时遇到训练数据中未覆盖的状态，导致错误累积。

### DAgger

DAgger（Dataset Aggregation）通过迭代式数据收集缓解分布偏移：

1. 使用当前策略 \(\pi_i\) 与环境交互收集数据
2. 由专家为收集到的状态标注正确动作
3. 将新数据加入训练集，重新训练策略
4. 重复直到策略收敛

### 扩散策略

扩散策略（Diffusion Policy）将动作预测建模为条件去噪过程，在操作任务中表现出色：

```python
# 扩散策略推理伪代码
def predict_action(observation, noise_scheduler, model):
    # 从纯噪声开始
    action = torch.randn(action_shape)

    # 逐步去噪
    for t in reversed(range(num_diffusion_steps)):
        noise_pred = model(action, t, observation)
        action = noise_scheduler.step(noise_pred, t, action)

    return action
```

优势：能表示多模态动作分布、生成平滑轨迹、对超参数不敏感。


## 端到端自动驾驶

### 从模块化到端到端

| 方面 | 模块化方案 | 端到端方案 |
|------|----------|----------|
| 架构 | 感知→预测→规划→控制 | 传感器输入→动作输出 |
| 优点 | 可解释、可调试 | 全局最优、无信息损失 |
| 缺点 | 模块间信息瓶颈 | 可解释性差、需大量数据 |
| 代表 | Apollo, Autoware | UniAD, PARA-Drive |

### UniAD

UniAD（统一自动驾驶，2023）是一个代表性的端到端自动驾驶框架，将感知、预测和规划统一在一个 Transformer 架构中：

```
多视角图像 → BEV 特征 → 跟踪查询 → 地图查询 → 运动查询 → 规划查询 → 轨迹输出
```


## 操作流水线

### 抓取姿态检测

机械臂抓取的核心是从视觉输入中预测稳定的抓取姿态（Grasp Pose）：

| 方法 | 输入 | 输出 | 代表工作 |
|------|------|------|---------|
| 平面抓取 | RGB-D | 2D 抓取矩形 | GG-CNN |
| 6-DoF 抓取 | 点云 | SE(3) 抓取姿态 | Contact-GraspNet |
| 语言条件抓取 | RGB + 语言 | 目标物体抓取姿态 | GraspGPT |

### 可供性预测（Affordance Prediction）

可供性（Affordance）描述物体可以被如何操作（如杯子的把手适合抓握、门把手适合旋转）：

```python
# 可供性预测网络
class AffordanceNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = ResNet18(pretrained=True)
        self.decoder = UNetDecoder()  # 生成像素级可供性热力图

    def forward(self, image, task_embedding):
        features = self.backbone(image)
        # 任务条件化：不同任务关注不同可供性
        conditioned = features * task_embedding.unsqueeze(-1).unsqueeze(-1)
        affordance_map = self.decoder(conditioned)  # [B, 1, H, W]
        return affordance_map
```


## 数据采集策略

### 遥操作（Teleoperation）

遥操作是机器人操作领域最常用的数据采集方式：

| 设备 | 成本 | 精度 | 适用场景 |
|------|------|------|---------|
| 键盘/游戏手柄 | 低 | 低 | 导航、简单移动 |
| SpaceMouse | 中 | 中 | 6-DoF 机械臂控制 |
| 动作捕捉手套 | 高 | 高 | 灵巧操作 |
| VR 控制器 | 中 | 高 | 双臂协作 |
| 主从遥操作 | 高 | 极高 | 精密操作 |

### 仿真数据生成

利用仿真环境大规模生成训练数据：

- **域随机化**（Domain Randomization）：随机化纹理、光照、物体位置
- **程序化生成**（Procedural Generation）：自动生成多样化场景
- **数据增强**：对真实数据进行几何和颜色变换

### ALOHA 数据采集系统

ALOHA（A Low-cost Open-source Hardware System for Bimanual Teleoperation）使用低成本的主从机械臂进行双臂遥操作数据采集，配合 ACT（Action Chunking with Transformers）策略训练，在精细操作任务上取得优异效果。


## 持续学习

### 在线模型更新

机器人在部署后会遇到训练时未见过的场景，持续学习（Continual Learning）使模型能不断适应新情况：

- **经验回放**（Experience Replay）：保留历史数据防止遗忘
- **弹性权重整合**（Elastic Weight Consolidation, EWC）：限制重要参数的变化
- **渐进式网络**（Progressive Networks）：为新任务添加新模块

### 人在回路学习

```
部署运行 → 检测失败案例 → 人工标注/纠正 → 增量训练 → 重新部署
     ↑                                                    |
     └────────────────── 持续循环 ←────────────────────────┘
```

关键实践：

1. 部署监控系统自动检测低置信度预测
2. 将不确定样本推送给人工审核
3. 增量训练时使用混合数据（新数据 + 历史数据回放）
4. A/B 测试验证新模型优于旧模型


## 参考资料

1. Hu, Y., et al. (2023). Planning-oriented Autonomous Driving (UniAD). *CVPR*.
2. Chi, C., et al. (2023). Diffusion Policy: Visuomotor Policy Learning via Action Diffusion. *RSS*.
3. Ross, S., Gordon, G., & Bagnell, J. A. (2011). A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning. *AISTATS*.
4. Zhao, T. Z., et al. (2023). Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ALOHA). *RSS*.
5. Sundermeyer, M., et al. (2021). Contact-GraspNet: Efficient 6-DoF Grasp Generation in Cluttered Scenes. *ICRA*.
6. Liu, Z., et al. (2023). BEVFusion: Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation. *ICRA*.
