from flask import Blueprint, request, jsonify
from database import farmer_outcomes_collection
from auth import verify_token
from datetime import datetime

insights_bp = Blueprint('insights', __name__)

def get_ph_range(ph):
    ph = float(ph)
    if ph < 5.5: return "below-5.5"
    elif ph < 6.0: return "5.5-6.0"
    elif ph < 6.5: return "6.0-6.5"
    elif ph < 7.0: return "6.5-7.0"
    elif ph < 7.5: return "7.0-7.5"
    else: return "above-7.5"

def get_confidence_level(total_count, success_rate):
    if total_count < 5:
        return "low"
    elif total_count < 20:
        return "medium"
    else:
        return "high"

def get_recommendation_strength(success_rate):
    if success_rate >= 70:
        return "strong"
    elif success_rate >= 40:
        return "cautious"
    else:
        return "avoid"

@insights_bp.route("/api/insights", methods=["POST"])
def get_insights():
    data = request.json

    crop = data.get("crop", "").lower().strip()
    season = data.get("season", "")
    location = data.get("location", "")
    soil_params = data.get("soil_params", {})

    ph_range = get_ph_range(soil_params.get("ph", 6.5))
    nitrogen = soil_params.get("nitrogen", "Medium")
    phosphorus = soil_params.get("phosphorus", "Medium")
    potassium = soil_params.get("potassium", "Medium")
    location_region = location.split(",")[0].strip() if "," in location else location

    insights = []

    # Level 1 — Exact match
    # Same crop + season + all soil params + region
    exact_match = farmer_outcomes_collection.find_one({
        "crop": crop,
        "season": season,
        "nitrogen": nitrogen,
        "phosphorus": phosphorus,
        "potassium": potassium,
        "ph_range": ph_range,
        "location_region": location_region
    })

    if exact_match and exact_match.get("total_count", 0) >= 3:
        insights.append({
            "match_type": "exact",
            "match_label": "Farmers in your exact conditions",
            "total_farmers": exact_match["total_count"],
            "success_count": exact_match.get("success_count", 0),
            "failure_count": exact_match.get("failure_count", 0),
            "success_rate": exact_match.get("success_rate", 0),
            "confidence": get_confidence_level(
                exact_match["total_count"],
                exact_match.get("success_rate", 0)
            ),
            "recommendation": get_recommendation_strength(
                exact_match.get("success_rate", 0)
            )
        })

    # Level 2 — Same crop + soil params (ignore region)
    soil_match = farmer_outcomes_collection.find_one({
        "crop": crop,
        "nitrogen": nitrogen,
        "phosphorus": phosphorus,
        "potassium": potassium,
        "ph_range": ph_range
    })

    if soil_match and soil_match.get("total_count", 0) >= 3:
        if not exact_match or soil_match["_id"] != exact_match["_id"]:
            insights.append({
                "match_type": "soil",
                "match_label": "Farmers with same soil profile",
                "total_farmers": soil_match["total_count"],
                "success_count": soil_match.get("success_count", 0),
                "failure_count": soil_match.get("failure_count", 0),
                "success_rate": soil_match.get("success_rate", 0),
                "confidence": get_confidence_level(
                    soil_match["total_count"],
                    soil_match.get("success_rate", 0)
                ),
                "recommendation": get_recommendation_strength(
                    soil_match.get("success_rate", 0)
                )
            })

    # Level 3 — Same crop + region only
    crop_region_matches = list(farmer_outcomes_collection.find({
        "crop": crop,
        "location_region": location_region
    }))

    if crop_region_matches:
        total = sum(m.get("total_count", 0) for m in crop_region_matches)
        success = sum(m.get("success_count", 0) for m in crop_region_matches)

        if total >= 3:
            rate = round(success / total * 100, 1)
            insights.append({
                "match_type": "region",
                "match_label": f"{crop.title()} farmers in {location_region}",
                "total_farmers": total,
                "success_count": success,
                "failure_count": total - success,
                "success_rate": rate,
                "confidence": get_confidence_level(total, rate),
                "recommendation": get_recommendation_strength(rate)
            })

    # Level 4 — Same crop overall
    all_crop_matches = list(farmer_outcomes_collection.find({"crop": crop}))

    if all_crop_matches:
        total = sum(m.get("total_count", 0) for m in all_crop_matches)
        success = sum(m.get("success_count", 0) for m in all_crop_matches)

        if total >= 5:
            rate = round(success / total * 100, 1)
            insights.append({
                "match_type": "crop",
                "match_label": f"All {crop.title()} farmers in India",
                "total_farmers": total,
                "success_count": success,
                "failure_count": total - success,
                "success_rate": rate,
                "confidence": get_confidence_level(total, rate),
                "recommendation": get_recommendation_strength(rate)
            })

    # If no data at all
    if not insights:
        return jsonify({
            "success": True,
            "has_data": False,
            "message": f"No community data yet for {crop.title()} farmers. Be the first to share your outcome!",
            "insights": []
        })

    return jsonify({
        "success": True,
        "has_data": True,
        "crop": crop.title(),
        "insights": insights
    })


@insights_bp.route("/api/insights/seed", methods=["POST"])
def seed_data():
    # Seed realistic farmer outcome data for demo
    farmer_outcomes_collection.delete_many({})

    seed_records = [
       # Rice - Mysuru
    {"crop": "rice", "season": "Kharif", "nitrogen": "Low", "phosphorus": "Medium", "potassium": "High", "ph_range": "6.5-7.0", "location_region": "Mysuru", "total_count": 47, "success_count": 38, "failure_count": 9, "success_rate": 80.9, "last_updated": datetime.utcnow()},
    # Rice - Mandya
    {"crop": "rice", "season": "Kharif", "nitrogen": "Medium", "phosphorus": "Medium", "potassium": "Medium", "ph_range": "6.5-7.0", "location_region": "Mandya", "total_count": 63, "success_count": 45, "failure_count": 18, "success_rate": 71.4, "last_updated": datetime.utcnow()},
    # Rice - Raichur
    {"crop": "rice", "season": "Kharif", "nitrogen": "Low", "phosphorus": "Low", "potassium": "High", "ph_range": "6.0-6.5", "location_region": "Raichur", "total_count": 38, "success_count": 28, "failure_count": 10, "success_rate": 73.7, "last_updated": datetime.utcnow()},
    # Wheat - Dharwad
    {"crop": "wheat", "season": "Rabi", "nitrogen": "Low", "phosphorus": "Low", "potassium": "Medium", "ph_range": "6.5-7.0", "location_region": "Dharwad", "total_count": 34, "success_count": 28, "failure_count": 6, "success_rate": 82.4, "last_updated": datetime.utcnow()},
    # Wheat - Gulbarga
    {"crop": "wheat", "season": "Rabi", "nitrogen": "Medium", "phosphorus": "Medium", "potassium": "High", "ph_range": "7.0-7.5", "location_region": "Gulbarga", "total_count": 89, "success_count": 72, "failure_count": 17, "success_rate": 80.9, "last_updated": datetime.utcnow()},
    # Wheat - Bijapur
    {"crop": "wheat", "season": "Rabi", "nitrogen": "Low", "phosphorus": "Medium", "potassium": "Medium", "ph_range": "7.0-7.5", "location_region": "Bijapur", "total_count": 42, "success_count": 31, "failure_count": 11, "success_rate": 73.8, "last_updated": datetime.utcnow()},
    # Maize - Hassan
    {"crop": "maize", "season": "Kharif", "nitrogen": "Low", "phosphorus": "Medium", "potassium": "Medium", "ph_range": "6.0-6.5", "location_region": "Hassan", "total_count": 28, "success_count": 18, "failure_count": 10, "success_rate": 64.3, "last_updated": datetime.utcnow()},
    # Maize - Tumkur
    {"crop": "maize", "season": "Kharif", "nitrogen": "Medium", "phosphorus": "Low", "potassium": "Medium", "ph_range": "6.5-7.0", "location_region": "Tumkur", "total_count": 33, "success_count": 22, "failure_count": 11, "success_rate": 66.7, "last_updated": datetime.utcnow()},
    # Cotton - Hubli
    {"crop": "cotton", "season": "Kharif", "nitrogen": "Medium", "phosphorus": "Low", "potassium": "High", "ph_range": "6.5-7.0", "location_region": "Hubli", "total_count": 52, "success_count": 31, "failure_count": 21, "success_rate": 59.6, "last_updated": datetime.utcnow()},
    # Cotton - Bellary
    {"crop": "cotton", "season": "Kharif", "nitrogen": "Low", "phosphorus": "Medium", "potassium": "High", "ph_range": "7.0-7.5", "location_region": "Bellary", "total_count": 44, "success_count": 27, "failure_count": 17, "success_rate": 61.4, "last_updated": datetime.utcnow()},
    # Tomato - Kolar
    {"crop": "tomato", "season": "Rabi", "nitrogen": "Low", "phosphorus": "Low", "potassium": "Medium", "ph_range": "6.0-6.5", "location_region": "Kolar", "total_count": 19, "success_count": 14, "failure_count": 5, "success_rate": 73.7, "last_updated": datetime.utcnow()},
    # Tomato - Chikkaballapur
    {"crop": "tomato", "season": "Rabi", "nitrogen": "Medium", "phosphorus": "Medium", "potassium": "Medium", "ph_range": "6.0-6.5", "location_region": "Chikkaballapur", "total_count": 25, "success_count": 18, "failure_count": 7, "success_rate": 72.0, "last_updated": datetime.utcnow()},
    # Sugarcane - Mandya
    {"crop": "sugarcane", "season": "Kharif", "nitrogen": "Medium", "phosphorus": "Medium", "potassium": "High", "ph_range": "6.5-7.0", "location_region": "Mandya", "total_count": 41, "success_count": 29, "failure_count": 12, "success_rate": 70.7, "last_updated": datetime.utcnow()},
    # Sugarcane - Belgaum
    {"crop": "sugarcane", "season": "Kharif", "nitrogen": "High", "phosphorus": "Medium", "potassium": "High", "ph_range": "6.5-7.0", "location_region": "Belgaum", "total_count": 36, "success_count": 25, "failure_count": 11, "success_rate": 69.4, "last_updated": datetime.utcnow()},
    # Groundnut - Chitradurga
    {"crop": "groundnut", "season": "Kharif", "nitrogen": "Low", "phosphorus": "Medium", "potassium": "Medium", "ph_range": "6.0-6.5", "location_region": "Chitradurga", "total_count": 36, "success_count": 22, "failure_count": 14, "success_rate": 61.1, "last_updated": datetime.utcnow()},
    # Groundnut - Davangere
    {"crop": "groundnut", "season": "Kharif", "nitrogen": "Low", "phosphorus": "Low", "potassium": "Medium", "ph_range": "6.5-7.0", "location_region": "Davangere", "total_count": 29, "success_count": 19, "failure_count": 10, "success_rate": 65.5, "last_updated": datetime.utcnow()},
    # Ragi - Mysuru
    {"crop": "ragi", "season": "Kharif", "nitrogen": "Low", "phosphorus": "Low", "potassium": "Medium", "ph_range": "6.0-6.5", "location_region": "Mysuru", "total_count": 55, "success_count": 42, "failure_count": 13, "success_rate": 76.4, "last_updated": datetime.utcnow()},
    # Ragi - Tumkur
    {"crop": "ragi", "season": "Kharif", "nitrogen": "Low", "phosphorus": "Medium", "potassium": "Low", "ph_range": "6.0-6.5", "location_region": "Tumkur", "total_count": 48, "success_count": 35, "failure_count": 13, "success_rate": 72.9, "last_updated": datetime.utcnow()},
    # Jowar - Gulbarga
    {"crop": "jowar", "season": "Kharif", "nitrogen": "Low", "phosphorus": "Medium", "potassium": "Medium", "ph_range": "6.5-7.0", "location_region": "Gulbarga", "total_count": 29, "success_count": 19, "failure_count": 10, "success_rate": 65.5, "last_updated": datetime.utcnow()},
    # Jowar - Bidar
    {"crop": "jowar", "season": "Kharif", "nitrogen": "Medium", "phosphorus": "Low", "potassium": "Medium", "ph_range": "7.0-7.5", "location_region": "Bidar", "total_count": 22, "success_count": 14, "failure_count": 8, "success_rate": 63.6, "last_updated": datetime.utcnow()},
    # Turmeric - Mysuru
    {"crop": "turmeric", "season": "Kharif", "nitrogen": "Medium", "phosphorus": "Medium", "potassium": "High", "ph_range": "6.0-6.5", "location_region": "Mysuru", "total_count": 23, "success_count": 17, "failure_count": 6, "success_rate": 73.9, "last_updated": datetime.utcnow()},
    # Onion - Belgaum
    {"crop": "onion", "season": "Rabi", "nitrogen": "Medium", "phosphorus": "Low", "potassium": "Medium", "ph_range": "6.5-7.0", "location_region": "Belgaum", "total_count": 31, "success_count": 20, "failure_count": 11, "success_rate": 64.5, "last_updated": datetime.utcnow()},
    # Banana - Shimoga
    {"crop": "banana", "season": "Kharif", "nitrogen": "High", "phosphorus": "Medium", "potassium": "High", "ph_range": "6.5-7.0", "location_region": "Shimoga", "total_count": 38, "success_count": 29, "failure_count": 9, "success_rate": 76.3, "last_updated": datetime.utcnow()},
    # Soybean - Dharwad
    {"crop": "soybean", "season": "Kharif", "nitrogen": "Low", "phosphorus": "Low", "potassium": "Medium", "ph_range": "6.5-7.0", "location_region": "Dharwad", "total_count": 45, "success_count": 30, "failure_count": 15, "success_rate": 66.7, "last_updated": datetime.utcnow()},
    # Coconut - Tumkur
    {"crop": "coconut", "season": "Kharif", "nitrogen": "Medium", "phosphorus": "Medium", "potassium": "High", "ph_range": "6.0-6.5", "location_region": "Tumkur", "total_count": 27, "success_count": 20, "failure_count": 7, "success_rate": 74.1, "last_updated": datetime.utcnow()},
    # Arecanut - Shimoga
    {"crop": "arecanut", "season": "Kharif", "nitrogen": "Medium", "phosphorus": "Low", "potassium": "High", "ph_range": "6.0-6.5", "location_region": "Shimoga", "total_count": 33, "success_count": 24, "failure_count": 9, "success_rate": 72.7, "last_updated": datetime.utcnow()},
    # Sunflower - Raichur
    {"crop": "sunflower", "season": "Rabi", "nitrogen": "Low", "phosphorus": "Medium", "potassium": "Medium", "ph_range": "6.5-7.0", "location_region": "Raichur", "total_count": 31, "success_count": 21, "failure_count": 10, "success_rate": 67.7, "last_updated": datetime.utcnow()},
    # Chilli - Hubli
    {"crop": "chilli", "season": "Kharif", "nitrogen": "Medium", "phosphorus": "Medium", "potassium": "Medium", "ph_range": "6.0-6.5", "location_region": "Hubli", "total_count": 26, "success_count": 17, "failure_count": 9, "success_rate": 65.4, "last_updated": datetime.utcnow()},
    # Coimbatore crops
    {"crop": "rice", "season": "Kharif", "nitrogen": "Low", "phosphorus": "Medium", "potassium": "Medium", "ph_range": "6.5-7.0", "location_region": "Coimbatore", "total_count": 44, "success_count": 32, "failure_count": 12, "success_rate": 72.7, "last_updated": datetime.utcnow()},
    {"crop": "sugarcane", "season": "Kharif", "nitrogen": "High", "phosphorus": "Medium", "potassium": "High", "ph_range": "6.5-7.0", "location_region": "Coimbatore", "total_count": 39, "success_count": 28, "failure_count": 11, "success_rate": 71.8, "last_updated": datetime.utcnow()},]

    farmer_outcomes_collection.insert_many(seed_records)

    return jsonify({
        "success": True,
        "message": f"Seeded {len(seed_records)} farmer outcome records!"
    })