# 机器学习

!!! note "引言"
    机器学习 (Machine Learning) 是人工智能的核心分支，研究如何让计算机从数据中自动学习规律并做出预测或决策。本页面介绍机器学习的基本概念、主要算法类别以及在机器人领域中的应用。

机器学习 (Machine Learning) 研究的主题是如何让计算机具备与人类同等的思考和分析能力。机器学习主要基于认知学、计算机科学，统计概率学以及信息决策学。典型的机器学习应用包括照片分类、垃圾邮件识别、自然语言处理等。最近很火热的围棋人工智能AlphaGo就是采用了深度神经网络对大量棋局进行学习，从而具备了顶尖围棋选手的水平。

机器学习的应用领域有：

- 经济学模型建立
- 图像处理和机器视觉
- 生物DNA解码
- 能源负载、使用、价格预测
- 汽车、航空和制造
- 自然语言处理
- ……


## 学习范式

Machine Learning从其采用的学习方式来说有以下三大类：

- **监督学习 (Supervised Learning)**：用于训练的数据包含已知结果（回归与分类问题）。
- **无监督学习 (Unsupervised Learning)**：用于训练的数据不包含已知结果（聚类问题）。
- **强化学习 (Reinforcement Learning)**：用于训练的数据不包含已知结果，但是可以用奖励函数 (Reward Function) 对其进行评价。

此外，还有一些介于上述范式之间的学习方式：

- **半监督学习 (Semi-supervised Learning)**：仅部分数据带有标签，结合有标签和无标签数据共同训练
- **自监督学习 (Self-supervised Learning)**：从数据自身结构中生成监督信号，无需人工标注
- **迁移学习 (Transfer Learning)**：将在一个任务上学到的知识迁移到新任务，减少对新数据的依赖


## 监督学习 (Supervised Learning)

监督学习从带有标签的训练数据中学习映射函数 \(f: X \rightarrow Y\)，其中 \(X\) 是输入特征，\(Y\) 是输出标签。根据输出类型的不同，监督学习分为回归 (Regression) 和分类 (Classification) 两大类。

### 线性回归 (Linear Regression)

线性回归是最基础的回归算法，假设输入与输出之间存在线性关系：

$$
y = w^T x + b
$$

通过最小化均方误差 (Mean Squared Error, MSE) 来拟合参数：

$$
\min_{w, b} \frac{1}{N} \sum_{i=1}^{N} (y_i - w^T x_i - b)^2
$$

线性回归虽然简单，但在许多实际问题中仍然有效，且具有良好的可解释性。

### 逻辑回归 (Logistic Regression)

尽管名字中包含"回归"，逻辑回归实际上是一种分类算法。它使用 Sigmoid 函数将线性组合映射到 \([0, 1]\) 区间，表示属于某一类的概率：

$$
P(y=1|x) = \sigma(w^T x + b) = \frac{1}{1 + e^{-(w^T x + b)}}
$$

### 支持向量机 (Support Vector Machine, SVM)

SVM 的核心思想是在特征空间中找到一个最大间隔超平面 (Maximum Margin Hyperplane) 来分隔不同类别的数据。对于非线性问题，SVM 通过核函数 (Kernel Function) 将数据映射到高维空间，使其线性可分。

常用的核函数有：

- 线性核 (Linear Kernel)：\(K(x_i, x_j) = x_i^T x_j\)
- 径向基核 (RBF Kernel)：\(K(x_i, x_j) = \exp(-\gamma \|x_i - x_j\|^2)\)
- 多项式核 (Polynomial Kernel)：\(K(x_i, x_j) = (x_i^T x_j + c)^d\)

### 决策树 (Decision Tree)

决策树通过递归地将数据按特征值进行分裂，构建一棵树形结构。每个内部节点表示一个特征上的判断条件，叶节点表示预测结果。分裂准则通常基于信息增益 (Information Gain) 或基尼不纯度 (Gini Impurity)。

### 随机森林 (Random Forest)

随机森林是一种集成学习 (Ensemble Learning) 方法，通过训练多棵决策树并取其投票结果（分类）或平均值（回归）来提高预测精度和鲁棒性。它引入了两个随机化机制：

- **样本随机化**：每棵树使用自助采样 (Bootstrap Sampling) 得到的子集训练
- **特征随机化**：每次分裂时只考虑随机选取的特征子集

### 神经网络 (Neural Network)

人工神经网络 (Artificial Neural Network, ANN) 由多层互联的神经元组成。每个神经元执行加权求和并通过激活函数 (Activation Function) 进行非线性变换：

$$
a = \sigma(W x + b)
$$

常用的激活函数有 ReLU (\(\max(0, x)\))、Sigmoid、Tanh 等。通过反向传播算法 (Backpropagation) 和梯度下降 (Gradient Descent) 更新网络参数。


## 无监督学习 (Unsupervised Learning)

无监督学习从不带标签的数据中发现隐藏的结构和模式。

### K均值聚类 (K-Means Clustering)

K-Means 将 \(N\) 个数据点划分为 \(K\) 个簇，使得每个数据点属于距其最近的簇中心所代表的簇。算法通过交替执行以下两步迭代收敛：

1. **分配步骤**：将每个数据点分配到最近的簇中心
2. **更新步骤**：重新计算每个簇的中心为其成员的均值

目标函数为最小化簇内平方和 (Within-Cluster Sum of Squares)：

$$
\min \sum_{k=1}^{K} \sum_{x_i \in C_k} \|x_i - \mu_k\|^2
$$

### 主成分分析 (Principal Component Analysis, PCA)

PCA 是一种降维 (Dimensionality Reduction) 方法，通过找到数据方差最大的方向（主成分），将高维数据投影到低维空间，同时尽可能保留原始数据的信息。PCA 在传感器数据预处理和特征压缩中广泛应用。

### 自编码器 (Autoencoder)

自编码器是一种无监督的神经网络，通过编码器 (Encoder) 将输入压缩为低维表示（潜在空间），再通过解码器 (Decoder) 重建原始输入。其变种包括变分自编码器 (Variational Autoencoder, VAE)，可用于数据生成和异常检测。


## 深度学习基础 (Deep Learning)

深度学习 (Deep Learning) 是机器学习的一个子领域，使用多层神经网络从原始数据中自动学习多层次的特征表示。

### 卷积神经网络 (Convolutional Neural Network, CNN)

CNN 专门用于处理具有网格结构的数据（如图像）。其核心操作是卷积 (Convolution)，通过可学习的卷积核提取局部特征：

- **卷积层 (Convolutional Layer)**：提取局部特征
- **池化层 (Pooling Layer)**：降低空间维度，增强平移不变性
- **全连接层 (Fully Connected Layer)**：进行最终的分类或回归

经典网络结构有 LeNet、AlexNet、VGG、ResNet、EfficientNet 等。CNN 在机器人视觉感知中应用广泛。

### 循环神经网络 (Recurrent Neural Network, RNN)

RNN 适用于处理序列数据（如时间序列、文本）。其隐藏状态能够保存历史信息：

$$
h_t = \sigma(W_h h_{t-1} + W_x x_t + b)
$$

标准 RNN 存在梯度消失/爆炸问题，改进的变种有长短期记忆网络 (Long Short-Term Memory, LSTM) 和门控循环单元 (Gated Recurrent Unit, GRU)。在机器人中，RNN 可用于轨迹预测和时间序列传感器数据处理。

### Transformer

Transformer 基于自注意力机制 (Self-Attention Mechanism)，能够并行处理序列中所有位置的信息，解决了 RNN 在长序列上的计算效率问题。其核心是缩放点积注意力 (Scaled Dot-Product Attention)：

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

Transformer 最初用于自然语言处理（如 BERT、GPT 系列），现已扩展到视觉领域（Vision Transformer, ViT）和机器人决策领域。


## 机器学习在机器人中的应用

机器学习为机器人的多个子系统提供了强大的工具：

| 应用领域 | 典型方法 | 具体应用 |
|---------|---------|---------|
| 感知 (Perception) | CNN、PointNet | 物体检测、语义分割、点云分类 |
| 定位 (Localization) | CNN、RNN | 视觉里程计、位姿估计 |
| 规划 (Planning) | 强化学习、模仿学习 | 运动规划、任务规划 |
| 控制 (Control) | 强化学习、神经网络 | 自适应控制、灵巧操作 |
| 人机交互 (HRI) | RNN、Transformer | 语音识别、手势识别、意图理解 |
| 预测 (Prediction) | LSTM、Transformer | 行人轨迹预测、故障预测 |


## 常用框架

| 框架 | 语言 | 特点 |
|------|------|------|
| scikit-learn | Python | 传统机器学习算法集合，适合快速原型开发 |
| PyTorch | Python/C++ | 动态计算图，学术研究首选 |
| TensorFlow / Keras | Python/C++ | 静态图优化，工业部署友好 |
| XGBoost / LightGBM | Python/C++ | 高性能梯度提升 (Gradient Boosting) 库 |
| JAX | Python | Google 推出的高性能数值计算库，支持自动微分和 JIT 编译 |


## 参考资料

1. 戴晓天，[机器学习 | 机器学习101](https://www.yfworld.com/?p=3378)，云飞机器人实验室
2. Bishop, C. M. (2006). *Pattern Recognition and Machine Learning*. Springer.
3. Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep Learning*. MIT Press. [在线版本](https://www.deeplearningbook.org/)
4. Murphy, K. P. (2022). *Probabilistic Machine Learning: An Introduction*. MIT Press. [在线版本](https://probml.github.io/pml-book/book1.html)
5. Vaswani, A., et al. (2017). Attention is all you need. *Advances in Neural Information Processing Systems*, 30.
