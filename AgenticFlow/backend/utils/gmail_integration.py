"""
Gmail Integration Module

This module provides functionality to interact with Gmail API using OAuth2 authentication.
It handles token management, email fetching, and sending replies.
"""
import os
import base64
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from database.database import get_db
from database.models import Token
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

# OAuth2 scopes for Gmail API
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]

class GmailIntegration:
    """Handles Gmail API integration including OAuth2 flow and email operations."""
    
    def __init__(self, user_id: int):
        """Initialize with user ID for token management."""
        self.user_id = user_id
        self.creds = None
        self.service = None
    
    def get_authorization_url(self) -> str:
        """Generate authorization URL for OAuth2 flow."""
        flow = InstalledAppFlow.from_client_config(
            settings.GOOGLE_CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
        
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return auth_url
    
    def save_credentials(self, code: str) -> None:
        """Exchange authorization code for tokens and save them."""
        flow = InstalledAppFlow.from_client_config(
            settings.GOOGLE_CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=settings.GOOGLE_REDICT_URI
        )
        
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        # Save tokens to database
        db = next(get_db())
        token_data = {
            'user_id': self.user_id,
            'provider': 'google',
            'access_token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': ' '.join(creds.scopes) if creds.scopes else '',
            'expires_at': creds.expiry.isoformat() if creds.expiry else None
        }
        
        # Update or create token
        token = db.query(Token).filter(
            Token.user_id == self.user_id,
            Token.provider == 'google'
        ).first()
        
        if token:
            for key, value in token_data.items():
                setattr(token, key, value)
        else:
            token = Token(**token_data)
            db.add(token)
        
        db.commit()
        db.refresh(token)
    
    def _get_credentials(self) -> bool:
        """Retrieve and refresh credentials from database."""
        db = next(get_db())
        token = db.query(Token).filter(
            Token.user_id == self.user_id,
            Token.provider == 'google'
        ).first()
        
        if not token:
            return False
            
        creds = Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri=token.token_uri,
            client_id=token.client_id,
            client_secret=token.client_secret,
            scopes=token.scopes.split() if token.scopes else None
        )
        
        # Refresh token if expired
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                
                # Update token in database
                token.access_token = creds.token
                token.expires_at = creds.expiry.isoformat() if creds.expiry else None
                db.commit()
                
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                return False
        
        self.creds = creds
        return True
    
    def get_service(self):
        """Get Gmail API service instance."""
        if not self.creds and not self._get_credentials():
            raise Exception("Not authenticated with Gmail")
            
        if not self.service:
            self.service = build('gmail', 'v1', credentials=self.creds)
            
        return self.service
    
    def fetch_emails(self, max_results: int = 10, query: str = '') -> List[Dict[str, Any]]:
        """Fetch emails from Gmail."""
        try:
            service = self.get_service()
            results = service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Parse email headers
                headers = {h['name'].lower(): h['value'] for h in msg_data.get('payload', {}).get('headers', [])}
                
                # Get message body
                body = ''
                if 'parts' in msg_data['payload']:
                    for part in msg_data['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body'].get('data', '')).decode('utf-8')
                            break
                        elif part['mimeType'] == 'text/html':
                            body = base64.urlsafe_b64decode(part['body'].get('data', '')).decode('utf-8')
                
                emails.append({
                    'id': msg_data['id'],
                    'thread_id': msg_data.get('threadId'),
                    'subject': headers.get('subject', '(No subject)'),
                    'from': headers.get('from', ''),
                    'to': headers.get('to', ''),
                    'date': headers.get('date', ''),
                    'body': body,
                    'snippet': msg_data.get('snippet', ''),
                    'labels': msg_data.get('labelIds', [])
                })
                
            return emails
            
        except HttpError as error:
            logger.error(f"Error fetching emails: {error}")
            raise Exception(f"Failed to fetch emails: {error}")
    
    def send_reply(self, to: str, subject: str, body: str, thread_id: str = None) -> Dict[str, Any]:
        """Send a reply email."""
        try:
            service = self.get_service()
            
            # Create email message
            message = self._create_message(to, subject, body, thread_id)
            
            # Send message
            sent_message = service.users().messages().send(
                userId='me',
                body={
                    'raw': message,
                    'threadId': thread_id
                } if thread_id else {'raw': message}
            ).execute()
            
            return {
                'message_id': sent_message['id'],
                'thread_id': sent_message.get('threadId'),
                'status': 'sent'
            }
            
        except HttpError as error:
            logger.error(f"Error sending email: {error}")
            raise Exception(f"Failed to send email: {error}")
    
    def _create_message(self, to: str, subject: str, body: str, thread_id: str = None) -> str:
        """Create a base64 encoded email message."""
        import email
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        # Add body
        message.attach(MIMEText(body, 'plain'))
        
        # Add thread ID if replying
        if thread_id:
            message['In-Reply-To'] = thread_id
            message['References'] = thread_id
        
        # Return base64 encoded message
        return base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    def get_email_thread(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a thread."""
        try:
            service = self.get_service()
            thread = service.users().threads().get(
                userId='me',
                id=thread_id,
                format='full'
            ).execute()
            
            messages = []
            for msg in thread.get('messages', []):
                headers = {h['name'].lower(): h['value'] for h in msg.get('payload', {}).get('headers', [])}
                messages.append({
                    'id': msg['id'],
                    'thread_id': thread_id,
                    'subject': headers.get('subject', '(No subject)'),
                    'from': headers.get('from', ''),
                    'to': headers.get('to', ''),
                    'date': headers.get('date', ''),
                    'snippet': msg.get('snippet', '')
                })
                
            return messages
            
        except HttpError as error:
            logger.error(f"Error fetching thread {thread_id}: {error}")
            raise Exception(f"Failed to fetch thread: {error}")
