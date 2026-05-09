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
feedbacks_collection = db["feedbacks"]
farmer_outcomes_collection = db["farmer_outcomes"]

print("✅ MongoDB connected successfully!")


farmer_outcomes_collection.create_index([
    ("crop", 1),
    ("season", 1),
    ("nitrogen", 1),
    ("phosphorus", 1),
    ("potassium", 1),
    ("ph_range", 1),
    ("location_region", 1)
], unique=True)