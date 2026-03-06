from pymongo import MongoClient

# MongoDB Atlas connection string
MONGO_URL = "mongodb+srv://23r01a66a4_admin:Sanju%2A28@cluster0.bffmp2a.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO_URL)

# Database
db = client["stock_ai"]

# Collections
users = db["users"]
alerts = db["alerts"]

print("MongoDB Connected Successfully")