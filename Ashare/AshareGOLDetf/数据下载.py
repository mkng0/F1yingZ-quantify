#F1yingZ
#开发时间: 2024/12/18 11:22
#下载库 pip install baostock -i https://pypi.tuna.tsinghua.edu.cn/simple

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 用于获取数据
import os
import yfinance as yf #国外的，要梯子；国内的使用akshare
import matplotlib.pyplot as plt


# 设置代理，指定HTTP 请求的代理服务器
proxy = 'http://127.0.0.1:10090' #本机的代理端口
os.environ['HTTP_PROXY'] = proxy 
os.environ['HTTPS_PROXY'] = proxy

# 获取股票的历史数据，方法一
df = yf.Ticker("AAPL").history(period="1y")
df

# 方法二：
aapl = yf.Ticker("aapl")
print(aapl.info)
# {'zip': '95014', 'sector': 'Technology' ...
# 市盈率（PE）
aapl.info['forwardPE']
 
# 新闻数据
print(aapl.news)

# 获取美股黄金ETF (GLD) 的历史行情数据
etf_data = yf.download('GLD', start='2013-08-01', end='2025-08-08')
# 只需要收盘价序列
Df = etf_data[['Close']]
# yfinance已自动设置Index为datetime格式的日期
# 去除空值
Df = Df.dropna()
# 去除空值
Df = Df.dropna()
# 画出黄金ETF的价格走势图
Df.Close.plot(figsize=(15, 8), color='red')
plt.ylabel('黄金ETF价格')
plt.title('黄金ETF价格序列')
plt.show()
# 查看Df的数据形式
print(Df)