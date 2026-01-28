"""非参数平滑模型"""
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.stats import gaussian_kde
import numpy as np

def fit_lowess(x, y, frac=0.3):
    """LOWESS平滑"""
    sorted_idx = np.argsort(x)
    x_sorted = x[sorted_idx]
    y_sorted = y[sorted_idx]
    result = lowess(y_sorted, x_sorted, frac=frac)
    return result[:, 0], result[:, 1]

def fit_kde(data):
    """核密度估计"""
    kde = gaussian_kde(data)
    return kde
