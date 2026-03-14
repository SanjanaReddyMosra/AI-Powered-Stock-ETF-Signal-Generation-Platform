import pandas as pd
import numpy as np

def calculate_metrics(df):
    """
    Calculate key performance metrics for the ML signal strategy.
    Expects df with 'close' and 'Signal' columns.
    """
    if 'Signal' not in df.columns or df.empty:
        return None

    # Calculate returns
    df = df.copy()
    df['returns'] = df['close'].pct_change()
    
    # Strategy returns: 
    # Logic: If Signal is BUY, we hold for the next day. 
    # If SELL, we are out (or short, but let's assume long-only for simplicity).
    # Shift signals by 1 to represent the action taken on the previous close
    df['position'] = df['Signal'].map({'BUY': 1, 'SELL': 0, 'HOLD': 0}).shift(1).fillna(0)
    df['strategy_returns'] = df['position'] * df['returns']
    
    # 1. Cumulative Returns
    equity_curve = (1 + df['strategy_returns']).cumprod()
    total_return = (equity_curve.iloc[-1] - 1) * 100 if not equity_curve.empty else 0
    
    # 2. Sharpe Ratio (Annualized, assuming 252 trading days)
    risk_free_rate = 0.02 # 2% proxy
    avg_return = df['strategy_returns'].mean() * 252
    std_dev = df['strategy_returns'].std() * np.sqrt(252)
    sharpe_ratio = (avg_return - risk_free_rate) / std_dev if std_dev != 0 else 0
    
    # 3. Max Drawdown
    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve - rolling_max) / rolling_max
    max_drawdown = drawdown.min() * 100
    
    # 4. Win Rate
    # A "win" is a profitable day when we have a position
    active_days = df[df['position'] == 1]
    if not active_days.empty:
        wins = active_days[active_days['returns'] > 0]
        win_rate = (len(wins) / len(active_days)) * 100
    else:
        win_rate = 0
        
    return {
        "total_return": total_return,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "equity_curve": equity_curve
    }

def run_backtest(df):
    """Wrapper for external calls"""
    return calculate_metrics(df)
