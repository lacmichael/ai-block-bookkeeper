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
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agents and models
from agents.document_processing_agent import agent as doc_agent
from agents.document_processing.models import DocumentProcessingRequest, DocumentProcessingResponse
from agents.shared_models import AuditResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Block Bookkeeper",
    description="Document processing and blockchain audit service",
    version="1.0.0"
)

# Global state for tracking responses
pending_requests: Dict[str, asyncio.Future] = {}
agent_threads_started = False

# Response models
class ProcessDocumentResponse(BaseModel):
    """Response from the complete document processing pipeline"""
    document_id: str
    success: bool
    processing_time_seconds: float
    document_processing: Optional[Dict] = None
    blockchain_audit: Optional[Dict] = None
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
        BusinessEventMessage,
        AuditResponse,
        Agent as UAAgent,
        Context,
        process_and_post_event,
        BusinessEvent,
        DocumentMetadata
    )
    from datetime import datetime
    
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
        ctx.logger.info("Ready to receive BusinessEvent messages for blockchain posting")
        ctx.logger.info("=" * 60)
    
    @audit_agent.on_message(model=BusinessEventMessage)
    async def handle_business_event(ctx, sender: str, msg: BusinessEventMessage):
        """Handle incoming BusinessEvent from Document Processing Agent"""
        ctx.logger.info(f"Received BusinessEvent {msg.event_id} from {sender}")
        ctx.logger.info(f"Confidence score: {msg.confidence_score:.2f}")
        
        # Convert dict back to BusinessEvent object
        event_dict = msg.business_event
        doc_meta_dict = event_dict.get('documents', [{}])[0] if event_dict.get('documents') else {}
        
        event = BusinessEvent(
            event_id=event_dict['event_id'],
            amount_minor=event_dict['amount_minor'],
            occurred_at=datetime.fromisoformat(event_dict['occurred_at'].replace('Z', '+00:00')),
            document_meta=DocumentMetadata(sha256=doc_meta_dict.get('sha256', '')),
            event_kind=event_dict.get('event_kind', 'transfer')
        )
        
        # Post to blockchain
        ctx.logger.info(f"Posting event {event.event_id} to blockchain...")
        result = await process_and_post_event(event, config)
        
        # Send response back to sender
        if result.get('success'):
            ctx.logger.info(f"✓ Successfully posted event {msg.event_id} to blockchain")
            response = AuditResponse(
                event_id=msg.event_id,
                document_id=msg.document_id,
                success=True,
                transaction_digest=result.get('digest'),
                blockchain_output=result.get('output')
            )
        else:
            ctx.logger.error(f"✗ Failed to post event {msg.event_id} to blockchain")
            response = AuditResponse(
                event_id=msg.event_id,
                document_id=msg.document_id,
                success=False,
                error_message=result.get('error', 'Unknown error'),
                blockchain_output=result.get('output')
            )
        
        await ctx.send(sender, response)
        ctx.logger.info(f"Sent audit response back to {sender}")
    
    # Start audit agent as background task
    asyncio.create_task(audit_agent.run_async())
    logger.info(f"✓ Audit Verification Agent started (address: {audit_agent.address})")
    
    # Store audit agent address for later use
    os.environ["AUDIT_AGENT_ADDRESS"] = audit_agent.address
    
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


@app.post("/process-document", response_model=ProcessDocumentResponse)
async def process_document(
    file: UploadFile = File(...),
    requester_id: str = "api-user"
):
    """
    Process a document and post to blockchain if confidence threshold is met.
    Waits for the complete pipeline to finish before responding.
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
        
        # Save file temporarily
        temp_dir = Path("/tmp/ai-block-bookkeeper")
        temp_dir.mkdir(exist_ok=True)
        
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
        
        # Create a future to wait for the complete pipeline
        response_future = asyncio.get_event_loop().create_future()
        pending_requests[document_id] = response_future
        
        # Send to document processing agent
        logger.info(f"Sending document {document_id} to processing agent...")
        
        # We need to send the message via the agent's internal messaging
        # Since we're running in the same process, we can use the agent's send method
        # However, we need to handle the response collection differently
        
        # For MVP, we'll use a simpler approach: directly call the processing client
        # and then the audit posting if confidence is high enough
        from agents.document_processing_client import DocumentProcessingClient
        from agents.audit_verification_agent import (
            process_and_post_event,
            load_config_from_env,
            BusinessEvent,
            DocumentMetadata
        )
        
        # Process document directly
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
        
        processing_client = DocumentProcessingClient(anthropic_api_key)
        doc_response = await processing_client.process_document(request)
        
        result = {
            "document_id": document_id,
            "success": doc_response.success,
            "processing_time_seconds": time.time() - start_time,
            "document_processing": {
                "success": doc_response.success,
                "business_event": doc_response.business_event,
                "extracted_data": doc_response.extracted_data,
                "error_message": doc_response.error_message,
                "processing_time": doc_response.processing_time_seconds
            }
        }
        
        # If document processing succeeded and confidence is high, post to blockchain
        if doc_response.success and doc_response.business_event:
            documents = doc_response.business_event.get('documents', [])
            confidence = documents[0].get('extraction_confidence', 0.0) if documents else 0.0
            
            logger.info(f"Document processing confidence: {confidence:.2f}")
            
            if confidence >= 0.80:
                logger.info("Confidence threshold met - posting to blockchain...")
                
                # Convert to BusinessEvent object
                event_dict = doc_response.business_event
                doc_meta_dict = documents[0] if documents else {}
                
                # Ensure amount_minor is an integer
                amount_minor = event_dict['amount_minor']
                if isinstance(amount_minor, str):
                    amount_minor = int(amount_minor)
                
                # Parse occurred_at - handle both string and datetime objects
                occurred_at = event_dict['occurred_at']
                if isinstance(occurred_at, str):
                    occurred_at = datetime.fromisoformat(occurred_at.replace('Z', '+00:00'))
                elif isinstance(occurred_at, datetime):
                    occurred_at = occurred_at
                else:
                    occurred_at = datetime.utcnow()
                
                event = BusinessEvent(
                    event_id=event_dict['event_id'],
                    amount_minor=amount_minor,
                    occurred_at=occurred_at,
                    document_meta=DocumentMetadata(sha256=doc_meta_dict.get('sha256', '')),
                    event_kind=event_dict.get('event_kind', 'transfer')
                )
                
                # Post to blockchain
                config = load_config_from_env()
                audit_result = await process_and_post_event(event, config)
                
                result["blockchain_audit"] = {
                    "success": audit_result.get('success'),
                    "transaction_digest": audit_result.get('digest'),
                    "output": audit_result.get('output'),
                    "error": audit_result.get('error')
                }
                
                if audit_result.get('success'):
                    logger.info(f"✓ Successfully posted to blockchain: {audit_result.get('digest')}")
                else:
                    logger.error(f"✗ Blockchain posting failed: {audit_result.get('error')}")
            else:
                logger.info(f"Confidence {confidence:.2f} below threshold (0.80) - skipping blockchain")
                result["blockchain_audit"] = {
                    "skipped": True,
                    "reason": f"Confidence {confidence:.2f} below threshold 0.80"
                }
        else:
            result["error_message"] = doc_response.error_message
        
        # Clean up pending request
        if document_id in pending_requests:
            del pending_requests[document_id]
        
        # Clean up temp file
        try:
            file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete temp file: {e}")
        
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

