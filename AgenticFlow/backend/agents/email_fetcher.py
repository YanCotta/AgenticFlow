"""Email Fetcher Agent

This agent is responsible for fetching emails from the user's Gmail account using the Gmail API.
"""
import logging
import base64
import email
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the token.json file
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

class EmailFetcher:
    """Agent responsible for fetching emails from Gmail accounts."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the EmailFetcher agent.
        
        Args:
            config: Configuration dictionary for the agent.
        """
        self.config = config or {}
        self.initialized = False
        self.service = None
    
    async def initialize(self) -> None:
        """Initialize the Gmail API service."""
        if self.initialized:
            return
            
        logger.info("Initializing Gmail API service")
        
        creds = None
        token_path = self.config.get('token_path', 'token.json')
        credentials_path = self.config.get('credentials_path', 'credentials.json')
        
        # Load existing credentials if they exist
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # If no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        self.initialized = True
    
    async def fetch_emails(self, limit: int = 10, unread_only: bool = True) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail.
        
        Args:
            limit: Maximum number of emails to fetch.
            unread_only: Whether to fetch only unread emails.
            
        Returns:
            List of email data dictionaries.
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Call the Gmail API
            query = 'is:unread' if unread_only else ''
            results = self.service.users().messages().list(
                userId='me',
                maxResults=limit,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = await self._get_message(msg['id'])
                if email_data:
                    emails.append(email_data)
                    
                    # Mark as read after processing
                    if unread_only:
                        await self.mark_as_read(msg['id'])
            
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    async def _get_message(self, msg_id: str) -> Dict[str, Any]:
        """Get a specific message by ID.
        
        Args:
            msg_id: The ID of the message to retrieve.
            
        Returns:
            Dictionary containing message data.
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='raw'
            ).execute()
            
            # Decode the raw email
            msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
            mime_msg = email.message_from_bytes(msg_str)
            
            # Extract email data
            email_data = {
                'id': msg_id,
                'thread_id': message.get('threadId'),
                'subject': self._get_header(mime_msg, 'Subject'),
                'from': self._get_header(mime_msg, 'From'),
                'to': self._get_header(mime_msg, 'To'),
                'date': self._get_header(mime_msg, 'Date'),
                'body': self._get_email_body(mime_msg),
                'labels': message.get('labelIds', []),
                'snippet': message.get('snippet', '')
            }
            
            return email_data
            
        except Exception as e:
            logger.error(f"Error getting message {msg_id}: {e}")
            return {}
    
    def _get_header(self, msg, header_name: str) -> str:
        """Get a header from an email message."""
        header = ''
        if msg[header_name]:
            header = email.header.decode_header(msg[header_name])[0][0]
            if isinstance(header, bytes):
                header = header.decode('utf-8', errors='ignore')
        return header or ''
    
    def _get_email_body(self, msg) -> str:
        """Extract the email body from a message."""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except Exception as e:
                        logger.error(f"Error decoding email body: {e}")
                        return ""
        else:
            try:
                return msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except Exception as e:
                logger.error(f"Error decoding email body: {e}")
                return ""
        return ""
    
    async def mark_as_read(self, msg_id: str) -> bool:
        """Mark an email as read.
        
        Args:
            msg_id: The ID of the message to mark as read.
            
        Returns:
            True if successful, False otherwise.
        """
        if not self.initialized:
            await self.initialize()
            
        try:
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error marking email {msg_id} as read: {e}")
            return False


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        fetcher = EmailFetcher()
        emails = await fetcher.fetch_emails(5)
        print(f"Fetched {len(emails)} emails")
    
    asyncio.run(main())
