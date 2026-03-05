import pandas as pd
import joblib

from src.feature_engineering import add_features


def signal(stock):

    model=joblib.load(f"models/{stock}.pkl")

    df=pd.read_csv(f"data/{stock}.csv")

    df=add_features(df)

    X=df[[
    "SMA10","SMA50","RSI","MACD",
    "BB_high","BB_low","returns","volatility"
    ]]

    latest=X.iloc[-1:]

    pred=model.predict(latest)[0]

    if pred==1:
        return "BUY"
    else:
        return "SELL"