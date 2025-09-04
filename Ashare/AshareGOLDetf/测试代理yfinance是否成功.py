import os
import yfinance as yf
import requests

def test_proxy():
    """测试代理是否正常工作"""
    proxy = 'http://127.0.0.1:10090'
    try:
        response = requests.get('https://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=10)
        if response.status_code == 200:
            print("代理测试成功！")
            return True
        else:
            print(f"代理测试失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"代理测试异常: {e}")
        return False

def test_yfinance():
    """测试yfinance数据获取"""
    try:
        # 设置代理
        proxy = 'http://127.0.0.1:10090'
        os.environ['HTTP_PROXY'] = proxy
        os.environ['HTTPS_PROXY'] = proxy
        print(f"已设置代理: {proxy}")
        print(f"yfinance版本: {yf.__version__}")
        
        # 尝试获取数据
        print("尝试获取AAPL数据...")
        ticker = yf.Ticker("AAPL")
        df = ticker.history(period="1y")
        
        if not df.empty:
            print("数据获取成功！")
            print(f"数据形状: {df.shape}")
            print("数据前5行:")
            print(df.head())
            return True
        else:
            print("数据获取成功，但返回空数据框")
            return False
    except Exception as e:
        print(f"yfinance数据获取异常: {e}")
        return False

if __name__ == "__main__":
    print("===== 开始测试 =====")
    proxy_ok = test_proxy()
    print("\n===== 测试yfinance =====")
    if proxy_ok:
        test_yfinance()
    else:
        print("代理测试失败，跳过yfinance测试")
    print("\n===== 测试结束 =====")