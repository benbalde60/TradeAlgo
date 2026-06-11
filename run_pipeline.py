# run_pipeline.py
import time
import pandas as pd
from aggregator import SentimentWindow
from events import event_surprise, event_signal
from technical import technical_confirm
from my_Signal import compute_S, decision_from_S
from backtest import run_backtest

PRICE_CSV = "eurusd_1h.csv"
NEWS_CSV = "news_feed.csv"
EVENTS_CSV = "events.csv"

# Load price data (ensure datetime index)
df_price = pd.read_csv(PRICE_CSV, parse_dates=['datetime']).sort_values('datetime').reset_index(drop=True)
df_price = df_price.rename(columns={'datetime': 'datetime'}).set_index('datetime')
df_price.index = pd.to_datetime(df_price.index)  # enforce datetime index

# Load news and events
df_news = pd.read_csv(NEWS_CSV) if True else pd.DataFrame(columns=['timestamp','text','author_id','followers','account_age_days','verified','posts_per_day'])
df_events = pd.read_csv(EVENTS_CSV) if True else pd.DataFrame(columns=['date','event_name','consensus','actual','significance'])

# Prepare sentiment window
sw = SentimentWindow(window_seconds=30*60)

# convert news timestamps to pandas datetime and sort, with validation
if not df_news.empty:
    df_news['timestamp'] = pd.to_datetime(df_news['timestamp'], errors='coerce')
    if df_news['timestamp'].isnull().any():
        bad_rows = df_news[df_news['timestamp'].isnull()].index.tolist()
        raise ValueError(f"Unparseable timestamps in news_feed.csv at rows: {bad_rows}")
    df_news = df_news.sort_values('timestamp').reset_index(drop=True)
news_idx = 0

# prepare events dict by date (date -> list)
if not df_events.empty:
    df_events['timestamp'] = pd.to_datetime(df_events['timestamp'], errors='coerce')
    if df_events['timestamp'].isnull().any():
        bad_rows = df_events[df_events['timestamp'].isnull()].index.tolist()
        raise ValueError(f"Unparseable dates in events.csv at rows: {bad_rows}")
events_list = []

for _, r in df_events.iterrows():
    events_list.append(r)

# signal function to pass into backtester
def signal_func(idx, df):
    # map index to pandas Timestamp explicitly
    ts = pd.to_datetime(df.index[idx])

    # ingest any news up to this timestamp into sentiment window
    global news_idx
    while news_idx < len(df_news) and pd.to_datetime(df_news.iloc[news_idx]['timestamp']) <= ts:
        row = df_news.iloc[news_idx]
        account_meta = {
            "author_id": row.get("author_id"),
            "followers": row.get("followers", 0),
            "account_age_days": row.get("account_age_days", 0),
            "verified": bool(row.get("verified", False)),
            "posts_per_day": row.get("posts_per_day", 0)
        }
        post_ts = pd.to_datetime(row['timestamp'])

        # Try POSIX float timestamp first; if SentimentWindow expects datetime object, fall back
        try:
            sw.add_post(str(row.get("text", "")), account_meta, timestamp=post_ts.timestamp())
        except TypeError:
            sw.add_post(str(row.get("text", "")), account_meta, timestamp=post_ts)

        news_idx += 1

    vw_sent, author_count = sw.aggregate()

    # event signal if event today (use date floor)
    evt_comp = 0.0

    for ev in events_list:
        ev_ts = pd.to_datetime(ev['timestamp'])

        # only use already released events
        if 0 <= (ts - ev_ts).total_seconds() <= 6 * 3600:
            surprise = event_surprise(ev['actual'], ev['consensus'])
            evt_comp += event_signal(ev['significance'], surprise)
        print("news processed:", news_idx, "sentiment window size:", sw.window)
    # novelty placeholder (0..1). For simulation use 0.2*author_count normalization
    novelty = min(author_count / 50.0, 1.0)

    # technical confirm: give technical window up to current idx (last 24-48 bars)
    lookback = max(0, idx - 48)
    df_slice = df.iloc[lookback:idx+1]
    tech = technical_confirm(df_slice)
    S = compute_S(evt_comp, vw_sent, novelty, tech)

    decision, score = decision_from_S(S)

    # DEBUG OUTPUT
    if idx % 50 == 0:
        print("S:", S, "components:", vw_sent, evt_comp, novelty, tech)
    if idx % 100 == 0:
        print({
            "timestamp": ts,
            "event": evt_comp,
            "sentiment": vw_sent,
            "novelty": novelty,
            "tech": tech,
            "S": S,
            "decision": decision
        })

    meta = {
        "vw_sentiment": vw_sent,
        "author_count": author_count,
        "evt_comp": evt_comp,
        "novelty": novelty,
        "tech_conf": tech
    }

    return decision, score, meta

if __name__ == "__main__":
    result = run_backtest(df_price.reset_index().rename(columns={'index': 'datetime'}).set_index('datetime'), signal_func)
    print("Total PnL:", result.get('total_pnl'))
    print("Win rate:", result.get('win_rate'))
    print("Avg trade PnL:", result.get('avg_pnl'))
    print("Max drawdown:", result.get('max_drawdown'))
    print("Trades executed:", len(result['trades']))
    result['trades'].to_csv("trades_out.csv", index=False)
    result['equity_curve'].to_csv("equity_curve.csv", index=False)