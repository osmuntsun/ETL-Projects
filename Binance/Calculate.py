import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import numpy as np


# 從環境變數讀取敏感資料
load_dotenv()  # 從 .env 文件加載環境變數
DB_PASSWORD = os.getenv("DB_PASSWORD")

def calculate_EMA(df, window):
    df[f'EMA_{window}'] = df['close'].ewm(span=window, adjust=False).mean()
    return df

def calculate_volatility(df):
    df["return"] = np.log(df["close"] / df["close"].shift(1))
    df["volatility"] = df["return"].rolling(20).std()
    return df

def read_data_from_db(symbol):
    conn = psycopg2.connect(
        host="localhost",
        database="Binance_DB",
        user="postgres",
        password=DB_PASSWORD
    )
    query = """
    SELECT timestamp, open, high, low, close, volume
    FROM futures_market_data
    WHERE symbol = %s
    ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, params=(symbol,))
    df = calculate_EMA(df, 12) # 計算EMA 12
    df = calculate_EMA(df, 26)  # 計算EMA 26
    df = calculate_volatility(df) # 計算波動率

    # 根據EMA的關係來判斷趨勢
    df["trend"] = "neutral"
    df.loc[df["EMA_12"] > df["EMA_26"], "trend"] = "bullish"
    df.loc[df["EMA_12"] < df["EMA_26"], "trend"] = "bearish"

    # 添加前一行的EMA值作為新的列，以便後續計算黃金交叉或是死亡交叉
    df["prev_ema12"] = df["EMA_12"].shift(1)
    df["prev_ema26"] = df["EMA_26"].shift(1)
    df["golden_cross"] = (
    (df["prev_ema12"] < df["prev_ema26"]) &
    (df["EMA_12"] > df["EMA_26"])
    )
    df["death_cross"] = (
    (df["prev_ema12"] > df["prev_ema26"]) &
    (df["EMA_12"] < df["EMA_26"])
    )

    # 根據黃金交叉和死亡交叉的條件來生成交易信號
    df["signal"] = "hold"
    df.loc[df["golden_cross"], "signal"] = "buy"
    df.loc[df["death_cross"], "signal"] = "sell"

    conn.close()
    return df



data = read_data_from_db("BTCUSDT")



#  繪製價格和EMA指標的圖表
import matplotlib.pyplot as plt

plt.figure(figsize=(12,6))
plt.plot(data["timestamp"], data["close"], label="Price")
plt.plot(data["timestamp"], data["EMA_12"], label="EMA12")
plt.plot(data["timestamp"], data["EMA_26"], label="EMA26")

plt.legend()
plt.show()

