from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from SanFranciscanos.db import get_mongo_db  # ← CORRECTO

def find_user_by_email(email):
    db = get_mongo_db()
    return db["users"].find_one({'email': email})

def get_user_by_id(user_id):
    db = get_mongo_db()
    return db["users"].find_one({'_id': ObjectId(user_id)})

def create_user(username, email, password):
    db = get_mongo_db()
    hashed_pw = generate_password_hash(password)
    user_data = {
        "username": username,
        "email": email,
        "password": hashed_pw,
        "photo": None
    }
    return db["users"].insert_one(user_data)

def update_user(user_id, updates: dict):
    db = get_mongo_db()
    return db["users"].update_one(
        {'_id': ObjectId(user_id)},
        {'$set': updates}
    )

def verify_password(user, password):
    return check_password_hash(user['password'], password)
