from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from datetime import datetime
import logging

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Flask ----------
app = Flask(__name__)
CORS(app)  # allow frontend calls (local + vercel)

# ---------- Gemini ----------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("⚠️ GEMINI_API_KEY not set")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

SYSTEM_CONTEXT = """
You are an AI assistant integrated into Siva Sastha Sai Krishna's portfolio terminal.
Keep responses concise, terminal-friendly, and professional.
"""

def get_ai_response(user_input: str) -> str:
    try:
        prompt = f"{SYSTEM_CONTEXT}\n\nUser query: {user_input}"
        resp = model.generate_content(prompt)
        return resp.text
    except Exception as e:
        logger.error(f"AI error: {e}")
        return f"[ERROR] AI system temporarily unavailable: {e}"

# ---------- Routes ----------
# IMPORTANT: Do NOT prefix with /api here. Vercel mounts this file at /api.
@app.get("/health")
def health():
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "ai_status": "connected" if GEMINI_API_KEY else "no_api_key"
    })

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "Message is required"}), 400
    return jsonify({
        "response": get_ai_response(msg),
        "timestamp": datetime.now().isoformat()
    })

@app.post("/chat-stream")
def chat_stream():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "Message is required"}), 400
    return jsonify({
        "response": get_ai_response(msg),
        "timestamp": datetime.now().isoformat(),
        "stream": True
    })

@app.get("/commands")
def commands():
    return jsonify({
        "commands": {
            "help": "Show available commands",
            "about": "Information about Siva",
            "skills": "Technical skills and expertise",
            "projects": "Featured projects and work",
            "certs": "Certifications and credentials",
            "contact": "Contact information",
            "ai": "Chat with AI assistant (usage: ai <your question>)",
            "clear": "Clear terminal screen"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(_e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(_e):
    return jsonify({"error": "Internal server error"}), 500

# Do NOT call app.run() on Vercel
