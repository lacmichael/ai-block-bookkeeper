#!/usr/bin/env python3
"""
Main FastAPI application for AI Block Bookkeeper
Includes chat routes and health check endpoints
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import structlog

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.database import supabase_config
    from api.routes.chat import router as chat_router
    from api.routes.verification import router as verification_router
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have installed the requirements: pip install -r requirements.txt")
    sys.exit(1)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="AI Block Bookkeeper",
    description="AI-powered financial analysis and bookkeeping system",
    version="1.0.0"
)

# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(verification_router, prefix="/api", tags=["verification"])

def check_supabase_connection() -> dict:
    """Check Supabase connection and return status"""
    try:
        # Check environment variables
        if not all([supabase_config.url, supabase_config.anon_key, supabase_config.service_role_key]):
            return {
                "status": "error",
                "message": "Missing Supabase environment variables",
                "details": {
                    "url_present": bool(supabase_config.url),
                    "anon_key_present": bool(supabase_config.anon_key),
                    "service_role_key_present": bool(supabase_config.service_role_key)
                }
            }
        
        # Create client
        client = supabase_config.get_client(use_service_role=True)
        
        # Test connection with a simple query
        try:
            # This will fail if table doesn't exist, but that's expected
            result = client.table("_health_check").select("*").limit(1).execute()
            connection_status = "connected"
            connection_message = "Database connection successful"
        except Exception as e:
            error_str = str(e).lower()
            if any(phrase in error_str for phrase in [
                "could not find the table", 
                "relation", 
                "does not exist",
                "pgrst205"
            ]):
                connection_status = "connected"
                connection_message = "Database connection successful (no test table exists, which is expected)"
            else:
                connection_status = "error"
                connection_message = f"Database connection failed: {str(e)}"
        
        return {
            "status": connection_status,
            "message": connection_message,
            "details": {
                "supabase_url": supabase_config.url,
                "timestamp": datetime.now().isoformat(),
                "client_created": True
            }
        }
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "details": {
                "timestamp": datetime.now().isoformat(),
                "error_type": type(e).__name__
            }
        }

@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "service": "AI Block Bookkeeper",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "chat": "/api/chat",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    try:
        connection_status = check_supabase_connection()
        
        if connection_status["status"] == "error":
            raise HTTPException(status_code=503, detail=connection_status)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "AI Block Bookkeeper",
                "timestamp": datetime.now().isoformat(),
                "database": connection_status
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Health check endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint - more detailed than health check"""
    try:
        connection_status = check_supabase_connection()
        
        # For readiness, we want to ensure the service is fully ready
        if connection_status["status"] != "connected":
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "service": "AI Block Bookkeeper",
                    "timestamp": datetime.now().isoformat(),
                    "database": connection_status,
                    "message": "Service not ready - database connection issues"
                }
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "ready",
                "service": "AI Block Bookkeeper",
                "timestamp": datetime.now().isoformat(),
                "database": connection_status,
                "message": "Service is ready to accept requests"
            }
        )
        
    except Exception as e:
        logger.error("Readiness check endpoint error", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "AI Block Bookkeeper",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "message": "Service not ready due to internal error"
            }
        )

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    print("🚀 Starting AI Block Bookkeeper FastAPI Server")
    print("📋 Available endpoints:")
    print("   GET / - Basic service info")
    print("   GET /health - Health check")
    print("   GET /ready - Readiness check")
    print("   POST /api/chat - Chat with Financial Analysis Agent")
    print("   GET /docs - API documentation")
    print("\n🌐 Starting server on http://127.0.0.1:8000")
    print("   Press Ctrl+C to stop the server")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
