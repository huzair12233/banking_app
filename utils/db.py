import os
from pymongo import MongoClient

client = MongoClient(os.environ.get('MONGO_URI'))
db = client.get_database()  # Uses the database in the URI

def get_collection(name):
    return db[name]
