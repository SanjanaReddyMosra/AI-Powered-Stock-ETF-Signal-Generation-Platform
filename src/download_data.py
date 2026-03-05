import yfinance as yf
import os

stocks = [
"RELIANCE.NS",
"TCS.NS",
"INFY.NS",
"HDFCBANK.NS",
"ICICIBANK.NS",
"SBIN.NS",
"ITC.NS",
"LT.NS",
"HINDUNILVR.NS",
"BAJFINANCE.NS"
]

os.makedirs("data",exist_ok=True)

def download():

    for stock in stocks:

        df=yf.download(stock,start="2015-01-01",end="2024-01-01")

        df.to_csv(f"data/{stock}.csv")

        print(stock,"downloaded")

if __name__=="__main__":
    download()