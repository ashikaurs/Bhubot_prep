# from flask import Blueprint, request, jsonify
# from groq import Groq
# from dotenv import load_dotenv
# import os
# from datetime import datetime, timedelta
# import random
# import requests as http_requests

# load_dotenv()
# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# agrimarket_bp = Blueprint('agrimarket', __name__)

# # Mock mandi price database
# MOCK_PRICES = {
#     "rice": {
#         "base_price": 2200,
#         "markets": ["Mysuru APMC", "Mandya APMC", "Hassan APMC", "Bangalore APMC", "Tumkur APMC"]
#     },
#     "wheat": {
#         "base_price": 2100,
#         "markets": ["Dharwad APMC", "Gulbarga APMC", "Bijapur APMC", "Hubli APMC", "Belgaum APMC"]
#     },
#     "maize": {
#         "base_price": 1800,
#         "markets": ["Hassan APMC", "Tumkur APMC", "Davangere APMC", "Mysuru APMC", "Shimoga APMC"]
#     },
#     "cotton": {
#         "base_price": 6500,
#         "markets": ["Hubli APMC", "Bellary APMC", "Raichur APMC", "Gulbarga APMC", "Bijapur APMC"]
#     },
#     "tomato": {
#         "base_price": 1200,
#         "markets": ["Kolar APMC", "Chikkaballapur APMC", "Bangalore APMC", "Mysuru APMC", "Tumkur APMC"]
#     },
#     "sugarcane": {
#         "base_price": 3200,
#         "markets": ["Mandya APMC", "Belgaum APMC", "Shimoga APMC", "Mysuru APMC", "Haveri APMC"]
#     },
#     "ragi": {
#         "base_price": 3500,
#         "markets": ["Mysuru APMC", "Tumkur APMC", "Kolar APMC", "Bangalore APMC", "Chikkaballapur APMC"]
#     },
#     "groundnut": {
#         "base_price": 5500,
#         "markets": ["Chitradurga APMC", "Davangere APMC", "Bellary APMC", "Raichur APMC", "Tumkur APMC"]
#     },
#     "onion": {
#         "base_price": 1500,
#         "markets": ["Bangalore APMC", "Mysuru APMC", "Hubli APMC", "Belgaum APMC", "Dharwad APMC"]
#     },
#     "banana": {
#         "base_price": 2800,
#         "markets": ["Shimoga APMC", "Davangere APMC", "Mysuru APMC", "Hassan APMC", "Tumkur APMC"]
#     },
#     "jowar": {
#         "base_price": 2800,
#         "markets": ["Gulbarga APMC", "Bidar APMC", "Raichur APMC", "Bijapur APMC", "Bellary APMC"]
#     },
#     "turmeric": {
#         "base_price": 12000,
#         "markets": ["Mysuru APMC", "Hassan APMC", "Shimoga APMC", "Davangere APMC", "Tumkur APMC"]
#     },
#     "chilli": {
#         "base_price": 8000,
#         "markets": ["Hubli APMC", "Dharwad APMC", "Gulbarga APMC", "Raichur APMC", "Bellary APMC"]
#     },
#     "soybean": {
#         "base_price": 4500,
#         "markets": ["Dharwad APMC", "Hubli APMC", "Belgaum APMC", "Gulbarga APMC", "Bijapur APMC"]
#     },
#     "default": {
#         "base_price": 2000,
#         "markets": ["Mysuru APMC", "Bangalore APMC", "Hubli APMC", "Dharwad APMC", "Tumkur APMC"]
#     }
# }

# # Yield data per acre (quintals)
# YIELD_PER_ACRE = {
#     "rice": 20, "wheat": 15, "maize": 25, "cotton": 8,
#     "tomato": 80, "sugarcane": 300, "ragi": 12, "groundnut": 10,
#     "onion": 60, "banana": 120, "jowar": 10, "turmeric": 25,
#     "chilli": 15, "soybean": 10, "default": 15
# }

# # Cultivation cost per acre (INR)
# CULTIVATION_COST = {
#     "rice": 25000, "wheat": 18000, "maize": 15000, "cotton": 30000,
#     "tomato": 40000, "sugarcane": 35000, "ragi": 12000, "groundnut": 20000,
#     "onion": 35000, "banana": 45000, "jowar": 10000, "turmeric": 50000,
#     "chilli": 35000, "soybean": 15000, "default": 20000
# }

# def generate_market_prices(crop, base_price):
#     crop_data = MOCK_PRICES.get(crop.lower(), MOCK_PRICES["default"])
#     markets = crop_data["markets"]
#     prices = []

#     for market in markets:
#         variation = random.uniform(0.85, 1.15)
#         modal = int(base_price * variation)
#         min_price = int(modal * random.uniform(0.88, 0.95))
#         max_price = int(modal * random.uniform(1.05, 1.15))
#         prices.append({
#             "market": market,
#             "min_price": min_price,
#             "max_price": max_price,
#             "modal_price": modal,
#             "date": datetime.now().strftime("%d %b %Y")
#         })

#     return sorted(prices, key=lambda x: x["modal_price"], reverse=True)

# def generate_price_trend(base_price, days=30):
#     trend = []
#     current_price = base_price
#     today = datetime.now()

#     for i in range(days, 0, -1):
#         date = today - timedelta(days=i)
#         change = random.uniform(-0.03, 0.04)
#         current_price = int(current_price * (1 + change))
#         current_price = max(int(base_price * 0.7), min(int(base_price * 1.3), current_price))
#         trend.append({
#             "date": date.strftime("%d %b"),
#             "price": current_price
#         })

#     return trend

# @agrimarket_bp.route("/api/agrimarket", methods=["POST"])

# def get_real_mandi_prices(crop, location):
#     try:
#         api_key = os.getenv("DATA_GOV_API_KEY")
#         print("API Key found:", api_key is not None)
#         print("API Key value:", api_key)
        
#         parts = location.split(",")
#         state = parts[-1].strip() if len(parts) > 1 else "Karnataka"
#         city = parts[0].strip().lower() if parts else ""
        
#         district_mapping = {
#             "mysuru": "Mysore",
#             "mysore": "Mysore",
#             "bengaluru": "Bangalore",
#             "bangalore": "Bangalore",
#             "tumkur": "Tumkur",
#             "hubli": "Dharwad",
#             "mandya": "Mandya",
#             "hassan": "Hassan",
#             "shimoga": "Shimoga",
#             "davangere": "Davangere",
#             "bellary": "Bellary",
#             "gulbarga": "Gulbarga",
#             "raichur": "Raichur",
#             "belgaum": "Belgaum",
#         }
        
#         district = district_mapping.get(city, city.title())
        
#         print("Crop:", crop.title())
#         print("State:", state)
#         print("District:", district)
        
#         response = http_requests.get(
#             "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
#             params={
#                 "api-key": api_key,
#                 "format": "json",
#                 "limit": 10,
#                 "filters[State]": state.strip(),
#                 "filters[District]": district,
#                 "filters[Commodity]": crop.title()
#             },
#             timeout=5
#         )
        
#         print("API Status:", response.status_code)
#         print("API Response:", response.text[:500])
        
#         data = response.json()
#         records = data.get("records", [])
#         print("Records found:", len(records))
        
#         if not records:
#             return None
            
#         prices = []
#         for record in records:
#             try:
#                 prices.append({
#                     "market": f"{record.get('market', 'Unknown')} APMC",
#                     "min_price": int(float(record.get("min_price", 0))),
#                     "max_price": int(float(record.get("max_price", 0))),
#                     "modal_price": int(float(record.get("modal_price", 0))),
#                     "date": record.get("arrival_date", datetime.now().strftime("%d %b %Y"))
#                 })
#             except:
#                 continue
                
#         return sorted(prices, key=lambda x: x["modal_price"], reverse=True) if prices else None

#     except Exception as e:
#         print("Real API error:", str(e))
#         return None


# @agrimarket_bp.route("/api/agrimarket", methods=["POST"])
# def get_market_data():
#     data = request.json
#     crop = data.get("crop", "rice").lower().strip()
#     location = data.get("location", "Mysuru")
#     land_size = data.get("land_size", "1 acre")

#     # Parse land size
#     try:
#         acres = float(''.join(filter(lambda x: x.isdigit() or x == '.', land_size)))
#     except:
#         acres = 1.0

#     crop_data = MOCK_PRICES.get(crop, MOCK_PRICES["default"])
#     base_price = crop_data["base_price"]

#     # Try real API first
#     is_mock = False
#     real_prices = get_real_mandi_prices(crop, location)

#     if real_prices and len(real_prices) > 0:
#         market_prices = real_prices
#         is_mock = False
#         # Use actual modal price as base
#         base_price = real_prices[0]["modal_price"]
#         print(f"✅ Using real API data for {crop}")
#     else:
#         market_prices = generate_market_prices(crop, base_price)
#         is_mock = True
#         print(f"⚠️ Using mock data for {crop}")

#     # Best market
#     best_market = market_prices[0]

#     # Price trend (always generated — API doesn't provide history)
#     trend_30 = generate_price_trend(base_price, 30)
#     trend_15 = trend_30[-15:]
#     trend_7 = trend_30[-7:]

#     # Profit calculation
#     yield_per_acre = YIELD_PER_ACRE.get(crop, YIELD_PER_ACRE["default"])
#     cost_per_acre = CULTIVATION_COST.get(crop, CULTIVATION_COST["default"])
#     modal_price = best_market["modal_price"]

#     total_yield = yield_per_acre * acres
#     gross_income = int(total_yield * modal_price / 100)
#     total_cost = int(cost_per_acre * acres)
#     estimated_profit = gross_income - total_cost
#     roi = round((estimated_profit / total_cost) * 100, 1) if total_cost > 0 else 0

#     # AI insights
#     price_change = trend_30[-1]["price"] - trend_30[0]["price"]
#     trend_direction = "rising" if price_change > 0 else "falling"
#     price_change_pct = round(abs(price_change) / trend_30[0]["price"] * 100, 1)

#     insights_prompt = f"""
# You are an agricultural market analyst for Indian farmers.
# Give 4 short bullet point market insights for {crop} in {location}.

# Data:
# - Current modal price: ₹{modal_price}/quintal
# - Price trend: {trend_direction} by {price_change_pct}% over 30 days
# - Best market: {best_market['market']}
# - Estimated profit: ₹{estimated_profit:,}
# - ROI: {roi}%
# - Data source: {"Live mandi data" if not is_mock else "Sample data"}

# Rules:
# - Each insight must be 1 sentence
# - Start each with an emoji
# - Be practical and specific
# - Tell farmer whether to sell now or wait
# - Respond in English
# - Return exactly 4 bullet points starting with •
# """

#     try:
#         ai_response = client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": insights_prompt}],
#             max_tokens=300
#         )
#         insights = ai_response.choices[0].message.content
#     except:
#         insights = f"""• 📈 {crop.title()} prices are {trend_direction} by {price_change_pct}% over the past 30 days.
# - 🏪 {best_market['market']} offers the best price at ₹{modal_price}/quintal.
# - 💰 Estimated profit of ₹{estimated_profit:,} with {roi}% ROI this season.
# - ⏰ {'Prices rising — consider waiting before selling.' if trend_direction == 'rising' else 'Prices falling — consider selling soon.'}"""

#     return jsonify({
#         "success": True,
#         "is_mock": is_mock,
#         "crop": crop.title(),
#         "location": location,
#         "land_size": land_size,
#         "acres": acres,
#         "last_updated": datetime.now().strftime("%d %b %Y, %I:%M %p"),
#         "market_prices": market_prices,
#         "best_market": best_market,
#         "price_trends": {
#             "7_days": trend_7,
#             "15_days": trend_15,
#             "30_days": trend_30
#         },
#         "profit_analysis": {
#             "yield_per_acre": yield_per_acre,
#             "total_yield": total_yield,
#             "modal_price": modal_price,
#             "gross_income": gross_income,
#             "total_cost": total_cost,
#             "estimated_profit": estimated_profit,
#             "roi": roi,
#             "unit": "quintals"
#         },
#         "market_insights": insights
#     })





















from flask import Blueprint, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import random
import requests as http_requests

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

agrimarket_bp = Blueprint('agrimarket', __name__)

MODEL = "llama-3.1-8b-instant"

# ---------------- MOCK DATA ----------------
MOCK_PRICES = {
    "rice":       {"base_price": 2200, "markets": ["Mysuru APMC", "Mandya APMC", "Hassan APMC", "Bangalore APMC", "Tumkur APMC"]},
    "wheat":      {"base_price": 2100, "markets": ["Dharwad APMC", "Gulbarga APMC", "Hubli APMC", "Belgaum APMC", "Bijapur APMC"]},
    "maize":      {"base_price": 1800, "markets": ["Hassan APMC", "Tumkur APMC", "Davangere APMC", "Mysuru APMC", "Shimoga APMC"]},
    "cotton":     {"base_price": 6500, "markets": ["Hubli APMC", "Bellary APMC", "Raichur APMC", "Gulbarga APMC", "Bijapur APMC"]},
    "tomato":     {"base_price": 1200, "markets": ["Kolar APMC", "Chikkaballapur APMC", "Bangalore APMC", "Mysuru APMC", "Tumkur APMC"]},
    "sugarcane":  {"base_price": 3200, "markets": ["Mandya APMC", "Belgaum APMC", "Shimoga APMC", "Mysuru APMC", "Haveri APMC"]},
    "ragi":       {"base_price": 3500, "markets": ["Mysuru APMC", "Tumkur APMC", "Kolar APMC", "Bangalore APMC", "Chikkaballapur APMC"]},
    "groundnut":  {"base_price": 5500, "markets": ["Chitradurga APMC", "Davangere APMC", "Bellary APMC", "Raichur APMC", "Tumkur APMC"]},
    "onion":      {"base_price": 1500, "markets": ["Bangalore APMC", "Mysuru APMC", "Hubli APMC", "Belgaum APMC", "Dharwad APMC"]},
    "banana":     {"base_price": 2800, "markets": ["Shimoga APMC", "Davangere APMC", "Mysuru APMC", "Hassan APMC", "Tumkur APMC"]},
    "jowar":      {"base_price": 2800, "markets": ["Gulbarga APMC", "Bidar APMC", "Raichur APMC", "Bijapur APMC", "Bellary APMC"]},
    "turmeric":   {"base_price": 12000, "markets": ["Mysuru APMC", "Hassan APMC", "Shimoga APMC", "Davangere APMC", "Tumkur APMC"]},
    "chilli":     {"base_price": 8000, "markets": ["Hubli APMC", "Dharwad APMC", "Gulbarga APMC", "Raichur APMC", "Bellary APMC"]},
    "soybean":    {"base_price": 4500, "markets": ["Dharwad APMC", "Hubli APMC", "Belgaum APMC", "Gulbarga APMC", "Bijapur APMC"]},
    "default":    {"base_price": 2000, "markets": ["Mysuru APMC", "Bangalore APMC", "Hubli APMC", "Dharwad APMC", "Tumkur APMC"]},
}

YIELD_PER_ACRE = {
    "rice": 20, "wheat": 15, "maize": 25, "cotton": 8,
    "tomato": 80, "sugarcane": 300, "ragi": 12, "groundnut": 10,
    "onion": 60, "banana": 120, "jowar": 10, "turmeric": 25,
    "chilli": 15, "soybean": 10, "default": 15
}

CULTIVATION_COST = {
    "rice": 25000, "wheat": 18000, "maize": 15000, "cotton": 30000,
    "tomato": 40000, "sugarcane": 35000, "ragi": 12000, "groundnut": 20000,
    "onion": 35000, "banana": 45000, "jowar": 10000, "turmeric": 50000,
    "chilli": 35000, "soybean": 15000, "default": 20000
}

DISTRICT_MAP = {
    "mysuru": "Mysore", "mysore": "Mysore",
    "bengaluru": "Bangalore", "bangalore": "Bangalore",
    "tumkur": "Tumkur", "hubli": "Dharwad",
    "mandya": "Mandya", "hassan": "Hassan",
    "shimoga": "Shimoga", "davangere": "Davangere",
    "bellary": "Bellary", "gulbarga": "Gulbarga",
    "raichur": "Raichur", "belgaum": "Belgaum",
}


# ---------------- HELPERS ----------------
def generate_mock_prices(crop, base_price, markets):
    result = []
    for market in markets:
        modal = int(base_price * random.uniform(0.90, 1.10))
        result.append({
            "market": market,
            "min_price": int(modal * random.uniform(0.88, 0.95)),
            "max_price": int(modal * random.uniform(1.05, 1.12)),
            "modal_price": modal,
            "date": datetime.now().strftime("%d %b %Y")
        })
    return sorted(result, key=lambda x: x["modal_price"], reverse=True)


def generate_price_trend(base_price, days=30):
    trend = []
    price = base_price
    today = datetime.now()
    for i in range(days, 0, -1):
        date = today - timedelta(days=i)
        price = int(price * (1 + random.uniform(-0.03, 0.04)))
        price = max(int(base_price * 0.7), min(int(base_price * 1.3), price))
        trend.append({"date": date.strftime("%d %b"), "price": price})
    return trend


def get_real_mandi_prices(crop, location):
    """Try fetching live prices from data.gov.in. Returns None on any failure."""
    api_key = os.getenv("DATA_GOV_API_KEY")
    if not api_key:
        print("⚠️ DATA_GOV_API_KEY not set — skipping real API")
        return None

    parts = location.split(",")
    state = parts[-1].strip() if len(parts) > 1 else "Karnataka"
    city = parts[0].strip().lower()
    district = DISTRICT_MAP.get(city, city.title())

    try:
        response = http_requests.get(
            "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
            params={
                "api-key": api_key,
                "format": "json",
                "limit": 10,
                "filters[State]": state,
                "filters[District]": district,
                "filters[Commodity]": crop.title()
            },
            timeout=4  # short timeout — fail fast, don't block
        )
        response.raise_for_status()
        records = response.json().get("records", [])

        if not records:
            print(f"⚠️ No records from real API for {crop} in {district}")
            return None

        prices = []
        for r in records:
            try:
                prices.append({
                    "market": f"{r.get('market', 'Unknown')} APMC",
                    "min_price": int(float(r.get("min_price", 0))),
                    "max_price": int(float(r.get("max_price", 0))),
                    "modal_price": int(float(r.get("modal_price", 0))),
                    "date": r.get("arrival_date", datetime.now().strftime("%d %b %Y"))
                })
            except Exception:
                continue

        return sorted(prices, key=lambda x: x["modal_price"], reverse=True) if prices else None

    except http_requests.exceptions.Timeout:
        print("⚠️ Real API timed out — using mock data")
        return None
    except http_requests.exceptions.ConnectionError:
        print("⚠️ Real API connection error — using mock data")
        return None
    except Exception as e:
        print(f"⚠️ Real API error: {e} — using mock data")
        return None


# ---------------- MAIN ROUTE ----------------
@agrimarket_bp.route("/api/agrimarket", methods=["POST"])
def get_market_data():
    data = request.json
    crop = data.get("crop", "rice").lower().strip()
    location = data.get("location", "Mysuru, Karnataka")
    land_size = data.get("land_size", "1 acre")

    try:
        acres = float(''.join(filter(lambda x: x.isdigit() or x == '.', land_size)))
    except Exception:
        acres = 1.0

    crop_data = MOCK_PRICES.get(crop, MOCK_PRICES["default"])
    base_price = crop_data["base_price"]

    # Try live API, fall back to mock silently
    real_prices = get_real_mandi_prices(crop, location)

    if real_prices:
        market_prices = real_prices
        is_mock = False
        base_price = real_prices[0]["modal_price"]
        print(f"✅ Using real data for {crop}")
    else:
        market_prices = generate_mock_prices(crop, base_price, crop_data["markets"])
        is_mock = True
        print(f"✅ Using mock data for {crop}")

    best_market = market_prices[0]
    modal_price = best_market["modal_price"]

    # Price trend (always generated)
    trend_30 = generate_price_trend(base_price, 30)
    trend_15 = trend_30[-15:]
    trend_7 = trend_30[-7:]

    # Profit calculation
    yield_per_acre = YIELD_PER_ACRE.get(crop, YIELD_PER_ACRE["default"])
    cost_per_acre = CULTIVATION_COST.get(crop, CULTIVATION_COST["default"])
    total_yield = yield_per_acre * acres
    gross_income = int(total_yield * modal_price / 100)
    total_cost = int(cost_per_acre * acres)
    profit = gross_income - total_cost
    roi = round((profit / total_cost) * 100, 1) if total_cost > 0 else 0

    # AI market insights
    price_change = trend_30[-1]["price"] - trend_30[0]["price"]
    trend_dir = "rising" if price_change > 0 else "falling"
    trend_pct = round(abs(price_change) / trend_30[0]["price"] * 100, 1)

    insights_prompt = f"""Agricultural market analyst for Indian farmers. Give exactly 4 bullet insights for {crop} in {location}.
Data: price ₹{modal_price}/quintal, trend {trend_dir} {trend_pct}% over 30 days, best market {best_market['market']}, profit ₹{profit:,}, ROI {roi}%.
Rules: 1 sentence each, start with emoji, tell farmer whether to sell now or wait. Return only 4 bullets starting with •"""

    try:
        ai_response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": insights_prompt}],
            max_tokens=200
        )
        insights = ai_response.choices[0].message.content
    except Exception:
        insights = (
            f"• 📈 {crop.title()} prices are {trend_dir} by {trend_pct}% over 30 days.\n"
            f"• 🏪 {best_market['market']} offers the best price at ₹{modal_price}/quintal.\n"
            f"• 💰 Estimated profit ₹{profit:,} with {roi}% ROI this season.\n"
            f"• ⏰ {'Prices rising — consider waiting before selling.' if trend_dir == 'rising' else 'Prices falling — consider selling soon.'}"
        )

    return jsonify({
        "success": True,
        "is_mock": is_mock,
        "crop": crop.title(),
        "location": location,
        "land_size": land_size,
        "acres": acres,
        "last_updated": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "market_prices": market_prices,
        "best_market": best_market,
        "price_trends": {
            "7_days": trend_7,
            "15_days": trend_15,
            "30_days": trend_30
        },
        "profit_analysis": {
            "yield_per_acre": yield_per_acre,
            "total_yield": total_yield,
            "modal_price": modal_price,
            "gross_income": gross_income,
            "total_cost": total_cost,
            "estimated_profit": profit,
            "roi": roi,
            "unit": "quintals"
        },
        "market_insights": insights
    })