# Airbnb 价格分析项目

## 项目结构

```
airbnb_analysis/
├── config/              # 配置模块
│   ├── settings.py      # 配置参数
│   └── constants.py     # 常量定义
├── data/                # 数据处理
│   ├── loader.py        # 数据加载
│   ├── preprocessor.py  # 数据预处理
│   └── raw/             # 原始数据
│       └── listings_2_cleaned 4.0.csv
├── models/              # 模型模块
│   ├── statistical_tests.py  # 统计检验
│   ├── regression.py    # 回归模型
│   └── smoothing.py     # 非参数平滑
├── visualization/       # 可视化
│   └── style.py         # 图表样式
├── analysis/            # 分析场景
│   ├── scenario1_physical_space.py    # 场景1: 物理空间溢价
│   ├── scenario2_location.py         # 场景2: 黄金地段
│   ├── scenario3_scale.py            # 场景3: 规模溢价
│   ├── scenario4_trust.py            # 场景4: 信任货币化
│   ├── scenario5_activity.py         # 场景5: 活跃度信号
│   └── comprehensive_model.py        # 综合模型
├── utils/               # 工具函数
│   └── dependencies.py  # 依赖管理
├── notebooks/           # Jupyter Notebooks
│   └── Data Cleaning and Feature Engineering.ipynb
├── docs/                # 文档
│   └── 分析结果总结.md
├── outputs/             # 输出目录
│   └── figures/         # 生成的图表
├── README.md            # 项目说明
└── requirements.txt     # 依赖列表

../main.py               # 主入口文件（在项目根目录）
```

## 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行分析：
```bash
python main.py
```

3. 查看结果：
所有图表将保存在 `airbnb_analysis/outputs/figures/` 目录下。

## 项目文件说明

- **数据文件**: `data/raw/listings_2_cleaned 4.0.csv` - 清洗后的数据
- **数据清洗**: `notebooks/Data Cleaning and Feature Engineering.ipynb` - 数据清洗和特征工程
- **分析结果**: `docs/分析结果总结.md` - 详细的分析结果总结

## 生成的图表

项目会生成19张图表，涵盖5个核心分析场景：

- **场景1**: 物理空间的溢价逻辑 (3张图)
- **场景2**: 黄金地段的绝对统治 (4张图)
- **场景3**: 运营专业化带来的规模溢价 (4张图)
- **场景4**: 信任的货币化 (3张图)
- **场景5**: 活跃度即需求的实时信号 (4张图)
- **综合模型**: 价格预测模型 (1张图)


