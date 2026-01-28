"""外推性验证可视化 - 展示NYC规律在其他城市的适用性"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from airbnb_analysis.config.settings import MULTI_CITY_RESULTS_DIR, OUTPUT_DIR
from airbnb_analysis.config.constants import SCENARIOS
from airbnb_analysis.visualization.style import setup_style, save_figure, set_legend_outside

def load_comparison_data():
    """加载对比数据"""
    summary_file = MULTI_CITY_RESULTS_DIR / "comparison_summary.json"
    all_results_file = MULTI_CITY_RESULTS_DIR / "all_cities_results.json"
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    with open(all_results_file, 'r', encoding='utf-8') as f:
        all_results = json.load(f)
    
    return summary, all_results

def create_generalizability_dashboard():
    """创建外推性验证仪表板"""
    print("="*80)
    print("生成外推性验证可视化")
    print("="*80)
    
    summary, all_results = load_comparison_data()
    
    # 1. 外推性验证主图：显示每个规律的可外推性
    create_generalizability_chart(summary)
    
    # 2. 检验方法说明图：展示如何检验外推性
    create_validation_method_chart(summary, all_results)
    
    # 3. 效应量一致性图：展示各城市效应量的一致性
    create_effect_consistency_chart(all_results)
    
    print("\n✓ 所有可视化已生成")

def create_generalizability_chart(summary):
    """创建外推性验证主图"""
    print("\n1. 生成外推性验证主图...")
    
    consistency_data = summary['consistency']
    df = pd.DataFrame(consistency_data)
    
    # 创建测试标签
    df['test_label'] = df.apply(
        lambda row: f"{SCENARIOS[row['scenario']]}\n{row['test_name']}", 
        axis=1
    )
    
    # 分类：强外推(100%)、高外推(80-99%)、部分外推(<80%)
    df['generalizability'] = df['significance_rate'].apply(
        lambda x: '强外推性 (100%)' if x == 1.0 
        else '高外推性 (80-99%)' if x >= 0.8 
        else '部分外推性 (<80%)'
    )
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # 颜色映射
    color_map = {
        '强外推性 (100%)': '#2ecc71',  # 绿色
        '高外推性 (80-99%)': '#3498db',  # 蓝色
        '部分外推性 (<80%)': '#e74c3c'  # 红色
    }
    
    # 绘制水平条形图
    y_pos = np.arange(len(df))
    colors = [color_map[cat] for cat in df['generalizability']]
    
    bars = ax.barh(y_pos, df['significance_rate'] * 100, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # 添加数值标签（英文）
    for i, (idx, row) in enumerate(df.iterrows()):
        rate = row['significance_rate'] * 100
        significant = row['significant_cities']
        total = row['total_cities']
        # 如果只有少数城市有数据，显示更详细的标签
        if total < 11:
            label_text = f'{significant}/{total} cities (limited data)'
        else:
            label_text = f'{significant}/{total} cities'
        ax.text(rate + 2, i, label_text, 
                va='center', fontsize=10, fontweight='bold')
    
    # 创建英文测试标签
    test_name_map = {
        'capacity_premium': 'Capacity Premium',
        'privacy_premium': 'Privacy Premium',
        'region_comparison': 'Region Comparison',
        'scale_price': 'Scale Price Premium',
        'scale_occupancy': 'Scale Occupancy Premium',
        'rating_occupancy': 'Rating-Occupancy',
        'superhost_comparison': 'Superhost Premium',
        'ltm_price': 'LTM-Price',
        'historical_price': 'Historical-Price',
        'ltm_occupancy': 'LTM-Occupancy'
    }
    
    scenario_name_map = {
        1: 'Physical Space',
        2: 'Location Premium',
        3: 'Scale Premium',
        4: 'Trust Monetization',
        5: 'Activity Signal'
    }
    
    # 创建英文标签
    df['test_label_en'] = df.apply(
        lambda row: f"{scenario_name_map[row['scenario']]}\n{test_name_map.get(row['test_name'], row['test_name'])}", 
        axis=1
    )
    
    # 设置y轴标签
    ax.set_yticks(y_pos)
    ax.set_yticklabels(df['test_label_en'], fontsize=10)
    
    # 设置x轴
    ax.set_xlabel('Significant Cities Ratio (%)', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 110)
    ax.axvline(x=80, color='gray', linestyle='--', linewidth=2, alpha=0.5, label='Generalizability Threshold (80%)')
    
    # 标题
    ax.set_title('Generalizability Validation of NYC Patterns\n(Based on Statistical Tests in 11 Cities)', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # 图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=color_map['强外推性 (100%)'], label='Strong Generalizability (100% cities)'),
        Patch(facecolor=color_map['高外推性 (80-99%)'], label='High Generalizability (80-99% cities)'),
        Patch(facecolor=color_map['部分外推性 (<80%)'], label='Partial Generalizability (<80% cities)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11, framealpha=0.9)
    
    # 网格
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    save_figure(fig, 'generalizability_validation.png', OUTPUT_DIR)
    plt.close()
    print("  ✓ 已保存: generalizability_validation.png")

def create_validation_method_chart(summary, all_results):
    """创建检验方法说明图"""
    print("\n2. 生成检验方法说明图...")
    
    consistency_data = summary['consistency']
    df = pd.DataFrame(consistency_data)
    
    # 提取每个城市的详细结果
    city_test_results = []
    for city_name, city_data in all_results.items():
        if 'error' in city_data:
            continue
        
        for scenario_num in range(1, 6):
            scenario_key = f'scenario{scenario_num}'
            scenario_data = city_data.get(scenario_key, {})
            
            for test_name, test_result in scenario_data.items():
                if isinstance(test_result, dict) and 'p_value' in test_result:
                    city_test_results.append({
                        'city': city_name,
                        'scenario': scenario_num,
                        'test_name': test_name,
                        'significant': test_result.get('significant', False),
                        'p_value': test_result.get('p_value', 1.0),
                    })
    
    df_city = pd.DataFrame(city_test_results)
    
    # 创建测试标识
    df['test_id'] = df.apply(
        lambda row: f"S{row['scenario']}: {row['test_name']}", 
        axis=1
    )
    
    # 合并数据
    df_city['test_id'] = df_city.apply(
        lambda row: f"S{row['scenario']}: {row['test_name']}", 
        axis=1
    )
    
    # 计算每个测试在每个城市的显著性
    pivot_data = df_city.pivot_table(
        index='test_id', 
        columns='city', 
        values='significant',
        aggfunc=lambda x: 1 if any(x) else 0
    )
    
    # 填充NaN并转换为整数
    pivot_data = pivot_data.fillna(0).astype(int)
    
    # 创建热力图
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # 按显著性率排序
    test_order = df.sort_values('significance_rate', ascending=True)['test_id'].tolist()
    pivot_data = pivot_data.reindex(test_order)
    
    # 绘制热力图
    sns.heatmap(
        pivot_data, 
        annot=True, 
        fmt='d',
        cmap='RdYlGn',
        cbar_kws={'label': 'Significant (1) / Not Significant (0)'},
        ax=ax,
        linewidths=0.5,
        linecolor='white',
        vmin=0,
        vmax=1
    )
    
    ax.set_title('Generalizability Validation: Statistical Significance Matrix\n(Green=Significant, Red=Not Significant)', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('City', fontsize=12, fontweight='bold')
    ax.set_ylabel('Patterns Found in NYC', fontsize=12, fontweight='bold')
    # 简化标签，避免中文显示问题
    ax.set_yticklabels([f"S{int(t.split(':')[0][1])}: {t.split(':')[1].strip()}" 
                        for t in test_order], rotation=0, ha='right', fontsize=9)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
    
    plt.tight_layout()
    save_figure(fig, 'validation_method_matrix.png', OUTPUT_DIR)
    plt.close()
    print("  ✓ 已保存: validation_method_matrix.png")

def create_effect_consistency_chart(all_results):
    """创建效应量一致性图"""
    print("\n3. 生成效应量一致性图...")
    
    # 提取相关系数数据
    corr_data = []
    premium_data = []
    
    for city_name, city_data in all_results.items():
        if 'error' in city_data:
            continue
        
        for scenario_num in range(1, 6):
            scenario_key = f'scenario{scenario_num}'
            scenario_data = city_data.get(scenario_key, {})
            
            for test_name, test_result in scenario_data.items():
                if isinstance(test_result, dict):
                    if 'correlation' in test_result and test_result['correlation'] is not None:
                        corr_data.append({
                            'city': city_name,
                            'scenario': scenario_num,
                            'test_name': test_name,
                            'correlation': test_result['correlation'],
                            'scenario_name': SCENARIOS.get(scenario_num, f'场景{scenario_num}')
                        })
                    if 'premium_ratio' in test_result and test_result['premium_ratio'] is not None:
                        premium_data.append({
                            'city': city_name,
                            'scenario': scenario_num,
                            'test_name': test_name,
                            'premium_ratio': test_result['premium_ratio'],
                            'scenario_name': SCENARIOS.get(scenario_num, f'场景{scenario_num}')
                        })
    
    if not corr_data and not premium_data:
        print("  ⚠ 没有效应量数据")
        return
    
    # 创建图形
    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    
    # 左图：相关系数分布
    if corr_data:
        df_corr = pd.DataFrame(corr_data)
        # 只显示有多个城市的测试
        test_counts = df_corr.groupby('test_name')['city'].nunique()
        valid_tests = test_counts[test_counts >= 3].index
        
        if len(valid_tests) > 0:
            df_corr_filtered = df_corr[df_corr['test_name'].isin(valid_tests)]
            
            # 映射测试名称到英文
            test_name_map = {
                'capacity_premium': 'Capacity Premium',
                'rating_occupancy': 'Rating-Occupancy',
                'ltm_price': 'LTM-Price',
                'historical_price': 'Historical-Price',
                'ltm_occupancy': 'LTM-Occupancy'
            }
            df_corr_filtered['test_name_en'] = df_corr_filtered['test_name'].map(test_name_map).fillna(df_corr_filtered['test_name'])
            
            sns.boxplot(
                data=df_corr_filtered, 
                x='test_name_en', 
                y='correlation',
                ax=axes[0],
                palette='Set2'
            )
            axes[0].axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
            axes[0].set_title('Cross-City Consistency of Effect Sizes (Correlation)', 
                             fontsize=13, fontweight='bold', pad=10)
            axes[0].set_xlabel('Test Type', fontsize=12)
            axes[0].set_ylabel('Correlation Coefficient', fontsize=12)
            axes[0].tick_params(axis='x', rotation=45)
            axes[0].grid(axis='y', alpha=0.3)
    
    # 右图：溢价倍数分布
    if premium_data:
        df_premium = pd.DataFrame(premium_data)
        test_counts = df_premium.groupby('test_name')['city'].nunique()
        valid_tests = test_counts[test_counts >= 3].index
        
        if len(valid_tests) > 0:
            df_premium_filtered = df_premium[df_premium['test_name'].isin(valid_tests)]
            
            # 映射测试名称到英文
            test_name_map = {
                'privacy_premium': 'Privacy Premium'
            }
            df_premium_filtered['test_name_en'] = df_premium_filtered['test_name'].map(test_name_map).fillna(df_premium_filtered['test_name'])
            
            sns.boxplot(
                data=df_premium_filtered, 
                x='test_name_en', 
                y='premium_ratio',
                ax=axes[1],
                palette='Set3'
            )
            axes[1].axhline(y=1, color='black', linestyle='--', linewidth=1, alpha=0.5, label='No Premium Baseline')
            axes[1].set_title('Cross-City Consistency of Effect Sizes (Premium Ratio)', 
                             fontsize=13, fontweight='bold', pad=10)
            axes[1].set_xlabel('Test Type', fontsize=12)
            axes[1].set_ylabel('Premium Ratio', fontsize=12)
            axes[1].tick_params(axis='x', rotation=45)
            axes[1].grid(axis='y', alpha=0.3)
            axes[1].legend()
    
    plt.tight_layout()
    save_figure(fig, 'effect_consistency.png', OUTPUT_DIR)
    plt.close()
    print("  ✓ 已保存: effect_consistency.png")

if __name__ == "__main__":
    setup_style()
    create_generalizability_dashboard()
