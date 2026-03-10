import pandas as pd
import numpy as np
from Calculate import *

data = read_data_from_db("BTCUSDT")
# 初始化資金和持倉狀態
initial_capital = 1000000  # 初始資金
cash = initial_capital  # 現金
position = 0  # 持倉量

portfolio_values = []

for index, row in data.iterrows():
    if row["signal"] == "buy" and cash > 0:
        # 買入，假設每次買入1000美元的BTC
        buy_amount = min(1000, cash)  # 確保不超過現金
        position += buy_amount / row["close"]  # 增加持倉量
        cash -= buy_amount  # 扣除支出的現金
    elif row["signal"] == "sell" and position > 0:
        # 賣出，假設每次賣出1000美元的BTC
        sell_amount = min(1000, position * row["close"])  # 確保不超過持倉量
        position -= sell_amount / row["close"]  # 減少持倉量
        cash += sell_amount  # 增加現金
    # 計算投資組合價值
    portfolio_value = cash + position * row["close"]
    portfolio_values.append(portfolio_value)

data["strategy_value"] = portfolio_values
# 計算策略的總回報率
total_return = (data["strategy_value"].iloc[-1] - initial_capital) / initial_capital
print(f"總回報率: {total_return:.2%}")

btc_hold = initial_capital / data.iloc[0]["close"]
data["buy_hold_value"] = btc_hold * data["close"]


buyhold_return = (data["buy_hold_value"].iloc[-1] / data["buy_hold_value"].iloc[0] - 1) * 100
print(f"買持有回報率: {buyhold_return:.2f}%")

print(data[["timestamp", "close", "signal", "strategy_value", "buy_hold_value"]].tail(10))

"""
時間區間 2026/2/1 - 2026/3/10 1H
透過EMA12和EMA26的交叉來判斷趨勢並進行交易，並與買持有策略進行比較。
成果為:
EMA交叉策略的總回報率: -0.00% (很微小的虧損，幾乎持平)
買持有策略的回報率: -20.73%
"""
