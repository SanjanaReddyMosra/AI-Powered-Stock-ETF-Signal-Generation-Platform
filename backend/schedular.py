from apscheduler.schedulers.background import BackgroundScheduler
from database import users
from alerts import send_email

import joblib
import pandas as pd
import yfinance as yf

from src.feature_engineering import add_features


def generate_signal(stock):

    model = joblib.load(f"models/{stock}.pkl")

    data = yf.download(stock, period="6mo")

    data = add_features(data)

    features = [
        "SMA10","SMA50","RSI","MACD",
        "BB_high","BB_low","returns",
        "volatility","momentum",
        "volatility_20","price_change",
        "ema20","ema50","trend_strength",
        "volume_ratio","price_range"
    ]

    latest = data[features].iloc[-1]

    prediction = model.predict([latest])[0]

    if prediction == 1:
        return "BUY"
    else:
        return "HOLD"


def check_alerts():

    for user in users.find():

        if not user["alerts_enabled"]:
            continue

        email = user["email"]

        for stock in user["watchlist"]:

            signal = generate_signal(stock)

            if signal == "BUY":

                send_email(email, stock, signal)


def start_scheduler():

    scheduler = BackgroundScheduler()

    scheduler.add_job(check_alerts, "interval", minutes=10)

    scheduler.start()