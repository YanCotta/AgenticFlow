"""
Main FastAPI application for AgenticFlow.

This module serves as the entry point for the AgenticFlow API.
"""
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import structlog
from structlog.contextvars import bind_contextvars, unbind_contextvars

from config import settings
from database import init_db, get_db, SessionLocal
from database.models import User

# Configure logging
from utils.logging import configure_logging

# Initialize logging
configure_logging()
logger = structlog.get_logger(__name__)

# Initialize Sentry if DSN is configured
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENV,
        traces_sample_rate=1.0,
    )

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Import routers after database initialization to avoid circular imports
from api.auth_endpoints import router as auth_router
from api.email_endpoints import router as email_router
from api.social_endpoints import router as social_router
from api.newsletter_endpoints import router as newsletter_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup: Initialize database
    logger.info("Starting up...")
    init_db()
    
    # Create initial admin user if it doesn't exist
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.FIRST_SUPERUSER).first()
        if not admin:
            admin = User(
                email=settings.FIRST_SUPERUSER,
                full_name="Admin",
                is_superuser=True,
                is_active=True,
            )
            admin.set_password(settings.FIRST_SUPERUSER_PASSWORD)
            db.add(admin)
            db.commit()
            logger.info("Created initial admin user", email=settings.FIRST_SUPERUSER)
    except Exception as e:
        logger.error("Error creating admin user", error=str(e))
        db.rollback()
    finally:
        db.close()
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

def create_app() -> FastAPI:
    """Create and configure the FastAPI app"""
    app = FastAPI(
        title="AgenticFlow API",
        description="API for AgenticFlow - Automated Email and Social Media Management",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add Sentry middleware if DSN is configured
    if settings.SENTRY_DSN:
        app.add_middleware(SentryAsgiMiddleware)
    
    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Include routers
    app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
    app.include_router(email_router, prefix="/api/emails", tags=["emails"])
    app.include_router(social_router, prefix="/api/social", tags=["social"])
    app.include_router(newsletter_router, prefix="/api/newsletters", tags=["newsletters"])
    
    # Add middleware for request logging and context binding
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        # Bind request context for logging
        bind_contextvars(
            request_id=request.headers.get("x-request-id"),
            user_agent=request.headers.get("user-agent"),
            ip=get_remote_address(request),
        )
        
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log the request
        logger.info(
            "Request processed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=f"{process_time:.4f}s",
        )
        
        # Add headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request.headers.get("x-request-id", "")
        
        # Clean up context
        unbind_contextvars("request_id", "user_agent", "ip")
        
        return response
    
    # Exception handlers
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
    
    # Health check endpoint
    @app.get("/api/health", tags=["health"])
    @limiter.limit("10/minute")
    async def health_check(request: Request):
        """Health check endpoint"""
        return {
            "status": "ok",
            "version": "1.0.0",
            "environment": settings.ENV,
            "timestamp": time.time(),
        }
    
    return app

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
