"""多城市数据加载器 - 从raw目录直接加载数据文件"""
import sys
from pathlib import Path
import gzip
import pandas as pd

BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from airbnb_analysis.config.settings import DATA_DIR
from airbnb_analysis.config.constants import FEATURE_COLS
from airbnb_analysis.data.adapter import standardize_columns
from airbnb_analysis.data.cleaner import clean_city_data

def extract_city_name(filename):
    """从文件名提取城市名称"""
    # 移除 'listings.csv.gz' 或 'listings.csv'
    name = filename.replace('listings.csv.gz', '').replace('listings.csv', '')
    # 移除可能的空格和特殊字符
    name = name.strip()
    return name

def find_all_city_data(data_dir=None):
    """查找所有城市数据文件"""
    if data_dir is None:
        data_dir = DATA_DIR
    
    data_dir = Path(data_dir)
    
    # 查找所有listings.csv.gz文件
    data_files = list(data_dir.glob("*listings.csv.gz"))
    
    # 也查找listings.csv文件（已解压的）
    csv_files = [f for f in data_dir.glob("*listings.csv") 
                 if not f.name.startswith('listings_2_cleaned')]  # 排除纽约的清洗数据
    
    all_files = data_files + csv_files
    
    city_data_map = {}
    
    for filepath in all_files:
        city_name = extract_city_name(filepath.name)
        if city_name:
            # 如果已经有.gz文件，优先使用.gz
            if filepath.suffix == '.gz':
                city_data_map[city_name] = filepath
            elif city_name not in city_data_map:
                # 如果没有.gz，使用.csv
                city_data_map[city_name] = filepath
    
    return city_data_map

def load_city_data_file(filepath):
    """加载单个城市数据文件"""
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"数据文件不存在: {filepath}")
    
    # 读取数据
    if filepath.suffix == '.gz' or str(filepath).endswith('.csv.gz'):
        with gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
            df = pd.read_csv(f, low_memory=False)
    else:
        df = pd.read_csv(filepath, low_memory=False)
    
    return df

def load_and_preprocess_city(filepath, city_name=None):
    """加载并预处理单个城市数据"""
    print(f"\n处理城市: {city_name or filepath.name}")
    
    # 加载数据
    df = load_city_data_file(filepath)
    print(f"  原始数据: {len(df)} 行, {len(df.columns)} 列")
    
    # 标准化列名
    df, column_status = standardize_columns(df)
    
    # 检查必需列
    required_cols = ['price', 'accommodates']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"  ⚠ 缺少必需列: {missing_cols}")
        print(f"  可用列（前10个）: {list(df.columns)[:10]}")
        return pd.DataFrame()
    
    # 清洗数据（按照notebook的逻辑）
    df = clean_city_data(df, city_name)
    
    return df

def load_all_cities_data(data_dir=None):
    """加载所有城市数据"""
    if data_dir is None:
        data_dir = DATA_DIR
    
    print("="*80)
    print("加载多城市数据")
    print("="*80)
    
    # 查找所有数据文件
    city_data_map = find_all_city_data(data_dir)
    
    if not city_data_map:
        print("⚠ 未找到任何城市数据文件")
        return {}
    
    print(f"\n找到 {len(city_data_map)} 个城市的数据文件:")
    for city, filepath in sorted(city_data_map.items()):
        print(f"  {city}: {filepath.name}")
    
    # 加载每个城市的数据
    cities_data = {}
    
    for city_name, filepath in sorted(city_data_map.items()):
        try:
            df = load_and_preprocess_city(filepath, city_name)
            if len(df) > 0:
                cities_data[city_name] = df
                print(f"  ✓ 成功加载: {len(df)} 行")
            else:
                print(f"  ✗ 预处理后数据为空")
        except Exception as e:
            print(f"  ✗ 加载失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n成功加载 {len(cities_data)} 个城市的数据")
    
    return cities_data

if __name__ == "__main__":
    cities_data = load_all_cities_data()
    print(f"\n加载了 {len(cities_data)} 个城市的数据")
