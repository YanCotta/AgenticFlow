#!/usr/bin/env python3
"""
Development server runner for AgenticFlow.

This script provides a convenient way to run the FastAPI application
with hot-reload enabled for development.
"""
import uvicorn
import os
from pathlib import Path

def main():
    """Run the FastAPI application with Uvicorn."""
    # Set up paths
    base_dir = Path(__file__).parent
    env_path = base_dir / ".env"
    
    # Load environment variables if .env exists
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv(env_path)
    
    # Configure Uvicorn
    config = uvicorn.Config(
        "backend.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "true").lower() == "true",
        reload_dirs=["backend"],
        log_level=os.getenv("LOG_LEVEL", "info"),
        workers=int(os.getenv("WORKERS", "1")),
    )
    
    # Create and run the server
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    main()
