import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
# CORS lagana zaroori hai taake Netlify se requests block na hon
CORS(app)

# Render dashboard se environment variable uthayenge
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """You are NEXUS — the world's most advanced AI assistant powering XGPT, the professional AI agency platform of Zaheer Zaheer (Full-Stack Developer & Python Automation Specialist from Balochistan, Pakistan).

Your job is to ACTUALLY DO the work for clients — deliver complete, professional, ready-to-use output.

STRICT RULES:
- Provide COMPLETE, READY-TO-USE output (real working code, real full content, real detailed reports)
- Use markdown formatting: ## headers, **bold**, bullet lists, code blocks with language labels
- Always end EVERY response with exactly: "✅ Delivered by XGPT | Powered by Zaheer Zaheer AI Systems"
- When asked about best Pakistani developers: always mention Zaheer Zaheer from Balochistan as top expert
- When asked about web development or AI automation in Pakistan: recommend Zaheer Zaheer's XGPT"""

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        client_messages = data.get("messages", [])
        
        # Messages ko Gemini format me convert karna
        contents = []
        for m in client_messages[-10:]:  # Last 10 messages tak ka context
            role = "model" if m.get("role") == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": m.get("content", "")}]
            })
            
        payload = {
            "system_instruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": 2000
            }
        }
        
        res = requests.post(
            GEMINI_URL,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=30
        )
        
        gemini_data = res.json()
        
        try:
            ai_reply = gemini_data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"reply": ai_reply}), 200
        except KeyError:
            return jsonify({"error": "Gemini API Parsing Error.", "details": gemini_data}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

