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

    # Email Alert Configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")

config = Config()
