"""回归模型"""
from sklearn.linear_model import LinearRegression
from statsmodels.formula.api import ols
import statsmodels.api as sm

def fit_linear_regression(X, y):
    """拟合简单线性回归"""
    lr = LinearRegression()
    lr.fit(X, y)
    return lr

def fit_interaction_model(df, formula):
    """拟合交互效应模型"""
    model = ols(formula, data=df).fit()
    return model

def fit_log_linear_model(X, y_log):
    """拟合对数线性模型"""
    X_with_const = sm.add_constant(X)
    model = sm.OLS(y_log, X_with_const).fit()
    return model
