"""
Email API Endpoints

This module contains FastAPI endpoints for email-related operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, HttpUrl
from datetime import datetime
import logging

# Import agents
from agents.email_fetcher import EmailFetcher
from agents.email_analyzer import EmailAnalyzer
from agents.reply_generator import ReplyGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/emails", tags=["emails"])

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Initialize agents
email_fetcher = EmailFetcher()
email_analyzer = EmailAnalyzer()
reply_generator = ReplyGenerator()

# Models
class Email(BaseModel):
    """Email model."""
    id: str
    subject: str
    from_email: EmailStr
    to: List[EmailStr]
    cc: List[EmailStr] = []
    bcc: List[EmailStr] = []
    body: str
    html_body: Optional[str] = None
    received_at: datetime
    labels: List[str] = []
    attachments: List[Dict[str, Any]] = []
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None

class EmailListResponse(BaseModel):
    """Response model for listing emails."""
    emails: List[Email]
    total: int
    page: int
    page_size: int

class EmailAnalysis(BaseModel):
    """Email analysis result model."""
    email_id: str
    intent: str
    categories: List[str]
    priority: str
    requires_response: bool
    sentiment: str
    key_entities: List[Dict[str, Any]]
    summary: str
    action_items: List[Dict[str, Any]] = []

class DraftReply(BaseModel):
    """Draft reply model."""
    email_id: str
    subject: str
    body: str
    tone: str
    is_html: bool = True
    context_used: List[str] = []

class SendReplyRequest(BaseModel):
    """Request model for sending a reply."""
    email_id: str
    draft_reply: Dict[str, Any]
    schedule_send: Optional[datetime] = None

# Background tasks
async def process_email_background(email_id: str):
    """Background task to process an email."""
    try:
        # Fetch the full email
        email = await email_fetcher.fetch_email(email_id)
        
        # Analyze the email
        analysis = await email_analyzer.analyze_email(email)
        
        # Store the analysis (in a real app, this would be saved to a database)
        logger.info(f"Processed email {email_id}: {analysis}")
        
    except Exception as e:
        logger.error(f"Error processing email {email_id}: {str(e)}")

# Routes
@router.get("/", response_model=EmailListResponse)
async def list_emails(
    page: int = 1,
    page_size: int = 20,
    label: Optional[str] = None,
    unread: Optional[bool] = None,
    query: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """List emails with optional filtering and pagination."""
    try:
        # In a real app, this would query the database with the filters
        emails = await email_fetcher.fetch_emails(limit=page_size)
        
        return EmailListResponse(
            emails=emails,
            total=len(emails),  # In a real app, this would be the total count
            page=page,
            page_size=page_size
        )
    except Exception as e:
        logger.error(f"Error listing emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve emails"
        )

@router.get("/{email_id}", response_model=Email)
async def get_email(
    email_id: str,
    token: str = Depends(oauth2_scheme)
):
    """Get a specific email by ID."""
    try:
        email = await email_fetcher.fetch_email(email_id)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        return email
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching email {email_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve email"
        )

@router.get("/{email_id}/analyze", response_model=EmailAnalysis)
async def analyze_email(
    email_id: str,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """Analyze an email's content and extract key information."""
    try:
        # Fetch the email
        email = await email_fetcher.fetch_email(email_id)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        
        # Analyze the email
        analysis = await email_analyzer.analyze_email(email)
        
        # Extract action items in the background
        background_tasks.add_task(
            email_analyzer.extract_action_items,
            email
        )
        
        return EmailAnalysis(
            email_id=email_id,
            **analysis
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing email {email_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not analyze email"
        )

@router.post("/{email_id}/draft-reply", response_model=DraftReply)
async def draft_reply(
    email_id: str,
    tone: str = "professional",
    length: str = "medium",
    token: str = Depends(oauth2_scheme)
):
    """Generate a draft reply to an email."""
    try:
        # Fetch the email
        email = await email_fetcher.fetch_email(email_id)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        
        # Generate the reply
        reply = await reply_generator.generate_reply(
            email_data=email,
            tone=tone,
            length=length
        )
        
        return DraftReply(
            email_id=email_id,
            subject=reply["subject"],
            body=reply["body"],
            tone=tone,
            context_used=reply.get("context_used", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating draft reply for email {email_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not generate draft reply"
        )

@router.post("/{email_id}/send-reply")
async def send_reply(
    email_id: str,
    request: SendReplyRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """Send a reply to an email."""
    try:
        # In a real app, this would send the email using an email service
        logger.info(f"Sending reply to email {email_id}")
        
        # Schedule the email to be sent later if requested
        if request.schedule_send:
            logger.info(f"Email scheduled to be sent at {request.schedule_send}")
            # In a real app, you would use a task queue like Celery or RQ
            background_tasks.add_task(
                send_scheduled_email,
                email_id=email_id,
                draft_reply=request.draft_reply,
                send_at=request.schedule_send
            )
            return {"status": "scheduled", "scheduled_at": request.schedule_send}
        
        # Send immediately
        logger.info(f"Sending email immediately: {request.draft_reply}")
        return {"status": "sent", "message_id": f"mock-{email_id}-{datetime.utcnow().timestamp()}"}
        
    except Exception as e:
        logger.error(f"Error sending reply to email {email_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not send reply"
        )

# Helper functions
async def send_scheduled_email(email_id: str, draft_reply: Dict[str, Any], send_at: datetime):
    """Helper function to send a scheduled email."""
    # In a real app, this would be handled by a task queue
    import time
    from datetime import datetime, timezone
    
    # Calculate delay in seconds
    now = datetime.now(timezone.utc)
    delay = (send_at - now).total_seconds()
    
    if delay > 0:
        logger.info(f"Waiting {delay} seconds to send email {email_id}")
        time.sleep(delay)
    
    # Send the email
    logger.info(f"Sending scheduled email {email_id}: {draft_reply}")
    # Actual email sending logic would go here
