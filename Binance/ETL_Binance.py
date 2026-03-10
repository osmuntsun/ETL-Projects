import requests
import psycopg2
from psycopg2 import errors
import datetime
import os
from dotenv import load_dotenv

# 從環境變數讀取敏感資料
load_dotenv()  # 從 .env 文件加載環境變數
DB_PASSWORD = os.getenv("DB_PASSWORD")

# get_klines 返回的是列表：[[timestamp, open, high, low, close, volume, ...], ...]
def get_klines(symbol, interval, timeZone='+8:00', limit=500):
    req = requests.Session()
    '''

    來源: https://developers.binance.com/docs/zh-CN/binance-spot-api-docs/rest-api/market-data-endpoints#k%E7%BA%BF%E6%95%B0%E6%8D%AE
    /api/v3/klines K棒數據
    預設抓取最近500筆資料，最多可抓取1000筆資料

    參數說明
    參數	類型	必填	說明   
    symbol	STRING	YES	交易對，例如：BTCUSDT
    interval	ENUM	YES	K線的時間間隔，請參考K線時間間隔說明
    startTime	LONG	NO	K線的開始時間，單位為毫秒
    endTime	LONG	NO	K線的結束時間，單位為毫秒
    timeZone STRING	NO	返回的K線數據的時間戳格式，預設為UTC，支持UTC和CST +8:00是換成台灣時間
    limit	INT	NO	返回的K線數據條數，預設為500，最大為1000
    '''
    palyload = {
        'symbol': symbol,
        'interval': interval,
        'timeZone': timeZone,
        'limit': limit
    }
    response = req.get("https://data-api.binance.vision/api/v3/klines", params=palyload).json()
    return response

def save_data_to_db(symbol,data):
    conn = psycopg2.connect(
        host="localhost",
        database="Binance_DB",
        user="postgres",
        password=DB_PASSWORD
    )

    cursor = conn.cursor()

    query = """
    INSERT INTO futures_market_data
    (symbol, timestamp, open, high, low, close, volume)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    dt = datetime.datetime.fromtimestamp(data[0] / 1000)

    try:
        cursor.execute(query,(
            symbol,
            dt, # 開盤時間
            data[1], # 開盤價
            data[2], # 最高價
            data[3], # 最低價
            data[4], # 收盤價
            data[5]  # 成交量
        ))
        conn.commit()
    except errors.UniqueViolation:
        # print(f"已有資料: {symbol} - {dt}")
        conn.rollback() # 發生錯誤時回滾事務，確保資料庫保持一致性
    except Exception as e:
        print(f"插入失敗: {e}")
        conn.rollback() # 發生錯誤時回滾事務，確保資料庫保持一致性
    finally:
        cursor.close()
        conn.close()
    
def get_latest_timestamp(symbol):
    conn = psycopg2.connect(
        host="localhost",
        database="Binance_DB",
        user="postgres",
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    query = """
    SELECT MAX(timestamp) FROM futures_market_data WHERE symbol = %s   
    """
    cursor.execute(query, (symbol,))
    # 獲取最新的時間戳，如果資料庫中沒有該交易對的資料，則返回 None
    latest_timestamp = cursor.fetchone()[0] 
    if latest_timestamp is None:
        latest_timestamp = datetime.datetime(2026, 1, 1) # 如果沒有資料，則從2020年1月1日開始抓取
    cursor.close()
    conn.close()
    return latest_timestamp

# 獲取最新的時間戳，這將用於確定從何時開始抓取新的K線數據
latest_timestamp = get_latest_timestamp("BTCUSDT")

# 計算從最新的時間戳到現在的時間差，並將其轉換為小時數
time_diff = datetime.datetime.now() - latest_timestamp

if time_diff.total_seconds() < 3600: # 如果時間差小於1小時，則不需要抓取新的數據
    print("時間差小於1小時，不需要抓取新的數據")
else:
    # 獲得K線數據
    limits = min(int(time_diff.total_seconds() // 3600), 1000) # 計算需要抓取的K線數量，最多不超過1000
    data = get_klines("BTCUSDT", "1h", timeZone='+8:00', limit=limits)
    # 將每筆K線數據存入資料庫，這裡 i 是每個 K 線項目，如 [timestamp, open, high, low, close, volume]
    for i in data:
        save_data_to_db("BTCUSDT", i)

