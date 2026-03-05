import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import yfinance as yf

from src.signal_generator import signal

stocks=[
"RELIANCE.NS",
"TCS.NS",
"INFY.NS",
"HDFCBANK.NS",
"ICICIBANK.NS"
]

st.title("AI Stock Signal Platform")

stock=st.selectbox("Select Stock",stocks)

df=yf.download(stock,start="2022-01-01")

st.line_chart(df["Close"])

s=signal(stock)

st.subheader("Trading Signal")

st.write(s)