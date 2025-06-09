import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 設定股票代號與標籤
tickers = {
    "TSM": "TSMC",
    "AAPL": "Apple",
    "NKE": "Nike"
}

# 加入 S&P500
sp500_symbol = "^GSPC"

# 下載 10 年資料（2014/06 ~ 2024/06）
symbols = list(tickers.keys()) + [sp500_symbol]
data = yf.download(symbols, start="2014-06-01", end="2024-06-01")["Close"]

# 計算總報酬率 (%)
returns = (data.iloc[-1] / data.iloc[0] - 1) * 100

# 計算年化報酬率（CAGR）
years = 10
cagr = (data.iloc[-1] / data.iloc[0]) ** (1 / years) - 1
cagr = cagr * 100

# 正規化股價（起始 = 100）
normalized = data / data.iloc[0] * 100

# 建立新的名稱列表（包含 ticker 與公司名稱）
new_labels = []
for t in data.columns:
    if t in tickers:
        new_labels.append(f"{tickers[t]} ({t})")
    elif t == "^GSPC":
        new_labels.append("S&P 500 (^GSPC)")
    else:
        new_labels.append(t)

# 套用名稱
returns.index = new_labels
cagr.index = new_labels
normalized.columns = new_labels

# 匯出報酬率與 CAGR 成 CSV
returns.round(2).sort_values(ascending=False).to_csv("10_year_returns.csv")
cagr.round(2).sort_values(ascending=False).to_csv("10_year_CAGR.csv")
print("📊 10-Year Return exported to '10_year_returns.csv'")
print("📈 10-Year CAGR exported to '10_year_CAGR.csv'")

# 印出年化報酬率
print("\n📈 10-Year CAGR (%):")
print(cagr.round(2).sort_values(ascending=False))

# 畫出 10 年正規化走勢圖
plt.figure(figsize=(12, 6))
for col in normalized.columns:
    plt.plot(normalized.index, normalized[col], label=col)

plt.title("10-Year Stock Performance Comparison (2014–2024)")
plt.xlabel("Year")
plt.ylabel("Normalized Price (Start = 100)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("10_year_chart.png")
plt.show()

# ========== 自訂區間分析與輸出 ==========

def analyze_period(years, label):
    end_date = data.index[-1]
    start_date = end_date - pd.DateOffset(years=years)
    period_data = data[(data.index >= start_date) & (data.index <= end_date)]

    # 總報酬率
    ret = (period_data.iloc[-1] / period_data.iloc[0] - 1) * 100

    # 年化報酬率
    cagr = (period_data.iloc[-1] / period_data.iloc[0]) ** (1 / years) - 1
    cagr = cagr * 100

    # 套用名稱（用 rename 避免 index 對不起來）
    rename_dict = {t: f"{tickers[t]} ({t})" for t in tickers}
    rename_dict["^GSPC"] = "S&P 500 (^GSPC)"

    ret = ret.rename(index=rename_dict)
    cagr = cagr.rename(index=rename_dict)

    # 匯出 CSV
    ret.round(2).sort_values(ascending=False).to_csv(f"{label}_returns.csv")
    cagr.round(2).sort_values(ascending=False).to_csv(f"{label}_CAGR.csv")

    # 印出
    print(f"\n📊 {label} Return (%):")
    print(ret.round(2).sort_values(ascending=False))

    print(f"\n📈 {label} CAGR (%):")
    print(cagr.round(2).sort_values(ascending=False))

    return period_data

# 畫圖函數
def plot_period(years, label):
    end_date = data.index[-1]
    start_date = end_date - pd.DateOffset(years=years)
    period_data = data[(data.index >= start_date) & (data.index <= end_date)]
    period_norm = period_data / period_data.iloc[0] * 100
    period_norm.columns = new_labels

    plt.figure(figsize=(12, 6))
    for col in period_norm.columns:
        plt.plot(period_norm.index, period_norm[col], label=col)

    plt.title(f"{label} Stock Performance Comparison")
    plt.xlabel("Year")
    plt.ylabel("Normalized Price (Start = 100)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{label}_normalized_chart.png")
    plt.show()

# 執行分析與畫圖
analyze_period(5, "5_year")
analyze_period(1, "1_year")
plot_period(5, "5_Year")
plot_period(1, "1_Year")

import numpy as np

init_money = 10_000_000  # 你的本金（單位：與股價相同，例如美金或台幣）

results = []

for ticker, label in tickers.items():
    prices = data[ticker].dropna()
    max_return = -np.inf
    best_buy_date = None
    best_final_value = None

    for buy_date in prices.index[:-1]:  # 最後一天不能買
        buy_price = prices.loc[buy_date]
        sell_price = prices.iloc[-1]
        shares = init_money / buy_price
        final_value = shares * sell_price
        profit = final_value - init_money
        ret_rate = profit / init_money

        if profit > max_return:
            max_return = profit
            best_buy_date = buy_date
            best_final_value = final_value

    results.append({
        "Stock": f"{label} ({ticker})",
        "Best Entry Date": best_buy_date.strftime("%Y-%m-%d"),
        "Total Profit": round(max_return, 2),
        "Final Value": round(best_final_value, 2),
        "Return Rate (%)": round(max_return / init_money * 100, 2)
    })

# 輸出最優進場時點
print("\n📈 Best Entry Strategies in 10 Years (ALL-IN Once):")
for r in results:
    print(f"\n{r['Stock']}")
    print(f"  ➤ Best Buy Date: {r['Best Entry Date']}")
    print(f"  ➤ Final Asset: {r['Final Value']:,}")
    print(f"  ➤ Total Profit: {r['Total Profit']:,}")
    print(f"  ➤ Return Rate: {r['Return Rate (%)']} %")

# 選出三檔中最強進場方案
best = max(results, key=lambda x: x["Total Profit"])
print("\n💡 Among all, the best is:")
print(f"{best['Stock']} on {best['Best Entry Date']} → profit {best['Total Profit']:,} ({best['Return Rate (%)']}%)")