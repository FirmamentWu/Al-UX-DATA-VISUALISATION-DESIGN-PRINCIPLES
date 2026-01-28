"""自动安装依赖"""
import subprocess
import sys

REQUIRED_PACKAGES = {
    'pandas': 'pandas',
    'numpy': 'numpy',
    'matplotlib': 'matplotlib',
    'seaborn': 'seaborn',
    'scipy': 'scipy',
    'statsmodels': 'statsmodels',
    'sklearn': 'scikit-learn',
    'requests': 'requests',
}

def install_package(package):
    """安装单个包"""
    try:
        module_name = package.split('-')[0] if '-' in package else package
        if module_name == 'scikit-learn':
            module_name = 'sklearn'
        __import__(module_name)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--user", package, "--quiet"
        ])

def ensure_dependencies():
    """确保所有依赖已安装"""
    for module, package in REQUIRED_PACKAGES.items():
        install_package(package)
