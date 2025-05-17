"""
Main FastAPI application for AgenticFlow.

This module serves as the entry point for the AgenticFlow API.
"""
import os
import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

# Import routers
from api.auth_endpoints import router as auth_router
from api.email_endpoints import router as email_router
from api.social_endpoints import router as social_router

# Import orchestrator
from agents.orchestrator import EmailOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AgenticFlow API",
    description="API for the AgenticFlow multi-agent email processing system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(email_router)
app.include_router(social_router)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Initialize orchestrator
orchestrator = EmailOrchestrator()

# Models
class ProcessEmailRequest(BaseModel):
    """Request model for processing an email."""
    email_data: Dict[str, Any]
    process_newsletter: bool = True
    generate_reply: bool = True
    post_to_social: bool = False

class ProcessEmailResponse(BaseModel):
    """Response model for the process email endpoint."""
    status: str
    result: Dict[str, Any]
    timestamp: str

# Routes
@app.get("/")
async def root():
    """Root endpoint that provides API information."""
    return {
        "name": "AgenticFlow API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "running"
    }

@app.post("/process-email", response_model=ProcessEmailResponse)
async def process_email(
    request: ProcessEmailRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    Process an email through the agent pipeline.
    
    This endpoint takes an email and processes it through the following steps:
    1. Analyze the email content
    2. If it's a newsletter, extract content and optionally post to social media
    3. If it needs a reply, generate a draft response
    """
    try:
        # Process the email using the orchestrator
        result = await orchestrator.process_email(request.email_data)
        
        return ProcessEmailResponse(
            status="success",
            result=result,
            timestamp=result.get("timestamp", "")
        )
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing email: {str(e)}"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services when the application starts."""
    logger.info("Starting up AgenticFlow API...")
    try:
        await orchestrator.initialize()
        logger.info("AgenticFlow API started successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when the application shuts down."""
    logger.info("Shutting down AgenticFlow API...")

# Run the application with uvicorn directly for development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
