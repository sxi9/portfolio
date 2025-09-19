from http.server import BaseHTTPRequestHandler
import os, json
from datetime import datetime
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
else:
    model = None

class handler(BaseHTTPRequestHandler):
    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    def do_POST(self):
        if not model:
            self._send_json({"response": "[ERROR] Missing GEMINI_API_KEY"}, 500)
            return

        data = self._read_json()
        msg = (data.get("message") or "").strip()
        if not msg:
            self._send_json({"error": "Message cannot be empty"}, 400)
            return

        try:
            resp = model.generate_content(f"User: {msg}")
            text = (resp.text or "").strip()
            self._send_json({"response": text, "timestamp": datetime.now().isoformat()}, 200)
        except Exception as e:
            self._send_json({"response": f"[ERROR] {e}"}, 500)

    def do_GET(self):
        # Optional: let GET say the endpoint exists
        self._send_json({"ok": True, "endpoint": "chat-stream"}, 200)

    def _send_json(self, obj, status=200):
        body = json.dumps(obj)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))
