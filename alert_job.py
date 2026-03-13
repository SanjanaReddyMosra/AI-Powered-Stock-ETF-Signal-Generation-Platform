import os
import time
import pytz
from datetime import datetime
from src.config import config
from src.ml_engine import generate_signals
from src.database import db
from src.notifier import send_signal_email

def is_trading_hours():
    """Checks if the current time is within US trading hours (9:30 AM - 4:00 PM ET, Mon-Fri)."""
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    
    # Check if it's a weekday (0=Monday, 4=Friday)
    if now.weekday() > 4:
        return False
        
    # Check time range
    start_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    end_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return start_time <= now <= end_time

def run_alert_job():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting AI Stock Alert Job...")
    
    # Check if it's trading hours (Optional: can be bypassed for testing)
    if not is_trading_hours() and os.getenv("BYPASS_MARKET_CHECK") != "true":
        print("Market is currently closed. Skipping alert cycle.")
        return

    # Check if we should even proceed with emails
    if not config.SENDER_EMAIL or not config.SENDER_PASSWORD:
        print("WARNING: SENDER_EMAIL or SENDER_PASSWORD not set in environment.")
        print("Emails will not be sent.")
        
    users = db.get_all_users()
    if not users:
        print("No users found in database.")
        return

    print(f"Found {len(users)} registered user(s). Processing {len(config.TARGET_TICKERS)} tickers...")

    for ticker in config.TARGET_TICKERS:
        try:
            # Get previous signal to detect changes
            previous_signal = db.get_last_signal(ticker)
            
            result = generate_signals(ticker)
            if not result:
                print(f"  [{ticker}] Failed to generate signal.")
                continue
                
            current_signal = result['signal']
            
            # Always save to local/db as preferred
            db.save_predictions(
                result['ticker'], 
                result['df_historical'].index[-1], 
                current_signal, 
                {
                    "accuracy": result['accuracy'],
                    "price": result['latest_price'],
                    "confidence": result['confidence']
                }
            )

            # Detect change and only alert on BUY/SELL
            if current_signal in ["BUY", "SELL"]:
                if current_signal != previous_signal:
                    print(f"  [{ticker}] {current_signal} signal CHANGE detected! Notifying users...")
                    
                    price = result['latest_price']
                    accuracy = result['accuracy']

                    # Notify registered users
                    for user in users:
                        email = user.get('email')
                        name = user.get('name', 'User')
                        if email:
                            send_signal_email(email, name, ticker, current_signal, price, accuracy)
                    
                    # Notify alert-only subscribers
                    subscribers = db.get_all_subscribers()
                    for sub in subscribers:
                        email = sub.get('email')
                        if email:
                            # Avoid double sending if they are also a registered user (simplified check)
                            if not any(u.get('email') == email for u in users):
                                send_signal_email(email, "Subscriber", ticker, current_signal, price, accuracy)
                else:
                    print(f"  [{ticker}] {current_signal} signal maintained. No alert.")
            else:
                print(f"  [{ticker}] {current_signal} signal (no alert).")
                
        except Exception as e:
            print(f"  [{ticker}] Error: {e}")

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Alert Job Cycle Completed.")

if __name__ == "__main__":
    # Check for continuous run flag
    if os.getenv("RUN_CONTINUOUS") == "true":
        interval = int(os.getenv("ALERT_INTERVAL_SECONDS", 900)) # Default 15 mins
        print(f"Starting Alert Job in continuous mode (Interval: {interval}s)...")
        while True:
            run_alert_job()
            print(f"Waiting {interval}s for next cycle...")
            time.sleep(interval)
    else:
        run_alert_job()
