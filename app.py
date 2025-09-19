# app.py  (single app for local dev)
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import os

# --- AI provider (Gemini) ---
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # fine for local testing

# Env / model
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
else:
    model = None

SYSTEM = "You are an AI assistant embedded in a portfolio terminal. Be concise, clear, and helpful."

# --- Routes ---
@app.get("/api/health")
def health():
    return jsonify({"status": "online", "timestamp": datetime.now().isoformat()})

@app.post("/api/chat-stream")
def chat_stream():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "Message cannot be empty"}), 400
    if not model:
        return jsonify({"response": "[ERROR] Missing GEMINI_API_KEY in your shell."}), 500

    try:
        resp = model.generate_content(f"{SYSTEM}\n\nUser: {msg}")
        text = (resp.text or "").strip()
        return jsonify({"response": text, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"response": f"[ERROR] {e}"}), 500
