#F1yingZ
#开发时间: 2024/12/18 15:49

#%%
import platform
import pickle
import time
import sklearn
import statsmodels

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt

from tqdm import tqdm
from pandas import to_datetime as dt
from statsmodels.stats.weightstats import ztest
from sklearn.linear_model import LinearRegression
from IPython.display import display

# simplified Chinese display
plt.rcParams['font.sans-serif'] = ['SimHei']
# plus/minus sign display
plt.rcParams['axes.unicode_minus'] = False

pd.set_option('display.float_format', lambda x: '%.3f' % x)
pd.DataFrame(index=[''], columns=['Last Run Time', 'Python', 'pandas', 'numpy', 'sklearn', 'statsmodels'], data=[
             [time.asctime(), platform.python_version(), pd.__version__, np.__version__, sklearn.__version__, statsmodels.__version__]])
#%%