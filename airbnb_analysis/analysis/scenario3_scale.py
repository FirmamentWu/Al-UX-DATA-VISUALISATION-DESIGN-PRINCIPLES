"""场景3: 运营专业化带来的规模溢价"""
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

def run_scenario3(df):
    """运行场景3的所有分析"""
    print("\n" + "="*80)
    print("场景3: 运营专业化带来的规模溢价")
    print("="*80)
    
    # 3.1 房东规模 → 价格
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    df_scale = df[df['host_listings_count_binned'].notna()].copy()

    sns.boxplot(data=df_scale, x='host_listings_count_binned', y=FEATURE_COLS['price'], 
               ax=axes[0], palette='mako', order=['1', '2-3', '4-5', '>5'])
    axes[0].set_title('Scale Premium: Price by Host Listing Count', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Host Listings Count', fontsize=12)
    axes[0].set_ylabel('Price ($)', fontsize=12)
    
    sns.violinplot(data=df_scale, x='host_listings_count_binned', y=FEATURE_COLS['price'], 
                  ax=axes[1], palette='mako', inner='quartile', order=['1', '2-3', '4-5', '>5'])
    axes[1].set_title('Price Distribution by Host Scale', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Host Listings Count', fontsize=12)
    axes[1].set_ylabel('Price ($)', fontsize=12)
    
    plt.tight_layout()
    save_figure(fig, '3_1_scale_premium_price.png', OUTPUT_DIR)
    plt.close()
    
    # 统计检验
    result = test_group_differences(df_scale, 'host_listings_count_binned', FEATURE_COLS['price'])
    if result:
        print(f"\n规模溢价分析 (价格):")
        print(f"  Kruskal-Wallis 检验 p-value: {result['p_value']:.4f}")
        print(f"  各规模组价格中位数:")
        for scale, median in result['medians'].items():
            print(f"    {scale}: ${median:.2f}")
    
    # 3.2 房东规模 → 入住率
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    sns.boxplot(data=df_scale, x='host_listings_count_binned', y=FEATURE_COLS['availability'], 
               ax=axes[0], palette='rocket', order=['1', '2-3', '4-5', '>5'])
    axes[0].set_title('Scale Effect on Occupancy: Availability by Host Scale', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Host Listings Count', fontsize=12)
    axes[0].set_ylabel('Availability (days/year)', fontsize=12)
    
    sns.violinplot(data=df_scale, x='host_listings_count_binned', y=FEATURE_COLS['availability'], 
                  ax=axes[1], palette='rocket', inner='quartile', order=['1', '2-3', '4-5', '>5'])
    axes[1].set_title('Occupancy Stability by Host Scale', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Host Listings Count', fontsize=12)
    axes[1].set_ylabel('Availability (days/year)', fontsize=12)
    
    plt.tight_layout()
    save_figure(fig, '3_2_scale_occupancy.png', OUTPUT_DIR)
    plt.close()
    
    # 统计检验
    result_occ = test_group_differences(df_scale, 'host_listings_count_binned', FEATURE_COLS['availability'])
    if result_occ:
        print(f"\n规模效应分析 (入住率):")
        print(f"  Kruskal-Wallis 检验 p-value: {result_occ['p_value']:.4f}")
        print(f"  各规模组空置天数中位数:")
        for scale, median in result_occ['medians'].items():
            print(f"    {scale}: {median:.1f} days")
    
    # 3.3 Entire home 场景下的规模溢价
    fig, ax = plt.subplots(figsize=(12, 8))
    
    df_entire = df[(df[FEATURE_COLS['room_type']] == 'Entire home/apt') & 
                   (df['host_listings_count_binned'].notna())].copy()
    
    sns.boxplot(data=df_entire, x='host_listings_count_binned', y=FEATURE_COLS['price'], 
               ax=ax, palette='viridis', order=['1', '2-3', '4-5', '>5'])
    ax.set_title('Scale Premium in Entire Home Scenario', fontsize=14, fontweight='bold')
    ax.set_xlabel('Host Listings Count', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    
    plt.tight_layout()
    save_figure(fig, '3_3_entire_home_scale.png', OUTPUT_DIR)
    plt.close()
    
    # 3.4 整租规模 vs 混合规模
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    df_entire_homes = df[df['entire_homes_binned'].notna()].copy()
    
    sns.boxplot(data=df_entire_homes, x='entire_homes_binned', y=FEATURE_COLS['price'], 
               ax=axes[0], palette='plasma', order=['0', '1', '2+'])
    axes[0].set_title('Price by Entire Home Specialization', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Number of Entire Homes', fontsize=12)
    axes[0].set_ylabel('Price ($)', fontsize=12)
    
    sns.boxplot(data=df_entire_homes, x='entire_homes_binned', y=FEATURE_COLS['availability'], 
               ax=axes[1], palette='plasma', order=['0', '1', '2+'])
    axes[1].set_title('Occupancy by Entire Home Specialization', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Number of Entire Homes', fontsize=12)
    axes[1].set_ylabel('Availability (days/year)', fontsize=12)
    
    plt.tight_layout()
    save_figure(fig, '3_4_entire_home_specialization.png', OUTPUT_DIR)
    plt.close()
    
    return {}

