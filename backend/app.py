import requests
import base64

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
    print("Received data:", data)

    soil_params = data.get("soil_params", {})
    crop = data.get("crop", "rice")
    language = data.get("language", "English")
    budget = data.get("budget", "medium")
    land_size = data.get("land_size", "1 acre")

    # shared context for both calls
    context = f"""
Crop: {crop}
Season: {data.get('season', 'Kharif')}
Location: {data.get('location', 'Karnataka, India')}
Land Size: {land_size}
Budget: {budget}
pH: {soil_params.get('ph', 6.5)}
N: {soil_params.get('nitrogen', 'Medium')}
P: {soil_params.get('phosphorus', 'Medium')}
K: {soil_params.get('potassium', 'Medium')}
Organic Carbon: {soil_params.get('organic_carbon', 0.5)}%
EC: {soil_params.get('ec', 0.4)} dS/m
Zn({soil_params.get('zinc','Medium')}), Fe({soil_params.get('iron','Medium')}), 
Mn({soil_params.get('manganese','Medium')}), Cu({soil_params.get('copper','Medium')}), 
B({soil_params.get('boron','Medium')}), S({soil_params.get('sulphur','Medium')})
Moisture: {mock_sensor['moisture']}%
Temperature: {mock_sensor['temperature']}°C
"""

    prompt_part1 = f"""
You are an expert agricultural advisor for Indian farmers.
Respond ONLY in {language}.
Complete every sentence fully. Never cut off midway.

SOIL DATA:
{context}

Generate ONLY these sections (Part 1 of 2):

📊 **Soil Health Score: [X]/100**
- pH ([value]): [X]/15 — [status]
- Nitrogen: [X]/20 — [status]
- Phosphorus: [X]/15 — [status]
- Potassium: [X]/15 — [status]
- Organic Carbon: [X]/15 — [status]
- Micronutrients: [X]/20 — [status]
- 🎯 Main Limiting Factor: **[problem]**
- ⚠️ If not fixed: [consequence for {crop}]

🧪 **Soil Analysis for {crop}**
- pH: [impact on {crop}]
- N/P/K: [growth impact]
- Organic Carbon: [soil health impact]
- EC: [salinity risk]
- Estimated soil type (approximation): [type] — confirm with texture test
- Moisture {mock_sensor['moisture']}%: [status]

🔴 **High Priority Actions**
- [urgent action] ⚠️ If not addressed: [yield loss]
- [second action] ⚠️ If not addressed: [consequence]

🟡 **Medium Priority Actions**
- [action + timing] ✅/⚠️
- [action] ✅/⚠️

🟢 **Low Priority Actions**
- [improvement] ✅
- [improvement] ✅

🌿 **Fertilizer Plan for {crop}**
- Approach: [Organic/Chemical/Combination] — [reason]
Organic:
- [product]: **[quantity]** per acre — [timing] ✅/⚠️
- [product]: **[quantity]** per acre — [timing] ✅/⚠️
Chemical (if needed):
- [product]: **[quantity]** per acre — [timing] ✅/⚠️/❌
Micronutrients:
- [nutrient]: **[Indian product]** — **[dose]** — [soil/foliar] — [timing] ✅
Nutrient Interaction:
- [N-P-K interaction note for {crop}]

Keep response between 250-350 words. Complete every sentence fully in {language}.
"""

    prompt_part2 = f"""
You are an expert agricultural advisor for Indian farmers.
Respond ONLY in {language}.
Complete every sentence fully. Never cut off midway.

SOIL DATA:
{context}

Generate ONLY these sections (Part 2 of 2):

💧 **Irrigation Plan for {crop}**
- Estimated soil type (approximation): [type] — [drainage note]
- Current moisture **{mock_sensor['moisture']}%**: [Deficit/Optimal/Surplus]
- Recommended method: [standing water cm for rice / mm per week for others]
Stage-wise:
- Land preparation: [advice]
- Germination/Transplanting: [water requirement]
- Vegetative growth: [water requirement]
- Flowering/Heading: [critical stage advice]
- Maturity: [reduce water advice]
- ⚠️ Water stress warning: [risk for {crop}]

💰 **Cost Estimate per Acre**
- Seeds: ₹[range]
- Organic inputs: ₹[range]
- Chemical fertilizers: ₹[range]
- Micronutrients: ₹[range]
- Irrigation: ₹[range]
- Labor: ₹[range]
- **Total: ₹[range]**
- Expected yield improvement: **[X–Y]%**
- Estimated return: ₹[range] investment → ₹[range] additional income

💡 **Practical Tips for {crop} in {data.get('location','your region')}**
- [low cost local tip] ✅
- [locally available practice] ✅
- [common mistake warning] ⚠️
- [do THIS WEEK] ✅

📅 **Week-by-Week Action Plan**
- **Week 1–2:** [urgent steps before/at sowing]
- **Week 3–4:** [early growth actions]
- **Week 5–8:** [vegetative stage actions]
- **At Harvest:** [soil care + next season prep]

Keep response between 250-350 words. Complete every sentence fully in {language}.
"""

    # make two separate API calls
    response1 = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt_part1}],
        max_tokens=2000
    )

    response2 = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt_part2}],
        max_tokens=2000
    )

    part1 = response1.choices[0].message.content
    part2 = response2.choices[0].message.content

    full_advice = part1 + "\n\n" + part2

    return jsonify({
        "advice": full_advice,
        "sensor": mock_sensor
    })
     
    

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "BhuBot backend is running!"})


@app.route("/api/ocr", methods=["POST"])
def ocr():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files['image']
    image_data = base64.b64encode(image_file.read()).decode('utf-8')

    print("Image size:", len(image_data))

    # Detect image type
    filename = image_file.filename.lower()
    if filename.endswith('.png'):
        media_type = "image/png"
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        media_type = "image/jpeg"
    else:
        media_type = "image/jpeg"

    # Use Groq vision to read soil card directly
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": """You are reading an Indian government soil health card.
Extract all soil parameters and return ONLY a JSON object.
No explanation, no markdown, no extra text — ONLY the JSON.

Return ONLY this exact JSON format:
{
    "ph": 6.5,
    "nitrogen": "Low",
    "phosphorus": "Medium",
    "potassium": "High",
    "organic_carbon": 0.5,
    "sulphur": "Low",
    "zinc": "Low",
    "iron": "Medium",
    "manganese": "Medium",
    "copper": "Medium",
    "boron": "Low",
    "ec": 0.4
}

Rules:
- ph, organic_carbon, ec must be numbers
- nitrogen, phosphorus, potassium, sulphur, zinc, iron, manganese, copper, boron must be "Low", "Medium", or "High"
- If value not found use defaults: ph=6.5, all nutrients="Medium", organic_carbon=0.5, ec=0.4
- Return ONLY the JSON, absolutely nothing else"""
                        }
                    ]
                }
            ],
            max_tokens=500
        )

        import json
        raw = response.choices[0].message.content.strip()
        print("Groq vision response:", raw)

        raw = raw.replace("```json", "").replace("```", "").strip()

        soil_params = json.loads(raw)
        return jsonify({
            "success": True,
            "soil_params": soil_params
        })

    except Exception as e:
        print("Vision error:", str(e))
        return jsonify({"error": str(e)}), 500




#     ocr_result = ocr_response.json()

#     print("Full OCR response:", ocr_result)  # add this

# # check for errors properly
#     if "ParsedResults" not in ocr_result:
#         error_msg = ocr_result.get("ErrorMessage", "Unknown error")
#         print("OCR Error:", error_msg)
#         return jsonify({"error": f"OCR service error: {error_msg}"}), 500

#     if ocr_result.get("IsErroredOnProcessing"):
#         return jsonify({"error": "OCR failed processing"}), 500


#     extracted_text = ocr_result["ParsedResults"][0]["ParsedText"]
#     print("OCR extracted text:", extracted_text)

#     # Now use Groq to parse the extracted text into soil parameters
#     parse_prompt = f"""
# You are a soil health card reader for Indian government soil health cards.
# Extract soil parameters from this text and return ONLY a JSON object.
# No explanation, no markdown, no extra text — just the JSON.

# Extracted text from soil card:
# {extracted_text}

# Return ONLY this JSON format:
# {{
#     "ph": 6.5,
#     "nitrogen": "Low",
#     "phosphorus": "Medium", 
#     "potassium": "High",
#     "organic_carbon": 0.5,
#     "sulphur": "Low",
#     "zinc": "Low",
#     "iron": "Medium",
#     "manganese": "Medium",
#     "copper": "Medium",
#     "boron": "Low",
#     "ec": 0.4
# }}

# Rules:
# - ph and organic_carbon and ec must be numbers
# - nitrogen, phosphorus, potassium, sulphur, zinc, iron, manganese, copper, boron must be "Low", "Medium", or "High"
# - If a value is not found in the text, use these defaults: ph=6.5, nitrogen="Medium", phosphorus="Medium", potassium="Medium", organic_carbon=0.5, sulphur="Medium", zinc="Medium", iron="Medium", manganese="Medium", copper="Medium", boron="Medium", ec=0.4
# - Return ONLY the JSON, nothing else
# """

#     parse_response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role": "user", "content": parse_prompt}],
#         max_tokens=500
#     )

#     import json
#     raw = parse_response.choices[0].message.content.strip()

#     # clean up any markdown if AI adds it
#     raw = raw.replace("```json", "").replace("```", "").strip()

#     try:
#         soil_params = json.loads(raw)
#         return jsonify({
#             "success": True,
#             "soil_params": soil_params,
#             "extracted_text": extracted_text
#         })
#     except:
#         return jsonify({"error": "Could not parse soil parameters", "raw": raw}), 500
    






@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    data = request.json
    user_message = data.get("message", "")
    chat_history = data.get("history", [])
    farm_context = data.get("farm_context", {})

    context_str = ""
    if farm_context:
        context_str = f"""
Current farm context:
- Crop: {farm_context.get('crop', 'Not specified')}
- Location: {farm_context.get('location', 'Not specified')}
- Season: {farm_context.get('season', 'Not specified')}
- Land Size: {farm_context.get('land_size', 'Not specified')}
- Budget: {farm_context.get('budget', 'Not specified')}
- Soil pH: {farm_context.get('ph', 'Not specified')}
- Nitrogen: {farm_context.get('nitrogen', 'Not specified')}
- Phosphorus: {farm_context.get('phosphorus', 'Not specified')}
- Potassium: {farm_context.get('potassium', 'Not specified')}
"""

    system_prompt = f"""You are BhuBot, a friendly and expert agricultural advisor for Indian farmers.
Answer farming questions clearly and practically. Focus on Indian farming conditions, locally available products, and affordable solutions.
Keep answers concise (3-5 sentences). Use simple language.
{f"Use this farm context when relevant: {context_str}" if context_str else ""}
If asked in another language, respond in that language."""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-6:]:  # keep last 6 messages for context
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=400
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})












if __name__ == "__main__":
    app.run(debug=True)