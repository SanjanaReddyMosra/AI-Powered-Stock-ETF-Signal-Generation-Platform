import pandas as pd
import ta


def create_features():

    # ---------- Read Data ----------

    df = pd.read_csv("data/stock_data.csv")

    df = df[['Open','High','Low','Close','Volume']]

    # Convert numeric safely
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # ---------- Technical Indicators ----------

    # RSI
    df['RSI'] = ta.momentum.RSIIndicator(
        close=df['Close']
    ).rsi()

    # EMA
    df['EMA20'] = ta.trend.EMAIndicator(
        close=df['Close'],
        window=20
    ).ema_indicator()

    df['EMA50'] = ta.trend.EMAIndicator(
        close=df['Close'],
        window=50
    ).ema_indicator()

    # Drop EMA warmup NaNs
    df.dropna(inplace=True)

    # MACD
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = macd.macd()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(
        close=df['Close']
    )

    df['BB_high'] = bb.bollinger_hband()
    df['BB_low'] = bb.bollinger_lband()

    # Price position inside Bollinger Band ⭐
    df['BB_position'] = (
        (df['Close'] - df['BB_low']) /
        (df['BB_high'] - df['BB_low'])
    )

    # ---------- Feature Engineering ----------

    df['Return'] = df['Close'].pct_change()

    # Momentum
    df['Momentum'] = df['Close'] - df['Close'].shift(5)

    # Lag Features
    for i in range(1, 6):
        df[f'lag{i}'] = df['Return'].shift(i)

    # Volatility
    df['volatility'] = df['Return'].rolling(10).std()

    # Volume Change
    df['Volume_change'] = df['Volume'].pct_change()

    # ---------- Smart Labeling (10-day horizon) ----------

    future_return = (
        df['Close'].shift(-10) - df['Close']
    ) / df['Close']

    def label(x):

        if x > 0.02:
            return 1   # BUY

        elif x < -0.02:
            return 0   # SELL

        else:
            return None

    df['Target'] = future_return.apply(label)

    # Remove HOLD rows
    df.dropna(subset=['Target'], inplace=True)

    # ---------- Trend Filter (Applied AFTER labeling) ----------

    df = df[
        abs(df['EMA20'] - df['EMA50'])
        >
        0.007 * df['Close']
    ]

    # Remove remaining NaNs
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    print("Total Samples:", len(df))

    # ---------- Save ----------

    df.to_csv(
        "data/features.csv",
        index=False
    )

    print("Features Created Successfully")


if __name__ == "__main__":
    create_features()