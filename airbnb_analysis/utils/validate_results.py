"""验证现有分析结果的统计有效性"""
import sys
from pathlib import Path
import pandas as pd
import json

BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from airbnb_analysis.data.loader import load_data
from airbnb_analysis.data.preprocessor import preprocess_data
from airbnb_analysis.models.statistical_tests import (
    test_privacy_premium, 
    test_group_differences, 
    compute_correlation
)
from airbnb_analysis.models.regression import fit_interaction_model
from airbnb_analysis.config.constants import FEATURE_COLS

def validate_scenario1(df):
    """验证场景1: 物理空间溢价"""
    results = {}
    
    # 1.1 隐私溢价
    privacy_result = test_privacy_premium(df)
    if privacy_result:
        results['privacy_premium'] = {
            'p_value': privacy_result['p_value'],
            'significant': privacy_result['p_value'] < 0.05,
            'premium_ratio': privacy_result['premium_ratio'],
            'median_entire': privacy_result['median_entire'],
            'median_private': privacy_result['median_private']
        }
    
    # 1.2 容量溢价
    df_cap = df[df[FEATURE_COLS['accommodates']].between(1, 10)].copy()
    if len(df_cap) > 100:
        corr_result = compute_correlation(
            df_cap[FEATURE_COLS['accommodates']],
            df_cap[FEATURE_COLS['price']]
        )
        results['capacity_premium'] = {
            'correlation': corr_result['correlation'],
            'p_value': corr_result['p_value'],
            'significant': corr_result['p_value'] < 0.05
        }
    
    # 1.3 交互效应
    df_model = df.copy()
    df_model['is_entire'] = (df_model[FEATURE_COLS['room_type']] == 'Entire home/apt').astype(int)
    df_model = df_model[df_model[FEATURE_COLS['price']].notna() & 
                        df_model[FEATURE_COLS['accommodates']].notna() &
                        df_model['is_entire'].notna()]
    
    if len(df_model) > 100:
        try:
            model = fit_interaction_model(df_model, 'price ~ accommodates * is_entire')
            results['interaction_effect'] = {
                'interaction_coef': model.params.get('accommodates:is_entire', None),
                'interaction_p_value': model.pvalues.get('accommodates:is_entire', None),
                'significant': model.pvalues.get('accommodates:is_entire', 1.0) < 0.05 if 'accommodates:is_entire' in model.pvalues else False
            }
        except Exception as e:
            results['interaction_effect'] = {'error': str(e)}
    
    return results

def validate_scenario2(df):
    """验证场景2: 位置溢价"""
    results = {}
    
    df_region = df[df[FEATURE_COLS['neighbourhood_group']].notna()].copy()
    if len(df_region) > 100:
        region_result = test_group_differences(
            df_region, 
            FEATURE_COLS['neighbourhood_group'], 
            FEATURE_COLS['price']
        )
        if region_result:
            results['region_comparison'] = {
                'p_value': region_result['p_value'],
                'significant': region_result['p_value'] < 0.05,
                'medians': region_result['medians']
            }
    
    return results

def validate_scenario3(df):
    """验证场景3: 规模溢价"""
    results = {}
    
    df_scale = df[df['host_listings_count_binned'].notna()].copy()
    if len(df_scale) > 100:
        # 价格
        price_result = test_group_differences(
            df_scale, 
            'host_listings_count_binned', 
            FEATURE_COLS['price']
        )
        if price_result:
            results['scale_price'] = {
                'p_value': price_result['p_value'],
                'significant': price_result['p_value'] < 0.05,
                'medians': price_result['medians']
            }
        
        # 入住率
        occ_result = test_group_differences(
            df_scale, 
            'host_listings_count_binned', 
            FEATURE_COLS['availability']
        )
        if occ_result:
            results['scale_occupancy'] = {
                'p_value': occ_result['p_value'],
                'significant': occ_result['p_value'] < 0.05,
                'medians': occ_result['medians']
            }
    
    return results

def validate_scenario4(df):
    """验证场景4: 信任货币化"""
    results = {}
    
    # 评分 vs 入住率
    df_rating = df[df[FEATURE_COLS['review_rating']].notna() & 
                   df[FEATURE_COLS['availability']].notna()].copy()
    if len(df_rating) > 100:
        corr_result = compute_correlation(
            df_rating[FEATURE_COLS['review_rating']],
            df_rating[FEATURE_COLS['availability']]
        )
        results['rating_occupancy'] = {
            'correlation': corr_result['correlation'],
            'p_value': corr_result['p_value'],
            'significant': corr_result['p_value'] < 0.05
        }
    
    # 超赞房东
    df_superhost = df[df[FEATURE_COLS['superhost']].notna() & 
                      df[FEATURE_COLS['availability']].notna()].copy()
    if len(df_superhost) > 100:
        superhost_occ = df_superhost[df_superhost[FEATURE_COLS['superhost']] == 't'][FEATURE_COLS['availability']].dropna()
        regular_occ = df_superhost[df_superhost[FEATURE_COLS['superhost']] == 'f'][FEATURE_COLS['availability']].dropna()
        
        if len(superhost_occ) > 10 and len(regular_occ) > 10:
            from scipy.stats import mannwhitneyu
            stat, p_value = mannwhitneyu(superhost_occ, regular_occ, alternative='two-sided')
            results['superhost_comparison'] = {
                'p_value': p_value,
                'significant': p_value < 0.05,
                'superhost_median': superhost_occ.median(),
                'regular_median': regular_occ.median()
            }
    
    return results

def validate_scenario5(df):
    """验证场景5: 活跃度信号"""
    results = {}
    
    # LTM vs 价格
    df_ltm = df[df[FEATURE_COLS['reviews_ltm']].notna() & 
                df[FEATURE_COLS['price']].notna()].copy()
    if len(df_ltm) > 100:
        corr_ltm_price = compute_correlation(
            df_ltm[FEATURE_COLS['reviews_ltm']],
            df_ltm[FEATURE_COLS['price']]
        )
        results['ltm_price'] = {
            'correlation': corr_ltm_price['correlation'],
            'p_value': corr_ltm_price['p_value'],
            'significant': corr_ltm_price['p_value'] < 0.05
        }
    
    # 历史评论 vs 价格
    df_hist = df[df[FEATURE_COLS['reviews_total']].notna() & 
                 df[FEATURE_COLS['price']].notna()].copy()
    if len(df_hist) > 100:
        corr_hist_price = compute_correlation(
            df_hist[FEATURE_COLS['reviews_total']],
            df_hist[FEATURE_COLS['price']]
        )
        results['historical_price'] = {
            'correlation': corr_hist_price['correlation'],
            'p_value': corr_hist_price['p_value'],
            'significant': corr_hist_price['p_value'] < 0.05
        }
    
    # LTM vs 入住率
    df_ltm_occ = df[df[FEATURE_COLS['reviews_ltm']].notna() & 
                    df[FEATURE_COLS['availability']].notna()].copy()
    if len(df_ltm_occ) > 100:
        corr_ltm_occ = compute_correlation(
            df_ltm_occ[FEATURE_COLS['reviews_ltm']],
            df_ltm_occ[FEATURE_COLS['availability']]
        )
        results['ltm_occupancy'] = {
            'correlation': corr_ltm_occ['correlation'],
            'p_value': corr_ltm_occ['p_value'],
            'significant': corr_ltm_occ['p_value'] < 0.05
        }
    
    return results

def validate_all_results():
    """验证所有场景的统计检验结果"""
    print("="*80)
    print("验证纽约数据的统计检验结果")
    print("="*80)
    
    # 加载数据
    df = load_data()
    df = preprocess_data(df)
    
    all_results = {}
    
    # 场景1
    print("\n验证场景1: 物理空间溢价...")
    all_results['scenario1'] = validate_scenario1(df)
    
    # 场景2
    print("验证场景2: 位置溢价...")
    all_results['scenario2'] = validate_scenario2(df)
    
    # 场景3
    print("验证场景3: 规模溢价...")
    all_results['scenario3'] = validate_scenario3(df)
    
    # 场景4
    print("验证场景4: 信任货币化...")
    all_results['scenario4'] = validate_scenario4(df)
    
    # 场景5
    print("验证场景5: 活跃度信号...")
    all_results['scenario5'] = validate_scenario5(df)
    
    # 生成汇总报告
    print("\n" + "="*80)
    print("统计检验结果汇总")
    print("="*80)
    
    significant_count = 0
    total_tests = 0
    
    for scenario, results in all_results.items():
        print(f"\n{scenario.upper()}:")
        for test_name, test_result in results.items():
            if isinstance(test_result, dict) and 'significant' in test_result:
                total_tests += 1
                status = "✓ 显著" if test_result['significant'] else "✗ 不显著"
                if test_result['significant']:
                    significant_count += 1
                p_val = test_result.get('p_value', 'N/A')
                print(f"  {test_name}: {status} (p={p_val})")
    
    print(f"\n总计: {significant_count}/{total_tests} 个检验显著 (p < 0.05)")
    
    # 保存结果
    output_dir = Path(__file__).parent.parent / "outputs" / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "ny_validation_results.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n结果已保存到: {output_file}")
    
    return all_results

if __name__ == "__main__":
    validate_all_results()
