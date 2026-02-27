from sklearn.metrics import classification_report
import joblib
import pandas as pd

def evaluate():

    model=joblib.load(
        "models/saved_model.pkl"
    )

    print("Loaded Successfully")

if __name__=="__main__":
    evaluate()