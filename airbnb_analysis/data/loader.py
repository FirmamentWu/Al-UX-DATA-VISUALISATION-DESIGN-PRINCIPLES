"""数据加载模块"""
import pandas as pd
from pathlib import Path
from airbnb_analysis.config.settings import DATA_DIR, DATA_FILE

def load_data(filepath=None):
    """加载清洗后的数据"""
    if filepath is None:
        filepath = DATA_DIR / DATA_FILE
    
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    print(f"Data loaded: {len(df)} rows, {len(df.columns)} columns")
    return df
