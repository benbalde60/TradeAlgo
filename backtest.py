# backtest.py
import pandas as pd
import numpy as np

PIP = 0.0001
SPREAD_PIPS = 0.1
SLIPPAGE_PIPS = 0.2
CONTRACT_SIZE = 100000  # standard lot
INITIAL_EQ = 100000
BASE_RISK_PCT = 0.005  # 0.5% per trade

def apply_fees(price, side):
    adj = (SPREAD_PIPS / 2 + SLIPPAGE_PIPS) * PIP
    return price + adj if side == 'BUY' else price - adj

def atr(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def position_size(equity, stop_pips, risk_pct=BASE_RISK_PCT):
    risk_amount = equity * risk_pct
    pip_value = 10  # USD per pip per standard lot on EURUSD ~ $10
    lots = risk_amount / (stop_pips * pip_value + 1e-9)
    return max(lots, 0.0)

def max_drawdown(equity_series):
    roll_max = equity_series.cummax()
    drawdown = (equity_series - roll_max) / roll_max
    return drawdown.min()

def run_backtest(df_1h, signal_func):
    """
    df_1h: DataFrame with datetime index and columns open, high, low, close
    signal_func(row_index) -> ('BUY'/'SELL'/'HOLD', score, additional_meta)
    """
    df = df_1h.copy()
    df['atr'] = atr(df)
    df['ema20'] = df['close'].ewm(span=20).mean()

    equity = INITIAL_EQ
    equity_curve = []
    trades = []

    i = 0
    while i < len(df):
        row = df.iloc[i]
        equity_curve.append(equity)
        dec, score, meta = signal_func(i, df)  # user-supplied signal function
        if dec == 'HOLD' or np.isnan(row['atr']):
            i += 1
            continue

        stop_pips = max((1.5 * row['atr']) / PIP, 1.0)
        target_pips = 2.0 * stop_pips

        lots = position_size(equity, stop_pips, BASE_RISK_PCT)
        if lots <= 0:
            i += 1
            continue

        entry_price = apply_fees(row['close'], dec)
        stop_price = entry_price - stop_pips * PIP if dec == 'BUY' else entry_price + stop_pips * PIP
        target_price = entry_price + target_pips * PIP if dec == 'BUY' else entry_price - target_pips * PIP

        exit_price = None
        exit_index = i
        max_horizon = min(i + 48, len(df) - 1)
        pnl_pips = None
        for j in range(i + 1, max_horizon + 1):
            high = df.iloc[j]['high']
            low = df.iloc[j]['low']
            if dec == 'BUY':
                if low <= stop_price:
                    exit_price = apply_fees(stop_price, 'SELL' if dec == 'BUY' else 'BUY')
                    exit_index = j
                    pnl_pips = -stop_pips
                    break
                if high >= target_price:
                    exit_price = apply_fees(target_price, 'SELL' if dec == 'BUY' else 'BUY')
                    exit_index = j
                    pnl_pips = target_pips
                    break
            else:
                if high >= stop_price:
                    exit_price = apply_fees(stop_price, 'SELL' if dec == 'BUY' else 'BUY')
                    exit_index = j
                    pnl_pips = -stop_pips
                    break
                if low <= target_price:
                    exit_price = apply_fees(target_price, 'SELL' if dec == 'BUY' else 'BUY')
                    exit_index = j
                    pnl_pips = target_pips
                    break

        if exit_price is None:
            exit_price = apply_fees(df.iloc[max_horizon]['close'], 'SELL' if dec == 'BUY' else 'BUY')
            raw_pips = (exit_price - entry_price) / PIP
            pnl_pips = raw_pips if dec == 'BUY' else -raw_pips

        pnl = lots * CONTRACT_SIZE * (pnl_pips * PIP)
        equity += pnl

        trades.append({
            'entry_index': i,
            'exit_index': exit_index,
            'decision': dec,
            'score': score,
            'entry': entry_price,
            'exit': exit_price,
            'lots': lots,
            'pnl': pnl,
            'equity': equity,
            **(meta or {})
        })

        i = exit_index + 1

    equity_curve = pd.Series(equity_curve, index=df.index[:len(equity_curve)])
    total_pnl = equity - INITIAL_EQ
    win_trades = [t for t in trades if t['pnl'] > 0]
    win_rate = len(win_trades) / len(trades) if trades else 0.0
    avg_pnl = np.mean([t['pnl'] for t in trades]) if trades else 0.0
    max_dd = max_drawdown(equity_curve)

    return {
        'equity_curve': equity_curve,
        'trades': pd.DataFrame(trades),
        'total_pnl': total_pnl,
        'win_rate': win_rate,
        'avg_pnl': avg_pnl,
        'max_drawdown': max_dd
    }