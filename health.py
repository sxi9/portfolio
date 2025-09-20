import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        # Check if API key is configured
        api_key = os.getenv('GEMINI_API_KEY')
        ai_status = 'connected' if api_key else 'no_api_key'

        response_data = {
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'ai_status': ai_status,
            'platform': 'vercel'
        }

        self.wfile.write(json.dumps(response_data).encode())

    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
