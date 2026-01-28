"""跨城市对比分析模块 - 比较各城市的统计检验结果"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns

BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from airbnb_analysis.config.settings import MULTI_CITY_RESULTS_DIR, OUTPUT_DIR, MULTI_CITY_CONFIG
from airbnb_analysis.config.constants import CITY_NAMES, SCENARIOS

def load_all_results():
    """加载所有城市的分析结果"""
    summary_file = MULTI_CITY_RESULTS_DIR / "all_cities_results.json"
    
    if not summary_file.exists():
        print(f"⚠ 结果文件不存在: {summary_file}")
        return {}
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    return results

def extract_test_results(all_results):
    """提取所有统计检验结果"""
    test_results = []
    
    for city_name, city_result in all_results.items():
        if 'error' in city_result:
            continue
        
        display_name = city_result.get('display_name', city_name)
        sample_size = city_result.get('sample_size', 0)
        
        # 遍历所有场景
        for scenario_num in range(1, 6):
            scenario_key = f'scenario{scenario_num}'
            scenario_data = city_result.get(scenario_key, {})
            
            # 遍历场景中的所有检验
            for test_name, test_result in scenario_data.items():
                if isinstance(test_result, dict) and 'p_value' in test_result:
                    test_results.append({
                        'city': city_name,
                        'city_display': display_name,
                        'scenario': scenario_num,
                        'scenario_name': SCENARIOS.get(scenario_num, f'场景{scenario_num}'),
                        'test_name': test_name,
                        'p_value': test_result['p_value'],
                        'significant': test_result.get('significant', False),
                        'sample_size': sample_size,
                        'correlation': test_result.get('correlation'),
                        'premium_ratio': test_result.get('premium_ratio'),
                        'interaction_coef': test_result.get('interaction_coef'),
                    })
    
    return pd.DataFrame(test_results)

def analyze_significance_consistency(df_results):
    """分析统计显著性的一致性"""
    print("\n" + "="*80)
    print("统计显著性一致性分析")
    print("="*80)
    
    if len(df_results) == 0:
        print("⚠ 没有可用的统计检验结果")
        return pd.DataFrame()
    
    # 按场景和检验分组
    grouped = df_results.groupby(['scenario', 'test_name'])
    
    consistency_summary = []
    
    for (scenario, test_name), group in grouped:
        total_cities = len(group)
        # 确保significant是布尔值或数值（处理字符串"True"/"False"）
        significant_series = group['significant'].astype(str)
        significant_series = significant_series.replace({'True': True, 'False': False, 'true': True, 'false': False})
        significant_series = pd.to_numeric(significant_series, errors='coerce').fillna(0)
        significant_cities = int(significant_series.sum())
        significance_rate = significant_cities / total_cities if total_cities > 0 else 0
        
        consistency_summary.append({
            'scenario': scenario,
            'scenario_name': group['scenario_name'].iloc[0],
            'test_name': test_name,
            'total_cities': total_cities,
            'significant_cities': significant_cities,
            'significance_rate': significance_rate,
            'is_universal': significance_rate >= 0.8,  # 80%以上城市显著认为是普遍规律
        })
    
    consistency_df = pd.DataFrame(consistency_summary)
    
    print("\n各检验的显著性一致性:")
    for _, row in consistency_df.iterrows():
        status = "✓ 普遍规律" if row['is_universal'] else "部分城市"
        print(f"  {row['scenario_name']} - {row['test_name']}: "
              f"{row['significant_cities']}/{row['total_cities']} ({row['significance_rate']*100:.1f}%) {status}")
    
    return consistency_df

def analyze_effect_direction(df_results):
    """分析效应方向的一致性"""
    print("\n" + "="*80)
    print("效应方向一致性分析")
    print("="*80)
    
    if len(df_results) == 0:
        print("⚠ 没有可用的统计检验结果")
        return pd.DataFrame()
    
    # 分析相关系数的方向
    if 'correlation' not in df_results.columns:
        print("⚠ 没有相关系数数据")
        return pd.DataFrame()
    
    corr_tests = df_results[df_results['correlation'].notna()].copy()
    
    if len(corr_tests) > 0:
        corr_grouped = corr_tests.groupby(['scenario', 'test_name'])
        
        direction_summary = []
        for (scenario, test_name), group in corr_grouped:
            positive = (group['correlation'] > 0).sum()
            negative = (group['correlation'] < 0).sum()
            total = len(group)
            
            direction_summary.append({
                'scenario': scenario,
                'scenario_name': group['scenario_name'].iloc[0],
                'test_name': test_name,
                'positive': positive,
                'negative': negative,
                'total': total,
                'direction_consistent': (positive / total >= 0.8) or (negative / total >= 0.8)
            })
        
        direction_df = pd.DataFrame(direction_summary)
        
        print("\n相关系数方向一致性:")
        for _, row in direction_df.iterrows():
            direction = "正相关" if row['positive'] > row['negative'] else "负相关"
            consistent = "✓ 一致" if row['direction_consistent'] else "不一致"
            print(f"  {row['scenario_name']} - {row['test_name']}: "
                  f"{direction} ({row['positive']}正/{row['negative']}负) {consistent}")
        
        return direction_df
    
    return pd.DataFrame()

def analyze_effect_size(df_results):
    """分析效应大小的分布"""
    print("\n" + "="*80)
    print("效应大小分析")
    print("="*80)
    
    # 相关系数
    corr_data = df_results[df_results['correlation'].notna()].copy()
    if len(corr_data) > 0:
        print("\n相关系数统计:")
        corr_summary = corr_data.groupby(['scenario', 'test_name'])['correlation'].agg([
            'count', 'mean', 'median', 'std', 'min', 'max'
        ])
        print(corr_summary)
    
    # 溢价倍数
    premium_data = df_results[df_results['premium_ratio'].notna()].copy()
    if len(premium_data) > 0:
        print("\n溢价倍数统计:")
        premium_summary = premium_data.groupby(['scenario', 'test_name'])['premium_ratio'].agg([
            'count', 'mean', 'median', 'std', 'min', 'max'
        ])
        print(premium_summary)
    
    return corr_data, premium_data

def create_comparison_visualizations(df_results):
    """创建跨城市对比可视化"""
    print("\n生成对比可视化...")
    
    # 1. 显著性一致性热力图
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 准备数据（转换significant为数值）
    df_results['significant_num'] = df_results['significant'].astype(str).replace({'True': 1, 'False': 0, 'true': 1, 'false': 0})
    df_results['significant_num'] = pd.to_numeric(df_results['significant_num'], errors='coerce').fillna(0)
    
    pivot_data = df_results.groupby(['scenario_name', 'test_name'])['significant_num'].mean().reset_index()
    pivot_table = pivot_data.pivot(index='scenario_name', columns='test_name', values='significant_num')
    
    sns.heatmap(pivot_table, annot=True, fmt='.2f', cmap='RdYlGn', 
                vmin=0, vmax=1, ax=ax, cbar_kws={'label': '显著性比例'})
    ax.set_title('跨城市统计显著性一致性', fontsize=14, fontweight='bold')
    ax.set_xlabel('检验类型', fontsize=12)
    ax.set_ylabel('场景', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "cross_city_significance_heatmap.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  保存: {output_file}")
    
    # 2. 相关系数分布箱线图
    corr_data = df_results[df_results['correlation'].notna()].copy()
    if len(corr_data) > 0:
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # 按场景分组
        sns.boxplot(data=corr_data, x='scenario_name', y='correlation', ax=axes[0])
        axes[0].set_title('各场景相关系数分布', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('场景', fontsize=12)
        axes[0].set_ylabel('相关系数', fontsize=12)
        axes[0].tick_params(axis='x', rotation=45)
        
        # 按检验类型分组
        sns.boxplot(data=corr_data, x='test_name', y='correlation', ax=axes[1])
        axes[1].set_title('各检验类型相关系数分布', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('检验类型', fontsize=12)
        axes[1].set_ylabel('相关系数', fontsize=12)
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        output_file = OUTPUT_DIR / "cross_city_correlation_distribution.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  保存: {output_file}")

def generate_comparison_report():
    """生成跨城市对比报告"""
    print("="*80)
    print("跨城市对比分析")
    print("="*80)
    
    # 加载结果
    all_results = load_all_results()
    if not all_results:
        print("⚠ 没有找到分析结果")
        return
    
    print(f"加载了 {len(all_results)} 个城市的结果")
    
    # 提取检验结果
    df_results = extract_test_results(all_results)
    print(f"\n提取了 {len(df_results)} 个统计检验结果")
    
    # 分析显著性一致性
    consistency_df = analyze_significance_consistency(df_results)
    
    # 分析效应方向
    direction_df = analyze_effect_direction(df_results)
    
    # 分析效应大小
    corr_data, premium_data = analyze_effect_size(df_results)
    
    # 创建可视化
    create_comparison_visualizations(df_results)
    
    # 创建外推性验证可视化（更直观的展示）
    try:
        from airbnb_analysis.analysis.generalizability_visualization import create_generalizability_dashboard
        create_generalizability_dashboard()
    except Exception as e:
        print(f"  ⚠ 外推性可视化生成失败: {e}")
    
    # 保存汇总数据
    summary_data = {
        'consistency': consistency_df.to_dict('records'),
        'direction': direction_df.to_dict('records') if len(direction_df) > 0 else [],
        'total_tests': len(df_results),
        'total_cities': len(all_results),
    }
    
    summary_file = MULTI_CITY_RESULTS_DIR / "comparison_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n对比分析完成，汇总数据已保存: {summary_file}")
    
    return summary_data

if __name__ == "__main__":
    generate_comparison_report()
