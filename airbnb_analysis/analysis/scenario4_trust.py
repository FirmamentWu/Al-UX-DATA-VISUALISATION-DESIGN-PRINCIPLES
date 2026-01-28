"""场景4: 信任的货币化"""
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

def run_scenario4(df):
    """运行场景4的所有分析"""
    print("\n" + "="*80)
    print("场景4: 信任的货币化")
    print("="*80)
    
        # 4.1 评分分布：阈值效应
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    df_rating = df[df[FEATURE_COLS['review_rating']].notna()].copy()
    
    # Histogram
    axes[0].hist(df_rating[FEATURE_COLS['review_rating']], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
    axes[0].axvline(df_rating[FEATURE_COLS['review_rating']].median(), color='red', linestyle='--', 
                   linewidth=2, label=f'Median: {df_rating[FEATURE_COLS["review_rating"]].median():.2f}')
    axes[0].axvline(4.7, color='orange', linestyle='--', linewidth=2, label='Threshold: 4.7')
    axes[0].set_xlabel('Review Score Rating', fontsize=12)
    axes[0].set_ylabel('Frequency', fontsize=12)
    axes[0].set_title('Rating Distribution: Trust Threshold Effect', fontsize=14, fontweight='bold')
    set_legend_outside(axes[0])
    axes[0].grid(True, alpha=0.3)
    
    # KDE
    rating_clean = df_rating[FEATURE_COLS['review_rating']].dropna()
    if len(rating_clean) > 10:
        kde = fit_kde(rating_clean)
        x_kde = np.linspace(rating_clean.min(), rating_clean.max(), 200)
        axes[1].plot(x_kde, kde(x_kde), 'b-', linewidth=2, label='KDE')
        axes[1].fill_between(x_kde, kde(x_kde), alpha=0.3)
        axes[1].axvline(4.7, color='orange', linestyle='--', linewidth=2, label='Threshold: 4.7')
        axes[1].set_xlabel('Review Score Rating', fontsize=12)
        axes[1].set_ylabel('Density', fontsize=12)
        axes[1].set_title('Rating Density: High Trust Concentration', fontsize=14, fontweight='bold')
        set_legend_outside(axes[1])
        axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_figure(fig, '4_1_rating_distribution.png', OUTPUT_DIR)
    plt.close()
    
    print(f"\n评分分布分析:")
    print(f"  评分中位数: {df_rating[FEATURE_COLS['review_rating']].median():.2f}")
    print(f"  评分 > 4.7 的比例: {(df_rating[FEATURE_COLS['review_rating']] > 4.7).mean()*100:.1f}%")

    # 4.2 评分 vs 入住率
    fig, ax = plt.subplots(figsize=(12, 8))
    
    df_rating_occ = df[df[FEATURE_COLS['review_rating']].notna() & df[FEATURE_COLS['availability']].notna()].copy()
    df_rating_occ = df_rating_occ[df_rating_occ[FEATURE_COLS['review_rating']].between(3, 5)]
    
    ax.scatter(df_rating_occ[FEATURE_COLS['review_rating']], df_rating_occ[FEATURE_COLS['availability']], 
              alpha=0.3, s=20, color='steelblue')
    
    # LOWESS
    x_lowess, y_lowess = fit_lowess(
        df_rating_occ[FEATURE_COLS['review_rating']].values,
        df_rating_occ[FEATURE_COLS['availability']].values,
        frac=ANALYSIS_CONFIG['lowess_frac']
    )
    ax.plot(x_lowess, y_lowess, 'r-', linewidth=3, label='LOWESS')
    
    # Linear regression
    X = df_rating_occ[[FEATURE_COLS['review_rating']]].values
    y = df_rating_occ[FEATURE_COLS['availability']].values
    lr = fit_linear_regression(X, y)
    x_line = np.linspace(df_rating_occ[FEATURE_COLS['review_rating']].min(), 
                         df_rating_occ[FEATURE_COLS['review_rating']].max(), 100)
    y_line = lr.predict(x_line.reshape(-1, 1))
    ax.plot(x_line, y_line, 'g--', linewidth=2, label=f'Linear: y={lr.coef_[0]:.1f}x+{lr.intercept_:.1f}')
    
    ax.set_xlabel('Review Score Rating', fontsize=12)
    ax.set_ylabel('Availability (days/year)', fontsize=12)
    ax.set_title('Trust Monetization: Rating vs Occupancy', fontsize=14, fontweight='bold')
    set_legend_outside(ax)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_figure(fig, '4_2_rating_vs_occupancy.png', OUTPUT_DIR)
    plt.close()
    
    corr_result = compute_correlation(
        df_rating_occ[FEATURE_COLS['review_rating']],
        df_rating_occ[FEATURE_COLS['availability']]
    )
    print(f"\n评分 vs 入住率:")
    print(f"  Spearman 相关系数: {corr_result['correlation']:.4f} (p={corr_result['p_value']:.4f})")
    
    # 4.3 超赞房东对比
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    df_superhost = df[df[FEATURE_COLS['superhost']].notna()].copy()
    df_superhost[FEATURE_COLS['superhost']] = df_superhost[FEATURE_COLS['superhost']].astype(str)
    
    sns.boxplot(data=df_superhost, x=FEATURE_COLS['superhost'], y=FEATURE_COLS['availability'], 
               ax=axes[0], palette='Set1')
    axes[0].set_title('Superhost vs Regular Host: Occupancy', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Is Superhost', fontsize=12)
    axes[0].set_ylabel('Availability (days/year)', fontsize=12)
    
    sns.boxplot(data=df_superhost, x=FEATURE_COLS['superhost'], y=FEATURE_COLS['price'], 
               ax=axes[1], palette='Set1')
    axes[1].set_title('Superhost vs Regular Host: Price', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Is Superhost', fontsize=12)
    axes[1].set_ylabel('Price ($)', fontsize=12)
    
    plt.tight_layout()
    save_figure(fig, '4_3_superhost_comparison.png', OUTPUT_DIR)
    plt.close()
    
    # 统计检验
    superhost_occ = df_superhost[df_superhost[FEATURE_COLS['superhost']] == 't'][FEATURE_COLS['availability']].dropna()
    regular_occ = df_superhost[df_superhost[FEATURE_COLS['superhost']] == 'f'][FEATURE_COLS['availability']].dropna()
    
    if len(superhost_occ) > 0 and len(regular_occ) > 0:
        stat, p_value = mannwhitneyu(superhost_occ, regular_occ, alternative='two-sided')
        print(f"\n超赞房东对比:")
        print(f"  超赞房东空置天数中位数: {superhost_occ.median():.1f}")
        print(f"  普通房东空置天数中位数: {regular_occ.median():.1f}")
        print(f"  Mann-Whitney U 检验 p-value: {p_value:.4f}")
    
    return {}

