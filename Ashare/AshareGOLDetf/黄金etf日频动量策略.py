# 黄金ETF日频动量策略
# 论文：An Effective Intraday Momentum Strategy for SP500

import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 设置中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

# 1. 获取黄金ETF日频数据
def get_daily_data(symbol='518880', start_date=None, end_date=None):
    """
    使用akshare获取黄金ETF的日频数据
    参数:
        symbol: ETF代码，默认518880(华安黄金ETF)
        start_date: 开始日期，格式'YYYYMMDD'
        end_date: 结束日期，格式'YYYYMMDD'
    返回:
        日频数据DataFrame
    """
    # 检查akshare版本
    print(f"akshare版本: {ak.__version__}")
    
    # 如果未指定日期，默认获取最近1年数据
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        
    print(f"尝试获取{start_date}至{end_date}的日频数据...")
    
    # 使用akshare获取日频数据
    try:
        df = ak.fund_etf_hist_em(symbol=symbol, period='daily', start_date=start_date, end_date=end_date)
        print("成功获取日频数据!")
    except Exception as e:
        print(f"获取日频数据失败: {str(e)[:100]}")
        # 尝试使用备选接口
        try:
            df = ak.fund_etf_hist(symbol=symbol)
            # 转换日期并筛选
            if '净值日期' in df.columns:
                df['date'] = pd.to_datetime(df['净值日期'])
                df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            else:
                raise Exception("数据中没有日期列")
        except Exception as e:
            print(f"备选接口也失败: {str(e)[:100]}")
            raise
    
    # 打印列名，帮助调试
    print(f"数据列名: {df.columns.tolist()}")
    
    # 处理数据
    if '日期' in df.columns:
        df['date'] = pd.to_datetime(df['日期'])
        df.set_index('date', inplace=True)
    elif '净值日期' in df.columns:
        df['date'] = pd.to_datetime(df['净值日期'])
        df.set_index('date', inplace=True)
    else:
        raise Exception("数据中没有日期列")
    
    # 重命名列 - 更灵活的映射
    column_mapping = {
        '开盘价': 'open',
        '最高价': 'high',
        '最低价': 'low',
        '收盘价': 'close',
        '收盘': 'close',  # 增加可能的列名映射
        '单位净值': 'close',  # 考虑ETF可能使用净值
        '成交量': 'volume',
        '成交额': 'volume'  # 增加成交额作为成交量的备选
    }
    
    # 寻找收盘价列
    close_columns = [col for col in df.columns if col in column_mapping and column_mapping[col] == 'close']
    if not close_columns:
        raise Exception(f"未找到收盘价相关列，可用列: {df.columns.tolist()}")
    
    # 只保留需要的列
    valid_columns = [col for col in df.columns if col in column_mapping]
    df = df[valid_columns]
    df.rename(columns={col: column_mapping[col] for col in valid_columns}, inplace=True)
    
    # 确保有close列
    if 'close' not in df.columns:
        raise Exception(f"重命名后仍未找到'close'列，列名: {df.columns.tolist()}")
    
    # 移除重复索引
    df = df[~df.index.duplicated(keep='last')]
    
    return df

# 2. 日频动量策略
def daily_momentum_strategy(df, window=20):
    """
    实现日频动量策略
    参数:
        df: 包含'close'列的DataFrame
        window: 动量计算窗口大小
    返回:
        包含策略信号的DataFrame
    """
    # 计算动量 (收益率)
    df['momentum'] = df['close'].pct_change(periods=window)
    
    # 生成信号: 动量为正则买入(1)，否则卖出(0)
    df['signal'] = np.where(df['momentum'] > 0, 1, 0)
    
    # 滞后信号以避免未来函数
    df['signal'] = df['signal'].shift(1)
    df['signal'].fillna(0, inplace=True)
    
    # 计算策略收益
    df['strategy_return'] = df['signal'] * df['close'].pct_change()
    df['cumulative_strategy'] = (1 + df['strategy_return']).cumprod()
    df['cumulative_benchmark'] = (1 + df['close'].pct_change()).cumprod()
    
    return df

# 3. 策略评估
def evaluate_strategy(df):
    """
    评估策略性能
    参数:
        df: 包含策略信号和收益的DataFrame
    """
    # 计算总收益率
    total_strategy_return = (df['cumulative_strategy'].iloc[-1] - 1) * 100
    total_benchmark_return = (df['cumulative_benchmark'].iloc[-1] - 1) * 100
    
    # 计算夏普率 (假设无风险利率为0)
    daily_strategy_return = df['strategy_return'].dropna()
    sharpe_ratio = np.sqrt(252) * daily_strategy_return.mean() / daily_strategy_return.std()
    
    print(f"策略总收益率: {total_strategy_return:.2f}%")
    print(f"基准总收益率: {total_benchmark_return:.2f}%")
    print(f"夏普率: {sharpe_ratio:.2f}")
    
    # 绘制累计收益曲线
    plt.figure(figsize=(12, 6))
    plt.plot(df['cumulative_strategy'], label='策略累计收益')
    plt.plot(df['cumulative_benchmark'], label='基准累计收益')
    plt.title('黄金ETF日频动量策略表现')
    plt.xlabel('日期')
    plt.ylabel('累计收益')
    plt.legend()
    plt.grid(True)
    plt.savefig('黄金ETF日频动量策略表现.png')
    plt.close()
    print("策略表现图已保存为'黄金ETF日频动量策略表现.png'")

# 4. 主函数
def main():
    # 获取日频数据
    print("正在获取黄金ETF日频数据...")
    df = get_daily_data(symbol='518880')
    print(f"成功获取数据: {len(df)} 条记录")
    print(df.head())
    # 检查数据
    if len(df) > 0:
        # 应用策略
        print("正在应用日频动量策略...")
        df = daily_momentum_strategy(df, window=20)
        
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