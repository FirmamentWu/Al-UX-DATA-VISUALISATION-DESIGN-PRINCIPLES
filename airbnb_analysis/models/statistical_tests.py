"""统计检验模型"""
from scipy.stats import mannwhitneyu, kruskal, spearmanr

def test_privacy_premium(df, price_col='price', room_type_col='room_type'):
    """测试隐私溢价（Mann-Whitney U检验）"""
    entire_home = df[df[room_type_col] == 'Entire home/apt'][price_col].dropna()
    private_room = df[df[room_type_col] == 'Private room'][price_col].dropna()
    
    if len(entire_home) > 0 and len(private_room) > 0:
        stat, p_value = mannwhitneyu(entire_home, private_room, alternative='two-sided')
        median_entire = entire_home.median()
        median_private = private_room.median()
        premium_ratio = median_entire / median_private if median_private > 0 else 0
        
        return {
            'statistic': stat,
            'p_value': p_value,
            'median_entire': median_entire,
            'median_private': median_private,
            'premium_ratio': premium_ratio
        }
    return None

def test_group_differences(df, group_col, value_col, min_samples=10):
    """Kruskal-Wallis检验（多组比较）"""
    groups = [
        group[value_col].dropna() 
        for name, group in df.groupby(group_col) 
        if len(group) >= min_samples
    ]
    
    if len(groups) > 2:
        stat, p_value = kruskal(*groups)
        medians = df.groupby(group_col)[value_col].median()
        return {
            'statistic': stat,
            'p_value': p_value,
            'medians': medians.to_dict()
        }
    return None

def compute_correlation(x, y, method='spearman'):
    """计算相关系数"""
    if method == 'spearman':
        corr_coef, p_value = spearmanr(x, y)
    else:
        from scipy.stats import pearsonr
        corr_coef, p_value = pearsonr(x, y)
    
    return {'correlation': corr_coef, 'p_value': p_value}
