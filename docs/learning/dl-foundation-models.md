# 基础模型

!!! note "引言"
    基础模型（Foundation Model）是在大规模数据上预训练的通用模型，通过微调或零样本学习（Zero-Shot Learning）适应下游任务。在机器人领域，视觉基础模型、大语言模型（Large Language Model, LLM）、视觉-语言模型以及视觉-语言-动作模型正在重塑机器人感知、规划和控制的范式，使机器人具备更强的泛化能力和开放世界理解能力。


## 视觉基础模型

### Vision Transformer（ViT）

Vision Transformer（ViT）由 Google 于 2020 年提出，将 Transformer 架构从自然语言处理引入计算机视觉。ViT 将图像分割为固定大小的图块（Patch），将每个图块线性投影为 Token，然后通过标准 Transformer 编码器处理。

核心流程：

1. 输入图像 \(x \in \mathbb{R}^{H \times W \times C}\) 分割为 \(N = HW/P^2\) 个图块
2. 每个图块线性投影为 \(D\) 维向量
3. 添加位置编码（Position Embedding）
4. 通过 \(L\) 层 Transformer 编码器
5. 取 [CLS] 标记的输出用于分类

### DINOv2

DINOv2（Meta, 2023）通过自监督学习（无需标注数据）训练 ViT，学到的特征在语义分割、深度估计、实例检索等任务上表现优异。对于机器人视觉，DINOv2 提供了强大的通用视觉特征提取器：

```python
import torch

# 加载 DINOv2 模型
model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vitb14')
model.eval()

# 提取图像特征
with torch.no_grad():
    features = model(images)  # [B, D] 全局特征
    patch_features = model.get_intermediate_layers(images, n=1)[0]
    # [B, N, D] 图块级特征，可用于密集预测
```

### Segment Anything Model（SAM）

SAM（Meta, 2023）是一个可提示的通用分割模型，支持通过点、框或文本提示分割任何物体。在机器人应用中，SAM 可用于：

- 未知物体的零样本分割（无需训练）
- 交互式场景理解
- 抓取目标选择


## 大语言模型与机器人规划

### LLM 作为任务规划器

大语言模型（如 GPT-4、Claude）蕴含丰富的世界知识和常识推理能力，可作为机器人高层任务规划器：

```
用户指令: "帮我准备一杯咖啡"

LLM 分解为子任务:
1. 走到厨房
2. 找到咖啡机
3. 打开咖啡机
4. 取一个杯子
5. 放置杯子在出水口下方
6. 按下冲泡按钮
7. 等待冲泡完成
8. 将咖啡端给用户
```

### SayCan

SayCan（Google, 2022）是将 LLM 与机器人能力结合的开创性工作。其核心思想是：

- LLM 提供**任务相关性评分**（"这个动作对完成任务有多相关？"）
- 机器人技能模型提供**可行性评分**（"这个动作在当前状态下能否成功执行？"）
- 最终选择 = 相关性 × 可行性

$$
\pi(a | s, l) = p(\text{useful} | a, l) \cdot p(\text{feasible} | a, s)
$$

其中 \(l\) 为语言指令，\(s\) 为当前状态，\(a\) 为候选动作。

### Code as Policies

Code as Policies（Google, 2022）让 LLM 直接生成可执行的机器人控制代码，而非自然语言计划。LLM 接收 API 文档和示例，输出调用机器人 API 的 Python 代码：

```python
# LLM 生成的代码示例
def pick_up_the_red_block():
    # 检测所有物体
    objects = detect_objects()
    # 找到红色方块
    red_block = [o for o in objects if o.color == 'red' and o.shape == 'block'][0]
    # 移动到物体上方
    move_to(red_block.position + [0, 0, 0.1])
    # 下降并抓取
    move_to(red_block.position)
    close_gripper()
    # 抬起
    move_to(red_block.position + [0, 0, 0.2])
```


## 视觉-语言模型

### CLIP

CLIP（Contrastive Language-Image Pre-training，OpenAI, 2021）通过对比学习将图像和文本映射到共享的嵌入空间。在机器人中的应用包括：

- **开放词汇目标检测**：无需训练即可检测任意文本描述的物体
- **语言引导的导航**：通过文本描述导航到目标位置
- **任务条件化感知**：根据任务描述关注相关物体

```python
import clip
import torch
from PIL import Image

model, preprocess = clip.load("ViT-B/32")

# 开放词汇物体识别
image = preprocess(Image.open("scene.jpg")).unsqueeze(0)
text_prompts = clip.tokenize([
    "a red cup",
    "a computer keyboard",
    "a robotic gripper",
    "a cardboard box"
])

with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text_prompts)

    similarity = (image_features @ text_features.T).softmax(dim=-1)
    print(f"最匹配: {similarity}")
```

### GPT-4V / GPT-4o

多模态大模型（如 GPT-4V）可以直接理解图像并回答关于机器人场景的问题，支持：

- 场景描述和物体识别
- 空间关系推理
- 故障诊断（"图中机器人哪里卡住了？"）
- 抓取策略建议


## 视觉-语言-动作模型

### RT-2

RT-2（Robotics Transformer 2，Google DeepMind, 2023）将视觉-语言模型（VLM）微调为可以直接输出机器人动作的模型。其关键创新是将机器人动作离散化为 Token，使得 VLM 可以在统一的 Token 空间中同时处理视觉、语言和动作。

RT-2 的架构：

```
输入: 相机图像 + 语言指令 ("pick up the can")
     ↓
  视觉-语言模型 (PaLI-X 或 PaLM-E)
     ↓
输出: 动作 Token → 解码为 [Δx, Δy, Δz, Δroll, Δpitch, Δyaw, gripper]
```

RT-2 展示了强大的泛化能力：

- 能执行训练数据中未出现的物体和指令组合
- 具备初步的推理能力（"把倒下的物体扶正"）
- 理解抽象概念（"移动到最不常见的物体旁"）

### Octo

Octo（UC Berkeley, 2024）是一个开源的通用机器人策略模型（Generalist Robot Policy），在 Open X-Embodiment 数据集上预训练。特点包括：

- 支持多种机器人形态（单臂、双臂、移动机器人）
- 支持多种输入（单目/双目相机、腕部相机、语言指令）
- 可通过少量数据微调适应新任务和新机器人

```python
from octo.model.octo_model import OctoModel

# 加载预训练模型
model = OctoModel.load_pretrained("hf://rail-berkeley/octo-base")

# 根据观测和语言指令预测动作
task = model.create_tasks(texts=["pick up the red cup"])
action = model.sample_actions(observations, task, rng=jax.random.PRNGKey(0))
```

### 扩散策略（Diffusion Policy）

Diffusion Policy（Columbia/Toyota Research, 2023）将扩散模型（Diffusion Model）应用于机器人策略学习，将动作生成建模为去噪扩散过程。优势包括：

- 能学习多模态动作分布（同一状态下多种合理动作）
- 生成平滑的长期轨迹
- 在接触丰富的操作任务中表现优异


## 开放词汇机器人感知

### 传统感知 vs 开放词汇感知

| 特性 | 传统感知 | 开放词汇感知 |
|------|---------|------------|
| 类别定义 | 训练时固定 | 运行时通过语言指定 |
| 新物体处理 | 需要重新训练 | 零样本识别 |
| 灵活性 | 低 | 高 |
| 精度 | 特定类别上更高 | 通用但可能略低 |
| 代表方法 | YOLOv8, Mask R-CNN | GroundingDINO, OWLv2 |

### GroundingDINO + SAM 组合

```python
# 开放词汇检测 + 分割流水线
# 1. GroundingDINO 根据文本提示检测目标框
# 2. SAM 根据检测框生成精确分割掩码

from groundingdino.util.inference import predict
from segment_anything import SamPredictor

# 文本提示检测
boxes, logits, phrases = predict(
    model=grounding_model,
    image=image,
    caption="red cup . blue bottle . green apple",
    box_threshold=0.3,
    text_threshold=0.25
)

# 对每个检测框生成分割掩码
sam_predictor.set_image(image)
masks, _, _ = sam_predictor.predict(
    box=boxes,
    multimask_output=False
)
```


## 发展趋势

1. **统一模型**：从分离的感知-规划-控制到端到端的统一模型
2. **数据规模**：Open X-Embodiment 等大规模跨机器人数据集推动泛化能力提升
3. **世界模型**：学习环境的预测模型（World Model），支持想象中的规划和推理
4. **物理理解**：从语义理解扩展到物理属性理解（重量、刚度、摩擦）
5. **人机交互**：自然语言成为人与机器人交互的主要接口


## 参考资料

1. Dosovitskiy, A., et al. (2020). An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale. *ICLR 2021*.
2. Oquab, M., et al. (2023). DINOv2: Learning Robust Visual Features without Supervision. *TMLR*.
3. Radford, A., et al. (2021). Learning Transferable Visual Models From Natural Language Supervision. *ICML*.
4. Ahn, M., et al. (2022). Do As I Can, Not As I Say: Grounding Language in Robotic Affordances. *CoRL*.
5. Brohan, A., et al. (2023). RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control. *CoRL*.
6. Team, O., et al. (2024). Octo: An Open-Source Generalist Robot Policy. *RSS*.
7. Chi, C., et al. (2023). Diffusion Policy: Visuomotor Policy Learning via Action Diffusion. *RSS*.
8. Kirillov, A., et al. (2023). Segment Anything. *ICCV*.
