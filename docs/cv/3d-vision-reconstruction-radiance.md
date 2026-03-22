# 三维重建与辐射场

!!! note "引言"
    三维重建（3D Reconstruction）是从二维图像或传感器数据恢复场景三维结构的过程，是机器人环境感知、自主导航和数字孪生的重要基础。传统方法以运动恢复结构（Structure from Motion, SfM）和多视角立体（Multi-View Stereo, MVS）为代表，近年来神经辐射场（Neural Radiance Fields, NeRF）和三维高斯散射（3D Gaussian Splatting, 3DGS）开创了基于神经场景表示的新范式。本文系统介绍各类三维重建方法的原理与实践。


## 运动恢复结构（SfM）

### 基本原理

SfM 从一组无序的二维图像中同时恢复相机位姿和场景的稀疏三维结构。其核心流程包括：

1. **特征提取与匹配**：检测每幅图像中的特征点（如 SIFT、SuperPoint），并在图像对之间建立特征匹配
2. **几何验证**：使用基础矩阵 \(F\) 或本质矩阵 \(E\) 过滤错误匹配
3. **增量重建**：从一对图像开始，逐步添加新图像，通过 PnP（Perspective-n-Point）算法估计新相机位姿，并三角化新的三维点
4. **光束法平差**（Bundle Adjustment, BA）：联合优化所有相机参数和三维点坐标

光束法平差的优化目标为最小化重投影误差：

$$
\min_{\{R_i, t_i\}, \{X_j\}} \sum_{i,j} \| \pi(R_i X_j + t_i, K_i) - x_{ij} \|^2
$$

其中 \(\pi(\cdot)\) 为投影函数，\(x_{ij}\) 为三维点 \(X_j\) 在第 \(i\) 幅图像中的观测位置。


### COLMAP

COLMAP 是目前最流行的开源 SfM 和 MVS 系统，由 Johannes Schonberger 开发。其特点包括：

- **增量式 SfM**：自动选择初始图像对，鲁棒的增量重建策略
- **特征匹配**：支持穷举匹配、空间匹配、词汇树匹配等多种策略
- **稠密重建**：内置基于 PatchMatch 的 MVS 模块
- **网格重建**：支持 Poisson 表面重建和 Delaunay 三角化

```bash
# COLMAP 命令行使用示例
# 特征提取
colmap feature_extractor \
    --database_path database.db \
    --image_path images/ \
    --ImageReader.single_camera 1 \
    --ImageReader.camera_model PINHOLE

# 特征匹配
colmap exhaustive_matcher \
    --database_path database.db

# 增量式 SfM
colmap mapper \
    --database_path database.db \
    --image_path images/ \
    --output_path sparse/

# 稠密重建
colmap image_undistorter \
    --image_path images/ \
    --input_path sparse/0/ \
    --output_path dense/

colmap patch_match_stereo \
    --workspace_path dense/

colmap stereo_fusion \
    --workspace_path dense/ \
    --output_path dense/fused.ply
```


## 多视角立体（MVS）

### PatchMatch Stereo

PatchMatch MVS 是目前最成功的稠密重建算法之一。与传统立体匹配不同，PatchMatch 对每个像素估计一个带有深度和法向量的倾斜平面，通过随机初始化和空间传播高效搜索最优解。

算法流程：

1. **随机初始化**：为每个像素随机赋予深度值和法向量
2. **空间传播**：将邻域像素的深度假设传播到当前像素
3. **随机扰动**：在当前最优解附近进行随机搜索
4. **多视角一致性检验**：过滤不一致的深度估计

匹配代价通常采用归一化互相关（NCC）或光度一致性度量，考虑倾斜平面带来的单应变换：

$$
C(p, d, \mathbf{n}) = \sum_{i \in \mathcal{V}(p)} w_i \cdot (1 - \text{NCC}(I_{\text{ref}}, I_i \circ H_i(d, \mathbf{n})))
$$

其中 \(H_i(d, \mathbf{n})\) 为由深度 \(d\) 和法向量 \(\mathbf{n}\) 诱导的单应矩阵。


### 基于学习的 MVS

| 方法 | 年份 | 核心思想 | DTU 精度 (mm) |
|------|------|----------|---------------|
| MVSNet | 2018 | 3D 代价体 + 方差融合 | 0.396 |
| CasMVSNet | 2020 | 级联代价体 | 0.325 |
| PatchMatchNet | 2021 | 学习式 PatchMatch | 0.427 |
| TransMVSNet | 2022 | Transformer 特征增强 | 0.321 |
| UniMVSNet | 2022 | 统一焦点损失 | 0.352 |


## 神经辐射场（NeRF）

### 基本原理

NeRF 由 Mildenhall 等人于 2020 年提出，使用多层感知机（Multi-Layer Perceptron, MLP）隐式表示场景的颜色和密度场。对于空间中任意一点 \(\mathbf{x} = (x, y, z)\) 和观察方向 \(\mathbf{d} = (\theta, \phi)\)，NeRF 输出该点的颜色 \(\mathbf{c}\) 和体积密度 \(\sigma\)：

$$
F_\Theta: (\mathbf{x}, \mathbf{d}) \rightarrow (\mathbf{c}, \sigma)
$$

渲染时沿相机光线 \(\mathbf{r}(t) = \mathbf{o} + t\mathbf{d}\) 进行体积渲染积分：

$$
\hat{C}(\mathbf{r}) = \int_{t_n}^{t_f} T(t) \sigma(\mathbf{r}(t)) \mathbf{c}(\mathbf{r}(t), \mathbf{d}) \, dt
$$

其中透射率 \(T(t) = \exp\left(-\int_{t_n}^{t} \sigma(\mathbf{r}(s)) ds\right)\) 表示光线从 \(t_n\) 到 \(t\) 不被遮挡的概率。

在实际实现中，连续积分通过分层采样离散化：

$$
\hat{C}(\mathbf{r}) = \sum_{i=1}^{N} T_i \alpha_i \mathbf{c}_i, \quad T_i = \prod_{j=1}^{i-1}(1-\alpha_j), \quad \alpha_i = 1 - \exp(-\sigma_i \delta_i)
$$

其中 \(\delta_i = t_{i+1} - t_i\) 为相邻采样点间距。


### 位置编码

为使 MLP 能够表示高频细节，NeRF 对输入坐标施加**位置编码**（Positional Encoding）：

$$
\gamma(p) = \left(\sin(2^0 \pi p), \cos(2^0 \pi p), \ldots, \sin(2^{L-1} \pi p), \cos(2^{L-1} \pi p)\right)
$$

通常对空间坐标使用 \(L=10\)（60 维），对方向使用 \(L=4\)（24 维）。


### 主要变体

| 方法 | 年份 | 训练时间 | 核心改进 |
|------|------|----------|----------|
| 原始 NeRF | 2020 | ~1-2 天 | 开创性工作 |
| Mip-NeRF | 2021 | ~1 天 | 锥形采样，抗混叠 |
| Instant-NGP | 2022 | ~5 秒 | 多分辨率哈希编码 |
| Mip-NeRF 360 | 2022 | ~3 小时 | 无界场景，空间收缩 |
| Nerfacto | 2023 | ~15 分钟 | nerfstudio 集成多种技巧 |
| Zip-NeRF | 2023 | ~5 小时 | 结合 Instant-NGP 与 Mip-NeRF 360 |

**Instant-NGP** 的关键创新是**多分辨率哈希编码**（Multi-resolution Hash Encoding），用可训练的哈希表替代 MLP 的位置编码，将训练时间从数小时缩短至数秒，同时保持甚至超越原始 NeRF 的渲染质量。


## 三维高斯散射（3D Gaussian Splatting）

### 基本原理

3D Gaussian Splatting（3DGS）由 Kerbl 等人于 2023 年提出，使用显式的三维高斯椭球体集合表示场景，通过可微光栅化实现实时高质量渲染。

每个高斯基元由以下参数定义：

- **位置** \(\boldsymbol{\mu} \in \mathbb{R}^3\)：高斯中心
- **协方差** \(\boldsymbol{\Sigma} \in \mathbb{R}^{3\times3}\)：通过旋转四元数 \(\mathbf{q}\) 和缩放向量 \(\mathbf{s}\) 参数化，\(\boldsymbol{\Sigma} = \mathbf{R} \mathbf{S} \mathbf{S}^T \mathbf{R}^T\)
- **不透明度** \(\alpha \in [0,1]\)
- **颜色**：用球谐函数（Spherical Harmonics, SH）系数表示视角相关的颜色

渲染公式与 NeRF 的体积渲染类似，但基于排序后的高斯基元：

$$
C = \sum_{i \in \mathcal{N}} c_i \alpha_i' \prod_{j=1}^{i-1} (1 - \alpha_j')
$$

其中 \(\alpha_i'\) 为二维投影高斯与像素的重叠权重乘以不透明度。


### 与 NeRF 的比较

| 特性 | NeRF | 3D Gaussian Splatting |
|------|------|----------------------|
| 场景表示 | 隐式（MLP） | 显式（高斯基元） |
| 渲染方式 | 光线行进 | 光栅化 |
| 训练时间 | 分钟到小时 | 分钟级 |
| 渲染速度 | 慢（逐像素） | 实时（>100 FPS） |
| 编辑能力 | 困难 | 直接操作基元 |
| 存储空间 | 小（网络权重） | 大（百万级高斯） |
| 几何质量 | 中（密度场提取） | 需要后处理 |


### 最新进展

- **2D Gaussian Splatting (2DGS)**：使用二维高斯盘替代三维椭球，改善表面重建质量
- **SuGaR**：从 3DGS 中提取高质量网格
- **GaussianEditor**：基于文本指令编辑 3D 高斯场景
- **Dynamic 3D Gaussians**：扩展到动态场景建模
- **Scaffold-GS**：使用神经锚点高斯减少冗余


## 网格重建

从点云或隐式场中提取三角网格是三维重建的重要后处理步骤。

### Poisson 表面重建

Poisson 表面重建将带法向量的定向点云转换为三角网格。算法将表面重建问题转化为泊松方程的求解：

$$
\nabla^2 \chi = \nabla \cdot \mathbf{V}
$$

其中 \(\mathbf{V}\) 为由输入法向量定义的向量场，\(\chi\) 为指示函数，其等值面即为重建表面。


### Marching Cubes

Marching Cubes 算法用于从体积数据（如 NeRF 的密度场、TSDF）中提取等值面。算法遍历规则网格的每个立方体，根据顶点值与阈值的关系确定表面穿过方式，查表生成三角面片。


## 机器人应用

### 场景理解

三维重建为机器人提供结构化的环境表示，支持：

- **语义三维重建**：结合二维语义分割（如 SAM）与三维重建，生成语义标注的三维地图
- **物体级重建**：分离并重建场景中的单个物体，支持抓取规划
- **可通行性分析**：从重建的三维地图中提取地形信息，判断机器人可通行区域


### 数字孪生

将真实环境通过三维重建转化为数字孪生模型：

1. 使用 RGB-D 相机或激光雷达扫描环境
2. 通过 SfM + MVS 或 3DGS 生成高保真三维模型
3. 导入仿真器（如 NVIDIA Isaac Sim）进行策略训练和验证

```bash
# 使用 nerfstudio 训练 NeRF 模型
# 安装 nerfstudio
pip install nerfstudio

# 处理数据（从图像目录自动运行 COLMAP）
ns-process-data images --data images/ --output-dir processed/

# 训练 nerfacto 模型
ns-train nerfacto --data processed/

# 导出点云用于下游任务
ns-export pointcloud \
    --load-config outputs/unnamed/nerfacto/config.yml \
    --output-dir exports/ \
    --num-points 1000000
```

```python
# 使用 Open3D 进行 Poisson 表面重建
import open3d as o3d
import numpy as np

# 加载带法向量的点云
pcd = o3d.io.read_point_cloud("dense_pointcloud.ply")

# 估计法向量（如尚未包含）
pcd.estimate_normals(
    search_param=o3d.geometry.KDTreeSearchParamHybrid(
        radius=0.1, max_nn=30))
pcd.orient_normals_consistent_tangent_plane(k=15)

# Poisson 表面重建
mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
    pcd, depth=9, width=0, scale=1.1, linear_fit=False)

# 根据密度过滤低置信度区域
densities = np.asarray(densities)
density_threshold = np.quantile(densities, 0.01)
vertices_to_remove = densities < density_threshold
mesh.remove_vertices_by_mask(vertices_to_remove)

# 简化网格
mesh_simplified = mesh.simplify_quadric_decimation(
    target_number_of_triangles=100000)

print(f"顶点数: {len(mesh_simplified.vertices)}")
print(f"三角面数: {len(mesh_simplified.triangles)}")

# 保存网格
o3d.io.write_triangle_mesh("reconstructed_mesh.ply", mesh_simplified)
```


## 参考资料

1. Schonberger J L, Frahm J M. Structure-from-Motion Revisited. *CVPR*, 2016.
2. Schonberger J L, et al. Pixelwise View Selection for Unstructured Multi-View Stereo. *ECCV*, 2016.
3. Mildenhall B, et al. NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis. *ECCV*, 2020.
4. Muller T, et al. Instant Neural Graphics Primitives with a Multiresolution Hash Encoding. *SIGGRAPH*, 2022.
5. Kerbl B, et al. 3D Gaussian Splatting for Real-Time Radiance Field Rendering. *SIGGRAPH*, 2023.
6. COLMAP 官方文档. https://colmap.github.io/
7. nerfstudio 官方文档. https://docs.nerf.studio/
8. Tancik M, et al. Nerfstudio: A Modular Framework for Neural Radiance Field Development. *SIGGRAPH*, 2023.
