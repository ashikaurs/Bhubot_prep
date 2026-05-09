from flask import Blueprint, request, jsonify
from database import users_collection
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

auth_bp = Blueprint('auth', __name__)

JWT_SECRET = os.getenv("JWT_SECRET")

def generate_token(user_id, email):
    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.json

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    location = data.get("location", "").strip()
    phone = data.get("phone", "").strip()

    # Validation
    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Check if email already exists
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    )

    # Save user
    user = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "location": location,
        "phone": phone,
        "created_at": datetime.utcnow()
    }

    result = users_collection.insert_one(user)
    token = generate_token(result.inserted_id, email)

    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "name": name,
            "email": email,
            "location": location
        }
    })

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json

    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Find user
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(user["_id"], email)

    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "name": user["name"],
            "email": user["email"],
            "location": user.get("location", "")
        }
    })

@auth_bp.route("/api/profile", methods=["GET"])
def get_profile():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = verify_token(token)

    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401

    user = users_collection.find_one({"email": payload["email"]})
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "name": user["name"],
        "email": user["email"],
        "location": user.get("location", ""),
        "phone": user.get("phone", "")
    })