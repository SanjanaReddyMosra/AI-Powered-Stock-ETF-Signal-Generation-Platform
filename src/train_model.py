import pandas as pd
import joblib

from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from sklearn.metrics import accuracy_score


def train():

    df = pd.read_csv(
        "data/features.csv"
    )

    # ---------- Features ----------

    X = df.drop(
        ['Target'],
        axis=1
    )

    X = X.select_dtypes(
        include=['float64','int64']
    )

    y = df['Target']

    X = X.values

    # ---------- Time Series Split ----------

    tscv = TimeSeriesSplit(
        n_splits=5
    )

    for train_i,test_i in tscv.split(X):

        X_train,X_test = X[
            train_i
        ],X[test_i]

        y_train,y_test = y.iloc[
            train_i
        ],y.iloc[test_i]

    # ---------- Models ----------

    xgb = XGBClassifier(

        n_estimators=900,
        max_depth=7,
        learning_rate=0.05,
        objective='binary:logistic',
        eval_metric='logloss'

    )

    rf = RandomForestClassifier(

        n_estimators=900,
        random_state=42

    )

    lgb = LGBMClassifier(

        n_estimators=900

    )

    # ---------- Training ----------

    xgb.fit(X_train,y_train)
    rf.fit(X_train,y_train)
    lgb.fit(X_train,y_train)

    # ---------- Probability Predictions ----------

    p1 = xgb.predict_proba(X_test)[:,1]
    p2 = rf.predict_proba(X_test)[:,1]
    p3 = lgb.predict_proba(X_test)[:,1]

    avg_prob = (p1 + p2 + p3) / 3

    threshold = 0.95

    final_pred = []
    filtered_y_test = []

    for i in range(len(avg_prob)):

    # Trend confirmation ⭐⭐⭐⭐⭐

        trend_up = X_test[i][ X.shape[1]-1 ] == 1

        if avg_prob[i] > threshold and trend_up:

            final_pred.append(1)
            filtered_y_test.append(y_test.iloc[i])

        elif avg_prob[i] < (1 - threshold) and not trend_up:

            final_pred.append(0)
            filtered_y_test.append(y_test.iloc[i])

    # ---------- Accuracy ----------

    acc = accuracy_score(
        filtered_y_test,
        final_pred
    )

    print(
        "Filtered Accuracy:",
        acc*100,"%"
    )

    print(
        "Trades Taken:",
        len(final_pred)
    )

    # ---------- Save ----------

    joblib.dump(

        (xgb,rf,lgb),

        "models/saved_model.pkl"

    )

    print(
        "Model Saved Successfully"
    )


if __name__ == "__main__":

    train()