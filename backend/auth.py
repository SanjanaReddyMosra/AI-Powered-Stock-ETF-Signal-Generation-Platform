from backend.database import users
from backend.models import User, Login
from passlib.hash import bcrypt


def register_user(data):

    email = data.email
    password = bcrypt.hash(data.password)

    existing = users.find_one({"email": email})

    if existing:
        return {"error": "User already exists"}

    user = {
        "email": email,
        "password": password,
        "watchlist": [],
        "alerts_enabled": True
    }

    users.insert_one(user)

    return {"message": "Registration successful"}


def login_user(data):

    user = users.find_one({"email": data.email})

    if not user:
        return {"error": "User not found"}

    if bcrypt.verify(data.password, user["password"]):
        return {"message": "Login successful"}

    return {"error": "Invalid password"}