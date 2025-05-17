"""
Main Flask application for AgenticFlow.

This module serves as the entry point for the AgenticFlow API.
"""
import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database models first to avoid circular imports
from database import models

# Import blueprints
from api.auth_endpoints import auth_bp
from api.email_endpoints import email_bp
from api.social_endpoints import social_bp

def create_app():
    """Create and configure the Flask app"""
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",  # In production, replace with specific origins
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize database
    from database.init_db import init_app
    init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(email_bp, url_prefix='/api/emails')
    app.register_blueprint(social_bp, url_prefix='/api/social')
    
    # Simple route for health check
    @app.route('/')
    def index():
        return jsonify({
            'status': 'ok',
            'message': 'AgenticFlow API is running',
            'version': '1.0.0'
        })
    
    return app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
