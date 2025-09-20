import json
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

        commands = {
            'help': 'Show available commands',
            'about': 'Information about Siva',
            'skills': 'Technical skills and expertise',
            'projects': 'Featured projects and work',
            'certs': 'Certifications and credentials',
            'contact': 'Contact information',
            'clear': 'Clear terminal screen'
        }

        response_data = {
            'commands': commands,
            'timestamp': datetime.now().isoformat()
        }

        self.wfile.write(json.dumps(response_data).encode())

    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
