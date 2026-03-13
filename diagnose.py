import os
import json
import sys

# Add current dir to path to import src
sys.path.append(os.getcwd())

try:
    from src.database import db
    from src.config import config
    
    print("--- DIAGNOSTIC START ---")
    print(f"Current Directory: {os.getcwd()}")
    print(f"MongoDB Connected: {db.is_connected()}")
    
    # Check local file existence
    if os.path.exists('mock_preds.json'):
        print(f"mock_preds.json exists. Size: {os.path.getsize('mock_preds.json')} bytes")
        with open('mock_preds.json', 'r') as f:
            data = json.load(f)
            print(f"Total entries in file: {len(data)}")
            if len(data) > 0:
                print(f"Sample Entry: {data[0]}")
    else:
        print("mock_preds.json MISSING from current directory!")

    # Test retrieval
    latest_preds = db.get_latest_predictions()
    print(f"Retrieved {len(latest_preds)} aggregated latest predictions.")
    for p in latest_preds:
        print(f"Ticker: {p['_id']}, Signal: {p['latest_prediction'].get('signal')}, Price: {p['latest_prediction'].get('metadata', {}).get('price')}")
    
    # Check Tickers in Config
    print(f"Target Tickers in Config: {config.TARGET_TICKERS}")
    
    print("--- DIAGNOSTIC END ---")

except Exception as e:
    print(f"DIAGNOSTIC CRASHED: {e}")
    import traceback
    traceback.print_exc()
