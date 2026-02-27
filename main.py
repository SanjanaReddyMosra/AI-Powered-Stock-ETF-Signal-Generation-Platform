from src.download_data import download_stock
from src.feature_engineering import create_features
from src.train_model import train

download_stock()

create_features()

train()