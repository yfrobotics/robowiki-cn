# 三维视觉参考资料

!!! note "引言"
    本页面汇集三维视觉领域的核心论文、教材、开源工具、数据集和常用公式，为学习和研究三维视觉提供系统化的参考索引。内容涵盖立体视觉、点云处理、三维重建和神经辐射场等方向，适合作为日常查阅的快速参考手册。


## 经典论文

### 立体视觉与深度估计

| 论文 | 作者 | 年份 | 会议/期刊 | 核心贡献 |
|------|------|------|-----------|----------|
| A Taxonomy and Evaluation of Dense Two-Frame Stereo | Scharstein & Szeliski | 2002 | IJCV | 立体匹配方法综述与基准 |
| Stereo Processing by SGM and Mutual Information | Hirschmuller | 2005/2008 | CVPR/TPAMI | 半全局匹配算法 |
| GC-Net | Kendall et al. | 2017 | ICCV | 首个端到端深度学习立体匹配 |
| RAFT-Stereo | Lipson et al. | 2021 | 3DV | 迭代更新立体匹配 |
| Depth Anything | Yang et al. | 2024 | CVPR | 大规模单目深度估计基础模型 |


### 点云处理与配准

| 论文 | 作者 | 年份 | 会议/期刊 | 核心贡献 |
|------|------|------|-----------|----------|
| A Method for Registration of 3-D Shapes | Besl & McKay | 1992 | TPAMI | 迭代最近点算法（ICP） |
| PointNet | Qi et al. | 2017 | CVPR | 直接处理点云的深度网络 |
| PointNet++ | Qi et al. | 2017 | NeurIPS | 层次化点云学习 |
| FPFH | Rusu et al. | 2009 | ICRA | 快速点特征直方图描述子 |
| Fast Global Registration | Zhou et al. | 2016 | ECCV | 无需初始化的快速全局配准 |
| GeoTransformer | Qin et al. | 2022 | CVPR | 几何感知 Transformer 配准 |


### 三维重建

| 论文 | 作者 | 年份 | 会议/期刊 | 核心贡献 |
|------|------|------|-----------|----------|
| SfM Revisited | Schonberger & Frahm | 2016 | CVPR | COLMAP 增量式 SfM |
| MVSNet | Yao et al. | 2018 | ECCV | 深度学习多视角立体 |
| NeRF | Mildenhall et al. | 2020 | ECCV | 神经辐射场 |
| Instant-NGP | Muller et al. | 2022 | SIGGRAPH | 多分辨率哈希编码加速 NeRF |
| 3D Gaussian Splatting | Kerbl et al. | 2023 | SIGGRAPH | 实时辐射场渲染 |
| 2D Gaussian Splatting | Huang et al. | 2024 | SIGGRAPH | 二维高斯改善表面重建 |


## 教材与专著

### 基础教材

| 书名 | 作者 | 出版社 | 说明 |
|------|------|--------|------|
| *Multiple View Geometry in Computer Vision* | Hartley & Zisserman | Cambridge | 多视图几何经典教材，涵盖对极几何、三维重建理论 |
| *Computer Vision: Algorithms and Applications* | Szeliski | Springer | 计算机视觉全面教材，免费在线版本 |
| *An Invitation to 3D Vision* | Ma et al. | Springer | 三维视觉入门，涵盖射影几何到运动恢复结构 |
| *Robotics, Vision and Control* | Corke | Springer | 机器人视觉实践导向教材 |
| *State Estimation for Robotics* | Barfoot | Cambridge | 机器人状态估计，包括视觉里程计相关理论 |


### 进阶参考

| 书名 | 作者 | 说明 |
|------|------|------|
| *Three-Dimensional Computer Vision* | Faugeras | 三维计算机视觉理论基础 |
| *Numerical Optimization* | Nocedal & Wright | 优化理论，光束法平差必备基础 |
| *视觉SLAM十四讲：从理论到实践* | 高翔 | 中文 SLAM 入门教材，含丰富代码示例 |
| *Probabilistic Robotics* | Thrun et al. | 概率机器人学，SLAM 理论基础 |


## 开源工具

### 通用三维视觉库

| 工具 | 语言 | 许可证 | 主要功能 |
|------|------|--------|----------|
| [Open3D](http://www.open3d.org/) | C++/Python | MIT | 点云处理、配准、重建、可视化 |
| [PCL](https://pointclouds.org/) | C++ | BSD | 点云滤波、分割、配准、特征提取 |
| [OpenCV](https://opencv.org/) | C++/Python | Apache 2.0 | 立体标定、视差计算、三维重投影 |
| [PyTorch3D](https://pytorch3d.org/) | Python | BSD | 可微渲染、点云/网格操作 |
| [Kaolin](https://github.com/NVIDIAGameWorks/kaolin) | Python | Apache 2.0 | NVIDIA 三维深度学习库 |


### 三维重建系统

| 工具 | 功能 | 输入 | 输出 |
|------|------|------|------|
| [COLMAP](https://colmap.github.io/) | SfM + MVS | 图像集合 | 稀疏/稠密点云、网格 |
| [OpenMVS](https://github.com/cdcseacave/openMVS) | MVS + 网格重建 | COLMAP 稀疏重建 | 稠密点云、纹理网格 |
| [Meshroom](https://alicevision.org/) | 照片建模（GUI） | 图像集合 | 纹理网格模型 |
| [nerfstudio](https://docs.nerf.studio/) | NeRF 训练框架 | 图像 + 位姿 | 辐射场模型、点云导出 |
| [gsplat](https://github.com/nerfstudio-project/gsplat) | 3DGS 渲染核心 | 高斯参数 | 渲染图像 |
| [SuGaR](https://github.com/Anttwo/SuGaR) | 3DGS 转网格 | 3DGS 模型 | 三角网格 |


### 点云标注与可视化

| 工具 | 用途 | 特点 |
|------|------|------|
| [CloudCompare](https://www.cloudcompare.org/) | 点云可视化与编辑 | 支持大规模点云，丰富的处理插件 |
| [MeshLab](https://www.meshlab.net/) | 网格处理与可视化 | 网格修复、简化、纹理映射 |
| [Rerun](https://www.rerun.io/) | 多模态数据可视化 | 支持点云、图像、时序数据的实时可视化 |
| [3D Slicer](https://www.slicer.org/) | 医学三维可视化 | 体数据分割与三维重建 |


## 数据集

### 自动驾驶

| 数据集 | 规模 | 传感器 | 标注 | 链接 |
|--------|------|--------|------|------|
| KITTI | 389 对立体图像 | 双目相机 + LiDAR | 视差、光流、位姿 | [cvlibs.net](http://www.cvlibs.net/datasets/kitti/) |
| nuScenes | 1000 场景 | 6 相机 + LiDAR + RADAR | 三维框、语义 | [nuscenes.org](https://www.nuscenes.org/) |
| Waymo Open | 1150 场景 | 5 相机 + 5 LiDAR | 三维框、分割 | [waymo.com/open](https://waymo.com/open/) |
| Argoverse 2 | 1000 场景 | 7 相机 + 2 LiDAR | 三维框、地图 | [argoverse.org](https://www.argoverse.org/) |


### 室内场景

| 数据集 | 规模 | 传感器 | 标注 | 链接 |
|--------|------|--------|------|------|
| ScanNet | 1513 场景 | RGB-D | 三维语义分割、实例 | [scan-net.org](http://www.scan-net.org/) |
| ScanNet++ | 460 场景 | 高分辨率 RGB-D + DSLR | 语义、实例、法向量 | [scannetpp](https://kaldir.vc.in.tum.de/scannetpp/) |
| Matterport3D | 90 栋建筑 | 全景 RGB-D | 语义、实例、布局 | [matterport3d](https://niessner.github.io/Matterport/) |
| NYU Depth V2 | 1449 帧 | Kinect RGB-D | 深度、语义分割 | [nyu](https://cs.nyu.edu/~silberman/datasets/) |
| Replica | 18 个房间 | 合成数据 | 稠密深度、语义 | [replica](https://github.com/facebookresearch/Replica-Dataset) |


### 物体与形状

| 数据集 | 规模 | 类型 | 用途 |
|--------|------|------|------|
| ShapeNet | 51,300 模型 | CAD 模型 | 形状生成、补全、分类 |
| ModelNet | 12,311 模型 | CAD 模型 | 三维形状分类 |
| CO3D | 19,000 视频 | 多视角视频 | 物体重建、新视角合成 |
| Objaverse | 800K+ 模型 | 三维模型 | 大规模三维预训练 |


### 配准基准

| 数据集 | 场景类型 | 配准难度 | 说明 |
|--------|----------|----------|------|
| 3DMatch | 室内 | 中 | 62 场景，点云配准标准基准 |
| 3DLoMatch | 室内 | 高 | 低重叠率（10-30%）配准 |
| KITTI Odometry | 室外 | 中 | LiDAR 里程计与配准 |
| ETH | 室外 | 高 | 大规模室外点云配准 |


## 基准排行榜

主要基准评测网站：

- **KITTI Stereo/Flow/Depth**: http://www.cvlibs.net/datasets/kitti/eval_stereo.php
- **ETH3D Benchmark**: https://www.eth3d.net/
- **DTU MVS Benchmark**: https://roboimagedata.compute.dtu.dk/
- **Tanks and Temples**: https://www.tanksandtemples.org/
- **ScanNet Benchmark**: http://kaldir.vc.in.tum.de/scannet_benchmark/
- **3DMatch Benchmark**: https://3dmatch.cs.princeton.edu/


## 公式快速参考

### 相机模型

**针孔相机模型**：将三维点 \(\mathbf{X} = [X, Y, Z]^T\) 投影到图像平面 \(\mathbf{x} = [u, v]^T\)：

$$
\begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = \frac{1}{Z} \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} X \\ Y \\ Z \end{bmatrix} = \frac{1}{Z} \mathbf{K} \mathbf{X}
$$

其中 \(f_x, f_y\) 为焦距（像素），\((c_x, c_y)\) 为主点坐标。

**带畸变模型**（径向畸变 + 切向畸变）：

$$
\begin{aligned}
x_d &= x(1 + k_1 r^2 + k_2 r^4 + k_3 r^6) + 2p_1 xy + p_2(r^2 + 2x^2) \\
y_d &= y(1 + k_1 r^2 + k_2 r^4 + k_3 r^6) + p_1(r^2 + 2y^2) + 2p_2 xy
\end{aligned}
$$

其中 \(r^2 = x^2 + y^2\)，\(k_1, k_2, k_3\) 为径向畸变系数，\(p_1, p_2\) 为切向畸变系数。


### 对极几何

**基础矩阵**（Fundamental Matrix）\(\mathbf{F}\)：

$$
\mathbf{x}_2^T \mathbf{F} \mathbf{x}_1 = 0
$$

- 秩为 2，包含 7 个自由度
- 由至少 8 对匹配点（8 点法）或 7 对匹配点（7 点法）估计

**本质矩阵**（Essential Matrix）\(\mathbf{E}\)：

$$
\mathbf{E} = \mathbf{K}_2^T \mathbf{F} \mathbf{K}_1 = [\mathbf{t}]_\times \mathbf{R}
$$

- 包含 5 个自由度（3 旋转 + 2 平移方向）
- 由至少 5 对匹配点估计（5 点法）

**单应矩阵**（Homography）\(\mathbf{H}\)：

$$
\mathbf{x}_2 \sim \mathbf{H} \mathbf{x}_1, \quad \mathbf{H} = \mathbf{K}_2 (\mathbf{R} - \frac{\mathbf{t} \mathbf{n}^T}{d}) \mathbf{K}_1^{-1}
$$

适用于平面场景或纯旋转运动，包含 8 个自由度。


### 三角化

给定两个相机的投影矩阵 \(\mathbf{P}_1, \mathbf{P}_2\) 和对应点 \(\mathbf{x}_1, \mathbf{x}_2\)，三维点 \(\mathbf{X}\) 通过求解齐次线性方程组获得：

$$
\begin{bmatrix} x_1 \mathbf{p}_1^{3T} - \mathbf{p}_1^{1T} \\ y_1 \mathbf{p}_1^{3T} - \mathbf{p}_1^{2T} \\ x_2 \mathbf{p}_2^{3T} - \mathbf{p}_2^{1T} \\ y_2 \mathbf{p}_2^{3T} - \mathbf{p}_2^{2T} \end{bmatrix} \mathbf{X} = \mathbf{0}
$$

其中 \(\mathbf{p}_i^{kT}\) 为投影矩阵 \(\mathbf{P}_i\) 的第 \(k\) 行。使用 SVD 求最小二乘解。


### 视差与深度

校正后双目相机的深度计算：

$$
Z = \frac{f \cdot b}{d}, \quad \text{深度误差} \quad \Delta Z = \frac{Z^2}{f \cdot b} \Delta d
$$

其中 \(f\) 为焦距（像素），\(b\) 为基线长度（米），\(d\) 为视差（像素），\(\Delta d\) 为视差测量误差。


### 刚体变换

**旋转表示**：

| 表示 | 参数数 | 优点 | 缺点 |
|------|--------|------|------|
| 旋转矩阵 \(\mathbf{R}\) | 9 (约束后 3) | 直接用于变换 | 冗余参数，需正交约束 |
| 四元数 \(\mathbf{q}\) | 4 (约束后 3) | 插值方便，无万向锁 | 双覆盖 |
| 轴角 \(\theta \hat{e}\) | 3 | 最小参数化 | 奇异性（\(\theta = 0\)） |
| 欧拉角 \((\phi, \theta, \psi)\) | 3 | 直观 | 万向锁问题 |

**罗德里格斯公式**（轴角转旋转矩阵）：

$$
\mathbf{R} = \cos\theta \, \mathbf{I} + (1-\cos\theta) \, \hat{e}\hat{e}^T + \sin\theta \, [\hat{e}]_\times
$$


### 体积渲染

NeRF 的体积渲染积分：

$$
C(\mathbf{r}) = \int_{t_n}^{t_f} T(t) \sigma(\mathbf{r}(t)) \mathbf{c}(\mathbf{r}(t), \mathbf{d}) \, dt, \quad T(t) = \exp\left(-\int_{t_n}^{t} \sigma(\mathbf{r}(s)) \, ds\right)
$$

离散化近似：

$$
\hat{C} = \sum_{i=1}^{N} T_i (1 - e^{-\sigma_i \delta_i}) \mathbf{c}_i, \quad T_i = \prod_{j=1}^{i-1} e^{-\sigma_j \delta_j}
$$


## 参考资料

1. Hartley R, Zisserman A. *Multiple View Geometry in Computer Vision*. 2nd Edition, Cambridge University Press, 2003.
2. Szeliski R. *Computer Vision: Algorithms and Applications*. 2nd Edition, Springer, 2022.
3. 高翔, 张涛 等. *视觉SLAM十四讲：从理论到实践*. 电子工业出版社, 2017.
4. Open3D 官方文档. http://www.open3d.org/docs/
5. COLMAP 官方文档. https://colmap.github.io/
6. nerfstudio 官方文档. https://docs.nerf.studio/
7. Awesome 3D Gaussian Splatting. https://github.com/MrNeRF/awesome-3D-gaussian-splatting
