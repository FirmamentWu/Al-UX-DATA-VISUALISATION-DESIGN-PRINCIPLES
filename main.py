"""主入口文件"""
import sys
from pathlib import Path

# 添加airbnb_analysis到路径
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from airbnb_analysis.utils.dependencies import ensure_dependencies
from airbnb_analysis.visualization.style import setup_style
from airbnb_analysis.data.loader import load_data
from airbnb_analysis.data.preprocessor import preprocess_data
from airbnb_analysis.analysis.scenario1_physical_space import run_scenario1
from airbnb_analysis.analysis.scenario2_location import run_scenario2
from airbnb_analysis.analysis.scenario3_scale import run_scenario3
from airbnb_analysis.analysis.scenario4_trust import run_scenario4
from airbnb_analysis.analysis.scenario5_activity import run_scenario5
from airbnb_analysis.analysis.comprehensive_model import run_comprehensive_model

def main():
    """主函数"""
    # 1. 确保依赖已安装
    ensure_dependencies()
    
    # 2. 设置样式
    setup_style()
    
    # 3. 加载和预处理数据
    df = load_data()
    df = preprocess_data(df)
    
    # 4. 运行所有场景分析
    results = {}
    results['scenario1'] = run_scenario1(df)
    results['scenario2'] = run_scenario2(df)
    results['scenario3'] = run_scenario3(df)
    results['scenario4'] = run_scenario4(df)
    results['scenario5'] = run_scenario5(df)
    results['comprehensive'] = run_comprehensive_model(df)
    
    print("\n" + "="*80)
    print("所有分析完成！")
    print("="*80)
    
    return results

if __name__ == "__main__":
    results = main()
