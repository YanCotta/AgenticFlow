"""
Main FastAPI application for AgenticFlow.

This module serves as the entry point for the AgenticFlow API.
"""
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import routers
from api.auth_endpoints import router as auth_router
from api.email_endpoints import router as email_router
from api.social_endpoints import router as social_router
from api.newsletter_endpoints import router as newsletter_router

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def create_app():
    """Create and configure the FastAPI app"""
    app = FastAPI(
        title="AgenticFlow API",
        description="API for AgenticFlow - Automated Email and Social Media Management",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
    app.include_router(email_router, prefix="/api/emails", tags=["emails"])
    app.include_router(social_router, prefix="/api/social", tags=["social"])
    app.include_router(newsletter_router, prefix="/api/newsletters", tags=["newsletters"])
    
    # Health check endpoint
    @app.get("/api/health", tags=["health"])
    async def health_check():
        return {
            "status": "ok",
            "message": "AgenticFlow API is running",
            "version": "1.0.0"
        }
    
    return app

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
