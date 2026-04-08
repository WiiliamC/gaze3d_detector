# 算法文档与代码实现差异分析

**文档目的**：记录 Swirski 2013 (algo_13.md) 和 Dierkes 2019 (algo_19.md) 算法设计与实际代码实现的差异，为后续优化提供参考。

---

## 1 算法概述对照

### 1.1 Swirski 2013 (algo_13.md) 核心流程
```
瞳孔椭圆检测 → 双圆反投影(2D→3D) → 球面瞳孔模型初始化 → 模型参数优化 → 输出视线+重投影椭圆
```

### 1.2 Dierkes 2019 (algo_19.md) 核心流程
```
瞳孔轮廓提取 → 椭圆拟合 → 椭圆反投影 → 眼球中心最小二乘估计 → 折射校正 → 时间融合 → 输出
```

### 1.3 代码库实现
```
瞳孔数据输入 → Observation构建(椭圆反投影+歧义消除) → 双球模型拟合(球心估计) → search_on_sphere精化 → 折射校正(多项式) → Kalman滤波 → 输出
```

---

## 2 关键差异汇总

### 2.1 模型优化方法差异 (algo_13 vs 代码)

| 方面 | algo_13.md 描述 | 代码库实现 |
|------|----------------|-----------|
| **优化策略1** | BFGS梯度上升，最大化区域对比度 | **未实现** |
| **优化策略2** | Levenberg-Marquardt边缘距离最小化 (Ceres Solver) | **未实现** |
| **替代方案** | - | search_on_sphere 网格搜索 |
| **参数优化** | 迭代优化球心+瞳孔球面角 | Dierkes线最小二乘闭式解 |

### 2.2 折射校正差异 (algo_19 vs 代码)

| 方面 | algo_19.md 描述 | 代码库实现 |
|------|----------------|-----------|
| **多项式阶数** | **5次多元多项式** | **3次多项式** (degree=3) |
| **训练数据** | 基于斯涅尔定律的合成眼图像 | 预训练.msgpack模型 |
| **模型文件** | 无 (在线训练) | 有 (refraction_models/*.msgpack) |

### 2.3 眼模型物理参数差异 (algo_19 vs 代码)

| 参数 | algo_19.md 数值 | 代码库数值 |
|------|----------------|-----------|
| **角膜半径 rc** | 6.0 mm | 未单独建模 |
| **眼球半径 re** | 7.8 mm | 未单独建模 |
| **虹膜半径 rs** | 12 mm | 未建模 |
| **眼球-瞳孔距离 R** | √(re²-rs²) ≈ 10.39 mm | `_EYE_RADIUS_DEFAULT = 10.3923 mm` |
| **角膜折射率 nref** | 1.3375 | 未使用 |

### 2.4 时间融合策略差异

| 方面 | algo_19.md 描述 | 代码库实现 |
|------|----------------|-----------|
| **融合方法** | 随机采样N帧，重复1000次蒙特卡洛，取均值 | BinBufferedObservationStorage + Kalman滤波 |
| **N值要求** | N≥10帧 | 置信度阈值过滤 |
| **误差规律** | 误差 ∝ 1/√N | - |

---

## 3 实现一致性良好的部分

### 3.1 Safaee-Rad 椭圆反投影 ✓
- 使用 `unproject_conicoid.h` 实现
- 基于论文 "Three-Dimensional Location Estimation of Circular Features" (1992)
- 输入：2D椭圆参数 → 输出：两个3D圆（存在歧义）

### 3.2 Dierkes线构建 ✓
- 定义：`origin = circle_center - R * normal`, `direction = circle_center`
- 代码位置：`observation.py:58-64`
- 与论文一致

### 3.3 歧义消除判据 ✓
- 论文公式：⟨T(n_i,k), E - T(p_i,k)⟩ > 0
- 代码实现：2D投影空间点积判据
- 代码位置：`eye_model/base.py:151-170`

### 3.4 球心最小二乘估计 ✓
- 公式：`E = (Σ(I - d_i d_i^T))^(-1) * Σ(I - d_i d_i^T)(-R n_i)`
- 代码位置：`eye_model/base.py:172-183`

### 3.5 全透视针孔相机模型 ✓
- 使用透视投影，拒绝弱透视近似
- 在 `projections.py` 中实现

### 3.6 视线向量计算 ✓
- gaze_vector = normalize(pupil_center - sphere_center)
- 代码位置：`eye_model/base.py:245-252`

---

## 4 Bug: 硬编码相机主点为图像中心

### 4.1 问题描述
代码中所有投影/反投影计算**假设相机主点位于图像中心**，未使用实际标定的主点坐标(cx, cy)。

### 4.2 CameraModel定义
```python
# pye3d/camera.py
class CameraModel(NamedTuple):
    focal_length: float
    resolution: Tuple[float, float]
    # 缺失: cx, cy 主点坐标
```

### 4.3 硬编码位置

| 文件 | 行号 | 代码 | 问题 |
|------|------|------|------|
| `detector_3d.py` | 328-329 | `center[0] - width / 2` | 假设主点=(width/2, height/2) |
| `projections.py` | 17 | `edges - np.asarray([width/2, height/2])` | 假设主点为图像中心 |
| `projections.py` | 85-86 | `center_x + width/2` | 假设主点为图像中心 |
| `projections.py` | 105-106 | `+= width/2, += height/2` | 假设主点为图像中心 |

### 4.4 影响
- 透射投影计算错误
- 眼球中心估计偏差
- 视线估计精度下降（尤其广角镜头）

### 4.5 建议修复方案

```python
# 1. 修改 CameraModel
class CameraModel(NamedTuple):
    focal_length: float
    resolution: Tuple[float, float]
    cx: float = None  # 主点x，默认None=width/2
    cy: float = None  # 主点y，默认None=height/2

# 2. 添加辅助函数
def get_principal_point(camera: CameraModel):
    width, height = camera.resolution
    cx = camera.cx if camera.cx is not None else width / 2
    cy = camera.cy if camera.cy is not None else height / 2
    return cx, cy

# 3. 替换所有 width/2, height/2 为实际主点
```

---

## 5 差异原因分析

### 5.1 优化方法未实现
- algo_13的BFGS/LM优化需要Ceres Solver集成和复杂梯度计算
- 代码选择了更简单的search_on-sphere网格搜索
- 精度可能略低于论文描述，但实现更简单

### 5.2 多项式阶数差异
- algo_19要求5次多项式
- 代码使用3次多项式（degree=3）
- 可能为了减少过拟合风险或降低计算复杂度

### 5.3 单球vs双球模型
- algo_19使用Le Grand双球模型（角膜+眼球）
- 代码简化为单球模型（眼球半径R固定）
- 简化模型牺牲了角膜折射的直接建模，但通过后置折射校正补偿

---

## 6 待优化项

| 优先级 | 事项 | 说明 |
|--------|------|------|
| **高** | 修复主点硬编码bug | 添加cx/cy到CameraModel |
| **中** | 增加多项式阶数 | 从3次提升到5次 |
| **中** | 实现Le Grand双球模型 | 更精确的角膜折射建模 |
| **低** | 集成Ceres Solver | 实现边缘距离优化 |
| **低** | 添加BFGS对比度优化 | 提升鲁棒性 |

---

## 7 文档版本

- 版本：V1.0
- 日期：2026.04.08
- 依据：algo_13.md, algo_19.md 源码分析
