"""多城市分析主程序 - 整合所有步骤"""
import sys
from pathlib import Path

# 添加airbnb_analysis到路径
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# 先确保依赖已安装，然后再导入其他模块
from airbnb_analysis.utils.dependencies import ensure_dependencies
print("正在检查并安装依赖...")
ensure_dependencies()

# 现在可以安全导入其他模块
from airbnb_analysis.visualization.style import setup_style
from airbnb_analysis.utils.validate_results import validate_all_results
from airbnb_analysis.analysis.multi_city_analysis import analyze_all_cities
from airbnb_analysis.analysis.cross_city_comparison import generate_comparison_report
from airbnb_analysis.config.settings import DATA_DIR

def main():
    """主函数 - 执行完整的多城市分析流程"""
    print("="*80)
    print("多城市数据验证与外推性分析")
    print("="*80)
    
    # 依赖已在导入时检查，这里跳过
    print("\n步骤1: 依赖检查完成")
    
    # 2. 设置样式
    print("\n步骤2: 设置可视化样式...")
    setup_style()
    
    # 3. 验证现有纽约数据的统计检验结果
    print("\n步骤3: 验证纽约数据的统计检验结果...")
    try:
        ny_validation = validate_all_results()
        print("✓ 纽约数据验证完成")
    except Exception as e:
        print(f"⚠ 纽约数据验证失败: {e}")
        ny_validation = None
    
    # 4. 检查多城市数据
    print("\n步骤4: 检查多城市数据...")
    
    # 检查数据目录
    if not DATA_DIR.exists():
        print(f"  ✗ 数据目录不存在: {DATA_DIR}")
        return
    
    # 查找数据文件
    from airbnb_analysis.data.multi_city_loader import find_all_city_data
    city_data_map = find_all_city_data()
    
    if not city_data_map:
        print("  ⚠ 未找到任何城市数据文件")
        print(f"  请在 {DATA_DIR} 目录下放置 *listings.csv.gz 文件")
        return
    
    print(f"  找到 {len(city_data_map)} 个城市的数据文件")
    
    # 5. 分析所有城市
    print("\n步骤5: 分析所有城市...")
    try:
        all_results = analyze_all_cities(data_dir=DATA_DIR)
        print(f"✓ 完成 {len(all_results)} 个城市的分析")
    except Exception as e:
        print(f"✗ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 6. 跨城市对比分析
    print("\n步骤6: 跨城市对比分析...")
    try:
        comparison_summary = generate_comparison_report()
        print("✓ 对比分析完成")
    except Exception as e:
        print(f"✗ 对比分析失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("所有分析完成！")
    print("="*80)
    print("\n结果文件位置:")
    print(f"  - 各城市分析结果: airbnb_analysis/outputs/multi_city_results/")
    print(f"  - 对比可视化: airbnb_analysis/outputs/figures/")
    print(f"  - 验证报告: airbnb_analysis/docs/multi_city_validation_report.md")

if __name__ == "__main__":
    main()
