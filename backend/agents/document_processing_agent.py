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
    DocumentProcessingResponse
)
from .document_processing_client import DocumentProcessingClient

# Query models
class HealthQuery(Model):
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Main handler for document processing requests"""
    logger.info(f"Processing document {msg.document_id} from {sender}")
    
    try:
        # Use the client directly to process the request
        response = await processing_client.process_document(msg)
        
        # Send response back to sender
        await ctx.send(sender, response)
        
        if response.success:
            logger.info(f"Document {msg.document_id} processed successfully in {response.processing_time_seconds:.2f} seconds")
        else:
            logger.error(f"Document {msg.document_id} processing failed: {response.error_message}")
        
    except Exception as e:
        error_msg = f"Error processing document {msg.document_id}: {str(e)}"
        logger.error(error_msg)
        
        response = DocumentProcessingResponse(
            document_id=msg.document_id,
            success=False,
            error_message=error_msg,
            processing_time_seconds=0.0
        )
        
        await ctx.send(sender, response)


@agent.on_event("startup")
async def startup(ctx: Context):
    """Agent startup handler"""
    logger.info("Document Processing Agent started")
    logger.info(f"Agent address: {agent.address}")
    

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
