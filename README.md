# AlgoSignal AI: Professional Trading Intelligence Platform

![AlgoSignal AI](https://raw.githubusercontent.com/SanjanaReddyMosra/AI-Powered-Stock-ETF-Signal-Generation-Platform/main/static/logo.png)

AlgoSignal AI is a high-performance, AI-driven stock and ETF signal generation platform. It leverages XGBoost machine learning models to provide real-time BUY/SELL/HOLD recommendations with integrated confidence metrics and price tracking.

## 🚀 Features

- **AI-Powered Signals**: Live signals for 10 top stocks/ETFs (AAPL, MSFT, NVDA, etc.).
- **Professional Dashboard**: Modern "Fire & Glass" UI with interactive stock cards.
- **Deep Analytics**: Historical price trends and AI confidence mapping using Chart.js.
- **Secure Authentication**: JWT-based user system for personalized experiences.
- **Market Intelligence**: Sortable tabular view for cross-asset comparison.
- **Backtesting & Analytics**: Automated reporting of Sharpe Ratio, Max Drawdown, and Win Rates with Equity Curve visualizations.
- **Interactive Dashboards**: Dual-layered visualization using both Streamlit (Advanced Analytics) and FastAPI/Vanilla JS (Real-time Monitoring).
- **Threshold Alerting**: Smart price-movement detection (>3%) integrated with the email alert engine.

## 🛠️ Tech Stack

- **Frontend**: HTML5, Vanilla CSS (Premium Fire Theme), Chart.js
- **Backend**: FastAPI (Python), Uvicorn
- **Database**: MongoDB Atlas (with local JSON fallback)
- **Machine Learning**: XGBoost, Scikit-learn, Pandas
- **APIs**: Yahoo Finance (yfinance)

## 📦 Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/SanjanaReddyMosra/AI-Powered-Stock-ETF-Signal-Generation-Platform.git
   cd AI-Powered-Stock-ETF-Signal-Generation-Platform
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   MONGO_URI=your_mongodb_uri
   JWT_SECRET=your_jwt_secret
   SENDER_EMAIL=your_email
   SENDER_PASSWORD=your_password
   ```

4. **Run the Platform**:
   - **Start the AI Engine**:
     ```bash
     $env:RUN_CONTINUOUS="true"; python alert_job.py
     ```
   - **Start the API Server**:
     ```bash
     python server.py
     ```

## 🌐 Deployment

This platform is ready for deployment on **Render**, **Railway**, or **Heroku**.

- **Procfile**: Included for automatic process detection.
- **Dynamic Port**: Configured to use the environment's `PORT` variable.
- **Static Assets**: Automatically served by FastAPI.

---
Developed with ❤️ for Advanced Trading Intelligence.
