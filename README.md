# ETL-Projects
這個 GitHub repository 收集了我在資料工程與 ETL 領域的專案，展示了我在資料抓取、轉換、清洗與儲存上的實作能力。每個專案都有完整程式碼、資料庫設計示意，以及執行方式說明。

技術:
Python: requests, psycopg2, pandas (可用於資料清理)

SQL: PostgreSQL

ETL: Extract → Transform → Load

API 整合與資料庫管理

排程: Airflow(Ubuntu)

## 如何使用

clone 專案：
git clone https://github.com/osmuntsun/ETL-Projects.git

安裝依賴：
pip install -r requirements.txt

執行程式:
python XXX.py


## 專案列表 (Projects)

### 1. Binance K線資料抓取與儲存
**目標**：建立一個自動化資料管線，從 Binance API 擷取加密貨幣 K 線 (OHLCV) 資料，進行資料轉換並存入 PostgreSQL 資料庫，並透過 Apache Airflow 進行排程，每小時自動更新市場資料，供後續量化分析與策略回測使用。

#### ETL Pipeline
    Binance API
        ↓
    Extract (Python requests)
        ↓
    Transform (data cleaning & timestamp conversion)
        ↓
    Load (PostgreSQL)
        ↓
    Airflow Scheduler (hourly update)

#### 主要功能
    1. 從 Binance REST API 擷取指定交易對的 K 線資料
    2. 將 API 回傳的 JSON 格式轉換為結構化資料
    3. 處理時間戳記轉換與資料型別清理
    4. 將資料儲存至 PostgreSQL
    5. 透過 Unique Constraint 避免重複資料寫入
    6. 使用 Apache Airflow 設定 DAG，每小時自動執行 ETL pipeline

#### 後續資料分析
    1. 在完成 ETL Pipeline 後，使用歷史資料進行技術分析與策略回測：
    2. 計算 Exponential Moving Average (EMA)
    3. 偵測 Golden Cross / Death Cross
    4. 建立 EMA crossover trading strategy
    5. 使用 Backtesting 比較策略績效與 Buy & Hold

