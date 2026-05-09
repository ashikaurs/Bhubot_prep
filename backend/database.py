from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["bhubot"]
    return db

db = get_db()

users_collection = db["users"]
soil_records_collection = db["soil_records"]

print("✅ MongoDB connected successfully!")