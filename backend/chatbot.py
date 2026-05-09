from flask import Blueprint, request, jsonify
from database import soil_records_collection, users_collection
from auth import verify_token
from groq import Groq
from dotenv import load_dotenv
from bson import ObjectId
import os

load_dotenv()

chatbot_bp = Blueprint('chatbot', __name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@chatbot_bp.route("/api/chatbot", methods=["POST"])
def chatbot():
    data = request.json
    user_message = data.get("message", "")
    chat_history = data.get("history", [])
    language = data.get("language", "English")

    # Get user from token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = verify_token(token)

    context_str = ""

    if payload:
        # Logged in user — fetch their latest soil record from MongoDB
        user_email = payload["email"]
        user = users_collection.find_one({"email": user_email})

        if user:
            # Get their most recent soil record
            latest_record = soil_records_collection.find_one(
                {"user_id": str(user["_id"])},
                sort=[("timestamp", -1)]
            )

            if latest_record:
                soil = latest_record.get("soil_params", {})
                context_str = f"""
Farmer Profile:
- Name: {user.get('name', 'Farmer')}
- Location: {user.get('location', 'India')}

Latest Soil Data:
- Crop: {latest_record.get('crop', 'Not specified')}
- Season: {latest_record.get('season', 'Not specified')}
- Land Size: {latest_record.get('land_size', 'Not specified')}
- Budget: {latest_record.get('budget', 'Not specified')}
- pH: {soil.get('ph', 'Not specified')}
- Nitrogen: {soil.get('nitrogen', 'Not specified')}
- Phosphorus: {soil.get('phosphorus', 'Not specified')}
- Potassium: {soil.get('potassium', 'Not specified')}
- Organic Carbon: {soil.get('organic_carbon', 'Not specified')}%
- Zinc: {soil.get('zinc', 'Not specified')}
- Boron: {soil.get('boron', 'Not specified')}
- EC: {soil.get('ec', 'Not specified')} dS/m
- Last updated: {latest_record.get('timestamp', 'Not specified')}
"""
            else:
                # User logged in but no soil records yet
                context_str = f"""
Farmer Profile:
- Name: {user.get('name', 'Farmer')}
- Location: {user.get('location', 'India')}
- Note: No soil records found yet for this farmer.
"""

    # Build system prompt
    system_prompt = f"""You are BhuBot, a friendly expert agricultural advisor for Indian farmers.
You have deep knowledge of Indian farming conditions, locally available fertilizers, and affordable solutions.

{"Use this farmer's actual data to give personalized advice:" + context_str if context_str else "No farmer profile available. Give general Indian farming advice."}

Rules:
- Respond ONLY in {language}
- Keep answers concise — 3 to 5 sentences maximum
- Always suggest locally available Indian products
- Be friendly and use simple language
- If farmer asks about their soil — refer to their actual data above
- Never make up data that isn't in the context
- If no soil data available, ask them to fill the form first"""

    # Build message history
    messages = [{"role": "system", "content": system_prompt}]

    # Add last 6 messages for context
    for msg in chat_history[-6:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add current message
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=400
    )

    reply = response.choices[0].message.content

    return jsonify({"reply": reply})


@chatbot_bp.route("/api/save-record", methods=["POST"])
def save_record():
    # Save soil record to MongoDB after advice is generated
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = verify_token(token)

    if not payload:
        return jsonify({"error": "Please login to save records"}), 401

    data = request.json
    user = users_collection.find_one({"email": payload["email"]})

    if not user:
        return jsonify({"error": "User not found"}), 404

    from datetime import datetime

    record = {
        "user_id": str(user["_id"]),
        "crop": data.get("crop"),
        "season": data.get("season"),
        "location": data.get("location"),
        "land_size": data.get("land_size"),
        "budget": data.get("budget"),
        "language": data.get("language"),
        "soil_params": data.get("soil_params", {}),
        "advice": data.get("advice", ""),
        "timestamp": datetime.utcnow()
    }

    result = soil_records_collection.insert_one(record)

    return jsonify({
        "success": True,
        "record_id": str(result.inserted_id)
    })