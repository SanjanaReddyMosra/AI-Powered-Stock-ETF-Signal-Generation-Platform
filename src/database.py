from pymongo import MongoClient
import bcrypt
import os
import json
from pymongo.errors import ConnectionFailure
from .config import config

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
        if not os.path.exists('mock_users.json'): return {}
        with open('mock_users.json', 'r') as f: return json.load(f)

    def _save_local_users(self, data):
        with open('mock_users.json', 'w') as f: json.dump(data, f)
        
    def _load_local_preds(self):
        if not os.path.exists('mock_preds.json'): return []
        with open('mock_preds.json', 'r') as f: return json.load(f)
        
    def _save_local_preds(self, data):
        with open('mock_preds.json', 'w') as f: json.dump(data, f)

    def get_user(self, email):
        if not self.is_connected():
            users = self._load_local_users()
            return users.get(email, None)
        return self.db.users.find_one({"email": email})

    def create_user(self, name, email, password_hash):
        if not self.is_connected():
            users = self._load_local_users()
            if email in users: return False
            users[email] = {"name": name, "email": email, "password_hash": password_hash}
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
        if not self.is_connected():
            preds = self._load_local_preds()
            preds.append({
                "ticker": ticker,
                "date": str(date),
                "signal": predicted_signal,
                "metadata": metadata
            })
            self._save_local_preds(preds)
            return

        self.db.predictions.insert_one({
            "ticker": ticker,
            "date": date,
            "signal": predicted_signal,
            "metadata": metadata
        })

        
    def get_latest_predictions(self):
        if not self.is_connected():
            return []
        # Return recent signals grouped by ticker
        pipeline = [
            {"$sort": {"date": -1}},
            {"$group": {
                "_id": "$ticker",
                "latest_prediction": {"$first": "$$ROOT"}
            }}
        ]
        return list(self.db.predictions.aggregate(pipeline))

db = Database()
