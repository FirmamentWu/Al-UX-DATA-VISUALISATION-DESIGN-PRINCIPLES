"""多城市分析框架 - 对每个城市运行相同的5个场景分析"""
import sys
from pathlib import Path
import pandas as pd
import json

BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH))

from airbnb_analysis.utils.validate_results import (
    validate_scenario1,
    validate_scenario2,
    validate_scenario3,
    validate_scenario4,
    validate_scenario5
)
from airbnb_analysis.data.multi_city_loader import load_all_cities_data
from airbnb_analysis.config.settings import DATA_DIR, MULTI_CITY_RESULTS_DIR, MULTI_CITY_CONFIG
from airbnb_analysis.config.constants import CITY_NAMES

def analyze_city(df, city_name):
    """对单个城市运行所有场景的分析"""
    print(f"\n{'='*80}")
    print(f"分析城市: {CITY_NAMES.get(city_name, city_name)}")
    print(f"{'='*80}")
    
    results = {
        'city_name': city_name,
        'display_name': CITY_NAMES.get(city_name, city_name),
        'sample_size': len(df),
        'scenario1': {},
        'scenario2': {},
        'scenario3': {},
        'scenario4': {},
        'scenario5': {},
    }
    
    # 检查样本量
    if len(df) < MULTI_CITY_CONFIG['min_samples_per_city']:
        print(f"  ⚠ 样本量不足: {len(df)} < {MULTI_CITY_CONFIG['min_samples_per_city']}")
        results['error'] = f"样本量不足: {len(df)}"
        return results
    
    try:
        # 场景1: 物理空间溢价
        print("\n场景1: 物理空间溢价...")
        results['scenario1'] = validate_scenario1(df)
        
        # 场景2: 位置溢价
        print("场景2: 位置溢价...")
        results['scenario2'] = validate_scenario2(df)
        
        # 场景3: 规模溢价
        print("场景3: 规模溢价...")
        results['scenario3'] = validate_scenario3(df)
        
        # 场景4: 信任货币化
        print("场景4: 信任货币化...")
        results['scenario4'] = validate_scenario4(df)
        
        # 场景5: 活跃度信号
        print("场景5: 活跃度信号...")
        results['scenario5'] = validate_scenario5(df)
        
        print(f"\n✓ {city_name} 分析完成")
        
    except Exception as e:
        print(f"  ✗ 分析失败: {e}")
        results['error'] = str(e)
    
    return results

def analyze_all_cities(data_dir=None, cities_data=None):
    """分析所有城市的数据"""
    if data_dir is None:
        data_dir = DATA_DIR
    
    # 如果没有提供数据，则加载
    if cities_data is None:
        cities_data = load_all_cities_data(data_dir)
    
    if not cities_data:
        print("⚠ 没有找到任何城市数据")
        return {}
    
    print(f"\n找到 {len(cities_data)} 个城市的数据")
    
    # 创建结果目录
    MULTI_CITY_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    all_results = {}
    
    # 分析每个城市
    for city_name, df in cities_data.items():
        result = analyze_city(df, city_name)
        all_results[city_name] = result
        
        # 保存单个城市的结果
        result_file = MULTI_CITY_RESULTS_DIR / f"{city_name}_results.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"  结果已保存: {result_file}")
    
    # 保存汇总结果
    summary_file = MULTI_CITY_RESULTS_DIR / "all_cities_results.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n{'='*80}")
    print("所有城市分析完成")
    print(f"{'='*80}")
    print(f"汇总结果已保存: {summary_file}")
    
    return all_results

def get_summary_statistics(all_results):
    """生成汇总统计"""
    summary = {
        'total_cities': len(all_results),
        'successful_cities': 0,
        'failed_cities': 0,
        'scenario_statistics': {}
    }
    
    # 统计各场景的显著性
    scenarios = ['scenario1', 'scenario2', 'scenario3', 'scenario4', 'scenario5']
    
    for scenario in scenarios:
        summary['scenario_statistics'][scenario] = {
            'total_tests': 0,
            'significant_tests': 0,
            'cities_with_results': 0
        }
    
    for city_name, result in all_results.items():
        if 'error' not in result:
            summary['successful_cities'] += 1
        else:
            summary['failed_cities'] += 1
        
        for scenario in scenarios:
            if scenario in result and isinstance(result[scenario], dict):
                summary['scenario_statistics'][scenario]['cities_with_results'] += 1
                
                for test_name, test_result in result[scenario].items():
                    if isinstance(test_result, dict) and 'significant' in test_result:
                        summary['scenario_statistics'][scenario]['total_tests'] += 1
                        if test_result['significant']:
                            summary['scenario_statistics'][scenario]['significant_tests'] += 1
    
    return summary

if __name__ == "__main__":
    results = analyze_all_cities()
    
    # 生成汇总统计
    summary = get_summary_statistics(results)
    print("\n汇总统计:")
    print(json.dumps(summary, indent=2, ensure_ascii=False, default=str))
