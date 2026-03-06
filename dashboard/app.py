import streamlit as st
import pandas as pd
import yfinance as yf
import joblib
import matplotlib.pyplot as plt
import sys
import os

# Allow Python to find src folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.feature_engineering import add_features

# ----------------------------
# Page configuration
# ----------------------------
st.set_page_config(page_title="AI Stock Signal Dashboard", layout="wide")

st.title("📈 AI-Powered Stock & ETF Signal Generation")

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
# Load Model
# ----------------------------
model_path = f"models/{stock}.pkl"

try:
    model = joblib.load(model_path)
except:
    st.error(f"Model not found for {stock}")
    st.stop()

# ----------------------------
# Download Data
# ----------------------------
data = yf.download(stock, period=period)

if data.empty:
    st.error("No market data available.")
    st.stop()

# ----------------------------
# Feature Engineering
# ----------------------------
data = add_features(data)

# Feature columns used in training
feature_cols = [
    "SMA10","SMA50","RSI","MACD",
    "BB_high","BB_low",
    "returns","volatility","momentum",
    "volatility_20","price_change",
    "ema20","ema50","trend_strength",
    "volume_ratio","price_range"
]

X = data[feature_cols]

# ----------------------------
# Prediction
# ----------------------------
pred = model.predict(X)
prob = model.predict_proba(X)

buy_prob = prob[-1][1]
sell_prob = prob[-1][0]

confidence = max(buy_prob, sell_prob)

# HOLD logic
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
# Stock Chart
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
# Prediction Probability
# ----------------------------
st.subheader("Prediction Probability")

st.write(f"🟢 Buy Probability: {buy_prob*100:.2f}%")
st.write(f"🔴 Sell Probability: {sell_prob*100:.2f}%")

# ----------------------------
# Latest Market Data
# ----------------------------
st.subheader("Latest Market Data")

st.dataframe(data.tail())