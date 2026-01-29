# 项目结构说明

## 完整目录结构

```
airbnb_analysis/
├── __init__.py
├── README.md                    # 项目说明文档
├── PROJECT_STRUCTURE.md         # 项目结构说明（本文件）
├── requirements.txt             # Python依赖包列表
│
├── config/                      # 配置模块
│   ├── __init__.py
│   ├── settings.py              # 配置参数（路径、图表样式等）
│   └── constants.py             # 常量定义（特征列名、场景名称等）
│
├── data/                        # 数据处理模块
│   ├── __init__.py
│   ├── loader.py                # 数据加载（NYC数据）
│   ├── preprocessor.py          # 数据预处理（NYC数据）
│   ├── cleaner.py               # 数据清洗（基于notebook逻辑）
│   ├── adapter.py               # 列名适配（跨城市数据标准化）
│   ├── multi_city_loader.py     # 多城市数据加载
│   └── raw/                     # 原始数据目录
│       ├── listings_2_cleaned 4.0.csv  # NYC清洗后的数据文件
│       ├── *listings.csv.gz     # 各城市压缩数据文件（11个城市）
│       └── ...
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
│   ├── scenario2_location.py         # 场景2: 黄金地段的绝对统治
│   ├── scenario3_scale.py             # 场景3: 运营专业化带来的规模溢价
│   ├── scenario4_trust.py             # 场景4: 信任的货币化
│   ├── scenario5_activity.py          # 场景5: 活跃度即需求的实时信号
│   ├── comprehensive_model.py         # 综合模型: 价格预测
│   ├── multi_city_analysis.py        # 多城市分析框架
│   ├── cross_city_comparison.py      # 跨城市对比分析
│   └── generalizability_visualization.py  # 外推性可视化
│
├── utils/                       # 工具函数模块
│   ├── __init__.py
│   ├── dependencies.py         # 依赖管理（自动安装缺失的包）
│   └── validate_results.py      # 结果验证（验证NYC数据的统计显著性）
│
├── notebooks/                   # Jupyter Notebooks
│   └── Data Cleaning and Feature Engineering.ipynb  # 数据清洗和特征工程
│
├── docs/                        # 文档目录
│   ├── comprehensive_analysis_report.md  # 综合分析报告（整合NYC和Multi-city）
│   ├── multi_city_validation_report.md  # 多城市验证报告模板
│   ├── 分析结果总结.md          # NYC分析结果总结
│   └── 跨城市分析结果报告.md    # 跨城市分析结果报告
│
└── outputs/                     # 输出目录
    ├── figures/                 # 生成的图表（22张PNG图片）
    │   ├── 1_1_privacy_premium.png
    │   ├── 1_2_capacity_premium.png
    │   ├── 1_3_interaction_effect.png
    │   ├── 2_1_spatial_price_heatmap.png
    │   ├── 2_2_region_comparison.png
    │   ├── 2_3_manhattan_subregions.png
    │   ├── 2_4_controlled_location_premium.png
    │   ├── 3_1_scale_premium_price.png
    │   ├── 3_2_scale_occupancy.png
    │   ├── 3_3_entire_home_scale.png
    │   ├── 3_4_entire_home_specialization.png
    │   ├── 4_1_rating_distribution.png
    │   ├── 4_2_rating_vs_occupancy.png
    │   ├── 4_3_superhost_comparison.png
    │   ├── 5_1_reviews_decoupling.png
    │   ├── 5_2_ltm_vs_price.png
    │   ├── 5_3_historical_vs_price.png
    │   ├── 5_4_ltm_vs_occupancy.png
    │   ├── comprehensive_price_model.png
    │   ├── generalizability_validation.png      # 外推性验证主图
    │   ├── validation_method_matrix.png          # 统计显著性矩阵图
    │   └── effect_consistency.png                 # 效应量一致性图
    ├── multi_city_results/       # 多城市分析结果
    │   ├── all_cities_results.json
    │   ├── comparison_summary.json
    │   ├── Albany_results.json
    │   ├── Amsterdam_results.json
    │   └── ... (其他城市结果文件)
    └── validation/              # 验证结果
        └── ny_validation_results.json

../main.py                       # NYC分析主入口文件（在项目根目录）
../multi_city_main.py            # 多城市分析主入口文件（在项目根目录）
```

## 模块说明

### 配置模块 (config/)
- **settings.py**: 集中管理所有配置参数
  - 路径配置（数据文件、输出目录）
  - 图表样式配置
  - 分析参数（分位数、LOWESS平滑参数等）
  - 分箱配置
  - 多城市数据路径配置

- **constants.py**: 定义常量
  - 场景名称映射
  - 特征列名映射（统一管理，便于修改）
  - 城市名称映射

### 数据处理模块 (data/)
- **loader.py**: NYC数据加载，自动从配置路径读取数据
- **preprocessor.py**: NYC数据预处理
  - 数值类型转换
  - 缺失值处理
  - 分箱特征创建

- **cleaner.py**: 数据清洗（基于notebook逻辑）
  - 处理 reviews_per_month 和 accommodates 的零值/NaN值
  - 处理 review_scores 系列（替换0为NaN，用中位数填充）
  - 处理 host_listings_count 和 host_total_listings_count
  - 价格转换（去除$和逗号）
  - IQR异常值检测和处理
  - 对数变换（log_price）

- **adapter.py**: 列名适配器
  - 将不同城市的列名映射到统一标准
  - 处理列名拼写差异

- **multi_city_loader.py**: 多城市数据加载
  - 自动查找所有城市数据文件
  - 使用 cleaner.py 进行数据清洗
  - 使用 adapter.py 进行列名标准化

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
  - 字体配置（支持Mac系统字体）

### 分析场景模块 (analysis/)
每个场景都是独立的模块，包含完整的分析逻辑：

**NYC分析场景：**
- **scenario1_physical_space.py**: 物理空间溢价（隐私溢价、容量溢价、交互效应）
- **scenario2_location.py**: 位置溢价（空间热力图、区域对比、子区域价格跃迁）
- **scenario3_scale.py**: 规模溢价（房东规模、入住率、专业化）
- **scenario4_trust.py**: 信任货币化（评分分布、评分vs入住率、超赞房东）
- **scenario5_activity.py**: 活跃度信号（历史vs LTM、LTM vs价格、LTM vs入住率）
- **comprehensive_model.py**: 综合价格预测模型

**跨城市分析模块：**
- **multi_city_analysis.py**: 多城市分析框架
  - 对每个城市运行相同的5个场景分析
  - 收集和汇总各城市的统计检验结果
  
- **cross_city_comparison.py**: 跨城市对比分析
  - 比较各城市的统计检验结果
  - 评估规律的普遍性
  - 生成对比报告
  
- **generalizability_visualization.py**: 外推性可视化
  - `create_generalizability_chart()`: 创建外推性验证主图
  - `create_validation_matrix()`: 创建统计显著性矩阵图
  - `create_effect_consistency_chart()`: 创建效应量一致性图

### 工具函数模块 (utils/)
- **dependencies.py**: 依赖管理
  - `ensure_dependencies()`: 自动检查并安装缺失的包
  
- **validate_results.py**: 结果验证
  - `validate_all_results()`: 验证NYC数据的统计显著性
  - 提取各场景的p值和统计量

## 使用方式

### 运行NYC分析
```bash
python main.py
```

### 运行多城市分析
```bash
python multi_city_main.py
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

### 运行跨城市分析
```python
from airbnb_analysis.analysis.multi_city_analysis import analyze_all_cities
from airbnb_analysis.analysis.cross_city_comparison import generate_comparison_report

# 分析所有城市
all_results = analyze_all_cities()

# 生成对比报告
comparison_summary = generate_comparison_report()
```

## 项目优势

1. **模块化**: 每个场景独立，便于维护和扩展
2. **可复用**: 工具函数可在多个场景复用
3. **可测试**: 各模块可独立测试
4. **配置集中**: 参数统一管理，易于修改
5. **职责清晰**: 数据、模型、可视化分离
6. **图例优化**: 所有legend都在图外，图表更美观
7. **跨城市支持**: 统一的数据清洗和分析流程，确保结果可比性
8. **外推性验证**: 系统化的方法验证规律在不同城市中的普遍性

## 数据流程

### NYC分析流程
1. 加载数据 (`loader.py`)
2. 预处理数据 (`preprocessor.py`)
3. 运行5个场景分析 (`scenario1-5.py`)
4. 生成综合模型 (`comprehensive_model.py`)
5. 保存图表到 `outputs/figures/`

### 多城市分析流程
1. 查找所有城市数据文件 (`multi_city_loader.py`)
2. 对每个城市：
   - 加载数据
   - 使用 `cleaner.py` 清洗数据（基于notebook逻辑）
   - 使用 `adapter.py` 标准化列名
   - 运行5个场景分析 (`multi_city_analysis.py`)
   - 保存结果到JSON文件
3. 跨城市对比分析 (`cross_city_comparison.py`)
4. 生成外推性可视化 (`generalizability_visualization.py`)
5. 生成对比报告

## 输出文件说明

### 图表文件 (outputs/figures/)
- **NYC场景图表** (19张): 涵盖5个核心分析场景和综合模型
- **跨城市验证图表** (3张):
  - `generalizability_validation.png`: 外推性验证主图
  - `validation_method_matrix.png`: 统计显著性矩阵图
  - `effect_consistency.png`: 效应量一致性图

### 结果文件 (outputs/multi_city_results/)
- **各城市结果**: `{City}_results.json` - 每个城市的详细分析结果
- **汇总结果**: `all_cities_results.json` - 所有城市的结果汇总
- **对比摘要**: `comparison_summary.json` - 跨城市对比摘要

### 文档文件 (docs/)
- **comprehensive_analysis_report.md**: 综合分析报告（整合NYC和Multi-city）
- **multi_city_validation_report.md**: 多城市验证报告模板
- **分析结果总结.md**: NYC分析结果总结
- **跨城市分析结果报告.md**: 跨城市分析结果报告
