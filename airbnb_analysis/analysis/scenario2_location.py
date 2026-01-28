"""场景2: 黄金地段的绝对统治"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from scipy.stats import mannwhitneyu, kruskal, spearmanr, gaussian_kde
from statsmodels.nonparametric.smoothers_lowess import lowess
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from statsmodels.formula.api import ols

BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from airbnb_analysis.models.statistical_tests import test_group_differences, test_privacy_premium, compute_correlation
from airbnb_analysis.models.regression import fit_linear_regression, fit_interaction_model, fit_log_linear_model
from airbnb_analysis.models.smoothing import fit_lowess, fit_kde
from airbnb_analysis.visualization.style import save_figure, set_legend_outside
from airbnb_analysis.config.settings import OUTPUT_DIR, ANALYSIS_CONFIG
from airbnb_analysis.config.constants import FEATURE_COLS

def run_scenario2(df):
    """运行场景2的所有分析"""
    print("\n" + "="*80)
    print("场景2: 黄金地段的绝对统治")
    print("="*80)
    
        # 2.1 空间价格热力图
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    
    # Geographic scatter
    df_loc = df[df[FEATURE_COLS['latitude']].notna() & df[FEATURE_COLS['longitude']].notna()].copy()
    price_low = df_loc[FEATURE_COLS['price']].quantile(ANALYSIS_CONFIG['price_quantile_low'])
    price_high = df_loc[FEATURE_COLS['price']].quantile(ANALYSIS_CONFIG['price_quantile_high'])
    df_loc = df_loc[df_loc[FEATURE_COLS['price']].between(price_low, price_high)]
    
    scatter = axes[0].scatter(df_loc[FEATURE_COLS['longitude']], df_loc[FEATURE_COLS['latitude']], 
                             c=df_loc[FEATURE_COLS['price']], s=20, alpha=0.5, 
                             cmap='YlOrRd', vmin=df_loc[FEATURE_COLS['price']].quantile(0.1),
                             vmax=df_loc[FEATURE_COLS['price']].quantile(0.9))
    axes[0].set_xlabel('Longitude', fontsize=12)
    axes[0].set_ylabel('Latitude', fontsize=12)
    axes[0].set_title('Spatial Price Distribution: Price Concentration in Core Areas', 
                      fontsize=14, fontweight='bold')
    plt.colorbar(scatter, ax=axes[0], label='Price ($)')
    
    # Hexbin plot for density
    hb = axes[1].hexbin(df_loc[FEATURE_COLS['longitude']], df_loc[FEATURE_COLS['latitude']], 
                        C=df_loc[FEATURE_COLS['price']],
                        gridsize=30, cmap='YlOrRd', reduce_C_function=np.median)
    axes[1].set_xlabel('Longitude', fontsize=12)
    axes[1].set_ylabel('Latitude', fontsize=12)
    axes[1].set_title('Price Density Heatmap (Median Price by Grid)', 
                      fontsize=14, fontweight='bold')
    plt.colorbar(hb, ax=axes[1], label='Median Price ($)')
    
    plt.tight_layout()
    save_figure(fig, '2_1_spatial_price_heatmap.png', OUTPUT_DIR)
    plt.close()

    # 2.2 区域分组对比
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    df_region = df[df[FEATURE_COLS['neighbourhood_group']].notna()].copy()
    order = df_region.groupby(FEATURE_COLS['neighbourhood_group'])[FEATURE_COLS['price']].median().sort_values(ascending=False).index
    
    # Boxplot
    sns.boxplot(data=df_region, x=FEATURE_COLS['neighbourhood_group'], y=FEATURE_COLS['price'], 
               ax=axes[0], palette='viridis', order=order)
    axes[0].set_title('Price Distribution by Borough', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Neighbourhood Group', fontsize=12)
    axes[0].set_ylabel('Price ($)', fontsize=12)
    axes[0].tick_params(axis='x', rotation=45)
    
    # Violin plot
    sns.violinplot(data=df_region, x=FEATURE_COLS['neighbourhood_group'], y=FEATURE_COLS['price'], 
                  ax=axes[1], palette='viridis', inner='quartile', order=order)
    axes[1].set_title('Price Distribution Shape by Borough', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Neighbourhood Group', fontsize=12)
    axes[1].set_ylabel('Price ($)', fontsize=12)
    axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    save_figure(fig, '2_2_region_comparison.png', OUTPUT_DIR)
    plt.close()
    
    # Kruskal-Wallis 检验
    result = test_group_differences(df_region, FEATURE_COLS['neighbourhood_group'], FEATURE_COLS['price'])
    if result:
        print(f"\n区域分组对比:")
        print(f"  Kruskal-Wallis 检验 p-value: {result['p_value']:.4f}")
        print(f"  各区域价格中位数:")
        for region, median in result['medians'].items():
            print(f"    {region}: ${median:.2f}")

    # 2.3 子区位跃迁（仅Manhattan）
    fig, ax = plt.subplots(figsize=(14, 8))
    
    df_manhattan = df[df[FEATURE_COLS['neighbourhood_group']] == 'Manhattan'].copy()
    df_manhattan = df_manhattan[df_manhattan[FEATURE_COLS['neighbourhood']].notna()]
    
    # 只显示有足够样本的子区域
    neighbourhood_counts = df_manhattan[FEATURE_COLS['neighbourhood']].value_counts()
    valid_neighbourhoods = neighbourhood_counts[neighbourhood_counts >= 20].index
    df_manhattan_filtered = df_manhattan[df_manhattan[FEATURE_COLS['neighbourhood']].isin(valid_neighbourhoods)]
    
    if len(df_manhattan_filtered) > 0:
        # 按中位数排序
        order = df_manhattan_filtered.groupby(FEATURE_COLS['neighbourhood'])[FEATURE_COLS['price']].median().sort_values(ascending=False).index[:15]
        
        sns.boxplot(data=df_manhattan_filtered, x=FEATURE_COLS['neighbourhood'], y=FEATURE_COLS['price'], 
                   ax=ax, palette='coolwarm', order=order)
        ax.set_title('Sub-location Premium: Price Variation within Manhattan', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Neighbourhood (Manhattan)', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.tick_params(axis='x', rotation=90)
        
        plt.tight_layout()
        save_figure(fig, '2_3_manhattan_subregions.png', OUTPUT_DIR)
        plt.close()
        
        print(f"\nManhattan子区域价格中位数 (Top 5):")
        top5 = df_manhattan_filtered.groupby(FEATURE_COLS['neighbourhood'])[FEATURE_COLS['price']].median().sort_values(ascending=False).head(5)
        for neigh, median in top5.items():
            print(f"  {neigh}: ${median:.2f}")

    # 2.4 控制物理条件后的位置溢价
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 固定条件：Private room, accommodates = 1
    df_controlled = df[(df[FEATURE_COLS['room_type']] == 'Private room') & 
                       (df[FEATURE_COLS['accommodates']] == 1)].copy()
    df_controlled = df_controlled[df_controlled[FEATURE_COLS['neighbourhood']].notna()]
    
    # 只显示有足够样本的子区域
    neighbourhood_counts = df_controlled[FEATURE_COLS['neighbourhood']].value_counts()
    valid_neighbourhoods = neighbourhood_counts[neighbourhood_counts >= 5].index
    df_controlled_filtered = df_controlled[df_controlled[FEATURE_COLS['neighbourhood']].isin(valid_neighbourhoods)]
    
    if len(df_controlled_filtered) > 0:
        # 按中位数排序
        order = df_controlled_filtered.groupby(FEATURE_COLS['neighbourhood'])[FEATURE_COLS['price']].median().sort_values(ascending=False).index[:15]
        
        sns.boxplot(data=df_controlled_filtered, x=FEATURE_COLS['neighbourhood'], y=FEATURE_COLS['price'], 
                   ax=ax, palette='Set3', order=order)
        ax.set_title('Location Premium After Controlling Physical Conditions\n(Private Room, Accommodates=1)', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Neighbourhood', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.tick_params(axis='x', rotation=90)
        
        plt.tight_layout()
        save_figure(fig, '2_4_controlled_location_premium.png', OUTPUT_DIR)
        plt.close()
        
        print(f"\n控制条件后（Private room, 1人）各区域价格中位数 (Top 5):")
        top5 = df_controlled_filtered.groupby(FEATURE_COLS['neighbourhood'])[FEATURE_COLS['price']].median().sort_values(ascending=False).head(5)
        for neigh, median in top5.items():
            print(f"  {neigh}: ${median:.2f}")
    
    return {}

