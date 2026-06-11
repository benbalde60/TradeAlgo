EUR/USD news+sentiment backtest pipeline (starter)

Files:

- requirements.txt
- sentiment.py
- filter.py
- aggregator.py
- events.py
- technical.py
- signal.py
- backtest.py
- run_pipeline.py

CSV inputs (examples):

- eurusd_1h.csv: datetime, open, high, low, close (1-hour bars)
- news_feed.csv: timestamp, text, author_id, followers, account_age_days, verified, posts_per_day
- events.csv: date, event_name, consensus, actual, significance

Run:

1. pip install -r requirements.txt
2. Fill CSV files (or use sample data).
3. python run_pipeline.py

Notes:

- This is a starter template. Calibrate weights, thresholds, and risk sizing before live use.
- Replace sentiment model, novelty detection, and news ingestion with production-grade sources/APIs for real deployments.
