import ta

def add_features(df):

    # Convert columns to 1D
    close = df["Close"].squeeze()
    high = df["High"].squeeze()
    low = df["Low"].squeeze()
    volume = df["Volume"].squeeze()

    df["SMA10"] = close.rolling(10).mean()
    df["SMA50"] = close.rolling(50).mean()

    df["RSI"] = ta.momentum.RSIIndicator(close=close).rsi()

    macd = ta.trend.MACD(close=close)
    df["MACD"] = macd.macd()

    bb = ta.volatility.BollingerBands(close=close)

    df["BB_high"] = bb.bollinger_hband()
    df["BB_low"] = bb.bollinger_lband()

    df["returns"] = close.pct_change()

    df["volatility"] = df["returns"].rolling(10).std()

    df["momentum"] = close - close.shift(10)

    df["volatility_20"] = df["returns"].rolling(20).std()

    df["price_change"] = close.pct_change(3)

    df["ema20"] = close.ewm(span=20).mean()
    df["ema50"] = close.ewm(span=50).mean()

    df["trend_strength"] = df["ema20"] - df["ema50"]

    df["volume_ma"] = volume.rolling(20).mean()
    df["volume_ratio"] = volume / df["volume_ma"]

    df["price_range"] = high - low

    df = df.dropna()

    return df