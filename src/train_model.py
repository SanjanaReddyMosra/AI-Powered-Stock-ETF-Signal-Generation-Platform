import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.utils import resample

from src.feature_engineering import add_features


def train(stock):

    df = pd.read_csv(f"data/{stock}.csv")

    df = df[["Open", "High", "Low", "Close", "Volume"]]

    numeric_cols = ["Open", "High", "Low", "Close", "Volume"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()

    # add technical indicators
    df = add_features(df)

    # create target
    df["future_price"] = df["Close"].shift(-10)
    df["target"] = (df["future_price"] > df["Close"] * 1.04).astype(int)

    df = df.dropna()

    # -------- BALANCE DATASET --------
    df_majority = df[df.target == 0]
    df_minority = df[df.target == 1]

    df_minority_upsampled = resample(
        df_minority,
        replace=True,
        n_samples=len(df_majority),
        random_state=42
    )

    df = pd.concat([df_majority, df_minority_upsampled])
    # ---------------------------------

    X = df[
        [
            "SMA10",
            "SMA50",
            "RSI",
            "MACD",
            "BB_high",
            "BB_low",
            "returns",
            "volatility",
            "momentum",
            "volatility_20",
            "price_change",
            "ema20",
            "ema50",
            "trend_strength",
            "volume_ratio",
            "price_range"
        ]
    ]

    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    rf = RandomForestClassifier(
        n_estimators=600,
        max_depth=18,
        class_weight="balanced",
        random_state=42
    )

    gb = GradientBoostingClassifier(
        n_estimators=600,
        learning_rate=0.05
    )

    rf.fit(X_train, y_train)
    gb.fit(X_train, y_train)

    rf_pred = rf.predict(X_test)
    gb_pred = gb.predict(X_test)

    rf_acc = accuracy_score(y_test, rf_pred)
    gb_acc = accuracy_score(y_test, gb_pred)

    if gb_acc > rf_acc:
        model = gb
        preds = gb_pred
        acc = gb_acc
    else:
        model = rf
        preds = rf_pred
        acc = rf_acc

    precision = precision_score(y_test, preds)
    recall = recall_score(y_test, preds)
    f1 = f1_score(y_test, preds)

    print(f"\n{stock} Performance")
    print(f"Accuracy  : {acc:.2f}")

    joblib.dump(model, f"models/{stock}.pkl")