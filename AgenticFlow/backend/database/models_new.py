"""
Database Models for AgenticFlow

This module contains SQLAlchemy models for the AgenticFlow application.
"""
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Index, ARRAY
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    """User model for authentication and user data."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    preferences = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    emails = relationship('Email', back_populates='user', cascade='all, delete-orphan')
    tokens = relationship('Token', back_populates='user', cascade='all, delete-orphan')
    social_posts = relationship('SocialPost', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password: str) -> None:
        """Set the user's password."""
        self.hashed_password = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.hashed_password, password)
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"

class Token(Base):
    """OAuth tokens for external services."""
    __tablename__ = 'tokens'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    service = Column(String(50), nullable=False)  # 'gmail', 'outlook', 'twitter', 'linkedin', etc.
    access_token = Column(String(1024), nullable=False)
    refresh_token = Column(String(1024))
    token_type = Column(String(50))
    expires_at = Column(DateTime)
    scopes = Column(ARRAY(String))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='tokens')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary."""
        return {
            'id': self.id,
            'service': self.service,
            'token_type': self.token_type,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'scopes': self.scopes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"<Token {self.service} for user {self.user_id}>"

class Email(Base):
    """Email message model."""
    __tablename__ = 'emails'
    
    id = Column(String(255), primary_key=True)  # Message ID from email provider
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    thread_id = Column(String(255), index=True)
    in_reply_to = Column(String(255), index=True)
    subject = Column(String(1024))
    from_email = Column(String(255), nullable=False, index=True)
    to = Column(ARRAY(String), default=[], index=True)
    cc = Column(ARRAY(String), default=[])
    bcc = Column(ARRAY(String), default=[])
    body = Column(Text)
    html_body = Column(Text)
    snippet = Column(String(1000))
    labels = Column(ARRAY(String), default=[], index=True)
    is_read = Column(Boolean, default=False, index=True)
    is_starred = Column(Boolean, default=False, index=True)
    is_important = Column(Boolean, default=False, index=True)
    has_attachments = Column(Boolean, default=False)
    received_at = Column(DateTime, index=True)
    read_at = Column(DateTime)
    replied_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='emails')
    attachments = relationship('Attachment', back_populates='email', cascade='all, delete-orphan')
    analyses = relationship('EmailAnalysis', back_populates='email', cascade='all, delete-orphan')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert email to dictionary."""
        return {
            'id': self.id,
            'thread_id': self.thread_id,
            'in_reply_to': self.in_reply_to,
            'subject': self.subject,
            'from_email': self.from_email,
            'to': self.to,
            'cc': self.cc,
            'bcc': self.bcc,
            'snippet': self.snippet,
            'labels': self.labels,
            'is_read': self.is_read,
            'is_starred': self.is_starred,
            'is_important': self.is_important,
            'has_attachments': self.has_attachments,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'replied_at': self.replied_at.isoformat() if self.replied_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'attachments': [a.to_dict() for a in self.attachments]
        }
    
    def __repr__(self) -> str:
        return f"<Email {self.id}: {self.subject}>"

class Attachment(Base):
    """Email attachment model."""
    __tablename__ = 'attachments'
    
    id = Column(String(255), primary_key=True)  # Attachment ID from email
    email_id = Column(String(255), ForeignKey('emails.id', ondelete='CASCADE'), nullable=False)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(255))
    size = Column(Integer)  # Size in bytes
    content_id = Column(String(255))  # For inline images in HTML emails
    download_url = Column(String(1024))  # URL to download the attachment
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    email = relationship('Email', back_populates='attachments')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert attachment to dictionary."""
        return {
            'id': self.id,
            'filename': self.filename,
            'content_type': self.content_type,
            'size': self.size,
            'download_url': self.download_url,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"<Attachment {self.filename} ({self.content_type})>"

class EmailAnalysis(Base):
    """Analysis results for an email."""
    __tablename__ = 'email_analyses'
    
    id = Column(Integer, primary_key=True)
    email_id = Column(String(255), ForeignKey('emails.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    status = Column(String(20), default='pending', index=True)  # pending, processing, completed, failed
    error = Column(Text)
    
    # Analysis results
    intent = Column(String(100))
    categories = Column(ARRAY(String), default=[])
    priority = Column(String(20))  # low, normal, high, urgent
    requires_response = Column(Boolean, default=False)
    sentiment = Column(String(20))  # positive, neutral, negative
    key_entities = Column(JSONB)  # List of entities with type and value
    summary = Column(Text)
    action_items = Column(JSONB)  # List of action items
    confidence = Column(Integer)  # 0-100 confidence score
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    email = relationship('Email', back_populates='analyses')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary."""
        return {
            'id': self.id,
            'email_id': self.email_id,
            'status': self.status,
            'error': self.error,
            'intent': self.intent,
            'categories': self.categories,
            'priority': self.priority,
            'requires_response': self.requires_response,
            'sentiment': self.sentiment,
            'key_entities': self.key_entities,
            'summary': self.summary,
            'action_items': self.action_items,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self) -> str:
        return f"<EmailAnalysis {self.id} for email {self.email_id} ({self.status})>"

class SocialPost(Base):
    """Social media post model."""
    __tablename__ = 'social_posts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)  # 'twitter', 'linkedin', etc.
    content = Column(Text, nullable=False)
    status = Column(String(20), default='draft', index=True)  # draft, scheduled, posted, failed
    scheduled_for = Column(DateTime, index=True)
    posted_at = Column(DateTime)
    post_id = Column(String(255))  # ID from the social platform
    error = Column(Text)
    metadata = Column(JSONB)  # Additional platform-specific data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='social_posts')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert social post to dictionary."""
        return {
            'id': self.id,
            'platform': self.platform,
            'content': self.content,
            'status': self.status,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'post_id': self.post_id,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"<SocialPost {self.id} on {self.platform} ({self.status})>"

# Add indexes for better query performance
Index('idx_emails_user_id', Email.user_id)
Index('idx_emails_thread_id', Email.thread_id)
Index('idx_emails_received_at', Email.received_at.desc())
Index('idx_email_analyses_status', EmailAnalysis.status)
Index('idx_social_posts_user_status', SocialPost.user_id, SocialPost.status)
Index('idx_social_posts_scheduled', SocialPost.scheduled_for, SocialPost.status)
Index('idx_tokens_user_service', Token.user_id, Token.service, unique=True)
