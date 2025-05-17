"""
Database Models

This module contains SQLAlchemy models for the AgenticFlow application.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, ForeignKey, JSON, Text,
    Table, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Create base class for models
Base = declarative_base()

# Association tables
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# Models
class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    emails = relationship('Email', back_populates='user')
    social_posts = relationship('SocialPost', back_populates='user')
    
    def __repr__(self):
        return f"<User {self.email}>"


class Role(Base):
    """Role model for role-based access control."""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    # Relationships
    users = relationship('User', secondary=user_roles, back_populates='roles')
    
    def __repr__(self):
        return f"<Role {self.name}>"


class Email(Base):
    """Email model for storing processed emails."""
    __tablename__ = 'emails'
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, index=True, nullable=False)
    thread_id = Column(String(255), index=True, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    from_email = Column(String(255), nullable=False)
    to_emails = Column(JSON, default=list)
    cc_emails = Column(JSON, default=list)
    bcc_emails = Column(JSON, default=list)
    subject = Column(String(255), nullable=True)
    body_plain = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    received_at = Column(DateTime, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    is_processed = Column(Boolean, default=False)
    is_newsletter = Column(Boolean, default=False)
    requires_reply = Column(Boolean, default=False)
    metadata_ = Column('metadata', JSON, default=dict)
    
    # Relationships
    user = relationship('User', back_populates='emails')
    email_analysis = relationship('EmailAnalysis', back_populates='email', uselist=False)
    
    def __repr__(self):
        return f"<Email {self.message_id}>"


class EmailAnalysis(Base):
    """Analysis results for processed emails."""
    __tablename__ = 'email_analyses'
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey('emails.id'), unique=True, nullable=False)
    intent = Column(String(100), nullable=True)
    sentiment = Column(String(50), nullable=True)
    categories = Column(JSON, default=list)
    key_phrases = Column(JSON, default=list)
    entities = Column(JSON, default=list)
    summary = Column(Text, nullable=True)
    confidence = Column(Integer, nullable=True)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    email = relationship('Email', back_populates='email_analysis')
    
    def __repr__(self):
        return f"<EmailAnalysis for Email {self.email_id}>"


class SocialPost(Base):
    """Social media posts created by the system."""
    __tablename__ = 'social_posts'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    platform = Column(String(50), nullable=False)  # 'twitter', 'linkedin', etc.
    post_id = Column(String(255), nullable=True)  # ID from the social platform
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, default=list)
    metadata_ = Column('metadata', JSON, default=dict)
    status = Column(String(50), default='draft')  # draft, scheduled, posted, failed
    scheduled_time = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='social_posts')
    
    __table_args__ = (
        UniqueConstraint('platform', 'post_id', name='uq_platform_post_id'),
    )
    
    def __repr__(self):
        return f"<SocialPost {self.platform} {self.id}>"


class EmailReply(Base):
    """Generated email replies."""
    __tablename__ = 'email_replies'
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    content = Column(Text, nullable=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    email = relationship('Email')
    
    def __repr__(self):
        return f"<EmailReply for Email {self.email_id}>"


class SystemLog(Base):
    """System logs for auditing and debugging."""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # info, warning, error, etc.
    module = Column(String(100), nullable=True)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<SystemLog {self.level} {self.message[:50]}>"


class APIAccessLog(Base):
    """API access logs for monitoring and analytics."""
    __tablename__ = 'api_access_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    method = Column(String(10), nullable=False)
    endpoint = Column(String(255), nullable=False)
    status_code = Column(Integer, nullable=False)
    client_ip = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    response_time = Column(Integer, nullable=True)  # in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship('User')
    
    def __repr__(self):
        return f"<APIAccessLog {self.method} {self.endpoint} {self.status_code}>"
