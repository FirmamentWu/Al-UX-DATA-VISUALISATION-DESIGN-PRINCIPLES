"""图表样式配置"""
import matplotlib.pyplot as plt
import seaborn as sns
from airbnb_analysis.config.settings import FIGURE_CONFIG, OUTPUT_DIR

def setup_style():
    """设置全局图表样式"""
    # 使用Mac系统字体（英文）
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = FIGURE_CONFIG['dpi']
    plt.rcParams['savefig.dpi'] = FIGURE_CONFIG['dpi']
    plt.rcParams['figure.figsize'] = FIGURE_CONFIG['figsize']
    
    sns.set_style(FIGURE_CONFIG['style'])
    sns.set_palette(FIGURE_CONFIG['palette'])

def save_figure(fig, filename, output_dir=None):
    """保存图表"""
    if output_dir is None:
        output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    fig.savefig(filepath, bbox_inches='tight', facecolor='white')
    print(f"Saved: {filepath}")

def set_legend_outside(ax, loc='center left', bbox_to_anchor=(1.02, 0.5)):
    """设置图例在图外"""
    ax.legend(loc=loc, bbox_to_anchor=bbox_to_anchor)
