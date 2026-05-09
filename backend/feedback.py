from flask import Blueprint, request, jsonify
from database import feedbacks_collection, soil_records_collection
from auth import verify_token
from datetime import datetime
from bson import ObjectId

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route("/api/feedback", methods=["POST"])
def submit_feedback():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = verify_token(token)

    if not payload:
        return jsonify({"error": "Please login to submit feedback"}), 401

    data = request.json

    # Validation
    rating = data.get("rating")
    helpful = data.get("helpful")
    comment = data.get("comment", "").strip()

    if rating is None or not (1 <= int(rating) <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    if helpful is None:
        return jsonify({"error": "Please answer if advice was helpful"}), 400

    feedback = {
        "user_id": payload["user_id"],
        "user_email": payload["email"],
        "record_id": data.get("record_id", ""),
        "crop": data.get("crop", ""),
        "location": data.get("location", ""),
        "rating": int(rating),
        "helpful": helpful,
        "comment": comment,
        "timestamp": datetime.utcnow()
    }

    result = feedbacks_collection.insert_one(feedback)

    return jsonify({
        "success": True,
        "feedback_id": str(result.inserted_id)
    })


@feedback_bp.route("/api/feedback/my", methods=["GET"])
def get_my_feedback():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    payload = verify_token(token)

    if not payload:
        return jsonify({"error": "Unauthorized"}), 401

    feedbacks = list(feedbacks_collection.find(
        {"user_email": payload["email"]},
        sort=[("timestamp", -1)]
    ))

    for f in feedbacks:
        f["_id"] = str(f["_id"])
        f["timestamp"] = f["timestamp"].strftime("%d %b %Y")

    return jsonify({"feedbacks": feedbacks})


@feedback_bp.route("/api/feedback/stats", methods=["GET"])
def get_stats():
    total = feedbacks_collection.count_documents({})
    helpful_count = feedbacks_collection.count_documents({"helpful": True})

    pipeline = [
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
    ]
    result = list(feedbacks_collection.aggregate(pipeline))
    avg_rating = round(result[0]["avg_rating"], 1) if result else 0

    return jsonify({
        "total_feedbacks": total,
        "helpful_percentage": round((helpful_count / total * 100)) if total > 0 else 0,
        "average_rating": avg_rating
    })