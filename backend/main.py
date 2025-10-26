"""
Main FastAPI application that orchestrates document processing and blockchain audit agents.
Runs both agents in background threads and exposes HTTP endpoints.
"""

import asyncio
import hashlib
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agents and models
from agents.document_processing_agent import agent as doc_agent
from agents.document_processing.models import DocumentProcessingRequest, DocumentProcessingResponse
from agents.shared_models import AuditResponse

# Import API routes
from api.routes import transactions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Block Bookkeeper",
    description="Document processing and blockchain audit service",
    version="1.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])

# Global state for tracking responses
pending_requests: Dict[str, asyncio.Future] = {}
agent_threads_started = False

# Response models
class ProcessDocumentResponse(BaseModel):
    """Response from the complete document processing pipeline"""
    document_id: str
    success: bool
    processing_time_seconds: float
    sui_digest: Optional[str] = None  # Sui transaction digest
    supabase_inserted: bool = False   # Whether data was inserted to Supabase
    document_processing: Optional[Dict] = None
    blockchain_audit: Optional[Dict] = None  # Legacy field for backward compatibility
    error_message: Optional[str] = None


class AgentInfo(BaseModel):
    """Information about running agents"""
    document_agent_address: str
    audit_agent_address: str
    document_agent_port: int
    audit_agent_port: int


async def start_agents_in_background():
    """Start both agents as background asyncio tasks"""
    global agent_threads_started
    
    if agent_threads_started:
        logger.info("Agents already started, skipping...")
        return
    
    logger.info("Starting agents as background tasks...")
    
    # Start document processing agent as background task
    asyncio.create_task(doc_agent.run_async())
    logger.info(f"✓ Document Processing Agent started (address: {doc_agent.address})")
    
    # For the audit agent, we need to import and create it here
    # instead of calling the main() function which creates its own agent
    from agents.audit_verification_agent import (
        load_config_from_env,
        Agent as UAAgent,
        Context,
        handle_audit_request_logic
    )
    from agents.document_processing.models import AuditVerificationRequest, AuditVerificationResponse
    
    config = load_config_from_env()
    
    # Create audit agent in this event loop
    audit_agent = UAAgent(
        name=os.environ.get("AUDIT_AGENT_NAME", "audit_verification_agent"),
        seed=os.environ.get("AUDIT_AGENT_SEED", "audit-verification-agent-seed-67890"),
        port=int(os.environ.get("AGENT_PORT", "8001")),
        endpoint=[f"http://127.0.0.1:{os.environ.get('AGENT_PORT', '8001')}/submit"]
    )
    
    @audit_agent.on_event("startup")
    async def audit_startup(ctx):
        ctx.logger.info("=" * 60)
        ctx.logger.info("Audit Verification Agent Started")
        ctx.logger.info("=" * 60)
        ctx.logger.info(f"Agent address: {audit_agent.address}")
        ctx.logger.info(f"Listening on port: {os.environ.get('AGENT_PORT', '8001')}")
        ctx.logger.info("Ready to receive AuditVerificationRequest messages")
        ctx.logger.info("=" * 60)
    
    @audit_agent.on_message(model=AuditVerificationRequest)
    async def handle_audit_request(ctx, sender: str, msg: AuditVerificationRequest):
        """Handle incoming AuditVerificationRequest from Document Processing Agent"""
        ctx.logger.info(f"Received audit request {msg.request_id} from {sender}")
        
        # Use the shared logic function from audit_verification_agent
        result = await handle_audit_request_logic(msg.business_event, msg.request_id, config)
        
        # Send response back to document agent
        response = AuditVerificationResponse(
            request_id=msg.request_id,
            success=result["success"],
            sui_digest=result.get("sui_digest"),
            error_message=result.get("error_message")
        )
        
        await ctx.send(sender, response)
        ctx.logger.info(f"Sent audit response for {msg.request_id}: success={result['success']}")
    
    # Start audit agent as background task
    asyncio.create_task(audit_agent.run_async())
    logger.info(f"✓ Audit Verification Agent started (address: {audit_agent.address})")
    
    # Store audit agent address for later use - doc agent needs this to send messages
    os.environ["AUDIT_AGENT_ADDRESS"] = audit_agent.address
    
    # Update document agent's AUDIT_AGENT_ADDRESS
    import agents.document_processing_agent as doc_agent_module
    doc_agent_module.AUDIT_AGENT_ADDRESS = audit_agent.address
    logger.info(f"✓ Configured document agent to send to audit agent: {audit_agent.address}")
    
    # Give agents time to initialize
    await asyncio.sleep(2)
    
    agent_threads_started = True
    logger.info("All agents initialized and ready")


@app.on_event("startup")
async def startup_event():
    """Initialize agents on application startup"""
    logger.info("=" * 60)
    logger.info("AI Block Bookkeeper API Starting")
    logger.info("=" * 60)
    
    # Start agents in background
    await start_agents_in_background()
    
    logger.info("=" * 60)
    logger.info("API Ready")
    logger.info("=" * 60)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "agents_running": agent_threads_started
    }


@app.get("/agent-info", response_model=AgentInfo)
async def get_agent_info():
    """Get information about running agents"""
    if not agent_threads_started:
        raise HTTPException(status_code=503, detail="Agents not yet started")
    
    return AgentInfo(
        document_agent_address=doc_agent.address,
        audit_agent_address=os.environ.get("AUDIT_AGENT_ADDRESS", ""),
        document_agent_port=8003,
        audit_agent_port=8001
    )


@app.get("/document/{document_id}")
async def get_document(document_id: str):
    """Retrieve a stored document by document_id"""
    from fastapi.responses import FileResponse
    
    upload_dir = Path("backend/uploads")
    for file in upload_dir.glob(f"{document_id}_*"):
        return FileResponse(file)
    raise HTTPException(status_code=404, detail="Document not found")


@app.post("/process-document", response_model=ProcessDocumentResponse)
async def process_document(
    file: UploadFile = File(...),
    requester_id: str = "api-user"
):
    """
    Process a document through the agent pipeline:
    1. Document agent extracts invoice data
    2. Document agent sends to audit agent for Sui posting  
    3. Document agent inserts to Supabase if Sui succeeds
    4. Returns complete response with sui_digest and supabase_inserted status
    """
    if not agent_threads_started:
        raise HTTPException(status_code=503, detail="Agents not yet initialized")
    
    start_time = time.time()
    document_id = str(uuid4())
    
    logger.info(f"Received document upload: {file.filename} (ID: {document_id})")
    
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Calculate file hash for tracking
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Save file to persistent storage
        temp_dir = Path("backend/uploads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = temp_dir / f"{document_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File saved to: {file_path}")
        
        # Determine file type
        file_extension = file.filename.lower().split('.')[-1]
        file_type_map = {
            'pdf': 'PDF',
            'csv': 'CSV',
            'xlsx': 'EXCEL',
            'xls': 'EXCEL',
            'jpg': 'IMAGE',
            'jpeg': 'IMAGE',
            'png': 'IMAGE'
        }
        file_type = file_type_map.get(file_extension, 'PDF')
        
        # Create processing request
        request = DocumentProcessingRequest(
            document_id=document_id,
            file_path=str(file_path),
            filename=file.filename,
            file_size=file_size,
            file_type=file_type,
            upload_timestamp=datetime.utcnow(),
            requester_id=requester_id,
            metadata={"file_hash": file_hash}
        )
        
        # Since we're in the same process, process synchronously:
        # 1. Extract invoice data
        # 2. Post to Sui blockchain  
        # 3. Insert to Supabase if Sui succeeds
        logger.info(f"Processing document {document_id} synchronously...")
        
        from agents.document_processing_client import DocumentProcessingClient
        from agents.audit_verification_agent import handle_audit_request_logic, load_config_from_env
        from agents.database_operations import insert_invoice_to_supabase
        from models.domain_models import BusinessEvent
        
        # Step 1: Extract invoice data
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
        
        processing_client = DocumentProcessingClient(anthropic_api_key)
        doc_response = await processing_client.process_document(request)
        
        if not doc_response.success:
            # Extraction failed
            return ProcessDocumentResponse(
                document_id=document_id,
                success=False,
                processing_time_seconds=time.time() - start_time,
                error_message=doc_response.error_message
            )
        
        logger.info(f"✓ Invoice extracted successfully")
        
        # Step 2: Post to Sui blockchain
        config = load_config_from_env()
        sui_result = await handle_audit_request_logic(
            doc_response.business_event,
            document_id,
            config
        )
        
        if not sui_result["success"]:
            # Sui posting failed
            logger.error(f"✗ Sui posting failed: {sui_result.get('error_message')}")
            return ProcessDocumentResponse(
                document_id=document_id,
                success=False,
                processing_time_seconds=time.time() - start_time,
                sui_digest=None,
                supabase_inserted=False,
                error_message=f"Blockchain posting failed: {sui_result.get('error_message')}",
                document_processing={
                    "success": doc_response.success,
                    "business_event": doc_response.business_event,
                    "extracted_data": doc_response.extracted_data
                }
            )
        
        logger.info(f"✓ Sui transaction posted: {sui_result.get('sui_digest')}")
        
        # Step 3: Insert to Supabase
        try:
            business_event = BusinessEvent(**doc_response.business_event)
            await insert_invoice_to_supabase(business_event, sui_result["sui_digest"], str(file_path))
            logger.info(f"✓ Data inserted to Supabase")
            supabase_inserted = True
        except Exception as e:
            logger.error(f"✗ Supabase insert failed: {str(e)}")
            supabase_inserted = False
        
        doc_response = DocumentProcessingResponse(
            document_id=document_id,
            success=True,
            processing_time_seconds=doc_response.processing_time_seconds,
            business_event=doc_response.business_event,
            extracted_data=doc_response.extracted_data,
            sui_digest=sui_result["sui_digest"],
            supabase_inserted=supabase_inserted
        )
        
        # Build result from agent response
        result = {
            "document_id": document_id,
            "success": doc_response.success,
            "processing_time_seconds": time.time() - start_time,
            "sui_digest": doc_response.sui_digest,
            "supabase_inserted": doc_response.supabase_inserted,
            "document_processing": {
                "success": doc_response.success,
                "business_event": doc_response.business_event,
                "extracted_data": doc_response.extracted_data,
                "error_message": doc_response.error_message,
                "processing_time": doc_response.processing_time_seconds
            }
        }
        
        if doc_response.error_message:
            result["error_message"] = doc_response.error_message
        
        # Log results
        if doc_response.sui_digest:
            logger.info(f"✓ Sui transaction posted: {doc_response.sui_digest}")
        if doc_response.supabase_inserted:
            logger.info(f"✓ Data inserted to Supabase")
        
        # Clean up pending request
        if document_id in pending_requests:
            del pending_requests[document_id]
        
        result["processing_time_seconds"] = time.time() - start_time
        
        return ProcessDocumentResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)
        
        # Clean up
        if document_id in pending_requests:
            del pending_requests[document_id]
        
        return ProcessDocumentResponse(
            document_id=document_id,
            success=False,
            processing_time_seconds=time.time() - start_time,
            error_message=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "8000"))
    
    logger.info(f"Starting API server on port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Set to True for development
        log_level="info"
    )

