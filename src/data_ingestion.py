import yfinance as yf
import pandas as pd
import numpy as np
import ta
import datetime
from .config import config

def fetch_data(ticker, lookback_years=config.LOOKBACK_PERIOD_YEARS):
    """Fetch historical daily data for a given ticker."""
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365 * lookback_years)
    
    try:
        df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        if df.empty:
            return None
        # Flatten MultiIndex columns if present (yfinance sometimes does this on single ticker)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def engineer_features(df):
    """
    Apply a comprehensive suite of technical indicators using the 'ta' library
    to maximize signal robustness and model accuracy.
    """
    df = df.copy()
    
    # Needs to ensure columns are clean
    df.columns = [col.lower() for col in df.columns]
    
    # 1. Momentum Indicators
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    df['stoch'] = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close']).stoch()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_diff'] = macd.macd_diff()

    # 2. Trend Indicators
    df['sma_20'] = ta.trend.SMAIndicator(df['close'], window=20).sma_indicator()
    df['sma_50'] = ta.trend.SMAIndicator(df['close'], window=50).sma_indicator()
    df['ema_20'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
    
    # 3. Volatility Indicators
    bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
    df['bb_high'] = bb.bollinger_hband()
    df['bb_low'] = bb.bollinger_lband()
    df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()

    # 4. Lagged Returns & Price Changes
    df['return_1d'] = df['close'].pct_change(1)
    df['return_5d'] = df['close'].pct_change(5)
    df['lag_1'] = df['close'].shift(1)
    df['lag_2'] = df['close'].shift(2)
    
    # Drop rows with NaNs introduced by indicator windows
    df = df.dropna()
    return df

def create_target_variable(df, forward_days=5):
    """
    Create classification target:
    1 = Buy (Price goes up by > 1% over next 5 days)
    0 = Hold (Price stays within -1% to 1%)
    -1 = Sell (Price goes down by < -1% over next 5 days)
    """
    df = df.copy()
    
    # Calculate future return
    df['future_return'] = df['close'].shift(-forward_days) / df['close'] - 1
    
    conditions = [
        (df['future_return'] > 0.01),
        (df['future_return'] < -0.01)
    ]
    choices = [1, -1] # 1: Buy, -1: Sell
    
    # 0 is Hold
    df['target'] = np.select(conditions, choices, default=0)
    
    # Drop the last 'forward_days' rows because we don't know their future return yet
    df = df.dropna()
    return df
