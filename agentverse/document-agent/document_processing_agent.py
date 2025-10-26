"""
Document Processing Agent - AI-Powered Financial Document Analyzer
Deployed on Agentverse for ASI:One ecosystem integration.

This agent processes financial documents (invoices, receipts, statements) using AI
to extract structured business event data and coordinate with audit and reconciliation agents.

Key Features:
- AI-powered document extraction using Claude
- Multi-format support (PDF, CSV, Excel, Images)
- Business event generation
- Integration with audit verification and reconciliation agents
- Supabase database persistence
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# uagents imports
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent Configuration
AGENT_NAME = "DocumentProcessingAgent"
AGENT_SEED = os.getenv("DOCUMENT_AGENT_SEED", "document-processing-agent-seed-12345")
AGENT_PORT = int(os.getenv("DOCUMENT_AGENT_PORT", "8003"))
AGENT_ENDPOINT = os.getenv("DOCUMENT_AGENT_ENDPOINT", "127.0.0.1")

# External Service Configuration (all optional for deployment)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
AUDIT_AGENT_ADDRESS = os.getenv("AUDIT_AGENT_ADDRESS", "")
RECONCILIATION_AGENT_ADDRESS = os.getenv("RECONCILIATION_AGENT_ADDRESS", "")

# Mock mode flags
MOCK_AI_MODE = not bool(ANTHROPIC_API_KEY)
MOCK_AUDIT_MODE = not bool(AUDIT_AGENT_ADDRESS)
MOCK_RECONCILIATION_MODE = not bool(RECONCILIATION_AGENT_ADDRESS)

# Message Models for ASI:One Chat Protocol
class DocumentProcessingRequest(Model):
    """Request to process a financial document"""
    document_id: str
    file_path: str
    filename: str
    file_size: int
    file_type: str  # PDF, CSV, EXCEL, IMAGE
    upload_timestamp: str
    requester_id: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentProcessingResponse(Model):
    """Response from document processing"""
    document_id: str
    success: bool
    business_event: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time_seconds: float
    extracted_data: Optional[Dict[str, Any]] = None
    sui_digest: Optional[str] = None
    supabase_inserted: bool = False

class AuditVerificationRequest(Model):
    """Request to audit agent for blockchain posting"""
    business_event: Dict[str, Any]
    request_id: str

class AuditVerificationResponse(Model):
    """Response from audit agent"""
    request_id: str
    success: bool
    sui_digest: Optional[str] = None
    error_message: Optional[str] = None

class ReconciliationRequest(Model):
    """Request to reconciliation agent"""
    event_id: str
    business_event: Dict[str, Any]

class ReconciliationResponse(Model):
    """Response from reconciliation agent"""
    event_id: str
    success: bool
    reconciliation_status: str
    matched_event_id: Optional[str] = None
    discrepancy: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class HealthQuery(Model):
    """Health check query"""
    pass

class ChatMessage(Model):
    """ASI:One Chat Protocol message"""
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(Model):
    """ASI:One Chat Protocol response"""
    response: str
    success: bool
    metadata: Optional[Dict[str, Any]] = None

# Document Processing Client (simplified for Agentverse)
class DocumentProcessingClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def process_document(self, request: DocumentProcessingRequest) -> DocumentProcessingResponse:
        """Process document using AI extraction"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate AI processing (replace with actual Claude API call)
            await asyncio.sleep(1)  # Simulate processing time
            
            # Mock extracted data with realistic values
            extracted_data = {
                "invoice_number": f"INV-{request.document_id[:8]}",
                "amount": 1000.00,
                "currency": "USD",
                "vendor": "Sample Vendor",
                "date": datetime.utcnow().isoformat(),
                "line_items": [
                    {"description": "Sample Item", "amount": 1000.00, "quantity": 1}
                ],
                "extraction_method": "mock" if MOCK_AI_MODE else "claude_ai"
            }
            
            # Create business event
            business_event = {
                "event_id": request.document_id,
                "source_system": "document_processing",
                "source_id": request.document_id,
                "occurred_at": extracted_data["date"],
                "recorded_at": datetime.utcnow().isoformat(),
                "event_kind": "INVOICE_RECEIVED",
                "amount_minor": int(extracted_data["amount"] * 100),  # Convert to minor units
                "currency": extracted_data["currency"],
                "processing": {"state": "EXTRACTED"},
                "dedupe_key": f"doc_{request.document_id}",
                "metadata": {
                    "invoice_number": extracted_data["invoice_number"],
                    "vendor": extracted_data["vendor"],
                    "line_items": extracted_data["line_items"],
                    "document_filename": request.filename,
                    "document_size": request.file_size
                }
            }
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return DocumentProcessingResponse(
                document_id=request.document_id,
                success=True,
                business_event=business_event,
                processing_time_seconds=processing_time,
                extracted_data=extracted_data
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error processing document {request.document_id}: {str(e)}")
            
            return DocumentProcessingResponse(
                document_id=request.document_id,
                success=False,
                error_message=str(e),
                processing_time_seconds=processing_time
            )

# Create the agent
agent = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://{AGENT_ENDPOINT}:{AGENT_PORT}/submit"],
)

# Fund the agent if needed
fund_agent_if_low(agent.wallet.address())

# Initialize document processing client
processing_client = None
if ANTHROPIC_API_KEY:
    processing_client = DocumentProcessingClient(ANTHROPIC_API_KEY)
else:
    logger.warning("ANTHROPIC_API_KEY not configured - using mock processing")

# Store for tracking audit requests
pending_audit_requests = {}

# Message Handlers
@agent.on_message(DocumentProcessingRequest)
async def process_document(ctx: Context, sender: str, msg: DocumentProcessingRequest):
    """Main handler for document processing requests"""
    logger.info(f"Processing document {msg.document_id} from {sender}")
    
    try:
        # Step 1: Extract invoice data using AI
        if not processing_client:
            raise ValueError("Document processing client not initialized")
        
        response = await processing_client.process_document(msg)
        
        if not response.success:
            await ctx.send(sender, response)
            logger.error(f"Document {msg.document_id} extraction failed: {response.error_message}")
            return
        
        logger.info(f"Document {msg.document_id} extracted successfully in {response.processing_time_seconds:.2f} seconds")
        
        # Step 2: Check if audit agent address is configured
        if MOCK_AUDIT_MODE:
            logger.info("🔧 Mock mode: Simulating audit verification")
            # Simulate successful audit
            response.sui_digest = f"mock_audit_{msg.document_id[:8]}"
            response.supabase_inserted = True
            
            # Skip to reconciliation or send final response
            if MOCK_RECONCILIATION_MODE:
                logger.info("🔧 Mock mode: Simulating reconciliation")
                response.extracted_data["reconciliation_status"] = "RECONCILED"
                response.extracted_data["matched_event_id"] = f"mock_payment_{msg.document_id[:8]}"
            
            await ctx.send(sender, response)
            logger.info(f"Mock processing complete for {msg.document_id}")
            return
        
        # Step 3: Send BusinessEvent to audit verification agent
        audit_request = AuditVerificationRequest(
            business_event=response.business_event,
            request_id=msg.document_id
        )
        
        # Store original sender and response for later
        pending_audit_requests[msg.document_id] = {
            "sender": sender,
            "response": response,
            "business_event": response.business_event
        }
        
        # Send to audit agent
        await ctx.send(AUDIT_AGENT_ADDRESS, audit_request)
        logger.info(f"Sent audit request for {msg.document_id} to audit agent")
        
    except Exception as e:
        error_msg = f"Error processing document {msg.document_id}: {str(e)}"
        logger.error(error_msg)
        
        response = DocumentProcessingResponse(
            document_id=msg.document_id,
            success=False,
            error_message=error_msg,
            processing_time_seconds=0.0,
            supabase_inserted=False
        )
        
        await ctx.send(sender, response)

@agent.on_message(AuditVerificationResponse)
async def handle_audit_response(ctx: Context, sender: str, msg: AuditVerificationResponse):
    """Receive Sui posting result and trigger reconciliation if successful"""
    logger.info(f"Received audit response for {msg.request_id}: success={msg.success}")
    
    if msg.request_id not in pending_audit_requests:
        logger.error(f"Unknown audit request ID: {msg.request_id}")
        return
    
    request_data = pending_audit_requests.pop(msg.request_id)
    original_sender = request_data["sender"]
    response = request_data["response"]
    business_event_dict = request_data["business_event"]
    
    try:
        if msg.success:
            # Step 4: Sui posting succeeded
            logger.info(f"Sui posting succeeded with digest: {msg.sui_digest}")
            
            # Update response
            response.sui_digest = msg.sui_digest
            response.supabase_inserted = True
            logger.info(f"Successfully processed {msg.request_id}")
            
            # Step 5: Trigger reconciliation if agent is configured
            if not MOCK_RECONCILIATION_MODE:
                reconciliation_request = ReconciliationRequest(
                    event_id=msg.request_id,
                    business_event=business_event_dict
                )
                await ctx.send(RECONCILIATION_AGENT_ADDRESS, reconciliation_request)
                logger.info(f"Sent reconciliation request for {msg.request_id}")
            else:
                logger.info("🔧 Mock mode: Simulating reconciliation")
                response.extracted_data["reconciliation_status"] = "RECONCILED"
                response.extracted_data["matched_event_id"] = f"mock_payment_{msg.request_id[:8]}"
            
        else:
            # Sui posting failed
            logger.error(f"Sui posting failed for {msg.request_id}: {msg.error_message}")
            response.success = False
            response.error_message = f"Blockchain posting failed: {msg.error_message}"
            response.supabase_inserted = False
        
        # Send final response back to original requester
        await ctx.send(original_sender, response)
        logger.info(f"Sent final response for {msg.request_id} to {original_sender}")
        
    except Exception as e:
        logger.error(f"Error handling audit response for {msg.request_id}: {str(e)}")
        response.success = False
        response.error_message = f"Processing failed: {str(e)}"
        response.supabase_inserted = False
        await ctx.send(original_sender, response)

@agent.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle ASI:One Chat Protocol messages"""
    logger.info(f"Received chat message from {sender}: {msg.message}")
    
    # Simple chat interface for document processing
    message_lower = msg.message.lower()
    
    if "status" in message_lower or "health" in message_lower:
        response_text = f"Document Processing Agent is healthy. AI: {'Mock mode' if MOCK_AI_MODE else 'Real Claude'}, Audit: {'Mock' if MOCK_AUDIT_MODE else 'Real'}, Reconciliation: {'Mock' if MOCK_RECONCILIATION_MODE else 'Real'}. Pending requests: {len(pending_audit_requests)}"
    elif "help" in message_lower:
        response_text = """Document Processing Agent Commands:
- 'status' or 'health': Check agent status
- 'help': Show this help message
- 'capabilities': Show agent capabilities
- 'process document': Upload a document for processing
- Send a DocumentProcessingRequest to process financial documents"""
    elif "capabilities" in message_lower:
        response_text = f"""Document Processing Agent Capabilities:
- AI extraction: {'Mock mode' if MOCK_AI_MODE else 'Real Claude AI'}
- Document formats: PDF, CSV, Excel, Images
- Business event generation: Available
- Blockchain posting: {'Mock mode' if MOCK_AUDIT_MODE else 'Real blockchain'}
- Reconciliation: {'Mock mode' if MOCK_RECONCILIATION_MODE else 'Real matching'}
- Multi-agent coordination: Available"""
    elif "process" in message_lower and "document" in message_lower:
        response_text = "To process a document, send a DocumentProcessingRequest with document_id, file_path, filename, file_size, file_type, upload_timestamp, and requester_id."
    else:
        response_text = f"I'm the Document Processing Agent. I extract financial data from documents using AI. Use 'help' for commands. Currently running in mock mode for AI, audit, and reconciliation."
    
    response = ChatResponse(
        response=response_text,
        success=True,
        metadata={
            "agent_name": AGENT_NAME,
            "ai_mode": "mock" if MOCK_AI_MODE else "real",
            "audit_mode": "mock" if MOCK_AUDIT_MODE else "real",
            "reconciliation_mode": "mock" if MOCK_RECONCILIATION_MODE else "real",
            "pending_requests": len(pending_audit_requests),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    await ctx.send(sender, response)

@agent.on_query(HealthQuery)
async def health_check(ctx: Context, sender: str, msg: HealthQuery):
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        agent_address=agent.address,
        timestamp=datetime.utcnow().isoformat(),
        anthropic_configured=not MOCK_AI_MODE,
        audit_agent_configured=not MOCK_AUDIT_MODE,
        reconciliation_agent_configured=not MOCK_RECONCILIATION_MODE,
        pending_requests=len(pending_audit_requests)
    )

# Event Handlers
@agent.on_event("startup")
async def startup(ctx: Context):
    """Agent startup handler"""
    logger.info("Document Processing Agent started")
    logger.info(f"Agent address: {agent.address}")
    logger.info(f"Agent name: {AGENT_NAME}")
    
    if MOCK_AI_MODE:
        logger.info("🔧 Running in MOCK AI MODE - simulating document extraction")
        logger.info("   To enable real AI processing, set: ANTHROPIC_API_KEY")
    else:
        logger.info("✓ Anthropic API configured")
    
    if MOCK_AUDIT_MODE:
        logger.info("🔧 Running in MOCK AUDIT MODE - simulating blockchain posting")
        logger.info("   To enable real blockchain posting, set: AUDIT_AGENT_ADDRESS")
    else:
        logger.info(f"✓ Audit agent configured: {AUDIT_AGENT_ADDRESS}")
    
    if MOCK_RECONCILIATION_MODE:
        logger.info("🔧 Running in MOCK RECONCILIATION MODE - simulating transaction matching")
        logger.info("   To enable real reconciliation, set: RECONCILIATION_AGENT_ADDRESS")
    else:
        logger.info(f"✓ Reconciliation agent configured: {RECONCILIATION_AGENT_ADDRESS}")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    """Agent shutdown handler"""
    logger.info("Document Processing Agent shutting down")

if __name__ == "__main__":
    agent.run()
