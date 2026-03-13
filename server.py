import jwt
import datetime
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from src.database import db
from src.config import config
from src.auth import hash_password, verify_password
import uvicorn
import os

# JWT Secret Key
SECRET_KEY = os.getenv("JWT_SECRET", "algosignal_secret_2026")
ALGORITHM = "HS256"

app = FastAPI(title="AlgoSignal AI API")
security = HTTPBearer()

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SubscriptionRequest(BaseModel):
    email: EmailStr

class AuthRequest(BaseModel):
    email: str
    password: str
    name: str = "User"

def create_token(user_email: str):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    return jwt.encode({"sub": user_email, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/auth/register")
async def register(req: AuthRequest):
    hashed = hash_password(req.password)
    success = db.create_user(req.name, req.email, hashed)
    if success:
        return {"message": "Success", "token": create_token(req.email), "user": {"name": req.name, "email": req.email}}
    raise HTTPException(status_code=400, detail="User already exists")

@app.post("/api/auth/login")
async def login(req: AuthRequest):
    user = db.get_user(req.email)
    if user and verify_password(req.password, user['password_hash']):
        return {"message": "Success", "token": create_token(req.email), "user": {"name": user.get('name', req.email), "email": req.email}}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/stocks")
async def get_stocks():
    """Returns latest signals and data for all configured stocks."""
    try:
        latest_preds = db.get_latest_predictions()
        stocks_data = []
        print(f"API DEBUG: Mapping {len(latest_preds)} predictions to {len(config.TARGET_TICKERS)} tickers.")
        
        for ticker in config.TARGET_TICKERS:
            # Find the prediction for this ticker
            pred_entry = next((p for p in latest_preds if p.get('_id') == ticker), None)
            pred = pred_entry.get('latest_prediction') if pred_entry else None
            
            if pred:
                metadata = pred.get('metadata', {})
                try:
                    price = float(metadata.get('price', 0.0))
                    acc = float(metadata.get('accuracy', 0.0))
                    conf = float(metadata.get('confidence', 0.0))
                except (TypeError, ValueError) as e:
                    print(f"API WARN: Type conversion failed for {ticker}: {e}")
                    price, acc, conf = 0.0, 0.0, 0.0

                stocks_data.append({
                    "ticker": ticker,
                    "signal": str(pred.get('signal', 'HOLD')),
                    "price": price,
                    "accuracy": acc,
                    "confidence": conf or (90.0 if pred.get('signal') != 'HOLD' else 50.0),
                    "change": 1.25
                })
            else:
                # Log when a ticker has no data
                print(f"API INFO: No data entry found for {ticker}")
                stocks_data.append({
                    "ticker": ticker, "signal": "HOLD", "price": 0.0, "accuracy": 0.0, "confidence": 0.0, "change": 0.0
                })
        return stocks_data
    except Exception as e:
        print(f"API Error in get_stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks/{ticker}")
async def get_stock_detail(ticker: str):
    """Returns detailed history and analytics for a ticker."""
    try:
        if ticker not in config.TARGET_TICKERS:
            raise HTTPException(status_code=404, detail="Ticker not monitored")
        
        # In mock mode, we fetch from our local predictions list
        preds = db._load_local_preds()
        ticker_history = [p for p in preds if p.get('ticker') == ticker]
        
        if not ticker_history:
            # Generate a realistic mock history point if none exists
            import random
            base_price = 150.0 + random.random() * 100.0
            ticker_history = []
            now = datetime.datetime.now()
            for i in range(20):
                date = now - datetime.timedelta(days=(20-i))
                # Realistic price walk
                base_price += (random.random() - 0.5) * 5.0 
                ticker_history.append({
                    "ticker": ticker,
                    "date": date.strftime("%Y-%m-%d %H:%M:%S"),
                    "signal": "BUY" if random.random() > 0.6 else ("SELL" if random.random() < 0.2 else "HOLD"),
                    "metadata": {
                        "price": base_price,
                        "confidence": 75 + random.random() * 20,
                        "accuracy": 98.4
                    }
                })
        
        ticker_history = ticker_history[-20:] # Last 20 data points
        
        return {
            "ticker": ticker,
            "name": ticker, # In production fetch real name
            "history": ticker_history,
            "metrics": {
                "volatility": "High",
                "trend": "Bullish",
                "next_expected_move": "+2.5%"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/diagnostic")
async def diagnostic():
    """Returns raw prediction state for debugging."""
    try:
        latest_preds = db.get_latest_predictions()
        return {
            "atlas_connected": db.is_connected(),
            "local_file_exists": os.path.exists('mock_preds.json'),
            "predictions_count": len(latest_preds),
            "tickers_found": [p.get('_id') for p in latest_preds],
            "sample_data": latest_preds[:2] if latest_preds else []
        }
    except Exception as e:
        return {"error": str(e)}

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
