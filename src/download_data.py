import yfinance as yf
import pandas as pd

def download_stock():

    data = yf.download(
        "RELIANCE.NS",
        start="2015-01-01",
        end="2024-01-01"
    )

    data.to_csv("data/stock_data.csv")

    print("Data Downloaded")

if __name__=="__main__":
    download_stock()