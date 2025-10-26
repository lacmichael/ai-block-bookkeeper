import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Load environment variables
load_dotenv()

from .document_processing.models import (
    DocumentProcessingRequest, 
    DocumentProcessingResponse,
    AuditVerificationRequest,
    AuditVerificationResponse
)
from .shared_models import ReconciliationRequest
from .document_processing_client import DocumentProcessingClient
from .database_operations import insert_invoice_to_supabase
from models.domain_models import BusinessEvent

# Query models
class HealthQuery(Model):
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store for tracking audit requests
pending_audit_requests = {}

# Get agent addresses from environment
AUDIT_AGENT_ADDRESS = os.getenv("AUDIT_AGENT_ADDRESS", "")
RECONCILIATION_AGENT_ADDRESS = os.getenv("RECONCILIATION_AGENT_ADDRESS", "")

# Create the agent
agent = Agent(
    name="DocumentProcessingAgent",
    seed="document-processing-agent-seed-phrase-12345",
    port=8003,
    endpoint=["http://127.0.0.1:8003/submit"],
)

# Fund the agent if needed
fund_agent_if_low(agent.wallet.address())

# Initialize the document processing client directly
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is required")

processing_client = DocumentProcessingClient(anthropic_api_key)


@agent.on_message(DocumentProcessingRequest)
async def process_document(ctx: Context, sender: str, msg: DocumentProcessingRequest):
    """Main handler for document processing requests - extract invoice and send to audit agent"""
    logger.info(f"Processing document {msg.document_id} from {sender}")
    
    try:
        # Step 1: Extract invoice data using Claude
        response = await processing_client.process_document(msg)
        
        if not response.success:
            # Extraction failed - send error response immediately
            await ctx.send(sender, response)
            logger.error(f"Document {msg.document_id} extraction failed: {response.error_message}")
            return
        
        logger.info(f"Document {msg.document_id} extracted successfully in {response.processing_time_seconds:.2f} seconds")
        
        # Step 2: Check if audit agent address is configured
        if not AUDIT_AGENT_ADDRESS:
            logger.warning("AUDIT_AGENT_ADDRESS not configured - skipping Sui posting and Supabase insert")
            response.error_message = "Audit agent not configured - data not persisted"
            response.supabase_inserted = False
            await ctx.send(sender, response)
            return
        
        # Step 3: Send BusinessEvent to audit verification agent for Sui posting
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
        logger.info(f"Sent audit request for {msg.document_id} to audit agent at {AUDIT_AGENT_ADDRESS}")
        
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
    """Receive Sui posting result and insert to Supabase if successful"""
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
            # Step 4: Sui posting succeeded - insert to Supabase
            logger.info(f"Sui posting succeeded with digest: {msg.sui_digest}")
            
            # Reconstruct BusinessEvent from dict
            business_event = BusinessEvent(**business_event_dict)
            
            # Insert to Supabase
            await insert_invoice_to_supabase(business_event, msg.sui_digest)
            
            # Update response
            response.sui_digest = msg.sui_digest
            response.supabase_inserted = True
            logger.info(f"Successfully inserted {msg.request_id} to Supabase")
            
            # Step 5: Trigger reconciliation if agent is configured
            if RECONCILIATION_AGENT_ADDRESS:
                reconciliation_request = ReconciliationRequest(
                    event_id=msg.request_id,
                    business_event=business_event_dict
                )
                await ctx.send(RECONCILIATION_AGENT_ADDRESS, reconciliation_request)
                logger.info(f"Sent reconciliation request for {msg.request_id} to reconciliation agent")
            else:
                logger.warning("RECONCILIATION_AGENT_ADDRESS not configured - skipping reconciliation")
            
        else:
            # Step 5: Sui posting failed - don't insert to Supabase
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
        response.error_message = f"Database insertion failed: {str(e)}"
        response.supabase_inserted = False
        await ctx.send(original_sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    """Agent startup handler"""
    logger.info("Document Processing Agent started")
    logger.info(f"Agent address: {agent.address}")
    if AUDIT_AGENT_ADDRESS:
        logger.info(f"Audit agent address configured: {AUDIT_AGENT_ADDRESS}")
    else:
        logger.warning("⚠️  AUDIT_AGENT_ADDRESS not configured - Sui posting will be skipped")
    
    if RECONCILIATION_AGENT_ADDRESS:
        logger.info(f"Reconciliation agent address configured: {RECONCILIATION_AGENT_ADDRESS}")
    else:
        logger.warning("⚠️  RECONCILIATION_AGENT_ADDRESS not configured - reconciliation will be skipped")
    

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    """Agent shutdown handler"""
    logger.info("Document Processing Agent shutting down")

# Health check endpoint
@agent.on_query(HealthQuery)
async def health_check(ctx: Context, sender: str, msg: HealthQuery):
    """Health check query handler"""
    return {
        "status": "healthy",
        "agent_address": agent.address,
        "timestamp": datetime.utcnow().isoformat(),
        "client_available": processing_client is not None
    }

if __name__ == "__main__":
    agent.run()
