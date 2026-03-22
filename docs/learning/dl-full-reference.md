# 深度学习参考资料

!!! note "引言"
    本页面汇集机器人深度学习相关的论文、教材、框架、数据集和硬件选型参考，为研究和工程实践提供快速索引。


## 关键论文

| 论文 | 年份 | 贡献 | 会议/期刊 |
|------|------|------|----------|
| AlexNet | 2012 | 深度 CNN 在 ImageNet 上的突破 | NeurIPS |
| ResNet | 2015 | 残差连接解决深层网络退化 | CVPR |
| Transformer (Attention Is All You Need) | 2017 | 自注意力机制架构 | NeurIPS |
| ViT (Vision Transformer) | 2020 | Transformer 用于图像分类 | ICLR |
| CLIP | 2021 | 视觉-语言对比学习 | ICML |
| SAM (Segment Anything) | 2023 | 通用可提示分割模型 | ICCV |
| RT-2 | 2023 | VLM 直接输出机器人动作 | CoRL |
| Diffusion Policy | 2023 | 扩散模型用于机器人策略 | RSS |
| Octo | 2024 | 开源通用机器人策略 | RSS |
| DINOv2 | 2023 | 自监督视觉基础模型 | TMLR |


## 推荐教材

| 教材 | 作者 | 内容特色 |
|------|------|---------|
| *Deep Learning* | Goodfellow, Bengio, Courville | DL 理论经典，免费在线版 |
| *Dive into Deep Learning* | Zhang, Lipton, Li, Smola | 交互式教材，含代码 |
| *Deep Learning for Robotics* | Various (Springer) | 机器人 DL 应用专题 |
| *Probabilistic Robotics* | Thrun, Burgard, Fox | 概率方法（贝叶斯滤波、SLAM） |
| 《动手学深度学习》 | 李沐等 | 中文版，PyTorch/MXNet 代码 |


## 深度学习框架对比

| 框架 | 优势 | 机器人生态 | 部署支持 |
|------|------|----------|---------|
| **PyTorch** | 灵活、调试友好、社区最活跃 | torchvision, timm, HuggingFace | TorchScript, ONNX, TensorRT |
| **JAX** | 函数式编程、XLA 编译、高性能 | Brax (物理仿真), Flax | SavedModel, ONNX |
| **TensorFlow** | TFLite 移动端部署成熟 | TF Agents, TF-ROS | TFLite, TF Serving |

推荐选择：**PyTorch** 是当前机器人深度学习的主流选择，生态最完整。


## 预训练模型资源

| 平台 | 模型类型 | 特色 |
|------|---------|------|
| HuggingFace Hub | NLP, CV, 多模态 | 最大的模型社区，统一 API |
| timm (PyTorch Image Models) | 图像分类 | 800+ 预训练模型，统一接口 |
| torchvision | 检测、分割、分类 | PyTorch 官方，稳定可靠 |
| MMDetection / MMSegmentation | 检测、分割 | OpenMMLab 生态，配置灵活 |
| Ultralytics Hub | YOLO 系列 | 一站式目标检测 |
| NVIDIA NGC | 企业级模型 | TensorRT 优化版本 |


## 机器人深度学习数据集

### 视觉感知

| 数据集 | 规模 | 任务 | 传感器 |
|--------|------|------|--------|
| COCO | 33 万张 | 检测/分割/关键点 | RGB |
| KITTI | 1.5 万帧 | 3D 检测/SLAM/光流 | 相机 + LiDAR + GPS |
| nuScenes | 40 万帧 | 3D 检测/跟踪/预测 | 6 相机 + LiDAR + Radar |
| Waymo Open | 20 万帧 | 3D 检测/跟踪 | 5 相机 + 5 LiDAR |
| ScanNet | 1513 场景 | 3D 语义分割 | RGB-D |

### 操作与模仿学习

| 数据集 | 规模 | 内容 | 机器人 |
|--------|------|------|--------|
| Open X-Embodiment | 100 万+ 轨迹 | 多机器人多任务 | 22 种机器人 |
| RoboNet | 1500 万帧 | 机器人交互视频 | 7 种机器人 |
| DROID | 7.6 万轨迹 | 多场景操作 | Franka |
| BridgeData V2 | 6 万轨迹 | 厨房操作 | WidowX |


## 硬件选型指南

### 训练 GPU

| GPU | 显存 | FP16 算力 | 适用场景 | 参考价格 |
|-----|------|----------|---------|---------|
| RTX 3090 | 24 GB | 142 TFLOPS | 个人研究 | ~¥8,000 |
| RTX 4090 | 24 GB | 330 TFLOPS | 个人/小团队 | ~¥14,000 |
| A100 40G | 40 GB | 312 TFLOPS | 团队/大模型 | ~¥70,000 |
| A100 80G | 80 GB | 312 TFLOPS | 大模型训练 | ~¥100,000 |
| H100 | 80 GB | 990 TFLOPS | 基础模型训练 | ~¥250,000 |

### 推理平台（机器人端）

| 平台 | 功耗 | GPU 算力 | 适用场景 |
|------|------|---------|---------|
| Jetson Nano | 5–10W | 472 GFLOPS | 教育、轻量推理 |
| Jetson Xavier NX | 10–15W | 21 TOPS | 中型机器人 |
| Jetson Orin NX | 10–25W | 100 TOPS | 高性能机器人 |
| Jetson AGX Orin | 15–60W | 275 TOPS | 自动驾驶、工业 |
| Intel NUC + dGPU | 40–100W | 可变 | 室内服务机器人 |


## 常用符号约定

| 符号 | 含义 |
|------|------|
| \(\mathbf{x}, \mathbf{s}\) | 状态/观测向量 |
| \(\mathbf{a}, \mathbf{u}\) | 动作/控制向量 |
| \(\pi_\theta\) | 参数为 \(\theta\) 的策略网络 |
| \(\mathcal{L}\) | 损失函数 |
| \(\nabla_\theta\) | 对参数 \(\theta\) 的梯度 |
| \(\mathcal{D}\) | 数据集 |
| \(\mathbb{E}\) | 期望 |
| \(\sigma(\cdot)\) | Softmax 或 Sigmoid 函数 |
| \(\text{KL}(\cdot \| \cdot)\) | KL 散度 |


## 参考资料

1. Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press. https://www.deeplearningbook.org/
2. Zhang, A., et al. (2023). *Dive into Deep Learning*. https://d2l.ai/
3. PyTorch 官方文档：https://pytorch.org/docs/
4. HuggingFace Hub：https://huggingface.co/models
5. timm 库：https://github.com/huggingface/pytorch-image-models
6. Open X-Embodiment 数据集：https://robotics-transformer-x.github.io/
7. Papers With Code 排行榜：https://paperswithcode.com/
