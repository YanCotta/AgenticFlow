"""
Database initialization for AgenticFlow

This module handles database connection and initialization.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

db = SQLAlchemy()

def init_app(app):
    """Initialize the database with the Flask app"""
    # Configure database
    db_url = os.getenv('DB_URL')
    if not db_url:
        # Default to SQLite if DB_URL is not set
        db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'agenticflow.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        db_url = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

def get_db():
    """Get a database session"""
    return db.session
