from pymongo import MongoClient
import bcrypt
import os
import json
from datetime import datetime
from pymongo.errors import ConnectionFailure
from .config import config

# Define absolute path to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCK_USERS_PATH = os.path.join(BASE_DIR, 'mock_users.json')
MOCK_PREDS_PATH = os.path.join(BASE_DIR, 'mock_preds.json')
MOCK_SUBS_PATH = os.path.join(BASE_DIR, 'mock_subscribers.json')

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        if config.MONGO_URI:
            try:
                self.client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
                # Test connection
                self.client.admin.command('ping')
                self.db = self.client[config.DB_NAME]
                print("MongoDB Atlas Connected.")
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
                
    def is_connected(self):
        return self.db is not None

    def _load_local_users(self):
        if not os.path.exists(MOCK_USERS_PATH): return {}
        try:
            with open(MOCK_USERS_PATH, 'r') as f: 
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, ValueError):
            return {}

    def _save_local_users(self, data):
        with open(MOCK_USERS_PATH, 'w') as f: json.dump(data, f)
        
    def _load_local_preds(self):
        if not os.path.exists(MOCK_PREDS_PATH): return []
        try:
            with open(MOCK_PREDS_PATH, 'r') as f: 
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, ValueError):
            return []
        
    def _save_local_preds(self, data):
        # Improved sanitization for all types
        def sanitize(obj):
            if isinstance(obj, dict):
                return {str(k): sanitize(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple, set)):
                return [sanitize(i) for i in obj]
            elif hasattr(obj, 'item') and hasattr(obj, 'dtype'): # Numpy scalars
                return obj.item()
            elif hasattr(obj, 'tolist'): # Numpy arrays
                return obj.tolist()
            elif hasattr(obj, 'isoformat'): # Dates/Times
                return obj.isoformat()
            try:
                # Check if natively serializable
                json.dumps(obj)
                return obj
            except:
                return str(obj)

        try:
            # We want to keep only the latest prediction per ticker to keep file small
            # but for history we might want more. Let's keep last 50 total for now.
            # However, the user wants to see them on dashboard.
            
            clean_data = sanitize(data)
            temp_file = MOCK_PREDS_PATH + '.tmp'
            with open(temp_file, 'w') as f: 
                json.dump(clean_data, f, indent=4)
            
            if os.path.exists(MOCK_PREDS_PATH):
                os.remove(MOCK_PREDS_PATH)
            os.rename(temp_file, MOCK_PREDS_PATH)
        except Exception as e:
            print(f"CRITICAL: Error saving local predictions: {e}")

    def _load_local_subscribers(self):
        if not os.path.exists(MOCK_SUBS_PATH): return []
        try:
            with open(MOCK_SUBS_PATH, 'r') as f: 
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, ValueError):
            return []
        
    def _save_local_subscribers(self, data):
        with open(MOCK_SUBS_PATH, 'w') as f: json.dump(data, f)

    def get_user(self, email):
        if not self.is_connected():
            users = self._load_local_users()
            return users.get(email, None)
        return self.db.users.find_one({"email": email})

    def get_all_users(self):
        if not self.is_connected():
            users = self._load_local_users()
            return list(users.values())
        return list(self.db.users.find({}))

    def create_user(self, name, email, password_hash):
        if not self.is_connected():
            users = self._load_local_users()
            if email in users: return False
            users[str(email)] = {"name": name, "email": email, "password_hash": password_hash}
            self._save_local_users(users)
            return True
            
        if self.get_user(email):
            return False  # User exists
        self.db.users.insert_one({
            "name": name,
            "email": email,
            "password_hash": password_hash
        })
        return True
        
    def save_predictions(self, ticker, date, predicted_signal, metadata):
        """Save historical model predictions per ticker"""
        # Always update local backup for reliability
        preds = self._load_local_preds()
        date_str = date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(date, 'strftime') else str(date)
        
        preds.append({
            "ticker": ticker,
            "date": date_str,
            "signal": predicted_signal,
            "metadata": metadata
        })
        self._save_local_preds(preds)

        # Also save to MongoDB if connected
        if self.is_connected():
            self.db.predictions.insert_one({
                "ticker": ticker,
                "date": date,
                "signal": predicted_signal,
                "metadata": metadata
            })

        
    def get_latest_predictions(self):
        latest_data = {} # ticker -> prediction_dict
        try:
            # 1. Load Local (as base)
            preds = self._load_local_preds()
            for p in preds:
                t = p.get('ticker')
                if t:
                    if t not in latest_data or str(p.get('date', '')) > str(latest_data[t].get('date', '')):
                        latest_data[t] = p

            # 2. Add/Override with Atlas
            if self.is_connected():
                pipeline = [
                    {"$sort": {"date": -1}},
                    {"$group": {"_id": "$ticker", "latest_prediction": {"$first": "$$ROOT"}}}
                ]
                atlas_results = list(self.db.predictions.aggregate(pipeline))
                for res in atlas_results:
                    t = res.get('_id')
                    data = res.get('latest_prediction')
                    if t and data:
                        # Atlas dates might be datetime objects, local are strings. Standardize for comparison.
                        atlas_date = str(data.get('date', ''))
                        if t not in latest_data or atlas_date > str(latest_data[t].get('date', '')):
                            latest_data[t] = data
            
            print(f"DB INFO: Combined {len(latest_data)} latest predictions from local/Atlas.")
        except Exception as e:
            print(f"DB ERROR in get_latest_predictions: {e}")
            
        return [{"_id": t, "latest_prediction": data} for t, data in latest_data.items()]

    def get_last_signal(self, ticker):
        """Retrieve the most recent recorded signal for a specific ticker."""
        if not self.is_connected():
            preds = self._load_local_preds()
            ticker_preds = [p for p in preds if p['ticker'] == ticker]
            if not ticker_preds:
                return None
            # Return signal of the last item (assuming they are appended in order)
            return ticker_preds[-1].get('signal')

        last_pred = self.db.predictions.find_one(
            {"ticker": ticker},
            sort=[("date", -1)]
        )
        return last_pred.get('signal') if last_pred else None

    def add_subscriber(self, email):
        """Add an email address to the subscribers list for alerts."""
        if not self.is_connected():
            subscribers = self._load_local_subscribers()
            if email not in subscribers:
                subscribers.append(email)
                self._save_local_subscribers(subscribers)
            return True
            
        if self.db.subscribers.find_one({"email": email}):
            return False
        self.db.subscribers.insert_one({"email": email, "subscribed_at": datetime.now()})
        return True

    def get_all_subscribers(self):
        """Retrieve all active email subscribers."""
        if not self.is_connected():
            return [{"email": e} for e in self._load_local_subscribers()]
        return list(self.db.subscribers.find({}))

db = Database()
