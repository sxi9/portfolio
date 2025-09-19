from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.get("/")
def health():
    return jsonify({"status": "online", "timestamp": datetime.now().isoformat()})
