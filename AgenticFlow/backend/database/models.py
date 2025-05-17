"""
Database Models for AgenticFlow

This module contains SQLAlchemy models for the AgenticFlow application.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class EmailSummaries(db.Model):
    """Model for storing email summaries"""
    __tablename__ = 'email_summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PendingReplies(db.Model):
    """Model for storing pending email replies"""
    __tablename__ = 'pending_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.String(255), nullable=False)
    reply_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class NewsletterContents(db.Model):
    """Model for storing newsletter contents"""
    __tablename__ = 'newsletter_contents'
    
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class SocialPosts(db.Model):
    """Model for social media posts"""
    __tablename__ = 'social_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)  # 'twitter', 'linkedin', etc.
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='draft')  # draft, scheduled, posted
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Prompts(db.Model):
    """Model for storing agent prompts"""
    __tablename__ = 'prompts'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_name = db.Column(db.String(100), nullable=False)
    prompt_text = db.Column(db.Text, nullable=False)

class Users(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_auth_token(self):
        return create_access_token(identity=self.username)

class Tokens(db.Model):
    """Model for storing OAuth tokens"""
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service = db.Column(db.String(50), nullable=False)  # 'gmail', 'linkedin', 'twitter'
    access_token = db.Column(db.String(512), nullable=False)
    refresh_token = db.Column(db.String(512))
    expires_at = db.Column(db.DateTime)
    
    user = db.relationship('Users', backref=db.backref('tokens', lazy=True))
