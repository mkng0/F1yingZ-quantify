import akshare as ak
import pandas as pd

# 获取新浪财经的ETF分类列表
etf_list = ak.fund_etf_category_sina(symbol="ETF基金")
# 去掉前两个字母
etf_list["代码"] = etf_list["代码"].str[2:]
print(etf_list.head())  
# etf_list.to_csv("etf_list.csv", encoding='utf-8-sig', index=False)
etf_codes=etf_list["代码"]


all_etf_data = []  
for code in etf_codes:
    try:
        # # 使用新浪接口获取单只ETF历史数据
        # df = ak.fund_etf_hist_sina(symbol=str(code),start_date="20240901",end_date="20250901")
        # 不复权
        df = ak.fund_etf_hist_em(symbol=str(code), period="daily", start_date="20240901",end_date="20250901", adjust="")
        # # 前复权
        # df = ak.fund_etf_hist_em(symbol=str(code), period="daily", start_date="20240901",end_date="20250901", adjust="qfq")
        # # 后复权
        # df = ak.fund_etf_hist_em(symbol=str(code), period="daily", start_date="20240901", end_date="20250901", adjust="hfq")
        df['symbol'] = code  # 在DataFrame中添加一列记录ETF代码
        all_etf_data.append(df)  # 将当前ETF的数据添加到列表中
    except Exception as e:
        print(f"获取 {code} 数据时出错: {e}")

# 合并所有ETF的数据
combined_df = pd.concat(all_etf_data, ignore_index=True)
combined_df.to_csv('A股ETF/all_etf_data.csv', index=False, encoding='utf-8-sig')
