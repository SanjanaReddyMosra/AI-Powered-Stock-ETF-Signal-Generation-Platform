import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "")
    DB_NAME = "stock_signal_db"

    # Define the 10 target stocks/ETFs
    TARGET_TICKERS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
        "NVDA", "META", "SPY", "QQQ", "JPM"
    ]
    
    # ML Parameters
    LOOKBACK_PERIOD_YEARS = 2
    TRAIN_TEST_SPLIT = 0.8
    TARGET_ACCURACY_THRESHOLD = 0.85

config = Config()
