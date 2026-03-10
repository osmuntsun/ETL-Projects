# ETL-Projects
這個 GitHub repository 收集了我在資料工程與 ETL 領域的專案，展示了我在資料抓取、轉換、清洗與儲存上的實作能力。每個專案都有完整程式碼、資料庫設計示意，以及執行方式說明。

技術:
Python: requests, psycopg2, pandas (可用於資料清理)

SQL: PostgreSQL

ETL: Extract → Transform → Load

API 整合與資料庫管理

排程: Airflow(Ubuntu)


## 專案列表 (Projects)

### 1. Binance K線資料抓取與儲存
**目標**：從 Binance API 取得 K 線數據，存入 PostgreSQL 資料庫，方便後續分析，並在Airflow進行每小時執行。  


如何使用

clone 專案：

git clone https://github.com/osmuntsun/ETL-Projects.git

安裝依賴：

pip install -r requirements.txt

執行程式:
python XXX.py
