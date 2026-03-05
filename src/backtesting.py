import pandas as pd
import joblib
from feature_engineering import add_features


def backtest(stock):

    model=joblib.load(f"models/{stock}.pkl")

    df=pd.read_csv(f"data/{stock}.csv")

    df=add_features(df)

    X=df[[
    "SMA10","SMA50","RSI","MACD",
    "BB_high","BB_low","returns","volatility"
    ]]

    df["prediction"]=model.predict(X)

    df["strategy_return"]=df["returns"]*df["prediction"]

    sharpe=df["strategy_return"].mean()/df["strategy_return"].std()

    win_rate=(df["strategy_return"]>0).mean()

    print("Sharpe Ratio:",sharpe)

    print("Win Rate:",win_rate)