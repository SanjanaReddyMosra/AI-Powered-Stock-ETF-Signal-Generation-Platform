AI-Powered Stock & ETF Signal Generation Platform

An AI-driven platform that generates Buy/Sell signals for stocks using machine learning and technical indicators. The system analyzes historical market data, extracts technical features, trains predictive models, and provides signals through an interactive Streamlit dashboard.

Features

Fetch historical stock data using Yahoo Finance API

Feature engineering using technical indicators (RSI, MACD, Moving Averages, Bollinger Bands, Volatility)

Train separate machine learning models for multiple stocks

Model comparison using Random Forest and Gradient Boosting

Performance evaluation using Accuracy, Precision, Recall, and F1 Score

Save trained models for signal generation

Interactive Streamlit dashboard for visualization

Automated Buy/Sell signal generation

Tech Stack

Python
Pandas
NumPy
Scikit-learn
TA (Technical Analysis Library)
yfinance
Streamlit
Joblib

Project Structure

AI-Powered-Stock-ETF-Signal-Generation-Platform

data/ – Historical stock datasets
models/ – Trained ML models

src/
download_data.py
feature_engineering.py
train_model.py
train_all_models.py
signal_generator.py

dashboard/
app.py – Streamlit dashboard

requirements.txt
README.md

Installation

Clone the repository

git clone https://github.com/SanjanaReddyMosra/AI-Powered-Stock-ETF-Signal-Generation-Platform.git

cd AI-Powered-Stock-ETF-Signal-Generation-Platform

Create a virtual environment

python -m venv venv
venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

Usage

Download stock data

python src/download_data.py

Train machine learning models

python -m src.train_all_models

Run the dashboard

streamlit run dashboard/app.py

Example Output

The system generates signals such as:

BUY → when the model predicts a strong upward trend
SELL → when no upward trend is predicted

The dashboard visualizes stock prices along with predicted signals.

Future Improvements

Deep Learning models (LSTM / Transformers)
Real-time signal alerts
Backtesting engine
Portfolio optimization
Cloud deployment

Author

Sanjana Reddy
