# 项目结构说明

## 完整目录结构

```
airbnb_analysis/
├── __init__.py
├── README.md                    # 项目说明文档
├── requirements.txt             # Python依赖包列表
│
├── config/                      # 配置模块
│   ├── __init__.py
│   ├── settings.py              # 配置参数（路径、图表样式等）
│   └── constants.py             # 常量定义（特征列名、场景名称等）
│
├── data/                        # 数据处理模块
│   ├── __init__.py
│   ├── loader.py                # 数据加载
│   ├── preprocessor.py          # 数据预处理
│   └── raw/                     # 原始数据目录
│       └── listings_2_cleaned 4.0.csv  # 清洗后的数据文件
│
├── models/                      # 模型模块
│   ├── __init__.py
│   ├── statistical_tests.py    # 统计检验（Mann-Whitney U, Kruskal-Wallis, Spearman等）
│   ├── regression.py            # 回归模型（线性回归、交互效应、对数线性）
│   └── smoothing.py             # 非参数平滑（LOWESS, KDE）
│
├── visualization/              # 可视化模块
│   ├── __init__.py
│   └── style.py                # 图表样式配置（包含set_legend_outside函数）
│
├── analysis/                    # 分析场景模块
│   ├── __init__.py
│   ├── scenario1_physical_space.py    # 场景1: 物理空间的溢价逻辑
│   ├── scenario2_location.py        # 场景2: 黄金地段的绝对统治
│   ├── scenario3_scale.py            # 场景3: 运营专业化带来的规模溢价
│   ├── scenario4_trust.py            # 场景4: 信任的货币化
│   ├── scenario5_activity.py         # 场景5: 活跃度即需求的实时信号
│   └── comprehensive_model.py       # 综合模型: 价格预测
│
├── utils/                       # 工具函数模块
│   ├── __init__.py
│   └── dependencies.py         # 依赖管理（自动安装缺失的包）
│
├── notebooks/                   # Jupyter Notebooks
│   └── Data Cleaning and Feature Engineering.ipynb  # 数据清洗和特征工程
│
├── docs/                        # 文档目录
│   └── 分析结果总结.md          # 详细的分析结果总结
│
└── outputs/                     # 输出目录
    └── figures/                 # 生成的图表（19张PNG图片）
        ├── 1_1_privacy_premium.png
        ├── 1_2_capacity_premium.png
        ├── 1_3_interaction_effect.png
        ├── 2_1_spatial_price_heatmap.png
        ├── 2_2_region_comparison.png
        ├── 2_3_manhattan_subregions.png
        ├── 2_4_controlled_location_premium.png
        ├── 3_1_scale_premium_price.png
        ├── 3_2_scale_occupancy.png
        ├── 3_3_entire_home_scale.png
        ├── 3_4_entire_home_specialization.png
        ├── 4_1_rating_distribution.png
        ├── 4_2_rating_vs_occupancy.png
        ├── 4_3_superhost_comparison.png
        ├── 5_1_reviews_decoupling.png
        ├── 5_2_ltm_vs_price.png
        ├── 5_3_historical_vs_price.png
        ├── 5_4_ltm_vs_occupancy.png
        └── comprehensive_price_model.png

../main.py                       # 主入口文件（在项目根目录）
```

## 模块说明

### 配置模块 (config/)
- **settings.py**: 集中管理所有配置参数
  - 路径配置（数据文件、输出目录）
  - 图表样式配置
  - 分析参数（分位数、LOWESS平滑参数等）
  - 分箱配置

- **constants.py**: 定义常量
  - 场景名称映射
  - 特征列名映射（统一管理，便于修改）

### 数据处理模块 (data/)
- **loader.py**: 数据加载，自动从配置路径读取数据
- **preprocessor.py**: 数据预处理
  - 数值类型转换
  - 缺失值处理
  - 分箱特征创建

### 模型模块 (models/)
- **statistical_tests.py**: 统计检验函数
  - `test_privacy_premium()`: Mann-Whitney U检验
  - `test_group_differences()`: Kruskal-Wallis检验
  - `compute_correlation()`: 相关系数计算

- **regression.py**: 回归模型
  - `fit_linear_regression()`: 简单线性回归
  - `fit_interaction_model()`: 交互效应模型
  - `fit_log_linear_model()`: 对数线性模型

- **smoothing.py**: 非参数平滑
  - `fit_lowess()`: LOWESS平滑
  - `fit_kde()`: 核密度估计

### 可视化模块 (visualization/)
- **style.py**: 图表样式管理
  - `setup_style()`: 设置全局图表样式
  - `save_figure()`: 统一保存图表
  - `set_legend_outside()`: 将legend移到图外（使用bbox_to_anchor=(1.02, 0.5)）

### 分析场景模块 (analysis/)
每个场景都是独立的模块，包含完整的分析逻辑：
- **scenario1_physical_space.py**: 物理空间溢价（隐私溢价、容量溢价、交互效应）
- **scenario2_location.py**: 位置溢价（空间热力图、区域对比、子区位跃迁）
- **scenario3_scale.py**: 规模溢价（房东规模、入住率、专业化）
- **scenario4_trust.py**: 信任货币化（评分分布、评分vs入住率、超赞房东）
- **scenario5_activity.py**: 活跃度信号（历史vs LTM、LTM vs价格、LTM vs入住率）
- **comprehensive_model.py**: 综合价格预测模型

## 使用方式

### 运行完整分析
```bash
python main.py
```

### 单独运行某个场景
```python
from airbnb_analysis.data.loader import load_data
from airbnb_analysis.data.preprocessor import preprocess_data
from airbnb_analysis.analysis.scenario1_physical_space import run_scenario1

df = load_data()
df = preprocess_data(df)
results = run_scenario1(df)
```

## 优势

1. **模块化**: 每个场景独立，便于维护和扩展
2. **可复用**: 工具函数可在多个场景复用
3. **可测试**: 各模块可独立测试
4. **配置集中**: 参数统一管理，易于修改
5. **职责清晰**: 数据、模型、可视化分离
6. **图例优化**: 所有legend都在图外，图表更美观
