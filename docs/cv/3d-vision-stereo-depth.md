# 立体视觉与深度估计

!!! note "引言"
    深度感知是机器人理解三维世界的基础能力。立体视觉（Stereo Vision）通过模拟人类双眼的视差原理来恢复场景深度，而单目深度估计（Monocular Depth Estimation）则利用深度学习从单张图像中推断深度信息。本文系统介绍立体视觉的几何原理、主流匹配算法、单目深度估计方法，以及主动深度传感器的工作原理，最后给出基于 OpenCV 的立体标定与深度图计算的完整实践代码。


## 立体视觉基础

### 对极几何

对极几何（Epipolar Geometry）描述了同一场景在两个不同视角下成像的几何约束关系。设空间点 \(P\) 在左右相机中的投影分别为 \(p_L\) 和 \(p_R\)，则它们满足**对极约束**：

$$
p_R^T F p_L = 0
$$

其中 \(F\) 为**基础矩阵**（Fundamental Matrix），是一个秩为 2 的 \(3 \times 3\) 矩阵，包含 7 个自由度。当相机内参已知时，可用**本质矩阵**（Essential Matrix）\(E\) 表示：

$$
E = K_R^T F K_L
$$

其中 \(K_L, K_R\) 分别为左右相机的内参矩阵。本质矩阵可以分解为旋转矩阵 \(R\) 和平移向量 \(t\) 的组合：

$$
E = [t]_\times R
$$

对极约束的几何意义：对于左图中的一个点 \(p_L\)，其在右图中的对应点 \(p_R\) 必定位于一条直线上，这条直线称为**对极线**（Epipolar Line）。


### 图像校正

图像校正（Rectification）将两幅图像变换到同一平面上，使所有对极线变为水平线。校正后，立体匹配问题从二维搜索简化为一维搜索，大幅降低计算复杂度。

校正过程包括：

1. **计算校正变换**：求取两个单应矩阵 \(H_L, H_R\)，使变换后的图像满足行对齐条件
2. **图像重映射**：使用插值方法对原始图像进行变换
3. **视差范围确定**：根据基线长度和场景深度范围确定搜索窗口

| 参数 | 说明 | 典型值 |
|------|------|--------|
| 基线长度 \(b\) | 两相机光心之间的距离 | 60-120 mm |
| 焦距 \(f\) | 相机焦距（像素单位） | 500-2000 px |
| 视差范围 | 最大视差与最小视差之差 | 64-256 px |
| 深度分辨率 | \(\Delta Z = Z^2 / (fb)\) | 取决于距离 |


### 视差与深度

对于校正后的立体图像对，空间点的深度 \(Z\) 与视差 \(d\) 的关系为：

$$
Z = \frac{f \cdot b}{d}
$$

其中 \(f\) 为焦距（像素），\(b\) 为基线长度（米），\(d = x_L - x_R\) 为视差（像素）。由此可见，深度与视差成反比，近处物体视差大、深度估计精度高，远处物体视差小、精度较低。


## 立体匹配算法

### 传统方法

立体匹配算法根据优化策略可分为**局部方法**和**全局方法**两大类。

**局部方法**在固定窗口内计算匹配代价，常用代价函数包括：

- **绝对差之和**（Sum of Absolute Differences, SAD）
- **平方差之和**（Sum of Squared Differences, SSD）
- **归一化互相关**（Normalized Cross-Correlation, NCC）
- **Census 变换**：基于像素邻域的相对排序，对光照变化鲁棒

**全局方法**将匹配问题建模为能量最小化问题：

$$
E(d) = \sum_p C(p, d_p) + \sum_{(p,q) \in \mathcal{N}} V(d_p, d_q)
$$

其中第一项为数据项（匹配代价），第二项为平滑项（鼓励相邻像素具有相似视差）。


### 半全局匹配（SGM）

半全局匹配（Semi-Global Matching, SGM）由 Hirschmuller 于 2005 年提出，是目前工业界应用最广泛的立体匹配算法。SGM 沿多个方向（通常为 8 或 16 个方向）进行一维路径优化，近似求解全局能量最小化问题。

沿方向 \(\mathbf{r}\) 的路径代价递推公式为：

$$
L_{\mathbf{r}}(p, d) = C(p, d) + \min \begin{cases} L_{\mathbf{r}}(p-\mathbf{r}, d) \\ L_{\mathbf{r}}(p-\mathbf{r}, d \pm 1) + P_1 \\ \min_i L_{\mathbf{r}}(p-\mathbf{r}, i) + P_2 \end{cases}
$$

其中 \(P_1\) 和 \(P_2\) 为惩罚参数，\(P_1\) 惩罚视差变化为 1 的情况，\(P_2\) 惩罚更大的视差跳变。最终聚合代价为所有方向的路径代价之和：

$$
S(p, d) = \sum_{\mathbf{r}} L_{\mathbf{r}}(p, d)
$$


### 基于深度学习的方法

近年来，深度学习方法在立体匹配精度上大幅超越传统算法。

| 方法 | 年份 | 核心思想 | KITTI 2015 D1-all |
|------|------|----------|-------------------|
| GC-Net | 2017 | 3D 卷积代价体 | 2.87% |
| PSMNet | 2018 | 空间金字塔池化 + 堆叠沙漏 | 2.32% |
| AANet | 2020 | 自适应聚合，无 3D 卷积 | 2.03% |
| RAFT-Stereo | 2021 | 迭代光流式更新 | 1.92% |
| CREStereo | 2022 | 级联循环优化 | 1.72% |
| UniMatch | 2023 | 统一光流/立体/深度框架 | 1.55% |

**RAFT-Stereo** 借鉴光流估计中 RAFT 的迭代更新思想，构建全对相关体（All-Pairs Correlation Volume），通过 GRU 单元迭代更新视差场。其优势在于内存效率高、推理速度快，并且可以灵活调整迭代次数以平衡精度与速度。


## 单目深度估计

### 监督学习方法

单目深度估计从单张 RGB 图像预测逐像素深度，本质上是一个病态问题（Ill-posed Problem），需要依赖场景先验知识。

**Eigen et al. (2014)** 首次使用深度神经网络进行单目深度估计，采用粗到细的多尺度架构。后续方法不断改进网络结构和损失函数设计。


### MiDaS 系列

MiDaS（Mixing Datasets for Monocular Depth Estimation）通过混合多个数据集训练，实现了出色的零样本泛化能力。其核心创新包括：

- **仿射不变损失**：由于不同数据集的深度标注尺度和偏移不一致，MiDaS 采用尺度和偏移不变的损失函数
- **多数据集训练策略**：同时使用室内外、合成与真实数据集进行训练
- **DPT 架构**：在 MiDaS v3 中引入 Dense Prediction Transformer（DPT），使用 Vision Transformer（ViT）作为骨干网络


### Depth Anything

Depth Anything（2024）是当前最先进的单目深度估计模型之一，其主要贡献：

1. **大规模无标签数据利用**：使用 6200 万张无标签图像进行自监督预训练
2. **知识蒸馏**：从教师模型（DINOv2）蒸馏到学生模型
3. **强数据增强**：对无标签数据施加强增强，迫使模型学习更鲁棒的特征

Depth Anything V2 进一步提升精度，采用合成数据训练、真实数据微调的两阶段策略，并提供多种模型尺寸（ViT-S/B/L/G）以适配不同计算预算。


## 主动深度传感器

### 结构光

结构光（Structured Light）传感器主动向场景投射已知光学图案（如条纹、散斑、编码图案），通过分析图案的变形来计算深度。

- **编码结构光**：投射时间编码或空间编码图案，精度高但需要多次拍摄
- **散斑结构光**：投射伪随机红外散斑图案（如 Intel RealSense D4xx 系列），可单帧获取深度
- **测量范围**：室内 0.2-10 m，受环境光干扰较大


### 飞行时间传感器

飞行时间（Time-of-Flight, ToF）传感器通过测量光脉冲的往返时间计算深度：

$$
Z = \frac{c \cdot \Delta t}{2}
$$

其中 \(c\) 为光速，\(\Delta t\) 为往返时间。ToF 传感器分为两类：

| 类型 | 原理 | 代表产品 | 分辨率 | 精度 |
|------|------|----------|--------|------|
| 直接 ToF（dToF） | 单光子计数 | Apple LiDAR | 低 | 高 |
| 间接 ToF（iToF） | 相位差测量 | Microsoft Azure Kinect | 中 | 中 |
| Flash LiDAR | 面阵照射 | Continental HFL110 | 中 | 高 |


## 深度补全

深度补全（Depth Completion）的目标是将稀疏深度图（如激光雷达点云投影）填充为稠密深度图，通常结合对应的 RGB 图像作为引导信号。

常见方法架构：

1. **早期融合**：将稀疏深度与 RGB 拼接为 4 通道输入
2. **晚期融合**：分别用两个编码器提取 RGB 和深度特征，在解码器阶段融合
3. **引导传播**：利用 RGB 图像的边缘信息引导深度值的空间传播

$$
D_{dense}(p) = \frac{\sum_{q \in \mathcal{N}(p)} w(p, q) \cdot D_{sparse}(q)}{\sum_{q \in \mathcal{N}(p)} w(p, q)}
$$

其中权重 \(w(p, q)\) 由 RGB 图像的相似度和空间距离共同决定。


## 实践：OpenCV 立体标定与深度图计算

以下代码演示使用 OpenCV 进行双目相机标定、图像校正和视差计算的完整流程。

### 双目标定

```python
import numpy as np
import cv2
import glob

# 棋盘格参数
CHECKERBOARD = (9, 6)  # 内角点数
square_size = 0.025     # 每格边长（米）

# 准备物体坐标（世界坐标系）
objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0],
                        0:CHECKERBOARD[1]].T.reshape(-1, 2) * square_size

obj_points = []   # 三维点
img_points_l = [] # 左图二维点
img_points_r = [] # 右图二维点

left_images = sorted(glob.glob("left/*.png"))
right_images = sorted(glob.glob("right/*.png"))

for left_path, right_path in zip(left_images, right_images):
    img_l = cv2.imread(left_path, cv2.IMREAD_GRAYSCALE)
    img_r = cv2.imread(right_path, cv2.IMREAD_GRAYSCALE)

    ret_l, corners_l = cv2.findChessboardCorners(img_l, CHECKERBOARD, None)
    ret_r, corners_r = cv2.findChessboardCorners(img_r, CHECKERBOARD, None)

    if ret_l and ret_r:
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
                    30, 0.001)
        corners_l = cv2.cornerSubPix(img_l, corners_l, (11, 11),
                                      (-1, -1), criteria)
        corners_r = cv2.cornerSubPix(img_r, corners_r, (11, 11),
                                      (-1, -1), criteria)
        obj_points.append(objp)
        img_points_l.append(corners_l)
        img_points_r.append(corners_r)

h, w = img_l.shape[:2]

# 单目标定
ret_l, K_l, dist_l, _, _ = cv2.calibrateCamera(
    obj_points, img_points_l, (w, h), None, None)
ret_r, K_r, dist_r, _, _ = cv2.calibrateCamera(
    obj_points, img_points_r, (w, h), None, None)

# 双目标定
flags = cv2.CALIB_FIX_INTRINSIC
ret, K_l, dist_l, K_r, dist_r, R, T, E, F = cv2.stereoCalibrate(
    obj_points, img_points_l, img_points_r,
    K_l, dist_l, K_r, dist_r, (w, h),
    flags=flags,
    criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-6)
)

print(f"立体标定重投影误差: {ret:.4f} 像素")
print(f"基线长度: {np.linalg.norm(T) * 1000:.1f} mm")
```


### 图像校正与视差计算

```python
# 立体校正
R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
    K_l, dist_l, K_r, dist_r, (w, h), R, T, alpha=0)

# 计算重映射矩阵
map1_l, map2_l = cv2.initUndistortRectifyMap(
    K_l, dist_l, R1, P1, (w, h), cv2.CV_16SC2)
map1_r, map2_r = cv2.initUndistortRectifyMap(
    K_r, dist_r, R2, P2, (w, h), cv2.CV_16SC2)

# 校正图像
img_left = cv2.imread("left/test.png", cv2.IMREAD_GRAYSCALE)
img_right = cv2.imread("right/test.png", cv2.IMREAD_GRAYSCALE)

rect_l = cv2.remap(img_left, map1_l, map2_l, cv2.INTER_LINEAR)
rect_r = cv2.remap(img_right, map1_r, map2_r, cv2.INTER_LINEAR)

# 使用 SGBM 计算视差图
num_disparities = 128  # 必须为 16 的倍数
block_size = 5

stereo = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=num_disparities,
    blockSize=block_size,
    P1=8 * block_size ** 2,
    P2=32 * block_size ** 2,
    disp12MaxDiff=1,
    uniquenessRatio=10,
    speckleWindowSize=100,
    speckleRange=32,
    mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY
)

disparity = stereo.compute(rect_l, rect_r).astype(np.float32) / 16.0

# 视差转深度
focal_length = P1[0, 0]       # 校正后焦距（像素）
baseline = abs(T[0, 0])       # 基线长度（米）

depth_map = np.zeros_like(disparity)
valid = disparity > 0
depth_map[valid] = (focal_length * baseline) / disparity[valid]

# 使用 Q 矩阵重投影为三维点云
points_3d = cv2.reprojectImageTo3D(disparity, Q)
mask = disparity > 0
output_points = points_3d[mask]
print(f"生成 {len(output_points)} 个三维点")
```


## 方法选择指南

| 场景 | 推荐方法 | 理由 |
|------|----------|------|
| 工业检测（高精度） | 编码结构光 | 亚毫米精度，可控环境 |
| 室内导航 | 双目相机 + SGM | 成本低，实时性好 |
| 室外自动驾驶 | 激光雷达 + 深度补全 | 远距离可靠，补全提升密度 |
| 移动端 AR | 单目深度估计 | 单相机即可，Depth Anything 泛化性强 |
| 机械臂抓取 | 结构光/ToF | 近距离高精度，不受纹理影响 |
| 大场景重建 | 多视角立体 (MVS) | 高分辨率稠密重建 |


## 参考资料

1. Hartley R, Zisserman A. *Multiple View Geometry in Computer Vision*. Cambridge University Press, 2003.
2. Hirschmuller H. Stereo processing by semiglobal matching and mutual information. *IEEE TPAMI*, 2008.
3. Lipson L, et al. RAFT-Stereo: Multilevel Recurrent Field Transforms for Stereo Matching. *3DV*, 2021.
4. Ranftl R, et al. Vision Transformers for Dense Prediction. *ICCV*, 2021.
5. Yang L, et al. Depth Anything: Unleashing the Power of Large-Scale Unlabeled Data. *CVPR*, 2024.
6. OpenCV 官方文档：Stereo Camera Calibration. https://docs.opencv.org/
