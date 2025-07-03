from pymongo import MongoClient

mongo = None

def init_db(app):
    global mongo
    mongo_uri = app.config.get('mongo_uri')
    mongo_client = MongoClient(mongo_uri)
    mongo = mongo_client[app.config.get('mongo_db')]
    app.mongo_db = mongo  # Para acceder desde current_app.mongo_db

def get_mongo_db():
    return mongo
