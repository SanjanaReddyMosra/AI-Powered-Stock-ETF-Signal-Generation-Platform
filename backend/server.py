from fastapi import FastAPI

from backend.models import User, Login, Watchlist
from backend.auth import register_user, login_user
from backend.database import users
from backend.scheduler import start_scheduler

app = FastAPI()

# Start background alert scheduler
start_scheduler()


@app.get("/")
def home():
    return {"message": "AI Stock Backend Running"}


@app.post("/register")
def register(user: User):
    return register_user(user)


@app.post("/login")
def login(user: Login):
    return login_user(user)


@app.post("/add_watchlist")
def add_watchlist(data: Watchlist):

    users.update_one(
        {"email": data.email},
        {"$push": {"watchlist": data.stock}}
    )

    return {"message": "Stock added to watchlist"}


@app.get("/watchlist/{email}")
def get_watchlist(email: str):

    user = users.find_one({"email": email})

    if not user:
        return {"error": "User not found"}

    return {"watchlist": user["watchlist"]}