TradeAlgo is a modular quantitative trading research framework designed to evaluate trading signals derived from a combination of:

News sentiment analysis (NLP-based)
Macroeconomic event surprises
Technical indicators (ATR, EMA)
Multi-factor signal aggregation

The system integrates these signals into a unified scoring model (S-score) and evaluates performance through a realistic event-driven backtesting engine that includes spreads, slippage, and dynamic position sizing.

This project demonstrates end-to-end capability in:

Data engineering
Signal processing
Financial modeling
Backtesting system design
NLP integration into quantitative workflows
System Architecture

The pipeline is structured into four core components:

1. Data Layer
Historical FX OHLCV data (EURUSD 1H)
News dataset with metadata (author credibility, engagement signals)
Economic event calendar (actual vs consensus)
2. Signal Generation Layer
Sentiment extraction using transformer-based NLP model
Event surprise quantification (actual vs forecast deviation)
Technical confirmation signals (ATR, trend filters)
3. Aggregation Layer
Rolling sentiment window with credibility-weighted scoring
Novelty adjustment based on unique information flow
Multi-factor signal fusion into a single S-score
4. Execution & Backtesting Engine
Event-driven simulation
Spread + slippage modeling
ATR-based dynamic stop-loss / take-profit
Risk-based position sizing
Equity curve tracking + performance metrics
Signal Model

The core decision variable is:

S-score = f(sentiment, event impact, novelty, technical confirmation)

Where:

Sentiment reflects aggregated NLP sentiment over a rolling window
Event impact measures macroeconomic surprise magnitude
Novelty estimates information freshness / crowding
Technical confirmation validates market structure alignment

Trade decisions are derived from:

BUY if S exceeds positive threshold
SELL if S falls below negative threshold
HOLD otherwise
Backtesting Engine Features

The backtester simulates realistic execution conditions:

Bid/ask spread modeling
Slippage approximation
Stop-loss and take-profit execution
Time-based trade exit horizon
Position sizing based on account risk %
Equity curve generation
Performance statistics:
Total PnL
Win rate
Average trade return
Maximum drawdown
Risk Model

Position sizing is dynamically computed using:

Fixed fractional risk model (default: 0.5% per trade)
ATR-based stop-loss distance
Pip-value normalization for FX instruments

This ensures:

consistent risk exposure across volatility regimes
scalable position sizing based on account equity
Technologies Used
Python 3.10+
Pandas / NumPy
HuggingFace Transformers (RoBERTa sentiment model)
Time-series simulation logic
Custom event-driven backtesting framework
How It Works
Load historical FX price data
Stream news and macro events chronologically
Compute rolling sentiment score
Align macroeconomic surprises with price timeline
Generate S-score from multi-factor fusion
Execute trades in simulated environment
Track equity curve and performance metrics

📈 Example Output
Total PnL: 5833.10
Win rate: 75%
Max drawdown: -1.0%
Trades executed: 12

Note: Results are dependent on dataset size, signal thresholds, and backtest configuration.

Limitations

This project is a research-grade prototype, not a production trading system.

Current limitations include:

Limited sample size in backtests
Simple threshold-based decision logic
No walk-forward validation
No parameter optimization framework
No execution latency modeling
No live market integration
Future Improvements

Planned enhancements:

 Signal calibration using quantile-based decisioning
 Walk-forward validation pipeline
 Benchmark strategies (MA crossover, random baseline)
 Sharpe ratio + statistical significance testing
 Regime detection (trend vs mean reversion)
 Probabilistic position sizing model
 Live data ingestion (broker API integration).
