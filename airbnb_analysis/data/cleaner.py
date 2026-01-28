"""数据清洗模块 - 参考notebook的逻辑"""
import pandas as pd
import numpy as np
from pathlib import Path

def clean_city_data(df, city_name=None):
    """按照notebook的逻辑清洗单个城市数据"""
    print(f"\n清洗数据: {city_name or 'Unknown'}")
    print(f"  原始数据: {len(df)} 行")
    
    df = df.copy()
    initial_count = len(df)
    
    # 1. 处理reviews_per_month缺失值
    if 'reviews_per_month' in df.columns:
        df['reviews_per_month'] = df['reviews_per_month'].fillna(0)
        df['has_reviews'] = (df['number_of_reviews'] > 0).astype(int)
    
    # 2. 处理accommodates为0
    if 'accommodates' in df.columns:
        df.loc[df['accommodates'] == 0, 'accommodates'] = np.nan
        if 'room_type' in df.columns:
            df['accommodates'] = df.groupby('room_type')['accommodates'].transform(
                lambda x: x.fillna(x.median())
            )
        else:
            df['accommodates'] = df['accommodates'].fillna(df['accommodates'].median())
        df['accommodates_was_zero'] = df['accommodates'].isna().astype(int)
    
    # 3. 处理review_scores为0（替换为NaN，然后用中位数填充）
    review_cols = [
        'review_scores_accuracy', 'review_scores_cleanliness', 'review_scores_checkin',
        'review_scores_communication', 'review_scores_location', 'review_scores_value',
        'review_scores_rating'
    ]
    
    for col in review_cols:
        if col in df.columns:
            df[col] = df[col].replace(0, np.nan)
            has_col = f'has_{col.replace("review_scores_", "")}_review'
            df[has_col] = df[col].notna().astype(int)
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
    
    # 4. 处理host_listings_count为0
    if 'host_listings_count' in df.columns:
        df['host_listings_count'] = df['host_listings_count'].replace(0, np.nan)
        df['has_host_listings_count'] = df['host_listings_count'].notna().astype(int)
        df['host_listings_count'] = df['host_listings_count'].fillna(df['host_listings_count'].median())
    
    if 'host_total_listings_count' in df.columns:
        df['host_total_listings_count'] = df['host_total_listings_count'].replace(0, np.nan)
        df['has_host_total_listings_count'] = df['host_total_listings_count'].notna().astype(int)
        df['host_total_listings_count'] = df['host_total_listings_count'].fillna(df['host_total_listings_count'].median())
    
    # 5. 处理价格（按照notebook的逻辑）
    if 'price' in df.columns:
        # 转换为字符串，移除$和逗号
        df['price'] = (
            df['price']
            .astype(str)
            .str.replace(r'[\$,]', '', regex=True)  # 使用regex移除$和逗号
            .str.strip()
        )
        
        # 转成数值
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        # 丢掉缺失和不合理值
        df = df[df['price'].notna()]
        df = df[df['price'] > 0]
        
        # 价格异常值处理（IQR方法）
        Q1 = df['price'].quantile(0.25)
        Q3 = df['price'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        df['is_outlier_iqr'] = (
            (df['price'] < lower_bound) |
            (df['price'] > upper_bound)
        )
        
        # 处理异常值类型
        df['outlier_type'] = 'normal'
        df.loc[df['price'] <= 0, 'outlier_type'] = 'impossible'
        
        p999 = df['price'].quantile(0.999)
        df.loc[
            (df['price'] > p999) &
            (df['price'] % 10 == 0),
            'outlier_type'
        ] = 'likely_error'
        
        df.loc[
            (df['is_outlier_iqr']) &
            (df['outlier_type'] == 'normal'),
            'outlier_type'
        ] = 'legit_extreme'
        
        # 删除不可能值和明显错误值
        df = df[df['outlier_type'] != 'impossible']
        df = df[df['outlier_type'] != 'likely_error']
        
        # 创建log_price
        df['log_price'] = np.log(df['price'])
    
    # 6. 确保accommodates有效
    if 'accommodates' in df.columns:
        df = df[df['accommodates'].notna() & (df['accommodates'] > 0)]
    
    # 7. 创建分箱特征（用于场景3分析）
    from airbnb_analysis.config.settings import BINNING_CONFIG
    
    if 'calculated_host_listings_count' in df.columns:
        df['host_listings_count_binned'] = pd.cut(
            df['calculated_host_listings_count'],
            bins=BINNING_CONFIG['host_listings'],
            labels=BINNING_CONFIG['host_listings_labels'],
            include_lowest=True
        )
    
    if 'calculated_host_listings_count_entire_homes' in df.columns:
        df['entire_homes_binned'] = pd.cut(
            df['calculated_host_listings_count_entire_homes'],
            bins=BINNING_CONFIG['entire_homes'],
            labels=BINNING_CONFIG['entire_homes_labels'],
            include_lowest=True
        )
    
    filtered_count = len(df)
    if initial_count > 0:
        print(f"  清洗后: {filtered_count} 行 (保留 {filtered_count/initial_count*100:.1f}%)")
    else:
        print(f"  清洗后: {filtered_count} 行")
    
    return df
