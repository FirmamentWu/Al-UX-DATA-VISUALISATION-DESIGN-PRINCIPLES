"""综合模型: 价格预测"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import statsmodels.api as sm

BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from airbnb_analysis.models.regression import fit_log_linear_model
from airbnb_analysis.visualization.style import save_figure
from airbnb_analysis.config.settings import OUTPUT_DIR
from airbnb_analysis.config.constants import FEATURE_COLS

def run_comprehensive_model(df):
    """运行综合价格预测模型"""
    print("\n" + "="*80)
    print("综合模型: 价格预测")
    print("="*80)
    
    print("\n" + "="*80)
    print("="*80)

# 准备建模数据
    df_model = df.copy()

# 特征工程
    df_model['is_entire'] = (df_model[FEATURE_COLS['room_type']] == 'Entire home/apt').astype(int)
    df_model['is_manhattan'] = (df_model[FEATURE_COLS['neighbourhood_group']] == 'Manhattan').astype(int)
    df_model['is_superhost'] = (df_model[FEATURE_COLS['superhost']] == 't').astype(int)
    df_model['log_accommodates'] = np.log1p(df_model[FEATURE_COLS['accommodates']])
    df_model['log_ltm'] = np.log1p(df_model[FEATURE_COLS['reviews_ltm']] + 1)
    df_model['log_host_listings'] = np.log1p(df_model[FEATURE_COLS['host_listings_count']] + 1)

# 选择特征
    features = ['is_entire', 'accommodates', 'is_manhattan', 'is_superhost',
                'calculated_host_listings_count', 'review_scores_rating', 
                'number_of_reviews_ltm', 'latitude', 'longitude']

# 过滤有效数据
    df_model_clean = df_model[features + ['price']].dropna()

    if len(df_model_clean) > 1000:
        X = df_model_clean[features]
        y = df_model_clean['price']
        
        # 使用log_price作为目标变量（因为价格右偏）
        if 'log_price' in df_model_clean.columns:
            y_log = df_model_clean['log_price']
        else:
            y_log = np.log(df_model_clean['price'])
        
        # 线性回归
        model = fit_log_linear_model(X, y_log)
        
        print("\n价格预测模型 (Log-linear):")
        print(model.summary().tables[1])
        
        # 特征重要性可视化
        fig, ax = plt.subplots(figsize=(10, 8))
        coef_df = pd.DataFrame({
            'Feature': features,
            'Coefficient': model.params[1:].values,
            'Abs_Coefficient': np.abs(model.params[1:].values)
        }).sort_values('Abs_Coefficient', ascending=True)
        
        ax.barh(coef_df['Feature'], coef_df['Coefficient'], color='steelblue')
        ax.axvline(0, color='black', linestyle='-', linewidth=0.5)
        ax.set_xlabel('Coefficient', fontsize=12)
        ax.set_ylabel('Feature', fontsize=12)
        ax.set_title('Price Prediction Model: Feature Coefficients', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        save_figure(fig, 'comprehensive_price_model.png', OUTPUT_DIR)
        plt.close()

    print("\n" + "="*80)
    print("所有分析完成！图表已保存。")
    print("="*80)

    return {}

