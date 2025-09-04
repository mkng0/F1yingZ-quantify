# 论文：An Effective Intraday Momentum Strategy for SP500
# 用于数据处理
import numpy as np
import pandas as pd
# 用于获取高频数据
import akshare as ak
# 用于可视化
import matplotlib.pyplot as plt
# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# 忽略警告
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime, timedelta

# 1. 获取黄金ETF高频数据 好像不能下载高频数据，暂时搁置这个方法，还是继续日频。
def get_high_frequency_data(symbol='518880', start_date=None, end_date=None, freq='60min'):
    """
    使用akshare获取黄金ETF的高频数据
    参数:
        symbol: ETF代码，默认518880(华安黄金ETF)
        start_date: 开始日期，格式'YYYYMMDD'
        end_date: 结束日期，格式'YYYYMMDD'
        freq: 频率，可选'5min', '15min', '30min', '60min' (1min可能不支持)
    返回:
        高频数据DataFrame
    """
    # 检查akshare版本
    print(f"akshare版本: {ak.__version__}")
    
    # 验证频率参数
    supported_freqs = ['5min', '15min', '30min', '60min']
    if freq not in supported_freqs:
        print(f"警告: 频率{freq}可能不被支持，将使用60min")
        freq = '60min'
    
    # 如果未指定日期，默认获取最近30天数据
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
    print(f"尝试获取{start_date}至{end_date}的{freq}数据...")
    
    # 使用akshare获取高频数据
    # 根据akshare 1.17.31版本调整接口
    try:
        # 尝试方法1: 使用fund_etf_hist_em获取数据 (支持的频率)
        print(f"方法1: 使用fund_etf_hist_em获取{freq}数据...")
        df = ak.fund_etf_hist_em(symbol=symbol, period=freq, start_date=start_date, end_date=end_date)
        print("成功获取高频数据!")
    except Exception as e:
        print(f"fund_etf_hist_em失败: {str(e)[:100]}")
        try:
            # 尝试方法2: 不指定start_date和end_date，获取所有可用数据后再筛选
            print(f"方法2: 使用fund_etf_hist_em获取所有{freq}数据后筛选...")
            df = ak.fund_etf_hist_em(symbol=symbol, period=freq)
            # 转换日期并筛选
            if '日期' in df.columns:
                df['date'] = pd.to_datetime(df['日期'])
                df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            else:
                raise Exception("数据中没有日期列")
        except Exception as e:
            print(f"方法2失败: {str(e)[:100]}")
            # 如果所有高频接口都失败，尝试获取日线数据作为备选
            print(" fallback到日线数据...")
            df = ak.fund_etf_hist_em(symbol=symbol, period='daily', start_date=start_date, end_date=end_date)
            df['date'] = pd.to_datetime(df['日期'])
            df.set_index('date', inplace=True)
            df.rename(columns={'收盘': 'close'}, inplace=True)
            return df
    
    # 处理成功获取的高频数据
    # 转换时间格式
    if '日期' in df.columns and '时间' in df.columns:
        df['datetime'] = pd.to_datetime(df['日期'] + ' ' + df['时间'])
    elif 'datetime' not in df.columns:
        df['datetime'] = pd.to_datetime(df.index)
    
    df.set_index('datetime', inplace=True)
    
    # 重命名列
    column_mapping = {
        '开盘价': 'open',
        '最高价': 'high',
        '最低价': 'low',
        '收盘价': 'close',
        '成交量': 'volume',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume'
    }
    
    # 只保留需要的列
    valid_columns = [col for col in df.columns if col in column_mapping]
    df = df[valid_columns]
    df.rename(columns={col: column_mapping[col] for col in valid_columns}, inplace=True)
    
    # 移除重复索引
    df = df[~df.index.duplicated(keep='last')]
    
    return df

# 2. 实现日内动量策略
def intraday_momentum_strategy(df, window=30):
    """
    基于论文《An Effective Intraday Momentum Strategy for SP500》实现的日内动量策略
    参数:
        df: 高频数据DataFrame
        window: 动量计算窗口
    返回:
        带有交易信号的DataFrame
    """
    # 计算日内收益率
    df['return'] = df['close'].pct_change()
    
    # 计算滚动动量
    df['momentum'] = df['return'].rolling(window=window).sum()
    
    # 生成交易信号: 当动量为正时买入，为负时卖出
    df['signal'] = np.where(df['momentum'] > 0, 1, -1)
    
    # 滞后信号以避免未来函数
    df['signal'] = df['signal'].shift(1)
    
    # 计算策略收益率
    df['strategy_return'] = df['signal'] * df['return']
    
    # 计算累计收益率
    df['cumulative_return'] = (1 + df['strategy_return']).cumprod()
    df['benchmark_return'] = (1 + df['return']).cumprod()
    
    return df

# 3. 策略评估与可视化
def evaluate_strategy(df):
    """
    评估策略性能并可视化结果
    参数:
        df: 带有策略信号和收益率的DataFrame
    """
    # 计算策略指标
    total_days = len(df)
    strategy_return = df['cumulative_return'].iloc[-1] - 1
    benchmark_return = df['benchmark_return'].iloc[-1] - 1
    
    # 计算夏普率 (假设无风险利率为0)
    sharpe_ratio = np.sqrt(252) * df['strategy_return'].mean() / df['strategy_return'].std()
    
    # 输出评估结果
    print(f"策略总收益率: {strategy_return:.2%}")
    print(f"基准总收益率: {benchmark_return:.2%}")
    print(f"夏普率: {sharpe_ratio:.2f}")
    
    # 绘制累计收益率曲线
    plt.figure(figsize=(15, 8))
    plt.plot(df['cumulative_return'], label='策略累计收益率')
    plt.plot(df['benchmark_return'], label='基准累计收益率')
    plt.title('黄金ETF高频动量策略表现')
    plt.xlabel('时间')
    plt.ylabel('累计收益率')
    plt.legend()
    plt.show()

# 4. 主函数
def main():
    # 获取高频数据
    print("正在获取黄金ETF高频数据...")
    # 使用60分钟频率，这是akshare可能支持的较高频率
    df = get_high_frequency_data(symbol='518880', freq='60min')
    print(f"成功获取数据: {len(df)} 条记录")
    
    # 检查数据频率
    if len(df) > 0:
        # 计算数据点之间的时间差
        time_diff = df.index.to_series().diff().dropna().min()
        print(f"数据最小时间间隔: {time_diff}")
        
        # 应用策略
        print("正在应用日内动量策略...")
        # 根据数据频率调整窗口参数
        if time_diff <= pd.Timedelta(minutes=15):
            window = 30
        else:
            window = 10
        df = intraday_momentum_strategy(df, window=window)
        
        # 评估策略
        print("正在评估策略性能...")
        evaluate_strategy(df)
        
        # 输出最新信号
        latest_signal = df['signal'].iloc[-1]
        signal_text = '买入' if latest_signal == 1 else '卖出'
        print(f"最新交易信号: {signal_text}")
    else:
        print("未获取到足够数据，无法运行策略")

if __name__ == "__main__":
    main()