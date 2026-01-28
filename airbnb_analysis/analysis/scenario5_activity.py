"""场景5: 活跃度即需求的实时信号"""
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

def run_scenario5(df):
    """运行场景5的所有分析"""
    print("\n" + "="*80)
    print("场景5: 活跃度即需求的实时信号")
    print("="*80)
    
    # 5.1 历史评论 vs 近一年评论：脱钩
    fig, ax = plt.subplots(figsize=(12, 8))
    
    df_reviews = df[df[FEATURE_COLS['reviews_total']].notna() & df[FEATURE_COLS['reviews_ltm']].notna()].copy()
    df_reviews = df_reviews[df_reviews[FEATURE_COLS['reviews_total']] <= df_reviews[FEATURE_COLS['reviews_total']].quantile(0.95)]
    df_reviews = df_reviews[df_reviews[FEATURE_COLS['reviews_ltm']] <= df_reviews[FEATURE_COLS['reviews_ltm']].quantile(0.95)]

    ax.scatter(df_reviews[FEATURE_COLS['reviews_total']], df_reviews[FEATURE_COLS['reviews_ltm']], 
          alpha=0.3, s=20, color='steelblue')

# 添加对角线参考线
    max_val = max(df_reviews[FEATURE_COLS['reviews_total']].max(), df_reviews[FEATURE_COLS['reviews_ltm']].max())
    ax.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Perfect Correlation', alpha=0.5)

# 标注异常区域（历史高但LTM低）
    high_hist_low_ltm = df_reviews[(df_reviews[FEATURE_COLS['reviews_total']] > df_reviews[FEATURE_COLS['reviews_total']].quantile(0.75)) & 
                                (df_reviews[FEATURE_COLS['reviews_ltm']] < df_reviews[FEATURE_COLS['reviews_ltm']].quantile(0.25))]
    if len(high_hist_low_ltm) > 0:
        ax.scatter(high_hist_low_ltm[FEATURE_COLS['reviews_total']], high_hist_low_ltm[FEATURE_COLS['reviews_ltm']], 
                  alpha=0.6, s=30, color='red', label='High History, Low LTM')

    ax.set_xlabel('Total Reviews (Historical)', fontsize=12)
    ax.set_ylabel('Reviews Last 12 Months (LTM)', fontsize=12)
    ax.set_title('Decoupling: Historical vs Recent Activity', fontsize=14, fontweight='bold')
    set_legend_outside(ax)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_figure(fig, '5_1_reviews_decoupling.png', OUTPUT_DIR)
    plt.close()

    corr_result = compute_correlation(df_reviews[FEATURE_COLS['reviews_total']], df_reviews[FEATURE_COLS['reviews_ltm']])
    print(f"\n历史评论 vs 近一年评论:")
    print(f"  Spearman 相关系数: {corr_result['correlation']:.4f} (p={corr_result['p_value']:.4f})")
    print(f"  历史高但LTM低的样本数: {len(high_hist_low_ltm)} ({len(high_hist_low_ltm)/len(df_reviews)*100:.1f}%)")

# 5.2 近一年评论 vs 价格
    fig, ax = plt.subplots(figsize=(12, 8))

    df_ltm_price = df[df[FEATURE_COLS['reviews_ltm']].notna() & df[FEATURE_COLS[FEATURE_COLS['price']]].notna()].copy()
    df_ltm_price = df_ltm_price[df_ltm_price[FEATURE_COLS['reviews_ltm']] <= df_ltm_price[FEATURE_COLS['reviews_ltm']].quantile(0.95)]
    df_ltm_price = df_ltm_price[df_ltm_price[FEATURE_COLS['price']].between(df_ltm_price[FEATURE_COLS['price']].quantile(0.01), 
                                                           df_ltm_price[FEATURE_COLS['price']].quantile(0.99))]

    ax.scatter(df_ltm_price[FEATURE_COLS['reviews_ltm']], df_ltm_price[FEATURE_COLS['price']], 
          alpha=0.3, s=20, color='steelblue')

# LOWESS
    sorted_idx = np.argsort(df_ltm_price[FEATURE_COLS['reviews_ltm']].values)
    x_sorted = df_ltm_price[FEATURE_COLS['reviews_ltm']].values[sorted_idx]
    y_sorted = df_ltm_price[FEATURE_COLS['price']].values[sorted_idx]
    x_lowess, y_lowess = fit_lowess(y_sorted, x_sorted, frac=ANALYSIS_CONFIG["lowess_frac"])
    ax.plot(x_lowess, y_lowess, 'r-', linewidth=3, label='LOWESS')

# Log transformation regression
    df_ltm_price['log_ltm'] = np.log1p(df_ltm_price[FEATURE_COLS['reviews_ltm']])
    X = df_ltm_price[['log_ltm']].values
    y = df_ltm_price[FEATURE_COLS['price']].values
    lr = LinearRegression()
    lr.fit(X, y)
    x_line = np.linspace(df_ltm_price[FEATURE_COLS['reviews_ltm']].min(), 
                     df_ltm_price[FEATURE_COLS['reviews_ltm']].max(), 100)
    y_line = lr.predict(np.log1p(x_line).reshape(-1, 1))
    ax.plot(x_line, y_line, 'g--', linewidth=2, label='Log-linear fit')

    ax.set_xlabel('Reviews Last 12 Months (LTM)', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.set_title('Real-time Pricing: LTM Reviews vs Price', fontsize=14, fontweight='bold')
    set_legend_outside(ax)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_figure(fig, '5_2_ltm_vs_price.png', OUTPUT_DIR)
    plt.close()

    corr_result = compute_correlation(df_ltm_price[FEATURE_COLS['reviews_ltm']], df_ltm_price[FEATURE_COLS['price']])
    print(f"\n近一年评论 vs 价格:")
    print(f"  Spearman 相关系数: {corr_result['correlation']:.4f} (p={corr_result['p_value']:.4f})")

# 5.3 历史评论 vs 价格（对照组）
    fig, ax = plt.subplots(figsize=(12, 8))

    df_hist_price = df[df[FEATURE_COLS['reviews_total']].notna() & df[FEATURE_COLS['price']].notna()].copy()
    df_hist_price = df_hist_price[df_hist_price[FEATURE_COLS['reviews_total']] <= df_hist_price[FEATURE_COLS['reviews_total']].quantile(0.95)]
    df_hist_price = df_hist_price[df_hist_price[FEATURE_COLS['price']].between(df_hist_price[FEATURE_COLS['price']].quantile(0.01), 
                                                               df_hist_price[FEATURE_COLS['price']].quantile(0.99))]

    ax.scatter(df_hist_price[FEATURE_COLS['reviews_total']], df_hist_price[FEATURE_COLS['price']], 
          alpha=0.3, s=20, color='lightcoral')

# LOWESS
    sorted_idx = np.argsort(df_hist_price[FEATURE_COLS['reviews_total']].values)
    x_sorted = df_hist_price[FEATURE_COLS['reviews_total']].values[sorted_idx]
    y_sorted = df_hist_price[FEATURE_COLS['price']].values[sorted_idx]
    x_lowess, y_lowess = fit_lowess(y_sorted, x_sorted, frac=ANALYSIS_CONFIG["lowess_frac"])
    ax.plot(x_lowess, y_lowess, 'r-', linewidth=3, label='LOWESS')

    ax.set_xlabel('Total Reviews (Historical)', fontsize=12)
    ax.set_ylabel('Price ($)', fontsize=12)
    ax.set_title('Control Group: Historical Reviews vs Price (Weaker Relationship)', 
            fontsize=14, fontweight='bold')
    set_legend_outside(ax)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_figure(fig, '5_3_historical_vs_price.png', OUTPUT_DIR)
    plt.close()

    corr_result_hist = compute_correlation(df_hist_price[FEATURE_COLS['reviews_total']], df_hist_price[FEATURE_COLS['price']])
    print(f"\n历史评论 vs 价格 (对照组):")
    print(f"  Spearman 相关系数: {corr_result_hist['correlation']:.4f} (p={corr_result_hist['p_value']:.4f})")
    # 注意：需要从之前的corr_result获取LTM相关系数
    print(f"  对比: LTM相关系数 vs 历史相关系数")

# 5.4 近一年评论 vs 入住率
    fig, ax = plt.subplots(figsize=(12, 8))

    df_ltm_occ = df[df[FEATURE_COLS['reviews_ltm']].notna() & df[FEATURE_COLS['availability']].notna()].copy()
    df_ltm_occ = df_ltm_occ[df_ltm_occ[FEATURE_COLS['reviews_ltm']] <= df_ltm_occ[FEATURE_COLS['reviews_ltm']].quantile(0.95)]

    ax.scatter(df_ltm_occ[FEATURE_COLS['reviews_ltm']], df_ltm_occ[FEATURE_COLS['availability']], 
          alpha=0.3, s=20, color='steelblue')

# LOWESS
    sorted_idx = np.argsort(df_ltm_occ[FEATURE_COLS['reviews_ltm']].values)
    x_sorted = df_ltm_occ[FEATURE_COLS['reviews_ltm']].values[sorted_idx]
    y_sorted = df_ltm_occ[FEATURE_COLS['availability']].values[sorted_idx]
    x_lowess, y_lowess = fit_lowess(y_sorted, x_sorted, frac=ANALYSIS_CONFIG["lowess_frac"])
    ax.plot(x_lowess, y_lowess, 'r-', linewidth=3, label='LOWESS')

# Linear regression
    X = df_ltm_occ[[FEATURE_COLS['reviews_ltm']]].values
    y = df_ltm_occ[FEATURE_COLS['availability']].values
    lr = LinearRegression()
    lr.fit(X, y)
    x_line = np.linspace(df_ltm_occ[FEATURE_COLS['reviews_ltm']].min(), 
                     df_ltm_occ[FEATURE_COLS['reviews_ltm']].max(), 100)
    y_line = lr.predict(x_line.reshape(-1, 1))
    ax.plot(x_line, y_line, 'g--', linewidth=2, label=f'Linear: y={lr.coef_[0]:.2f}x+{lr.intercept_:.1f}')

    ax.set_xlabel('Reviews Last 12 Months (LTM)', fontsize=12)
    ax.set_ylabel('Availability (days/year)', fontsize=12)
    ax.set_title('Activity as Demand Signal: LTM Reviews vs Occupancy', 
            fontsize=14, fontweight='bold')
    set_legend_outside(ax)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_figure(fig, '5_4_ltm_vs_occupancy.png', OUTPUT_DIR)
    plt.close()

    corr_result = compute_correlation(df_ltm_occ[FEATURE_COLS['reviews_ltm']], df_ltm_occ[FEATURE_COLS['availability']])
    print(f"\n近一年评论 vs 入住率:")
    print(f"  Spearman 相关系数: {corr_result['correlation']:.4f} (p={corr_result['p_value']:.4f})")


    return {}

