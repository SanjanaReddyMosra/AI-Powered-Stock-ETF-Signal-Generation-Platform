import os
import json
from unittest.mock import MagicMock, patch
from alert_job import run_alert_job
from src.database import db
from src.config import config

def test_signal_change_logic():
    print("Running end-to-end signal change detection test...")
    
    # Setup mock data path
    mock_preds_file = 'mock_preds.json'
    if os.path.exists(mock_preds_file):
        os.remove(mock_preds_file)
        
    # Ensure test runs even if market is closed
    os.environ["BYPASS_MARKET_CHECK"] = "true"
        
    # Mock config
    config.TARGET_TICKERS = ["AAPL"]
    config.SENDER_EMAIL = "test@example.com"
    config.SENDER_PASSWORD = "password"
    
    # Mock database to use local files (is_connected = False)
    db.is_connected = MagicMock(return_value=False)
    
    # Mock users
    with open('mock_users.json', 'w') as f:
        json.dump({"test@example.com": {"name": "Tester", "email": "test@example.com"}}, f)

    with patch('alert_job.generate_signals') as mock_gen, \
         patch('alert_job.send_signal_email') as mock_send:
        
        # Test 1: First signal (BUY) - Should send email
        print("\nTest 1: Initial BUY signal...")
        mock_gen.return_value = {
            'ticker': 'AAPL',
            'signal': 'BUY',
            'latest_price': 150.0,
            'accuracy': 90.0,
            'df_historical': MagicMock(index=[0])
        }
        run_alert_job()
        assert mock_send.call_count == 1
        print("PASS: Email sent for initial BUY.")
        
        # Test 2: Same signal (BUY) - Should NOT send email
        print("\nTest 2: Sequential BUY signal (no change)...")
        mock_send.reset_mock()
        run_alert_job()
        assert mock_send.call_count == 0
        print("PASS: No email sent for duplicate BUY.")
        
        # Test 3: Different signal (SELL) - Should send email
        print("\nTest 3: Signal change to SELL...")
        mock_send.reset_mock()
        mock_gen.return_value['signal'] = 'SELL'
        run_alert_job()
        assert mock_send.call_count == 1
        print("PASS: Email sent for signal change to SELL.")
        
        # Test 4: HOLD signal - Should NOT send email even if changed
        print("\nTest 4: Signal change to HOLD...")
        mock_send.reset_mock()
        mock_gen.return_value['signal'] = 'HOLD'
        run_alert_job()
        assert mock_send.call_count == 0
        print("PASS: No email sent for HOLD signal.")

    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    try:
        test_signal_change_logic()
    finally:
        # Cleanup
        if os.path.exists('mock_preds.json'):
            os.remove('mock_preds.json')
