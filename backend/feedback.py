# from flask import Blueprint, request, jsonify
# from database import feedbacks_collection, soil_records_collection
# from auth import verify_token
# from datetime import datetime
# from bson import ObjectId

# feedback_bp = Blueprint('feedback', __name__)

# @feedback_bp.route("/api/feedback", methods=["POST"])
# def submit_feedback():
#     token = request.headers.get("Authorization", "").replace("Bearer ", "")
#     payload = verify_token(token)

#     if not payload:
#         return jsonify({"error": "Please login to submit feedback"}), 401

#     data = request.json

#     # Validation
#     rating = data.get("rating")
#     helpful = data.get("helpful")
#     comment = data.get("comment", "").strip()

#     if rating is None or not (1 <= int(rating) <= 5):
#         return jsonify({"error": "Rating must be between 1 and 5"}), 400

#     if helpful is None:
#         return jsonify({"error": "Please answer if advice was helpful"}), 400

#     feedback = {
#         "user_id": payload["user_id"],
#         "user_email": payload["email"],
#         "record_id": data.get("record_id", ""),
#         "crop": data.get("crop", ""),
#         "location": data.get("location", ""),
#         "rating": int(rating),
#         "helpful": helpful,
#         "comment": comment,
#         "timestamp": datetime.utcnow()
#     }

#     result = feedbacks_collection.insert_one(feedback)

#     return jsonify({
#         "success": True,
#         "feedback_id": str(result.inserted_id)
#     })


# @feedback_bp.route("/api/feedback/my", methods=["GET"])
# def get_my_feedback():
#     token = request.headers.get("Authorization", "").replace("Bearer ", "")
#     payload = verify_token(token)

#     if not payload:
#         return jsonify({"error": "Unauthorized"}), 401

#     feedbacks = list(feedbacks_collection.find(
#         {"user_email": payload["email"]},
#         sort=[("timestamp", -1)]
#     ))

#     for f in feedbacks:
#         f["_id"] = str(f["_id"])
#         f["timestamp"] = f["timestamp"].strftime("%d %b %Y")

#     return jsonify({"feedbacks": feedbacks})


# @feedback_bp.route("/api/feedback/stats", methods=["GET"])
# def get_stats():
#     total = feedbacks_collection.count_documents({})
#     helpful_count = feedbacks_collection.count_documents({"helpful": True})

#     pipeline = [
#         {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
#     ]
#     result = list(feedbacks_collection.aggregate(pipeline))
#     avg_rating = round(result[0]["avg_rating"], 1) if result else 0

#     return jsonify({
#         "total_feedbacks": total,
#         "helpful_percentage": round((helpful_count / total * 100)) if total > 0 else 0,
#         "average_rating": avg_rating
#     })





















from flask import Blueprint, request, jsonify
from database import feedbacks_collection, soil_records_collection, farmer_outcomes_collection
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

    # Save feedback
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

    # ---- AUTO SAVE TO FARMER OUTCOMES ----
    # Handle both boolean and string versions of helpful
    if isinstance(helpful, str):
        helpful = helpful.lower() == 'true'

    outcome = "success" if (int(rating) >= 4 and helpful == True) else \
          "failure" if (int(rating) <= 2 and helpful == False) else \
          "neutral"

    print("Rating:", int(rating), "Helpful:", helpful, "Outcome:", outcome) 

    if outcome != "neutral":
        
        # Get soil record
        soil_record = None
        if data.get("record_id"):
            try:
                soil_record = soil_records_collection.find_one(
                    {"_id": ObjectId(data.get("record_id"))}
                )
            except:
                pass

        soil = soil_record.get("soil_params", {}) if soil_record else {}

        # Normalize ph to range
        ph = float(soil.get("ph", 6.5))
        if ph < 5.5:
            ph_range = "below-5.5"
        elif ph < 6.0:
            ph_range = "5.5-6.0"
        elif ph < 6.5:
            ph_range = "6.0-6.5"
        elif ph < 7.0:
            ph_range = "6.5-7.0"
        elif ph < 7.5:
            ph_range = "7.0-7.5"
        else:
            ph_range = "above-7.5"

        # Normalize location to region
        location = data.get("location", "")
        location_region = location.split(",")[0].strip() if "," in location else location

        # Build key for this combination
        outcome_key = {
            "crop": data.get("crop", "").lower().strip(),
            "season": soil_record.get("season", "") if soil_record else "",
            "nitrogen": soil.get("nitrogen", "Medium"),
            "phosphorus": soil.get("phosphorus", "Medium"),
            "potassium": soil.get("potassium", "Medium"),
            "ph_range": ph_range,
            "location_region": location_region
        }

        # Increment counts using upsert
        if outcome == "success":
            farmer_outcomes_collection.update_one(
                outcome_key,
                {
                    "$inc": {"total_count": 1, "success_count": 1},
                    "$set": {"last_updated": datetime.utcnow()},
                    "$setOnInsert": {
                        "failure_count": 0,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
        else:
            farmer_outcomes_collection.update_one(
                outcome_key,
                {
                    "$inc": {"total_count": 1, "failure_count": 1},
                    "$set": {"last_updated": datetime.utcnow()},
                    "$setOnInsert": {
                        "success_count": 0,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )

        # Recalculate success rate
        updated = farmer_outcomes_collection.find_one(outcome_key)
        if updated and updated.get("total_count", 0) > 0:
            success_rate = round(
                updated["success_count"] / updated["total_count"] * 100, 1
            )
            farmer_outcomes_collection.update_one(
                outcome_key,
                {"$set": {"success_rate": success_rate}}
            )

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