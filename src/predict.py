import joblib
import pandas as pd


def predict():

    xgb,rf,lgb,scaler=joblib.load(
        "models/saved_model.pkl"
    )

    df=pd.read_csv("data/features.csv")

    X=df.drop(['Target'],axis=1)

    X=X.select_dtypes(include=['float64','int64'])

    X=scaler.transform(X)

    p1=xgb.predict(X)
    p2=rf.predict(X)
    p3=lgb.predict(X)

    final=(p1+p2+p3)/3

    print(final[-10:])


if __name__=="__main__":
    predict()