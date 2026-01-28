"""数据预处理模块"""
import pandas as pd
import numpy as np
from airbnb_analysis.config.settings import BINNING_CONFIG
from airbnb_analysis.config.constants import FEATURE_COLS

def preprocess_data(df):
    """数据预处理主函数"""
    df = df.copy()
    
    # 转换数值类型
    numeric_cols = [
        FEATURE_COLS['price'], FEATURE_COLS['accommodates'],
        FEATURE_COLS['latitude'], FEATURE_COLS['longitude'],
        FEATURE_COLS['host_listings_count'],
        FEATURE_COLS['entire_homes_count'],
        FEATURE_COLS['review_rating'],
        FEATURE_COLS['reviews_total'],
        FEATURE_COLS['reviews_ltm'],
        FEATURE_COLS['availability'],
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 过滤有效数据
    df = df[
        df[FEATURE_COLS['price']].notna() & 
        (df[FEATURE_COLS['price']] > 0)
    ]
    df = df[
        df[FEATURE_COLS['accommodates']].notna() & 
        (df[FEATURE_COLS['accommodates']] > 0)
    ]
    
    # 创建分箱变量
    df = create_binned_features(df)
    
    print(f"After preprocessing: {len(df)} rows")
    return df

def create_binned_features(df):
    """创建分箱特征"""
    df = df.copy()
    
    # 房东规模分箱
    if FEATURE_COLS['host_listings_count'] in df.columns:
        df['host_listings_count_binned'] = pd.cut(
            df[FEATURE_COLS['host_listings_count']],
            bins=BINNING_CONFIG['host_listings'],
            labels=BINNING_CONFIG['host_listings_labels']
        )
    
    # 整租房源数分箱
    if FEATURE_COLS['entire_homes_count'] in df.columns:
        df['entire_homes_binned'] = pd.cut(
            df[FEATURE_COLS['entire_homes_count']],
            bins=BINNING_CONFIG['entire_homes'],
            labels=BINNING_CONFIG['entire_homes_labels']
        )
    
    return df
