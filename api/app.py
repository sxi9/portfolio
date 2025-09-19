from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins for Vercel deployment

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

# System context for the AI
SYSTEM_CONTEXT = """
You are an AI assistant integrated into Siva Sastha Sai Krishna's portfolio terminal. 
You should respond as Siva's virtual assistant, speaking on his behalf and helping visitors learn about his work.

IMPORTANT: Keep responses concise, terminal-friendly, and professional. Use a slightly technical tone but remain approachable.

=== SIVA'S COMPLETE PROFILE ===

ABOUT:
- Full name: Siva Sastha Sai Krishna
- Role: Cybersecurity & AI/ML Engineer
- Location: Bengaluru, Karnataka, India
- Email: sivasasthasaikrishna@gmail.com
- Phone: +91 93804 12078
- GitHub: https://github.com/sxi9
- LinkedIn: https://www.linkedin.com/in/s-astha-sai-krishna-040719296

TECHNICAL SKILLS:
- Cybersecurity: Nmap, Wireshark, Burp Suite, Metasploit, Nessus, ARP spoofing detection, Network monitoring, Threat intelligence (VirusTotal, Shodan, MISP, Anomali)
- AI/ML: LangChain, Ollama, RAG (Chroma), TensorFlow, MediaPipe, Hugging Face APIs, Prompt Engineering
- Web/Backend: Python, Flask, FastAPI, Node.js, React, Streamlit
- Data/Cloud: Pandas, PyPDF, MongoDB, MySQL, AWS, Azure
- DevOps: Modular pipelines, CI/CD, Docker
- Operating Systems: Windows, Ubuntu

FEATURED PROJECTS:
1. Panasonic RAG Product Recommender - Agentic chatbot using LangChain + Ollama; RAG over CSV/PDF via Chroma; JSON logic extraction; Chainlit UI
2. Drone Network Intrusion Detection - Real-time monitoring for unauthorized devices, IP/MAC spoofing; Nmap + Scapy; Flask dashboard; multithreaded engine
3. VITA - AI Indian Sign Language Translator - MediaPipe + TensorFlow; real-time ISL to speech; Streamlit/Flask app
4. BYOD Network Management Portal - pfSense REST APIs; auth & dashboards; improved network efficiency
5. Homelab on Proxmox - Self-hosted services (AdGuard, OpenVPN, Immich, NxWitness) with Cloudflare Tunnels

CERTIFICATIONS:
- ISC2 — CC (Certified in Cybersecurity)
- IBM Cybersecurity
- Fortinet Certified Associate in Cybersecurity
- Cyber Security & Ethical Hacking — Quantum Learning (Nov 2023)
- Data Science with Python — Simplilearn (May 2023)

WORK EXPERIENCE & ACHIEVEMENTS:
- Built threat-detection systems for network and endpoint security
- Developed RAG-powered product recommendation systems
- Created real-time network intrusion detection systems
- Implemented AI-powered sign language translation
- Experience with homelab setup and self-hosted services
- Strong background in both offensive and defensive cybersecurity

RESPONSE GUIDELINES:
- Always respond as if you're Siva's assistant helping visitors learn about his work
- For work/project questions, provide specific details from the profile above
- For technical questions, reference his actual skills and experience
- Keep responses under 4-5 sentences for terminal readability
- Use technical language but make it accessible
- If asked about availability/hiring, mention his contact information
- For general questions not about Siva, provide helpful but brief responses
"""

def get_ai_response(user_input):
    """Get response from Gemini AI with error handling"""
    try:
        if not GEMINI_API_KEY:
            return "[ERROR] Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
        
        # Combine system context with user input
        prompt = f"{SYSTEM_CONTEXT}\n\nUser query: {user_input}"
        
        # Generate response
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return f"[ERROR] AI system temporarily unavailable: {str(e)}"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'ai_status': 'connected' if GEMINI_API_KEY else 'no_api_key',
        'platform': 'vercel'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint for AI responses"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get AI response
        ai_response = get_ai_response(user_message)
        
        logger.info(f"Chat request: {user_message[:50]}... -> Response generated")
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chat-stream', methods=['POST'])
def chat_stream():
    """Streaming chat endpoint for real-time responses"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get AI response (we'll simulate streaming on frontend)
        ai_response = get_ai_response(user_message)
        
        logger.info(f"Streaming chat request: {user_message[:50]}... -> Response generated")
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'stream': True
        })
        
    except Exception as e:
        logger.error(f"Streaming chat endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/commands', methods=['GET'])
def get_available_commands():
    """Get list of available commands"""
    commands = {
        'help': 'Show available commands',
        'about': 'Information about Siva',
        'skills': 'Technical skills and expertise',
        'projects': 'Featured projects and work',
        'certs': 'Certifications and credentials',
        'contact': 'Contact information',
        'clear': 'Clear terminal screen'
    }
    
    return jsonify({
        'commands': commands,
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# For Vercel, we need this
if __name__ == '__main__':
    app.run(debug=False)

# Vercel serverless function handler
def handler(request, response):
    return app(request, response)
