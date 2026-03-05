import ta


def add_features(df):

    df["SMA10"] = df["Close"].rolling(10).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()

    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()

    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()

    bb = ta.volatility.BollingerBands(df["Close"])

    df["BB_high"] = bb.bollinger_hband()
    df["BB_low"] = bb.bollinger_lband()

    df["returns"] = df["Close"].pct_change()

    df["volatility"] = df["returns"].rolling(10).std()

    df["momentum"] = df["Close"] - df["Close"].shift(10)

    df["volatility_20"] = df["returns"].rolling(20).std()

    df["price_change"] = df["Close"].pct_change(3)

    df["ema20"] = df["Close"].ewm(span=20).mean()
    df["ema50"] = df["Close"].ewm(span=50).mean()

    df["trend_strength"] = df["ema20"] - df["ema50"]

    df["volume_ma"] = df["Volume"].rolling(20).mean()
    df["volume_ratio"] = df["Volume"] / df["volume_ma"]

    df["price_range"] = df["High"] - df["Low"]

    df = df.dropna()

    return df