# 点云配准

!!! note "引言"
    点云配准（Point Cloud Registration）是将多个视角获取的点云数据对齐到统一坐标系的过程，是三维重建、同时定位与建图（Simultaneous Localization and Mapping, SLAM）、物体识别等任务的核心步骤。本文系统介绍迭代最近点（Iterative Closest Point, ICP）系列算法、基于特征的配准方法、全局配准策略以及近年来的深度学习方法，最后给出基于 Open3D 的完整配准流水线代码。


## 问题定义

给定源点云 \(\mathcal{P} = \{p_i\}\) 和目标点云 \(\mathcal{Q} = \{q_j\}\)，配准的目标是找到最优的刚体变换 \((\mathbf{R}, \mathbf{t})\)，使得变换后的源点云与目标点云尽可能对齐：

$$
\min_{\mathbf{R}, \mathbf{t}} \sum_{i} \rho\left(\| \mathbf{R} p_i + \mathbf{t} - q_{c(i)} \|\right)
$$

其中 \(c(i)\) 为 \(p_i\) 在目标点云中的对应点索引，\(\rho(\cdot)\) 为损失函数。根据是否需要初始位姿估计，配准方法分为**局部配准**（Local Registration）和**全局配准**（Global Registration）。


## 迭代最近点算法（ICP）

### 点到点 ICP

经典的点到点 ICP（Point-to-Point ICP）由 Besl 和 McKay 于 1992 年提出，交替执行以下两个步骤直至收敛：

1. **对应关系建立**：对源点云中每个点，在目标点云中找到最近邻点
2. **变换估计**：基于对应点对，求解最优刚体变换

最优变换的闭合解通过奇异值分解（Singular Value Decomposition, SVD）求得：

$$
\mathbf{H} = \sum_{i} (p_i - \bar{p})(q_{c(i)} - \bar{q})^T
$$

$$
\mathbf{H} = \mathbf{U} \mathbf{\Sigma} \mathbf{V}^T
$$

$$
\mathbf{R}^* = \mathbf{V} \mathbf{U}^T, \quad \mathbf{t}^* = \bar{q} - \mathbf{R}^* \bar{p}
$$

其中 \(\bar{p}\) 和 \(\bar{q}\) 分别为源点云和目标点云的质心。


### 点到面 ICP

点到面 ICP（Point-to-Plane ICP）由 Chen 和 Medioni 于 1992 年提出，将误差度量改为点到目标表面法线方向的距离：

$$
\min_{\mathbf{R}, \mathbf{t}} \sum_{i} \left[ (\mathbf{R} p_i + \mathbf{t} - q_{c(i)}) \cdot \mathbf{n}_{c(i)} \right]^2
$$

其中 \(\mathbf{n}_{c(i)}\) 为目标点 \(q_{c(i)}\) 处的法向量。点到面 ICP 收敛速度通常比点到点 ICP 快一个数量级，特别适合平面较多的场景。

| 变体 | 误差度量 | 收敛速度 | 适用场景 |
|------|----------|----------|----------|
| 点到点 | 欧氏距离 | 慢 | 通用 |
| 点到面 | 法线方向距离 | 快 | 平面场景 |
| 对称 ICP | 双向法线距离 | 快 | 曲面场景 |
| 带颜色 ICP | 几何 + 颜色差异 | 中 | RGB-D 数据 |


### 广义 ICP（GICP）

广义 ICP（Generalized ICP）由 Segal 等人于 2009 年提出，将点到点和点到面 ICP 统一在概率框架下。GICP 将每个点的局部表面建模为高斯分布：

$$
\min_{\mathbf{T}} \sum_{i} d_i^T (\mathbf{C}_i^{\mathcal{Q}} + \mathbf{T} \mathbf{C}_i^{\mathcal{P}} \mathbf{T}^T)^{-1} d_i
$$

其中 \(d_i = q_{c(i)} - \mathbf{T} p_i\) 为残差向量，\(\mathbf{C}_i^{\mathcal{P}}\) 和 \(\mathbf{C}_i^{\mathcal{Q}}\) 分别为源点和目标点的局部协方差矩阵。

GICP 的优势在于：

- 在平面区域自动退化为点到面 ICP
- 在特征丰富区域行为接近点到点 ICP
- 对噪声和异常值更加鲁棒


### 鲁棒核函数

实际数据中不可避免存在异常值（Outliers），标准 ICP 对异常值非常敏感。常用的鲁棒化策略包括：

- **截断距离**：丢弃对应距离超过阈值的点对
- **Huber 核函数**：\(\rho(r) = \begin{cases} r^2/2 & |r| \leq \delta \\ \delta(|r| - \delta/2) & |r| > \delta \end{cases}\)
- **Tukey 核函数**：当残差超过阈值时权重为零，完全忽略异常值
- **加权最小二乘**：根据对应质量分配权重


## 基于特征的配准

### 局部特征描述子

特征描述子将点云中每个关键点的局部几何结构编码为固定长度的向量，用于建立不同点云之间的对应关系。

**FPFH（Fast Point Feature Histograms）** 是最常用的手工设计描述子。对于关键点 \(p\) 及其邻域内每对点 \((p, p_k)\)，计算 Darboux 框架下的三个角度特征 \((\alpha, \phi, \theta)\)，然后构建简化的特征直方图（Simplified Point Feature Histogram, SPFH），最终通过邻域加权聚合得到 FPFH：

$$
FPFH(p) = SPFH(p) + \frac{1}{k} \sum_{i=1}^{k} \frac{1}{w_k} SPFH(p_k)
$$

其中 \(w_k\) 为 \(p\) 与 \(p_k\) 之间的距离权重。FPFH 描述子维度通常为 33 维。

**SHOT（Signatures of Histograms of Orientations）** 描述子将关键点的球形邻域划分为多个空间格子，在每个格子中计算法向量方向的直方图，拼接形成最终描述子。SHOT 同时编码了几何和拓扑信息，区分能力强。

| 描述子 | 维度 | 计算速度 | 区分能力 | 旋转不变 |
|--------|------|----------|----------|----------|
| PFH | 125 | 慢 | 高 | 是 |
| FPFH | 33 | 快 | 中 | 是 |
| SHOT | 352 | 中 | 高 | 是 |
| 3DSC | 1980 | 慢 | 高 | 否 |
| RoPS | 135 | 中 | 高 | 是 |


### 关键点检测

为减少计算量，通常先在点云中检测少量关键点，再计算描述子：

- **ISS（Intrinsic Shape Signatures）**：基于协方差矩阵特征值比的关键点检测
- **Harris 3D**：将 Harris 角点检测器扩展到三维，基于法向量变化率
- **体素下采样**：均匀采样，简单高效，常作为基线方法


## 全局配准

当两个点云之间没有初始位姿估计时，需要使用全局配准方法。

### 基于 RANSAC 的配准

随机采样一致性（Random Sample Consensus, RANSAC）配准的流程：

1. 从特征匹配中随机选取 3 组对应点
2. 基于这 3 组对应计算刚体变换
3. 将变换应用于源点云，统计内点（Inlier）数量
4. 重复多次迭代，保留内点数最多的变换

RANSAC 所需迭代次数 \(N\) 与内点比例 \(w\)、采样点数 \(n\) 和期望成功概率 \(p\) 的关系：

$$
N = \frac{\log(1-p)}{\log(1-w^n)}
$$


### 快速全局配准（FGR）

快速全局配准（Fast Global Registration, FGR）由 Zhou 等人于 2016 年提出，通过 Geman-McClure 鲁棒核函数和分阶段优化避免了 RANSAC 的随机采样过程，将全局配准问题转化为确定性的优化问题：

$$
\min_{\mathbf{T}} \sum_{(p,q) \in \mathcal{K}} \frac{\mu \| \mathbf{T} p - q \|^2}{\mu + \| \mathbf{T} p - q \|^2}
$$

其中 \(\mu\) 为退火参数，随优化过程逐步减小。FGR 通常比 RANSAC 快一到两个数量级。


## 基于深度学习的方法

### DCP（Deep Closest Point）

DCP 使用 DGCNN 提取点云特征，通过注意力机制建立软对应关系，最后用 SVD 层求解变换。其优势在于端到端可训练，且 SVD 层保证输出的变换矩阵具有正确的旋转矩阵结构。


### PointNetLK

PointNetLK 将 Lucas-Kanade 光流算法推广到三维，使用 PointNet 提取全局特征，通过迭代优化特征空间中的对齐误差来估计变换。该方法不需要显式的对应关系建立。


### 最新进展

| 方法 | 年份 | 特点 | 适用场景 |
|------|------|------|----------|
| DCP | 2019 | 注意力 + SVD | 物体级配准 |
| PRNet | 2019 | 迭代配准，部分重叠 | 部分可见 |
| RPM-Net | 2020 | 软对应 + 退火 | 噪声数据 |
| PREDATOR | 2021 | 重叠区域关注 | 低重叠率 |
| GeoTransformer | 2022 | 几何感知 Transformer | 大场景 |
| RoITr | 2023 | 旋转不变 Transformer | 任意旋转 |


## 配准流水线

一个完整的点云配准流水线通常包括以下步骤：

```
预处理 → 下采样 → 法向量估计 → 特征提取 → 全局配准 → 局部精细配准 → 后处理
```

### 预处理

- **去噪**：统计离群点移除（Statistical Outlier Removal, SOR）
- **下采样**：体素网格下采样（Voxel Downsampling），控制点云密度
- **法向量估计**：通过 PCA 拟合局部平面，计算法向量并统一朝向


## 实践：Open3D 配准流水线

以下代码使用 Open3D 实现从预处理到精细配准的完整流程。

```python
import open3d as o3d
import numpy as np
import copy


def preprocess_point_cloud(pcd, voxel_size):
    """预处理：下采样 + 法向量估计 + FPFH 特征计算"""
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 2
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(
            radius=radius_normal, max_nn=30))

    radius_feature = voxel_size * 5
    fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(
            radius=radius_feature, max_nn=100))

    return pcd_down, fpfh


def global_registration(source_down, target_down,
                        source_fpfh, target_fpfh, voxel_size):
    """基于 FPFH 特征的 RANSAC 全局配准"""
    distance_threshold = voxel_size * 1.5

    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down,
        source_fpfh, target_fpfh,
        mutual_filter=True,
        max_correspondence_distance=distance_threshold,
        estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        ransac_n=3,
        checkers=[
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(distance_threshold)
        ],
        criteria=o3d.pipelines.registration.RANSACConvergenceCriteria(
            max_iteration=100000, confidence=0.999))

    return result


def fast_global_registration(source_down, target_down,
                              source_fpfh, target_fpfh, voxel_size):
    """快速全局配准（FGR）"""
    distance_threshold = voxel_size * 0.5

    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_down, target_down,
        source_fpfh, target_fpfh,
        o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=distance_threshold))

    return result


def refine_registration(source, target, init_transform, voxel_size):
    """点到面 ICP 精细配准"""
    distance_threshold = voxel_size * 0.4

    result = o3d.pipelines.registration.registration_icp(
        source, target,
        distance_threshold, init_transform,
        o3d.pipelines.registration.TransformationEstimationPointToPlane(),
        o3d.pipelines.registration.ICPConvergenceCriteria(
            max_iteration=200))

    return result


def evaluate_registration(source, target, transformation, threshold):
    """评估配准质量"""
    evaluation = o3d.pipelines.registration.evaluate_registration(
        source, target, threshold, transformation)

    print(f"  适应度 (fitness): {evaluation.fitness:.4f}")
    print(f"  内点 RMSE: {evaluation.inlier_rmse:.6f}")
    print(f"  对应点数: {len(evaluation.correspondence_set)}")

    return evaluation


# ===== 主流程 =====
voxel_size = 0.05  # 体素大小（米）

# 加载点云
source = o3d.io.read_point_cloud("source.ply")
target = o3d.io.read_point_cloud("target.ply")

# 去除离群点
source, _ = source.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
target, _ = target.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)

# 预处理
source_down, source_fpfh = preprocess_point_cloud(source, voxel_size)
target_down, target_fpfh = preprocess_point_cloud(target, voxel_size)

print(f"源点云: {len(source.points)} 点 → 下采样: {len(source_down.points)} 点")
print(f"目标点云: {len(target.points)} 点 → 下采样: {len(target_down.points)} 点")

# 全局配准
print("\n=== 全局配准 (RANSAC) ===")
result_global = global_registration(
    source_down, target_down, source_fpfh, target_fpfh, voxel_size)
evaluate_registration(source_down, target_down,
                      result_global.transformation, voxel_size * 1.5)

# 精细配准
print("\n=== 精细配准 (ICP Point-to-Plane) ===")
source.estimate_normals(
    o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 2, max_nn=30))
target.estimate_normals(
    o3d.geometry.KDTreeSearchParamHybrid(radius=voxel_size * 2, max_nn=30))

result_icp = refine_registration(
    source, target, result_global.transformation, voxel_size)
evaluate_registration(source, target,
                      result_icp.transformation, voxel_size * 0.4)

# 应用变换并可视化
source_aligned = copy.deepcopy(source)
source_aligned.transform(result_icp.transformation)

source_aligned.paint_uniform_color([1, 0, 0])   # 红色：源点云
target.paint_uniform_color([0, 0, 1])            # 蓝色：目标点云
o3d.visualization.draw_geometries([source_aligned, target],
                                   window_name="配准结果")

print("\n最终变换矩阵:")
print(result_icp.transformation)
```


## 多帧配准与位姿图优化

当需要配准多帧点云时（如三维扫描），逐帧两两配准会导致累积误差（Drift）。位姿图优化（Pose Graph Optimization）通过在闭环约束下联合优化所有帧的位姿来消除漂移：

$$
\min_{\{T_i\}} \sum_{(i,j) \in \mathcal{E}} \| \log(T_{ij}^{-1} T_i^{-1} T_j) \|_{\Sigma_{ij}}^2
$$

其中 \(T_{ij}\) 为帧 \(i\) 到帧 \(j\) 的相对变换观测值，\(\Sigma_{ij}\) 为信息矩阵。Open3D 提供了 `registration_colored_icp` 和 `PoseGraph` 类来实现多帧配准和位姿图优化。


## 参考资料

1. Besl P J, McKay N D. A method for registration of 3-D shapes. *IEEE TPAMI*, 1992.
2. Chen Y, Medioni G. Object modelling by registration of multiple range images. *Image and Vision Computing*, 1992.
3. Segal A, Haehnel D, Thrun S. Generalized-ICP. *RSS*, 2009.
4. Rusu R B, Blodow N, Beetz M. Fast Point Feature Histograms (FPFH) for 3D registration. *ICRA*, 2009.
5. Zhou Q Y, Park J, Koltun V. Fast Global Registration. *ECCV*, 2016.
6. Wang Y, Solomon J M. Deep Closest Point. *ICCV*, 2019.
7. Qin Z, et al. Geometric Transformer for Fast and Robust Point Cloud Registration. *CVPR*, 2022.
8. Open3D 官方文档：Point Cloud Registration. http://www.open3d.org/docs/
