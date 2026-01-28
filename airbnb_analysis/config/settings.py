"""项目配置参数"""
from pathlib import Path

# 路径配置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"  # 数据文件在data/raw目录（所有城市数据都在这里）
OUTPUT_DIR = BASE_DIR / "outputs" / "figures"
MULTI_CITY_RESULTS_DIR = BASE_DIR / "outputs" / "multi_city_results"  # 多城市分析结果目录

# 数据文件
DATA_FILE = "listings_2_cleaned 4.0.csv"

# 图表配置
FIGURE_CONFIG = {
    'dpi': 300,
    'figsize': (12, 8),
    'style': 'whitegrid',
    'palette': 'husl',
    'font_sans_serif': ['Arial Unicode MS', 'SimHei', 'DejaVu Sans'],
}

# 分析参数
ANALYSIS_CONFIG = {
    'price_quantile_low': 0.01,
    'price_quantile_high': 0.99,
    'accommodates_max': 10,
    'lowess_frac': 0.3,
    'min_samples_per_group': 10,
}

# 分箱配置
BINNING_CONFIG = {
    'host_listings': [0, 1, 3, 5, float('inf')],
    'host_listings_labels': ['1', '2-3', '4-5', '>5'],
    'entire_homes': [-0.5, 0.5, 1.5, float('inf')],
    'entire_homes_labels': ['0', '1', '2+'],
}

# 多城市配置
MULTI_CITY_CONFIG = {
    # 城市列表将从实际数据文件中自动检测
    'min_samples_per_city': 100,  # 每个城市最少样本数
    'significance_level': 0.05,  # 统计显著性水平
    'data_file_pattern': '*listings.csv.gz',  # 数据文件匹配模式
}
