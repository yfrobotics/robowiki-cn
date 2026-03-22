# 深度学习训练与部署

!!! note "引言"
    将深度学习模型从研究原型转化为机器人上可靠运行的推理引擎，需要掌握分布式训练、混合精度训练、模型压缩和边缘部署等工程技术。本文介绍从训练到部署的完整流水线，重点关注机器人系统常用的 NVIDIA Jetson 等边缘计算平台。


## 分布式训练

### 数据并行（Data Parallel）

数据并行是最常用的分布式训练策略，将一个批次的数据分配到多个 GPU 上，每个 GPU 运行相同的模型副本。

**PyTorch DistributedDataParallel（DDP）**是推荐的数据并行方式：

```python
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data.distributed import DistributedSampler

def setup(rank, world_size):
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

def train(rank, world_size):
    setup(rank, world_size)

    model = MyModel().to(rank)
    model = DDP(model, device_ids=[rank])

    dataset = MyDataset()
    sampler = DistributedSampler(dataset, num_replicas=world_size, rank=rank)
    dataloader = DataLoader(dataset, batch_size=32, sampler=sampler)

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

    for epoch in range(num_epochs):
        sampler.set_epoch(epoch)  # 保证每个 epoch 数据打乱不同
        for batch in dataloader:
            loss = model(batch)
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

# 启动命令
# torchrun --nproc_per_node=4 train.py
```

### 全分片数据并行（FSDP）

FSDP（Fully Sharded Data Parallel）将模型参数、梯度和优化器状态分片到多个 GPU，大幅降低单卡显存需求，适合训练大模型：

```python
from torch.distributed.fsdp import FullyShardedDataParallel as FSDP
from torch.distributed.fsdp import ShardingStrategy

model = FSDP(
    model,
    sharding_strategy=ShardingStrategy.FULL_SHARD,
    auto_wrap_policy=size_based_auto_wrap_policy,
    mixed_precision=MixedPrecision(
        param_dtype=torch.float16,
        reduce_dtype=torch.float16,
        buffer_dtype=torch.float16,
    ),
)
```


## 混合精度训练

混合精度训练（Mixed Precision Training）使用 FP16 进行前向和反向传播以加速计算，同时保持 FP32 的主权重副本以保证精度：

```python
from torch.amp import autocast, GradScaler

scaler = GradScaler()

for batch in dataloader:
    optimizer.zero_grad()

    # 自动混合精度：前向传播使用 FP16
    with autocast(device_type='cuda'):
        output = model(batch['input'])
        loss = criterion(output, batch['target'])

    # 梯度缩放防止 FP16 下溢
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

混合精度训练通常可以将训练速度提升 1.5–2 倍，显存占用减少约 30%。


## 模型压缩

### 剪枝（Pruning）

剪枝通过移除模型中不重要的权重或结构（通道、层）来减小模型：

| 剪枝类型 | 方法 | 加速效果 | 精度影响 |
|---------|------|---------|---------|
| 非结构化剪枝 | 按权重大小移除单个参数 | 需要稀疏计算支持 | 小 |
| 结构化剪枝 | 移除整个通道或层 | 直接减少计算量 | 中等 |
| 彩票假说 | 找到稀疏子网络重新训练 | 高 | 小 |

### 量化（Quantization）

量化将浮点权重和激活转换为低精度整数表示：

```python
import torch.quantization as quant

# 训练后静态量化（Post-Training Static Quantization）
model.eval()
model.qconfig = quant.get_default_qconfig('x86')
model_prepared = quant.prepare(model)

# 使用校准数据集收集激活统计
with torch.no_grad():
    for batch in calibration_loader:
        model_prepared(batch)

model_quantized = quant.convert(model_prepared)
```

| 量化方案 | 位宽 | 模型大小 | 速度提升 | 精度损失 |
|---------|------|---------|---------|---------|
| FP32（基线） | 32 bit | 1× | 1× | — |
| FP16 | 16 bit | 0.5× | 1.5–2× | 极小 |
| INT8 | 8 bit | 0.25× | 2–4× | 小（<1%） |
| INT4 | 4 bit | 0.125× | 3–6× | 中等 |

### 知识蒸馏（Knowledge Distillation）

知识蒸馏使用大模型（教师）的软标签指导小模型（学生）训练：

$$
\mathcal{L} = \alpha \mathcal{L}_{CE}(y, \hat{y}_{student}) + (1-\alpha) T^2 \cdot \text{KL}(\sigma(\frac{z_{teacher}}{T}), \sigma(\frac{z_{student}}{T}))
$$

其中 \(T\) 为温度参数（通常 2–20），\(\alpha\) 为硬标签和软标签损失的权重。


## 边缘部署

### TensorRT

TensorRT 是 NVIDIA 的高性能推理优化器，通过层融合、内核自动调优、精度校准等技术大幅提升推理速度：

```python
import tensorrt as trt
import numpy as np

# 从 ONNX 模型构建 TensorRT 引擎
logger = trt.Logger(trt.Logger.WARNING)
builder = trt.Builder(logger)
network = builder.create_network(
    1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
)
parser = trt.OnnxParser(network, logger)

with open("model.onnx", "rb") as f:
    parser.parse(f.read())

config = builder.create_builder_config()
config.set_flag(trt.BuilderFlag.FP16)  # 启用 FP16

engine = builder.build_serialized_network(network, config)
```

### ONNX Runtime

ONNX Runtime 是跨平台的推理引擎，支持多种硬件加速后端：

```python
import onnxruntime as ort
import numpy as np

# 加载 ONNX 模型
session = ort.InferenceSession(
    "model.onnx",
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)

# 推理
input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
outputs = session.run(None, {"input": input_data})
```

### NVIDIA Jetson 部署优化

| 优化技术 | 效果 | 实现方式 |
|---------|------|---------|
| TensorRT FP16 | 推理速度提升 2–3× | `model.export(format='engine', half=True)` |
| INT8 量化 | 推理速度提升 3–5× | 使用校准数据集量化 |
| DLA 加速 | 降低 GPU 功耗 | `config.set_flag(trt.BuilderFlag.GPU_FALLBACK)` |
| 功耗模式 | 控制功耗/性能 | `sudo nvpmodel -m 0` (最大性能) |
| 风扇控制 | 防止热降频 | `sudo jetson_clocks` |

### Jetson 平台性能参考

| 模型 | Jetson Nano | Xavier NX | Orin NX | AGX Orin |
|------|------------|-----------|---------|----------|
| ResNet-50 (FP16) | 36 FPS | 170 FPS | 340 FPS | 680 FPS |
| YOLOv8n (FP16) | 15 FPS | 90 FPS | 100 FPS | 200 FPS |
| MobileNetV2 (INT8) | 80 FPS | 300 FPS | 500 FPS | 900 FPS |


## 实验管理

### Weights & Biases (W&B)

```python
import wandb

wandb.init(project="robot-perception", name="yolov8-finetune")

for epoch in range(num_epochs):
    train_loss = train_one_epoch(model, dataloader)
    val_metrics = evaluate(model, val_loader)

    wandb.log({
        "epoch": epoch,
        "train_loss": train_loss,
        "val_mAP50": val_metrics["mAP50"],
        "val_mAP50-95": val_metrics["mAP50-95"],
        "learning_rate": optimizer.param_groups[0]["lr"],
    })

# 保存最佳模型为 artifact
artifact = wandb.Artifact("best-model", type="model")
artifact.add_file("best.pt")
wandb.log_artifact(artifact)
```

### MLflow

```python
import mlflow

mlflow.set_experiment("robot-perception")

with mlflow.start_run():
    mlflow.log_params({
        "model": "yolov8n",
        "epochs": 100,
        "batch_size": 16,
        "learning_rate": 1e-3,
    })

    # 训练...

    mlflow.log_metrics({
        "mAP50": 0.85,
        "mAP50-95": 0.62,
        "inference_time_ms": 8.5,
    })

    mlflow.pytorch.log_model(model, "model")
```


## 训练流水线最佳实践

1. **数据加载**：使用 `num_workers > 0` 和 `pin_memory=True` 避免 GPU 空等数据
2. **梯度累积**：在显存不足时模拟大批次，`if (step + 1) % accum_steps == 0: optimizer.step()`
3. **学习率调度**：使用余弦退火（Cosine Annealing）或 OneCycleLR
4. **早停**：监控验证集指标，连续 N 个 epoch 不提升则停止
5. **检查点**：每个 epoch 保存模型，记录最佳验证指标对应的权重
6. **可复现性**：固定随机种子、记录完整配置、使用版本控制管理代码和数据


## 参考资料

1. Micikevicius, P., et al. (2018). Mixed Precision Training. *ICLR*.
2. Hinton, G., Vinyals, O., & Dean, J. (2015). Distilling the Knowledge in a Neural Network. *NeurIPS Workshop*.
3. NVIDIA TensorRT 文档：https://docs.nvidia.com/deeplearning/tensorrt/
4. PyTorch 分布式训练教程：https://pytorch.org/tutorials/intermediate/ddp_tutorial.html
5. ONNX Runtime 文档：https://onnxruntime.ai/docs/
6. Weights & Biases 文档：https://docs.wandb.ai/
