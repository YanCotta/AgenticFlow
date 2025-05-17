from flask import Flask, jsonify, request
from agents.orchestrator import EmailOrchestrator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "Multi-Agentic AI System is running"})

@app.route('/process_email', methods=['POST'])
def process_email():
    try:
        data = request.get_json()
        email_content = data.get('email_content')
        
        if not email_content:
            return jsonify({"error": "No email content provided"}), 400
        
        # Initialize and run the email orchestrator
        orchestrator = EmailOrchestrator()
        result = orchestrator.process_email(email_content)
        
        return jsonify({"result": result})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
