from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# ---- Choose ONE provider. Example below shows Gemini. ----
USE_GEMINI = True

if USE_GEMINI:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")

SYSTEM = (
    "You are an AI assistant embedded in Siva Sastha Sai Krishna’s portfolio terminal. "
    "Be concise, clear, and helpful. Use short paragraphs and bullet points where useful."
)

@app.post("/")
def chat_stream():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "Message cannot be empty"}), 400

    # If key missing, return helpful error
    if USE_GEMINI and not os.getenv("GEMINI_API_KEY"):
        return jsonify({"response": "[ERROR] Missing GEMINI_API_KEY in Vercel → Project → Settings → Environment Variables."}), 500

    try:
        if USE_GEMINI:
            resp = model.generate_content(f"{SYSTEM}\n\nUser: {msg}")
            text = (resp.text or "").strip()
        else:
            text = "AI is configured but no model selected."

        return jsonify({"response": text, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"response": f"[ERROR] {e}"}), 500
