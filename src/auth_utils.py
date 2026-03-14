import bcrypt
import re
from .database import db

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def is_password_strong(password):
    if len(password) < 6: return False, "Password must be at least 6 characters."
    if not re.search(r'[A-Z]', password): return False, "Password must contain at least 1 uppercase letter."
    if not re.search(r'[a-z]', password): return False, "Password must contain at least 1 lowercase letter."
    if not re.search(r'\d', password): return False, "Password must contain at least 1 number."
    if not re.search(r'[!@#\$%\^&\*\(\)_\+\-=\[\]\{\};:\'",<>\./\?\\|]', password): return False, "Password must contain at least 1 symbol."
    return True, ""

def core_register_user(name, email, password):
    email = email.lower()
    is_valid, msg = is_password_strong(password)
    if not is_valid:
        return False, msg
    
    hashed = hash_password(password)
    success = db.create_user(name, email, hashed)
    if success:
        return True, "User registered successfully"
    return False, "Email already exists or database is unavailable"

def core_login_user(email, password):
    email = email.lower()
    user = db.get_user(email)
    if user and verify_password(password, user['password_hash']):
        return True, user
    return False, None
