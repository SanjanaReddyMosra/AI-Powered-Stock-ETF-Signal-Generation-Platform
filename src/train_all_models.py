from src.train_model import train
import os

os.makedirs("models", exist_ok=True)

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

print("Starting training for all stocks...\n")

for stock in stocks:
    print(f"Training model for {stock}...")
    train(stock)

print("\nAll models trained successfully.")