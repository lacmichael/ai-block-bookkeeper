#!/usr/bin/env python3
"""
Health check endpoint for Supabase connection
Simple FastAPI app with health check endpoints
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config.database import supabase_config
    from supabase import Client
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn
    import structlog
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
    title="AI Block Bookkeeper Health Check",
    description="Health check endpoints for Supabase connection",
    version="1.0.0"
)

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
        "service": "AI Block Bookkeeper Health Check",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
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

@app.get("/status")
async def status_check():
    """Detailed status endpoint with all system information"""
    try:
        connection_status = check_supabase_connection()
        
        return {
            "service": "AI Block Bookkeeper",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "python_version": sys.version,
                "working_directory": os.getcwd()
            },
            "database": connection_status,
            "dependencies": {
                "supabase_installed": True,
                "fastapi_installed": True,
                "structlog_installed": True
            }
        }
        
    except Exception as e:
        logger.error("Status check endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

def run_health_check():
    """Run a one-time health check and exit"""
    print("🏥 Running AI Block Bookkeeper Health Check...")
    
    try:
        connection_status = check_supabase_connection()
        
        if connection_status["status"] == "connected":
            print("✅ Health check PASSED")
            print(f"   Status: {connection_status['message']}")
            print(f"   Database: Connected to {supabase_config.url}")
            print(f"   Timestamp: {connection_status['details']['timestamp']}")
            print("\n🎉 Your Supabase connection is working correctly!")
            return True
        else:
            print("❌ Health check FAILED")
            print(f"   Error: {connection_status['message']}")
            if 'details' in connection_status:
                print(f"   Details: {connection_status['details']}")
            return False
            
    except Exception as e:
        print(f"❌ Health check FAILED with exception: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    import sys
    
    # Check if user wants to run the server
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        print("🏥 Starting AI Block Bookkeeper Health Check Service")
        print("📋 Available endpoints:")
        print("   GET / - Basic service info")
        print("   GET /health - Health check")
        print("   GET /ready - Readiness check")
        print("   GET /status - Detailed status")
        print("   GET /docs - API documentation")
        print("\n🌐 Starting server on http://localhost:8000")
        print("   Press Ctrl+C to stop the server")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Run one-time health check and exit
        success = run_health_check()
        
        if success:
            print("\n" + "="*60)
            print("✅ READY TO BUILD YOUR FASTAPI APPLICATION!")
            print("="*60)
            print("\nNext steps:")
            print("1. Create your database tables in Supabase dashboard")
            print("2. Build your main FastAPI application")
            print("3. Use the database service for your domain models")
            print("\nTo run the health check server: python health_check.py --server")
            sys.exit(0)
        else:
            print("\n❌ Fix the connection issues before proceeding")
            sys.exit(1)
