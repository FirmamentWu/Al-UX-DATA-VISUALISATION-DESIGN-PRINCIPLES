"""场景1: 物理空间的溢价逻辑"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
from pathlib import Path

BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from airbnb_analysis.models.statistical_tests import test_privacy_premium, compute_correlation
from airbnb_analysis.models.regression import fit_linear_regression, fit_interaction_model
from airbnb_analysis.models.smoothing import fit_lowess
from airbnb_analysis.visualization.style import save_figure, set_legend_outside
from airbnb_analysis.config.settings import OUTPUT_DIR, ANALYSIS_CONFIG
from airbnb_analysis.config.constants import FEATURE_COLS

def analyze_privacy_premium(df):
    """1.1 隐私溢价分析"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    room_types = df[FEATURE_COLS['room_type']].dropna().unique()
    room_types_clean = [rt for rt in room_types if pd.notna(rt)]
    df_room = df[df[FEATURE_COLS['room_type']].isin(room_types_clean)]
    
    # Boxplot
    sns.boxplot(
        data=df_room, 
        x=FEATURE_COLS['room_type'], 
        y=FEATURE_COLS['price'], 
        ax=axes[0], 
        palette='Set2'
    )
    axes[0].set_title('Privacy Premium: Entire Home vs Private Room', 
                     fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Room Type', fontsize=12)
    axes[0].set_ylabel('Price ($)', fontsize=12)
    axes[0].tick_params(axis='x', rotation=45)
    
    # Violin plot
    sns.violinplot(
        data=df_room, 
        x=FEATURE_COLS['room_type'], 
        y=FEATURE_COLS['price'], 
        ax=axes[1], 
        palette='Set2', 
        inner='quartile'
    )
    axes[1].set_title('Price Distribution by Room Type', 
                     fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Room Type', fontsize=12)
    axes[1].set_ylabel('Price ($)', fontsize=12)
    axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    save_figure(fig, '1_1_privacy_premium.png', OUTPUT_DIR)
    plt.close()
    
    # 统计检验
    result = test_privacy_premium(df)
    if result:
        print(f"\n隐私溢价分析:")
        print(f"  Entire home 中位数: ${result['median_entire']:.2f}")
        print(f"  Private room 中位数: ${result['median_private']:.2f}")
        print(f"  溢价倍数: {result['premium_ratio']:.2f}x")
        print(f"  Mann-Whitney U 检验 p-value: {result['p_value']:.4f}")
    
    return result

def analyze_capacity_premium(df):
    """1.2 容量溢价分析"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # 数据过滤
    df_cap = df[
        df[FEATURE_COLS['accommodates']].between(1, ANALYSIS_CONFIG['accommodates_max'])
    ].copy()
    price_low = df_cap[FEATURE_COLS['price']].quantile(ANALYSIS_CONFIG['price_quantile_low'])
    price_high = df_cap[FEATURE_COLS['price']].quantile(ANALYSIS_CONFIG['price_quantile_high'])
    df_cap = df_cap[df_cap[FEATURE_COLS['price']].between(price_low, price_high)]
    
    # 散点图
    axes[0].scatter(
        df_cap[FEATURE_COLS['accommodates']], 
        df_cap[FEATURE_COLS['price']], 
        alpha=0.3, s=20, color='steelblue'
    )
    
    # 线性回归
    X = df_cap[[FEATURE_COLS['accommodates']]].values
    y = df_cap[FEATURE_COLS['price']].values
    lr = fit_linear_regression(X, y)
    
    x_line = np.linspace(
        df_cap[FEATURE_COLS['accommodates']].min(),
        df_cap[FEATURE_COLS['accommodates']].max(), 
        100
    )
    y_line = lr.predict(x_line.reshape(-1, 1))
    axes[0].plot(x_line, y_line, 'r-', linewidth=2, 
                label=f'Linear: y={lr.coef_[0]:.2f}x+{lr.intercept_:.2f}')
    
    # LOWESS
    x_lowess, y_lowess = fit_lowess(
        df_cap[FEATURE_COLS['accommodates']].values,
        df_cap[FEATURE_COLS['price']].values,
        frac=ANALYSIS_CONFIG['lowess_frac']
    )
    axes[0].plot(x_lowess, y_lowess, 'g-', linewidth=2, label='LOWESS')
    
    axes[0].set_xlabel('Accommodates (Capacity)', fontsize=12)
    axes[0].set_ylabel('Price ($)', fontsize=12)
    axes[0].set_title('Capacity Premium: Linear Pricing Relationship', 
                     fontsize=14, fontweight='bold')
    set_legend_outside(axes[0])
    axes[0].grid(True, alpha=0.3)
    
    # Boxplot
    df_cap_grouped = df_cap[df_cap[FEATURE_COLS['accommodates']].between(1, 8)].copy()
    sns.boxplot(
        data=df_cap_grouped, 
        x=FEATURE_COLS['accommodates'], 
        y=FEATURE_COLS['price'], 
        ax=axes[1], 
        palette='viridis'
    )
    axes[1].set_xlabel('Accommodates', fontsize=12)
    axes[1].set_ylabel('Price ($)', fontsize=12)
    axes[1].set_title('Price Distribution by Capacity', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    save_figure(fig, '1_2_capacity_premium.png', OUTPUT_DIR)
    plt.close()
    
    # 相关性检验
    corr_result = compute_correlation(
        df_cap[FEATURE_COLS['accommodates']],
        df_cap[FEATURE_COLS['price']]
    )
    print(f"\n容量溢价分析:")
    print(f"  Spearman 相关系数: {corr_result['correlation']:.4f} "
          f"(p={corr_result['p_value']:.4f})")
    print(f"  线性回归系数: {lr.coef_[0]:.2f} "
          f"(每增加1人，价格增加${lr.coef_[0]:.2f})")
    
    return {'lr': lr, 'correlation': corr_result}

def analyze_interaction_effect(df):
    """1.3 交互效应分析"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # 数据过滤
    df_cap = df[
        df[FEATURE_COLS['accommodates']].between(1, ANALYSIS_CONFIG['accommodates_max'])
    ].copy()
    price_low = df_cap[FEATURE_COLS['price']].quantile(ANALYSIS_CONFIG['price_quantile_low'])
    price_high = df_cap[FEATURE_COLS['price']].quantile(ANALYSIS_CONFIG['price_quantile_high'])
    df_cap = df_cap[df_cap[FEATURE_COLS['price']].between(price_low, price_high)]
    
    # Facet scatter plot
    for room_type in ['Entire home/apt', 'Private room']:
        df_subset = df_cap[df_cap[FEATURE_COLS['room_type']] == room_type]
        if len(df_subset) > 0:
            axes[0].scatter(
                df_subset[FEATURE_COLS['accommodates']], 
                df_subset[FEATURE_COLS['price']], 
                alpha=0.4, s=30, label=room_type
            )
            
            # Regression line for each room type
            X_sub = df_subset[[FEATURE_COLS['accommodates']]].values
            y_sub = df_subset[FEATURE_COLS['price']].values
            if len(X_sub) > 1:
                lr_sub = fit_linear_regression(X_sub, y_sub)
                x_line_sub = np.linspace(
                    df_subset[FEATURE_COLS['accommodates']].min(), 
                    df_subset[FEATURE_COLS['accommodates']].max(), 
                    100
                )
                y_line_sub = lr_sub.predict(x_line_sub.reshape(-1, 1))
                axes[0].plot(x_line_sub, y_line_sub, '--', linewidth=2, alpha=0.8)
    
    axes[0].set_xlabel('Accommodates', fontsize=12)
    axes[0].set_ylabel('Price ($)', fontsize=12)
    axes[0].set_title('Privacy Premium Independent of Capacity', 
                     fontsize=14, fontweight='bold')
    set_legend_outside(axes[0])
    axes[0].grid(True, alpha=0.3)
    
    # Grouped boxplot
    df_interaction = df_cap[
        df_cap[FEATURE_COLS['room_type']].isin(['Entire home/apt', 'Private room'])
    ].copy()
    df_interaction = df_interaction[
        df_interaction[FEATURE_COLS['accommodates']].between(1, 6)
    ]
    sns.boxplot(
        data=df_interaction, 
        x=FEATURE_COLS['accommodates'], 
        y=FEATURE_COLS['price'], 
        hue=FEATURE_COLS['room_type'], 
        ax=axes[1], 
        palette='Set2'
    )
    axes[1].set_xlabel('Accommodates', fontsize=12)
    axes[1].set_ylabel('Price ($)', fontsize=12)
    axes[1].set_title('Price by Capacity and Room Type', fontsize=14, fontweight='bold')
    set_legend_outside(axes[1], bbox_to_anchor=(1.15, 0.5))
    
    plt.tight_layout()
    save_figure(fig, '1_3_interaction_effect.png', OUTPUT_DIR)
    plt.close()
    
    # 交互效应模型
    df_model = df_cap[
        df_cap[FEATURE_COLS['room_type']].isin(['Entire home/apt', 'Private room'])
    ].copy()
    df_model['is_entire'] = (df_model[FEATURE_COLS['room_type']] == 'Entire home/apt').astype(int)
    
    model = fit_interaction_model(df_model, 'price ~ accommodates * is_entire')
    print(f"\n交互效应模型:")
    print(model.summary().tables[1])
    
    return {'model': model}

def run_scenario1(df):
    """运行场景1的所有分析"""
    print("\n" + "="*80)
    print("场景1: 物理空间的溢价逻辑")
    print("="*80)
    
    result1 = analyze_privacy_premium(df)
    result2 = analyze_capacity_premium(df)
    result3 = analyze_interaction_effect(df)
    
    return {
        'privacy_premium': result1,
        'capacity_premium': result2,
        'interaction': result3
    }
