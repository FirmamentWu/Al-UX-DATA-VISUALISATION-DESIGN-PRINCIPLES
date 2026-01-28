"""数据格式适配模块 - 处理不同城市数据格式差异"""
import pandas as pd
import numpy as np
from pathlib import Path
import gzip

from airbnb_analysis.config.constants import FEATURE_COLS

# 不同城市可能的列名变体
COLUMN_MAPPINGS = {
    'price': ['price', 'Price', 'PRICE'],
    'accommodates': ['accommodates', 'Accommodates', 'ACCOMMODATES'],
    'room_type': ['room_type', 'Room Type', 'ROOM_TYPE', 'roomType'],
    'neighbourhood_group_cleansed': [
        'neighbourhood_group_cleansed', 
        'neighbourhood_group', 
        'Neighbourhood Group',
        'neighborhood_group_cleansed',
        'neighborhood_group'
    ],
    'neighbourhood_cleansed': [
        'neighbourhood_cleansed',
        'neighbourhood',
        'Neighbourhood',
        'neighborhood_cleansed',
        'neighborhood'
    ],
    'calculated_host_listings_count': [
        'calculated_host_listings_count',
        'host_listings_count',
        'Host Listings Count',
        'calculatedHostListingsCount'
    ],
    'calculated_host_listings_count_entire_homes': [
        'calculated_host_listings_count_entire_homes',
        'host_listings_count_entire_homes',
        'calculatedHostListingsCountEntireHomes'
    ],
    'review_scores_rating': [
        'review_scores_rating',
        'review_rating',
        'Review Scores Rating',
        'reviewScoresRating'
    ],
    'number_of_reviews': [
        'number_of_reviews',
        'reviews_total',
        'Number of Reviews',
        'numberOfReviews'
    ],
    'number_of_reviews_ltm': [
        'number_of_reviews_ltm',
        'reviews_ltm',
        'Number of Reviews (LTM)',
        'numberOfReviewsLTM'
    ],
    'availability_365': [
        'availability_365',
        'availability',
        'Availability 365',
        'availability365'
    ],
    'host_is_superhost': [
        'host_is_superhost',
        'superhost',
        'Host Is Superhost',
        'hostIsSuperhost'
    ],
    'latitude': ['latitude', 'Latitude', 'LATITUDE'],
    'longitude': ['longitude', 'Longitude', 'LONGITUDE'],
}

def find_column(df, possible_names):
    """在DataFrame中查找列名（支持多种变体）"""
    for name in possible_names:
        if name in df.columns:
            return name
    return None

def standardize_columns(df):
    """标准化列名，将不同变体映射到标准列名"""
    df = df.copy()
    
    standardized = {}
    for standard_name, possible_names in COLUMN_MAPPINGS.items():
        found_col = find_column(df, possible_names)
        if found_col:
            if found_col != standard_name:
                df[standard_name] = df[found_col]
            standardized[standard_name] = True
        else:
            standardized[standard_name] = False
    
    return df, standardized

def load_city_data(filepath):
    """加载城市数据（支持gzip压缩）"""
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"数据文件不存在: {filepath}")
    
    # 如果是gzip文件
    if filepath.suffix == '.gz' or str(filepath).endswith('.csv.gz'):
        print(f"  读取gzip压缩文件: {filepath}")
        with gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
            df = pd.read_csv(f, low_memory=False)
    else:
        print(f"  读取CSV文件: {filepath}")
        df = pd.read_csv(filepath, low_memory=False)
    
    return df

def adapt_city_data(filepath, city_name=None):
    """适配城市数据格式"""
    print(f"\n适配数据格式: {city_name or filepath}")
    
    # 加载数据
    df = load_city_data(filepath)
    print(f"  原始数据: {len(df)} 行, {len(df.columns)} 列")
    
    # 标准化列名
    df, column_status = standardize_columns(df)
    
    # 检查必需列
    required_cols = list(FEATURE_COLS.values())
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"  ⚠ 缺失列: {', '.join(missing_cols)}")
    else:
        print(f"  ✓ 所有必需列都存在")
    
    # 显示列名映射情况
    print(f"  列名标准化情况:")
    for standard_name, found in column_status.items():
        status = "✓" if found else "✗"
        print(f"    {status} {standard_name}")
    
    return df

def check_data_quality(df, city_name=None):
    """检查数据质量"""
    print(f"\n检查数据质量: {city_name or 'Unknown'}")
    
    quality_report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_columns': [],
        'missing_data': {},
        'data_types': {}
    }
    
    # 检查必需列
    required_cols = list(FEATURE_COLS.values())
    for col in required_cols:
        if col not in df.columns:
            quality_report['missing_columns'].append(col)
        else:
            missing_pct = df[col].isna().sum() / len(df) * 100
            quality_report['missing_data'][col] = {
                'missing_count': df[col].isna().sum(),
                'missing_percentage': missing_pct
            }
            quality_report['data_types'][col] = str(df[col].dtype)
    
    # 打印报告
    print(f"  总行数: {quality_report['total_rows']}")
    print(f"  总列数: {quality_report['total_columns']}")
    print(f"  缺失列数: {len(quality_report['missing_columns'])}")
    
    if quality_report['missing_columns']:
        print(f"  缺失的列: {', '.join(quality_report['missing_columns'])}")
    
    print(f"  数据缺失情况:")
    for col, info in quality_report['missing_data'].items():
        if info['missing_count'] > 0:
            print(f"    {col}: {info['missing_count']} ({info['missing_percentage']:.1f}%)")
    
    return quality_report

def process_city_data(filepath, city_name=None):
    """完整处理城市数据：加载、适配、质量检查"""
    # 适配数据格式
    df = adapt_city_data(filepath, city_name)
    
    # 检查数据质量
    quality_report = check_data_quality(df, city_name)
    
    return df, quality_report

if __name__ == "__main__":
    # 测试适配功能
    import sys
    from pathlib import Path
    
    BASE_PATH = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(BASE_PATH))
    
    # 测试纽约数据
    ny_data_path = BASE_PATH / "airbnb_analysis" / "data" / "raw" / "listings_2_cleaned 4.0.csv"
    if ny_data_path.exists():
        print("测试适配纽约数据...")
        df, report = process_city_data(ny_data_path, "New York")
        print(f"\n适配后的数据形状: {df.shape}")
