"""
Email API Endpoints

This module contains FastAPI endpoints for email-related operations.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Email, EmailAnalysis as DBAnalysis, User
from agents.email_fetcher import EmailFetcher
from agents.email_analyzer import EmailAnalyzer
from agents.reply_generator import ReplyGenerator
from .auth_endpoints import get_current_active_user
from config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/emails", tags=["emails"])

# Initialize agents
email_fetcher = EmailFetcher()
email_analyzer = EmailAnalyzer(api_key=settings.OPENAI_API_KEY)
reply_generator = ReplyGenerator(api_key=settings.OPENAI_API_KEY)

# Constants
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Request/Response Models
class EmailBase(BaseModel):
    """Base email model."""
    subject: str
    from_email: EmailStr
    to: List[EmailStr]
    cc: List[EmailStr] = []
    bcc: List[EmailStr] = []
    body: str
    html_body: Optional[str] = None
    received_at: datetime
    labels: List[str] = []
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None

class EmailCreate(EmailBase):
    """Email creation model."""
    pass

class EmailResponse(EmailBase):
    """Email response model."""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class EmailListResponse(BaseModel):
    """Email list response model."""
    emails: List[EmailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class EmailAnalysis(BaseModel):
    """Email analysis model."""
    email_id: str
    intent: str
    categories: List[str]
    priority: str
    requires_response: bool
    sentiment: str
    key_entities: List[Dict[str, Any]]
    summary: str
    action_items: List[Dict[str, Any]] = []
    confidence: float
    created_at: datetime
    
    class Config:
        orm_mode = True

class DraftReply(BaseModel):
    """Draft reply model."""
    email_id: str
    subject: str
    body: str
    tone: str
    is_html: bool = True
    context_used: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SendReplyRequest(BaseModel):
    """Send reply request model."""
    email_id: str
    draft_reply: Dict[str, Any]
    schedule_send: Optional[datetime] = None

class EmailSearchQuery(BaseModel):
    """Email search query model."""
    query: Optional[str] = None
    from_email: Optional[EmailStr] = None
    to_email: Optional[EmailStr] = None
    subject: Optional[str] = None
    label: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    has_attachments: Optional[bool] = None
    is_read: Optional[bool] = None
    is_starred: Optional[bool] = None
    
    class Config:
        schema_extra = {
            "example": {
                "query": "important project",
                "from_email": "sender@example.com",
                "start_date": "2023-01-01T00:00:00Z",
                "end_date": "2023-12-31T23:59:59Z"
            }
        }

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

# Helper functions
async def get_email_or_404(db: Session, email_id: str) -> Email:
    """Get an email by ID or raise 404 if not found."""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email with ID {email_id} not found"
        )
    return email

# Routes
@router.get("/", response_model=EmailListResponse)
async def list_emails(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE, description="Items per page"),
    query: Optional[str] = Query(None, description="Search query"),
    label: Optional[str] = Query(None, description="Filter by label"),
    unread: Optional[bool] = Query(None, description="Filter by read status"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
):
    """
    List emails with pagination and filtering.
    
    Args:
        db: Database session
        current_user: Authenticated user
        page: Page number (1-based)
        page_size: Number of items per page
        query: Search query string
        label: Filter by label
        unread: Filter by read status
        start_date: Filter by start date
        end_date: Filter by end date
        
    Returns:
        Paginated list of emails
    """
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Build base query
        db_query = db.query(Email).filter(Email.user_id == current_user.id)
        
        # Apply filters
        if query:
            db_query = db_query.filter(
                (Email.subject.ilike(f"%{query}%")) |
                (Email.body.ilike(f"%{query}%")) |
                (Email.from_email.ilike(f"%{query}%"))
            )
            
        if label:
            db_query = db_query.filter(Email.labels.any(label))
            
        if unread is not None:
            db_query = db_query.filter(Email.is_read == (not unread))
            
        if start_date:
            db_query = db_query.filter(Email.received_at >= start_date)
            
        if end_date:
            db_query = db_query.filter(Email.received_at <= end_date)
        
        # Get total count
        total = db_query.count()
        
        # Apply pagination and ordering
        emails = (
            db_query
            .order_by(Email.received_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return EmailListResponse(
            emails=emails,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error listing emails: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving emails"
        )

@router.post("/search", response_model=EmailListResponse)
async def search_emails(
    search_query: EmailSearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, le=MAX_PAGE_SIZE, description="Items per page"),
):
    """
    Search emails with advanced query parameters.
    
    Args:
        search_query: Search query parameters
        db: Database session
        current_user: Authenticated user
        page: Page number (1-based)
        page_size: Number of items per page
        
    Returns:
        Paginated list of matching emails
    """
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Build base query
        db_query = db.query(Email).filter(Email.user_id == current_user.id)
        
        # Apply filters from search query
        if search_query.query:
            db_query = db_query.filter(
                (Email.subject.ilike(f"%{search_query.query}%")) |
                (Email.body.ilike(f"%{search_query.query}%")) |
                (Email.from_email.ilike(f"%{search_query.query}%"))
            )
            
        if search_query.from_email:
            db_query = db_query.filter(Email.from_email == search_query.from_email)
            
        if search_query.to_email:
            db_query = db_query.filter(Email.to.any(search_query.to_email))
            
        if search_query.subject:
            db_query = db_query.filter(Email.subject.ilike(f"%{search_query.subject}%"))
            
        if search_query.label:
            db_query = db_query.filter(Email.labels.any(search_query.label))
            
        if search_query.start_date:
            db_query = db_query.filter(Email.received_at >= search_query.start_date)
            
        if search_query.end_date:
            db_query = db_query.filter(Email.received_at <= search_query.end_date)
            
        if search_query.has_attachments is not None:
            db_query = db_query.filter(Email.has_attachments == search_query.has_attachments)
            
        if search_query.is_read is not None:
            db_query = db_query.filter(Email.is_read == search_query.is_read)
            
        if search_query.is_starred is not None:
            db_query = db_query.filter(Email.is_starred == search_query.is_starred)
        
        # Get total count
        total = db_query.count()
        
        # Apply pagination and ordering
        emails = (
            db_query
            .order_by(Email.received_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        return EmailListResponse(
            emails=emails,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error searching emails: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching emails"
        )

@router.get("/{email_id}", response_model=Email)
async def get_email(
    email_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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
