from bson.objectid import ObjectId
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

def find_user_by_email(email):
    return current_app.mongo_db.users.find_one({'email': email})

def get_user_by_id(user_id):
    return current_app.mongo_db.users.find_one({'_id': ObjectId(user_id)})

def create_user(username, email, password):
    hashed_pw = generate_password_hash(password)
    user_data = {
        "username": username,
        "email": email,
        "password": hashed_pw,
        "photo": None
    }
    return current_app.mongo_db.users.insert_one(user_data)

def update_user(user_id, updates: dict):
    return current_app.mongo_db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': updates}
    )

def verify_password(user, password):
    return check_password_hash(user['password'], password)
