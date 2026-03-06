import streamlit as st
import pandas as pd
import yfinance as yf
import joblib
import matplotlib.pyplot as plt
import requests
import sys
import os

# Allow Python to find src folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.feature_engineering import add_features

BACKEND_URL = "http://127.0.0.1:8000"

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="AI Stock Signal Platform", layout="wide")

# ----------------------------
# Session State
# ----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "email" not in st.session_state:
    st.session_state.email = None

# ----------------------------
# Sidebar menu
# ----------------------------
menu = st.sidebar.selectbox(
    "Menu",
    ["Login", "Register", "Dashboard"]
)

# ----------------------------
# REGISTER PAGE
# ----------------------------
if menu == "Register":

    st.title("📝 Register")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):

        res = requests.post(
            f"{BACKEND_URL}/register",
            json={
                "email": email,
                "password": password
            }
        )

        st.success(res.json()["message"])

# ----------------------------
# LOGIN PAGE
# ----------------------------
elif menu == "Login":

    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        res = requests.post(
            f"{BACKEND_URL}/login",
            json={
                "email": email,
                "password": password
            }
        )

        result = res.json()

        if "message" in result:

            st.session_state.logged_in = True
            st.session_state.email = email

            st.success("Login successful")

        else:
            st.error(result["error"])

# ----------------------------
# DASHBOARD
# ----------------------------
elif menu == "Dashboard":

    if not st.session_state.logged_in:
        st.warning("Please login first.")
        st.stop()

    st.title("📈 AI-Powered Stock Signal Dashboard")

    # ----------------------------
    # Sidebar
    # ----------------------------
    stocks = [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "SBIN.NS",
        "ITC.NS",
        "LT.NS",
        "BAJFINANCE.NS",
        "HINDUNILVR.NS"
    ]

    stock = st.sidebar.selectbox("Select Stock", stocks)

    period = st.sidebar.selectbox(
        "Select Time Period",
        ["3mo", "6mo", "1y", "2y"]
    )

    # ----------------------------
    # Add to watchlist
    # ----------------------------
    if st.sidebar.button("Add to Watchlist"):

        requests.post(
            f"{BACKEND_URL}/add_watchlist",
            json={
                "email": st.session_state.email,
                "stock": stock
            }
        )

        st.sidebar.success("Added to watchlist")

    # ----------------------------
    # Load model
    # ----------------------------
    model_path = f"models/{stock}.pkl"

    try:
        model = joblib.load(model_path)
    except:
        st.error("Model not found")
        st.stop()

    # ----------------------------
    # Download data
    # ----------------------------
    data = yf.download(stock, period=period)

    if data.empty:
        st.error("No market data available")
        st.stop()

    # ----------------------------
    # Feature engineering
    # ----------------------------
    data = add_features(data)

    feature_cols = [
        "SMA10","SMA50","RSI","MACD",
        "BB_high","BB_low",
        "returns","volatility","momentum",
        "volatility_20","price_change",
        "ema20","ema50","trend_strength",
        "volume_ratio","price_range"
    ]

    X = data[feature_cols]

    latest_data = X.tail(1)

    pred = model.predict(latest_data)
    prob = model.predict_proba(latest_data)

    buy_prob = prob[-1][1]
    sell_prob = prob[-1][0]

    confidence = max(buy_prob, sell_prob)

    # ----------------------------
    # HOLD logic
    # ----------------------------
    if buy_prob > 0.60:
        signal = "BUY"
    elif sell_prob > 0.60:
        signal = "SELL"
    else:
        signal = "HOLD"

    # ----------------------------
    # Metrics
    # ----------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Latest Price", round(data["Close"].iloc[-1], 2))

    with col2:
        if signal == "BUY":
            st.success("🟢 BUY SIGNAL")
        elif signal == "SELL":
            st.error("🔴 SELL SIGNAL")
        else:
            st.warning("🟡 HOLD")

    with col3:
        st.metric("Confidence", f"{confidence*100:.2f}%")

    # ----------------------------
    # Chart
    # ----------------------------
    st.subheader("Stock Price Chart")

    fig, ax = plt.subplots()

    ax.plot(data["Close"], label="Close Price")
    ax.plot(data["SMA10"], label="SMA10")
    ax.plot(data["SMA50"], label="SMA50")

    ax.set_xlabel("Date")
    ax.set_ylabel("Price")

    ax.legend()

    st.pyplot(fig)

    # ----------------------------
    # Probability
    # ----------------------------
    st.subheader("Prediction Probability")

    st.write(f"🟢 Buy Probability: {buy_prob*100:.2f}%")
    st.write(f"🔴 Sell Probability: {sell_prob*100:.2f}%")

    # ----------------------------
    # Latest market data
    # ----------------------------
    st.subheader("Latest Market Data")

    st.dataframe(data.tail())