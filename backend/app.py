from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Mock sensor data (replace with real IoT later)
mock_sensor = {
    "moisture": 42,
    "temperature": 28.5
}

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    
    soil_params = data.get("soil_params", {})
    crop = data.get("crop", "rice")
    language = data.get("language", "English")
    budget = data.get("budget", "medium")
    land_size = data.get("land_size", "1 acre")

    prompt = f"""
You are BhuBot, a friendly agricultural advisor for Indian farmers.
Respond ONLY in {language}.
Be simple, friendly, and practical.

Farmer's soil data:
- pH: {soil_params.get('ph', 6.5)}
- Nitrogen (N): {soil_params.get('nitrogen', 'Medium')}
- Phosphorus (P): {soil_params.get('phosphorus', 'Low')}
- Potassium (K): {soil_params.get('potassium', 'High')}
- Organic Carbon: {soil_params.get('organic_carbon', 0.5)}%
- Sulphur: {soil_params.get('sulphur', 'Medium')}

Live sensor readings:
- Soil Moisture: {mock_sensor['moisture']}%
- Soil Temperature: {mock_sensor['temperature']}°C

Farmer context:
- Crop: {crop}
- Land size: {land_size}
- Budget: {budget}

Give personalized fertilizer advice. 
Prioritize bio/organic fertilizers first.
Only suggest chemicals if absolutely necessary.
Give specific quantities per acre.
Keep it conversational and easy to understand.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    return jsonify({
        "advice": response.choices[0].message.content,
        "sensor": mock_sensor
    })

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "BhuBot backend is running!"})

if __name__ == "__main__":
    app.run(debug=True)