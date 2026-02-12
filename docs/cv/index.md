# 机器视觉

!!! note "引言"
    机器视觉 (Computer Vision) 是让机器人"看懂"世界的核心技术。它研究如何从图像或视频中提取有意义的信息，使机器人能够识别物体、理解场景、估计位姿并做出决策。本页面概述了机器视觉在机器人中的主要任务、常用方法和技术框架。


## 机器视觉在机器人中的角色

视觉是人类获取信息最重要的感官通道，约 80% 的环境信息通过视觉获取。类似地，机器视觉为机器人提供了丰富的环境感知能力，是实现自主行为的关键。

机器视觉在机器人系统中承担的主要功能包括：

- **环境理解**：识别和理解机器人所处的场景
- **目标交互**：检测、定位和跟踪操作目标
- **自主导航**：通过视觉信息进行定位和地图构建
- **质量检测**：在工业场景中检测产品缺陷


## 相机模型与图像形成

理解机器视觉的基础是相机模型 (Camera Model)。最常用的模型是针孔相机模型 (Pinhole Camera Model)，它描述了三维空间点到二维图像平面的投影关系：

$$
s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} R & t \end{bmatrix} \begin{bmatrix} X \\ Y \\ Z \\ 1 \end{bmatrix}
$$

其中 \((u, v)\) 是像素坐标，\(f_x, f_y\) 是焦距，\((c_x, c_y)\) 是主点坐标，\(R\) 和 \(t\) 分别是旋转矩阵和平移向量，\(s\) 是比例因子。

相机标定 (Camera Calibration) 是确定这些内参 (Intrinsic Parameters) 和外参 (Extrinsic Parameters) 的过程，是所有视觉算法的前置步骤。常用的标定方法是 Zhang 的棋盘格标定法 [1]。


## 图像处理与预处理

原始图像通常需要经过预处理才能被后续算法有效利用。常见的预处理操作包括：

- **灰度化 (Grayscale Conversion)**：将彩色图像转换为灰度图像，降低计算量
- **去噪 (Denoising)**：使用高斯滤波 (Gaussian Filter)、中值滤波 (Median Filter) 或双边滤波 (Bilateral Filter) 去除噪声
- **边缘检测 (Edge Detection)**：使用 Canny、Sobel 等算子提取图像中的边缘信息
- **直方图均衡化 (Histogram Equalization)**：增强图像对比度
- **形态学操作 (Morphological Operations)**：腐蚀 (Erosion)、膨胀 (Dilation)、开运算 (Opening)、闭运算 (Closing) 等
- **特征提取 (Feature Extraction)**：提取关键点和描述子，如 SIFT、SURF、ORB 等


## 核心视觉任务

机器视觉中常见的问题与技术主要包含：

### 目标检测 (Object Detection)

目标检测是在图像中定位并识别特定类别物体的任务，输出为目标的边界框 (Bounding Box) 和类别标签。

主要方法分为两类：

- **两阶段检测器 (Two-stage Detectors)**：先生成候选区域，再进行分类和回归。代表算法有 R-CNN、Fast R-CNN、Faster R-CNN。精度高但速度较慢。
- **单阶段检测器 (Single-stage Detectors)**：直接从图像预测目标位置和类别。代表算法有 SSD、YOLO 系列（YOLOv3 ~ YOLOv8）、RetinaNet。速度快，适合实时应用。

轻量级检测网络如 MobileNet、EfficientDet 适合部署在嵌入式平台（如 NVIDIA Jetson）上。

详见 [目标检测](object-detection.md) 页面。

### 图像分割 (Image Segmentation)

图像分割将图像中的每个像素分配到特定的类别或实例：

- **语义分割 (Semantic Segmentation)**：为每个像素赋予类别标签，不区分同类的不同实例。代表算法有 FCN、U-Net、DeepLab 系列。
- **实例分割 (Instance Segmentation)**：不仅区分类别，还区分同类的不同个体。代表算法有 Mask R-CNN。
- **全景分割 (Panoptic Segmentation)**：结合语义分割和实例分割，对图像进行完整的场景解析。

### 目标跟踪 (Object Tracking)

目标跟踪是在视频序列中持续定位特定目标的任务。按方法分为：

- **基于相关滤波的跟踪 (Correlation Filter)**：KCF、MOSSE 等，速度快但对遮挡敏感
- **基于深度学习的跟踪 (Deep Learning)**：SiamFC、SiamRPN 等，鲁棒性更强
- **多目标跟踪 (Multi-Object Tracking, MOT)**：SORT、DeepSORT 等，同时跟踪多个目标

### 位姿估计 (Pose Estimation)

位姿估计是确定物体或人体在三维空间中的位置和姿态：

- **物体位姿估计 (Object Pose Estimation)**：估计已知物体的 6DoF 位姿（3个平移 + 3个旋转），用于机器人抓取
- **人体姿态估计 (Human Pose Estimation)**：检测人体关键点（关节位置），用于人机交互。代表算法有 OpenPose、MediaPipe Pose

### 三维视觉 (3D Vision)

三维视觉从二维图像中恢复场景的三维结构：

- **双目视觉 (Stereo Vision)**：通过立体匹配计算稠密深度图
- **运动恢复结构 (Structure from Motion, SfM)**：从多视角图像重建三维点云
- **三维点云处理 (Point Cloud Processing)**：对激光雷达或深度相机生成的点云进行分类、分割和识别。代表算法有 PointNet、PointNet++
- **同时定位与地图构建 (SLAM)**：实时构建环境地图并定位机器人自身位置。代表系统有 ORB-SLAM、LSD-SLAM


## 常用框架与工具

| 框架/工具 | 类型 | 主要特点 |
|-----------|------|---------|
| OpenCV | 传统视觉库 | 功能全面、跨平台、C++/Python 接口、实时性好 |
| PyTorch | 深度学习框架 | 动态图、研究友好、生态丰富（torchvision、detectron2） |
| TensorFlow | 深度学习框架 | 部署友好（TensorFlow Lite、TensorFlow.js）、TensorRT 加速 |
| ONNX Runtime | 推理引擎 | 跨框架模型推理、支持多种硬件加速 |
| MediaPipe | 端侧AI框架 | Google 推出的轻量级实时感知框架，支持手势、人脸、姿态检测 |
| Open3D | 三维视觉库 | 点云处理、三维重建、可视化 |
| PCL | 点云库 | 三维点云处理的经典 C++ 库，与 ROS 集成紧密 |


## 视觉处理流水线

一个典型的机器人视觉处理流水线 (Pipeline) 如下：

```
图像采集 → 预处理 → 特征提取/深度学习推理 → 后处理 → 输出结果
   │           │              │                    │          │
 相机驱动    去噪/增强    检测/分割/识别      NMS/滤波    位姿/语义
```

在实际系统中，需要关注以下工程问题：

- **推理速度**：嵌入式平台上的模型优化（量化、剪枝、蒸馏）
- **多相机同步**：多摄像头系统的时间戳同步和外参标定
- **与 ROS 集成**：使用 `image_transport`、`cv_bridge` 等 ROS 包
- **GPU 加速**：CUDA、TensorRT、OpenCL 等并行计算技术


## 参考资料

1. Zhang, Z. (2000). A flexible new technique for camera calibration. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 22(11), 1330-1334.
2. Szeliski, R. (2022). *Computer Vision: Algorithms and Applications* (2nd ed.). Springer. [在线版本](https://szeliski.org/Book/)
3. Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press. [在线版本](https://www.deeplearningbook.org/)
4. Hartley, R. & Zisserman, A. (2004). *Multiple View Geometry in Computer Vision* (2nd ed.). Cambridge University Press.
