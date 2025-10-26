"""
Test script for Document Processing Agent → Audit Verification Agent integration.

This script creates a test agent that sends a DocumentProcessingRequest to the
Document Agent and monitors the response. It demonstrates real agent-to-agent
communication using the Fetch.ai uAgents framework.

Usage:
    1. Start Audit Agent in terminal 1: python audit_verification_agent.py
    2. Start Document Agent in terminal 2: python document_processing_agent.py
    3. Update DOCUMENT_AGENT_ADDRESS below with the address from step 2
    4. Run this script: python test_agent_integration.py
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from uagents import Agent, Context

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

from agents.document_processing.models import DocumentProcessingRequest, DocumentProcessingResponse
from agents.shared_models import AuditResponse

# Configuration
DOCUMENT_AGENT_ADDRESS = os.getenv("DOCUMENT_AGENT_ADDRESS", "")
TEST_PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "example", "example_invoice_01.pdf")

# Create test agent
test_agent = Agent(
    name="TestAgent",
    seed="test-agent-seed-99999",
    port=8999,
    endpoint=["http://127.0.0.1:8999/submit"]
)

# Track test state
test_state = {
    "document_response_received": False,
    "audit_response_received": False,
    "test_complete": False
}


@test_agent.on_event("startup")
async def startup(ctx: Context):
    """Test agent startup"""
    ctx.logger.info("=" * 60)
    ctx.logger.info("Agent Integration Test Started")
    ctx.logger.info("=" * 60)
    ctx.logger.info(f"Test Agent address: {test_agent.address}")
    
    # Check configuration
    ctx.logger.info("\n1. Checking Configuration...")
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    audit_address = os.getenv("AUDIT_AGENT_ADDRESS")
    doc_address = DOCUMENT_AGENT_ADDRESS
    
    ctx.logger.info(f"   ANTHROPIC_API_KEY: {'✓ Set' if anthropic_key else '✗ Missing'}")
    ctx.logger.info(f"   AUDIT_AGENT_ADDRESS: {audit_address if audit_address else '✗ Missing'}")
    ctx.logger.info(f"   DOCUMENT_AGENT_ADDRESS: {doc_address if doc_address else '✗ Missing'}")
    
    if not doc_address:
        ctx.logger.error("\n✗ DOCUMENT_AGENT_ADDRESS not set!")
        ctx.logger.error("   Update the variable in this script or set in .env")
        ctx.logger.error("   Get it from Document Agent startup logs")
        return
    
    if not os.path.exists(TEST_PDF_PATH):
        ctx.logger.error(f"\n✗ Test PDF not found: {TEST_PDF_PATH}")
        return
    
    ctx.logger.info(f"\n2. Test PDF: {TEST_PDF_PATH}")
    ctx.logger.info(f"   File size: {os.path.getsize(TEST_PDF_PATH)} bytes")
    
    # Send test request after a short delay
    await asyncio.sleep(2)
    await send_test_request(ctx)


async def send_test_request(ctx: Context):
    """Send a document processing request to the Document Agent"""
    ctx.logger.info("\n3. Sending DocumentProcessingRequest to Document Agent...")
    
    request = DocumentProcessingRequest(
        document_id="test_integration_001",
        file_path=os.path.abspath(TEST_PDF_PATH),
        filename="example_invoice_01.pdf",
        file_size=os.path.getsize(TEST_PDF_PATH),
        file_type="PDF",
        upload_timestamp=datetime.utcnow(),
        requester_id="test_agent"
    )
    
    ctx.logger.info(f"   → Sending to: {DOCUMENT_AGENT_ADDRESS}")
    ctx.logger.info(f"   → Document ID: {request.document_id}")
    
    await ctx.send(DOCUMENT_AGENT_ADDRESS, request)
    ctx.logger.info("   ✓ Request sent! Waiting for response...")


@test_agent.on_message(model=DocumentProcessingResponse)
async def handle_document_response(ctx: Context, sender: str, msg: DocumentProcessingResponse):
    """Handle response from Document Agent"""
    ctx.logger.info("\n4. ✓ Received DocumentProcessingResponse from Document Agent")
    ctx.logger.info(f"   Sender: {sender}")
    ctx.logger.info(f"   Document ID: {msg.document_id}")
    ctx.logger.info(f"   Success: {msg.success}")
    ctx.logger.info(f"   Processing Time: {msg.processing_time_seconds:.2f}s")
    
    test_state["document_response_received"] = True
    
    if msg.success and msg.business_event:
        # Extract confidence
        docs = msg.business_event.get('documents', [])
        confidence = docs[0].get('extraction_confidence', 0.0) if docs else 0.0
        
        ctx.logger.info(f"   Extraction Confidence: {confidence:.2f}")
        
        # Extract key info
        amount = msg.business_event.get('amount_minor', 0)
        currency = msg.business_event.get('currency', 'USD')
        event_id = msg.business_event.get('event_id', 'N/A')
        
        ctx.logger.info(f"   Event ID: {event_id}")
        ctx.logger.info(f"   Amount: {currency} ${amount/100:.2f}")
        
        if confidence >= 0.80:
            ctx.logger.info("\n   → Confidence >= 0.80: Should send to Audit Agent")
            ctx.logger.info("   → Watch Document Agent logs for 'Sending BusinessEvent to Audit Agent'")
            ctx.logger.info("   → Watch Audit Agent logs for 'Received BusinessEvent'")
            
            # Wait a bit for audit response
            ctx.logger.info("\n   Waiting 10 seconds for blockchain posting...")
            await asyncio.sleep(10)
        else:
            ctx.logger.info(f"\n   → Confidence {confidence:.2f} < 0.80: No blockchain posting")
            test_state["test_complete"] = True
    else:
        ctx.logger.error(f"   ✗ Error: {msg.error_message}")
        test_state["test_complete"] = True
    
    # Check if we should complete
    if test_state["document_response_received"] and not test_state["test_complete"]:
        await asyncio.sleep(2)
        test_state["test_complete"] = True


@test_agent.on_message(model=AuditResponse)
async def handle_audit_response(ctx: Context, sender: str, msg: AuditResponse):
    """
    This won't normally be called (AuditResponse goes to Document Agent),
    but included for completeness.
    """
    ctx.logger.info("\n5. ℹ️  Received AuditResponse (unexpected - should go to Document Agent)")
    ctx.logger.info(f"   Event ID: {msg.event_id}")
    ctx.logger.info(f"   Success: {msg.success}")
    
    test_state["audit_response_received"] = True
    test_state["test_complete"] = True


@test_agent.on_interval(period=5.0)
async def check_completion(ctx: Context):
    """Check if test is complete and shutdown"""
    if test_state["test_complete"]:
        ctx.logger.info("\n" + "=" * 60)
        ctx.logger.info("Test Complete!")
        ctx.logger.info("=" * 60)
        ctx.logger.info(f"Document Response: {'✓' if test_state['document_response_received'] else '✗'}")
        ctx.logger.info(f"Audit Response: {'✓' if test_state['audit_response_received'] else '-'}")
        ctx.logger.info("\nCheck Document Agent and Audit Agent logs for full flow.")
        ctx.logger.info("=" * 60)
        
        # Shutdown after logging
        await asyncio.sleep(2)
        ctx.logger.info("Shutting down test agent...")
        os._exit(0)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Agent Integration Test with uAgents")
    print("=" * 60)
    print("\nPre-flight checks:")
    print(f"  Document Agent Address: {DOCUMENT_AGENT_ADDRESS or '✗ NOT SET'}")
    print(f"  Test PDF exists: {'✓' if os.path.exists(TEST_PDF_PATH) else '✗'}")
    
    if not DOCUMENT_AGENT_ADDRESS:
        print("\n✗ ERROR: DOCUMENT_AGENT_ADDRESS not set")
        print("  1. Start Document Agent: python document_processing_agent.py")
        print("  2. Copy address from logs (agent1q...)")
        print("  3. Set DOCUMENT_AGENT_ADDRESS in .env or update this script")
        sys.exit(1)
    
    print("\nStarting test agent...")
    print("This will send a real DocumentProcessingRequest using uAgents!\n")
    
    test_agent.run()

