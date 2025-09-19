from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from datetime import datetime
import logging

# -------------------------------
# Logging setup
# -------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# Flask setup
# -------------------------------
app = Flask(__name__)
CORS(app)  # Allow frontend calls

# -------------------------------
# Gemini AI setup
# -------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("⚠️ GEMINI_API_KEY not set in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# -------------------------------
# System context for answers
# -------------------------------
SYSTEM_CONTEXT = """
You are an AI assistant integrated into Siva Sastha Sai Krishna's portfolio terminal. 
You should respond as Siva's virtual assistant, speaking on his behalf and helping visitors learn about his work.

IMPORTANT: Keep responses concise, terminal-friendly, and professional. Use a slightly technical tone but remain approachable.
"""

# -------------------------------
# Helper: AI Response
# -------------------------------
def get_ai_response(user_input: str) -> str:
    try:
        prompt = f"{SYSTEM_CONTEXT}\n\nUser query: {user_input}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"AI error: {e}")
        return f"[ERROR] AI system temporarily unavailable: {e}"

# -------------------------------
# Routes
# -------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "ai_status": "connected" if GEMINI_API_KEY else "no_api_key"
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """AI chat endpoint"""
    data = request.get_json()
    if not data or not data.get("message", "").strip():
        return jsonify({"error": "Message is required"}), 400

    user_message = data["message"].strip()
    ai_response = get_ai_response(user_message)

    return jsonify({
        "response": ai_response,
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/chat-stream", methods=["POST"])
def chat_stream():
    """Simulated streaming endpoint"""
    data = request.get_json()
    if not data or not data.get("message", "").strip():
        return jsonify({"error": "Message is required"}), 400

    user_message = data["message"].strip()
    ai_response = get_ai_response(user_message)

    return jsonify({
        "response": ai_response,
        "timestamp": datetime.now().isoformat(),
        "stream": True
    })

@app.route("/api/commands", methods=["GET"])
def get_available_commands():
    """Return list of available commands"""
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

# -------------------------------
# Error handlers
# -------------------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# -------------------------------
# IMPORTANT for Vercel:
# Do NOT call app.run()
# Just expose `app`
# -------------------------------
