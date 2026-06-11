# technical.py
import pandas as pd
import numpy as np

def ema(series, span=20):
    return series.ewm(span=span).mean()

def atr(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def technical_confirm(df_hourly):
    """
    df_hourly: DataFrame with columns ['open','high','low','close'], indexed by time ascending.
    Returns +1 buy confirm, -1 sell confirm, 0 none.
    """
    if len(df_hourly) < 25:
        return 0
    close = df_hourly['close']
    ema20 = ema(close, span=20)
    # EMA crossover check (last bar)
    if close.iloc[-1] > ema20.iloc[-1] and close.iloc[-2] <= ema20.iloc[-2]:
        return 1
    if close.iloc[-1] < ema20.iloc[-1] and close.iloc[-2] >= ema20.iloc[-2]:
        return -1
    # breakout by ATR
    atr_val = atr(df_hourly).iloc[-1]
    if np.isnan(atr_val) or atr_val <= 0:
        return 0
    high_max = df_hourly['high'].rolling(14).max().iloc[-1]
    low_min = df_hourly['low'].rolling(14).min().iloc[-1]
    if close.iloc[-1] > high_max + 0.2 * atr_val:
        return 1
    if close.iloc[-1] < low_min - 0.2 * atr_val:
        return -1
    return 0