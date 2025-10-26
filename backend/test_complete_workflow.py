#!/usr/bin/env python3
"""
Complete workflow test: Document Processing → Audit Verification → Reconciliation
Tests the entire pipeline from invoice processing to reconciliation matching.
"""
import asyncio
import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv
from uagents import Agent, Context

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

from agents.document_processing.models import DocumentProcessingRequest, DocumentProcessingResponse
from agents.shared_models import ReconciliationRequest, ReconciliationResponse
from config.database import supabase_config

# Configuration
DOCUMENT_AGENT_ADDRESS = os.getenv("DOCUMENT_AGENT_ADDRESS", "")
RECONCILIATION_AGENT_ADDRESS = os.getenv("RECONCILIATION_AGENT_ADDRESS", "")

# Create test agent
test_agent = Agent(
    name="WorkflowTestAgent",
    seed="workflow-test-agent-seed-12345",
    port=8998,
    endpoint=["http://127.0.0.1:8998/submit"]
)

# Track test state
test_state = {
    "document_response_received": False,
    "reconciliation_response_received": False,
    "test_complete": False,
    "invoice_event_id": None,
    "payment_event_id": None
}

def create_mock_invoice_pdf():
    """Create a mock invoice PDF file that matches our payment"""
    import tempfile
    import hashlib
    
    # Create a simple text-based "PDF" content for testing
    invoice_content = f"""
INVOICE

Invoice Number: INV-2024-001
Date: {datetime.now().strftime('%Y-%m-%d')}
Due Date: {(datetime.now().replace(day=1) + timedelta(days=32)).strftime('%Y-%m-%d')}

Bill To:
NnovateSoft Solutions LLC
123 Innovation Drive
San Francisco, CA 94105

From:
Booksy Inc.
456 Business Plaza
New York, NY 10001

Description: Software licensing and services
Amount: $5,261.16

Payment Terms: NET 30
Reference: REF-2024-001
"""
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False)
    temp_file.write(invoice_content)
    temp_file.close()
    
    return temp_file.name

async def verify_existing_payment():
    """Verify the existing payment transaction exists"""
    try:
        client = supabase_config.get_client(use_service_role=True)
        
        # Find the payment we created earlier
        result = client.table("business_events")\
            .select("*")\
            .eq("event_kind", "PAYMENT_SENT")\
            .ilike("description", "%Booksy%")\
            .order("recorded_at", desc=True)\
            .limit(1)\
            .execute()
        
        if result.data:
            payment = result.data[0]
            test_state["payment_event_id"] = payment["event_id"]
            print(f"✅ Found existing payment: {payment['event_id']}")
            print(f"   Amount: ${payment['amount_minor']/100:.2f}")
            print(f"   Description: {payment['description']}")
            return True
        else:
            print("❌ No existing payment found")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying payment: {e}")
        return False

@test_agent.on_event("startup")
async def startup(ctx: Context):
    """Test agent startup"""
    ctx.logger.info("=" * 80)
    ctx.logger.info("COMPLETE WORKFLOW TEST: Document → Audit → Reconciliation")
    ctx.logger.info("=" * 80)
    ctx.logger.info(f"Test Agent address: {test_agent.address}")
    
    # Check configuration
    ctx.logger.info("\n1. Checking Configuration...")
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    audit_address = os.getenv("AUDIT_AGENT_ADDRESS")
    doc_address = DOCUMENT_AGENT_ADDRESS
    recon_address = RECONCILIATION_AGENT_ADDRESS
    
    ctx.logger.info(f"   ANTHROPIC_API_KEY: {'✓ Set' if anthropic_key else '✗ Missing'}")
    ctx.logger.info(f"   AUDIT_AGENT_ADDRESS: {audit_address if audit_address else '✗ Missing'}")
    ctx.logger.info(f"   DOCUMENT_AGENT_ADDRESS: {doc_address if doc_address else '✗ Missing'}")
    ctx.logger.info(f"   RECONCILIATION_AGENT_ADDRESS: {recon_address if recon_address else '✗ Missing'}")
    
    if not doc_address:
        ctx.logger.error("\n✗ DOCUMENT_AGENT_ADDRESS not set!")
        return
    
    if not recon_address:
        ctx.logger.error("\n✗ RECONCILIATION_AGENT_ADDRESS not set!")
        return
    
    # Verify existing payment
    ctx.logger.info("\n2. Verifying existing payment transaction...")
    payment_exists = await verify_existing_payment()
    
    if not payment_exists:
        ctx.logger.error("✗ No existing payment found - create one first!")
        return
    
    # Create mock invoice
    ctx.logger.info("\n3. Creating mock invoice document...")
    invoice_file = create_mock_invoice_pdf()
    ctx.logger.info(f"   Created: {invoice_file}")
    
    # Send test request after a short delay
    await asyncio.sleep(2)
    await send_invoice_processing_request(ctx, invoice_file)

async def send_invoice_processing_request(ctx: Context, invoice_file: str):
    """Send an invoice processing request to the Document Agent"""
    ctx.logger.info("\n4. Sending Invoice Processing Request...")
    
    request = DocumentProcessingRequest(
        document_id=f"test_invoice_{uuid4().hex[:8]}",
        file_path=os.path.abspath(invoice_file),
        filename="booksy_invoice_2024_001.pdf",
        file_size=os.path.getsize(invoice_file),
        file_type="PDF",
        upload_timestamp=datetime.now(timezone.utc),
        requester_id="workflow_test_agent"
    )
    
    ctx.logger.info(f"   → Sending to: {DOCUMENT_AGENT_ADDRESS}")
    ctx.logger.info(f"   → Document ID: {request.document_id}")
    
    await ctx.send(DOCUMENT_AGENT_ADDRESS, request)
    ctx.logger.info("   ✓ Request sent! Waiting for response...")

@test_agent.on_message(model=DocumentProcessingResponse)
async def handle_document_response(ctx: Context, sender: str, msg: DocumentProcessingResponse):
    """Handle response from Document Agent"""
    ctx.logger.info("\n5. ✓ Received DocumentProcessingResponse from Document Agent")
    ctx.logger.info(f"   Sender: {sender}")
    ctx.logger.info(f"   Document ID: {msg.document_id}")
    ctx.logger.info(f"   Success: {msg.success}")
    ctx.logger.info(f"   Processing Time: {msg.processing_time_seconds:.2f}s")
    ctx.logger.info(f"   Supabase Inserted: {msg.supabase_inserted}")
    
    test_state["document_response_received"] = True
    
    if msg.success and msg.business_event:
        # Extract key info
        amount = msg.business_event.get('amount_minor', 0)
        currency = msg.business_event.get('currency', 'USD')
        event_id = msg.business_event.get('event_id', 'N/A')
        event_kind = msg.business_event.get('event_kind', 'N/A')
        
        test_state["invoice_event_id"] = event_id
        
        ctx.logger.info(f"   Event ID: {event_id}")
        ctx.logger.info(f"   Event Kind: {event_kind}")
        ctx.logger.info(f"   Amount: {currency} ${amount/100:.2f}")
        
        if msg.supabase_inserted:
            ctx.logger.info("   ✓ Invoice inserted to Supabase")
            ctx.logger.info("   → Should trigger reconciliation automatically")
            ctx.logger.info("   → Watch for reconciliation agent logs")
            
            # Wait for reconciliation
            ctx.logger.info("\n   Waiting 15 seconds for reconciliation...")
            await asyncio.sleep(15)
        else:
            ctx.logger.warning("   ⚠️ Invoice not inserted to Supabase")
    else:
        ctx.logger.error(f"   ✗ Error: {msg.error_message}")
    
    test_state["test_complete"] = True

@test_agent.on_message(model=ReconciliationResponse)
async def handle_reconciliation_response(ctx: Context, sender: str, msg: ReconciliationResponse):
    """Handle response from Reconciliation Agent"""
    ctx.logger.info("\n6. ✓ Received ReconciliationResponse from Reconciliation Agent")
    ctx.logger.info(f"   Sender: {sender}")
    ctx.logger.info(f"   Event ID: {msg.event_id}")
    ctx.logger.info(f"   Success: {msg.success}")
    ctx.logger.info(f"   Reconciliation Status: {msg.reconciliation_status}")
    
    if msg.matched_event_id:
        ctx.logger.info(f"   Matched Event ID: {msg.matched_event_id}")
    
    if msg.discrepancy:
        ctx.logger.info(f"   Discrepancy: {msg.discrepancy}")
    
    if msg.error_message:
        ctx.logger.error(f"   Error: {msg.error_message}")
    
    test_state["reconciliation_response_received"] = True
    test_state["test_complete"] = True

async def verify_reconciliation_results():
    """Verify reconciliation results in database"""
    try:
        ctx.logger.info("\n7. Verifying reconciliation results in database...")
        
        client = supabase_config.get_client(use_service_role=True)
        
        # Check reconciliation records
        recon_result = client.table("reconciliations")\
            .select("*")\
            .order("reconciled_at", desc=True)\
            .limit(5)\
            .execute()
        
        if recon_result.data:
            ctx.logger.info(f"   ✓ Found {len(recon_result.data)} reconciliation record(s)")
            for recon in recon_result.data:
                ctx.logger.info(f"   - Reconciliation ID: {recon['reconciliation_id']}")
                ctx.logger.info(f"     Invoice Event: {recon['invoice_event_id']}")
                ctx.logger.info(f"     Payment Event: {recon['payment_event_id']}")
                ctx.logger.info(f"     Match Type: {recon['match_type']}")
                ctx.logger.info(f"     Confidence: {recon['confidence']}")
        else:
            ctx.logger.warning("   ⚠️ No reconciliation records found")
        
        # Check event statuses
        if test_state["invoice_event_id"]:
            event_result = client.table("business_events")\
                .select("*")\
                .eq("event_id", test_state["invoice_event_id"])\
                .execute()
            
            if event_result.data:
                event = event_result.data[0]
                ctx.logger.info(f"   Invoice Event Status: {event.get('processing_state', 'N/A')}")
        
        if test_state["payment_event_id"]:
            event_result = client.table("business_events")\
                .select("*")\
                .eq("event_id", test_state["payment_event_id"])\
                .execute()
            
            if event_result.data:
                event = event_result.data[0]
                ctx.logger.info(f"   Payment Event Status: {event.get('processing_state', 'N/A')}")
                
    except Exception as e:
        ctx.logger.error(f"   ✗ Error verifying results: {e}")

@test_agent.on_interval(period=5.0)
async def check_completion(ctx: Context):
    """Check if test is complete and shutdown"""
    if test_state["test_complete"]:
        ctx.logger.info("\n" + "=" * 80)
        ctx.logger.info("WORKFLOW TEST COMPLETE!")
        ctx.logger.info("=" * 80)
        ctx.logger.info(f"Document Processing: {'✓' if test_state['document_response_received'] else '✗'}")
        ctx.logger.info(f"Reconciliation: {'✓' if test_state['reconciliation_response_received'] else '✗'}")
        
        # Verify results
        await verify_reconciliation_results()
        
        ctx.logger.info("\nCheck all agent logs for complete workflow details.")
        ctx.logger.info("=" * 80)
        
        # Cleanup
        if 'invoice_file' in locals():
            try:
                os.unlink(invoice_file)
                ctx.logger.info("Cleaned up temporary invoice file")
            except:
                pass
        
        # Shutdown after logging
        await asyncio.sleep(2)
        ctx.logger.info("Shutting down test agent...")
        os._exit(0)

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("COMPLETE WORKFLOW TEST")
    print("=" * 80)
    print("\nThis test will:")
    print("1. Process a mock invoice through Document Agent")
    print("2. Send it to Audit Agent for blockchain posting")
    print("3. Insert to Supabase database")
    print("4. Trigger Reconciliation Agent")
    print("5. Match invoice to existing payment")
    print("6. Create reconciliation records")
    print("\nPre-flight checks:")
    print(f"  Document Agent Address: {DOCUMENT_AGENT_ADDRESS or '✗ NOT SET'}")
    print(f"  Reconciliation Agent Address: {RECONCILIATION_AGENT_ADDRESS or '✗ NOT SET'}")
    
    if not DOCUMENT_AGENT_ADDRESS or not RECONCILIATION_AGENT_ADDRESS:
        print("\n✗ ERROR: Agent addresses not set")
        print("  1. Start Document Agent: python document_processing_agent.py")
        print("  2. Start Reconciliation Agent: python reconciliation_agent.py")
        print("  3. Set addresses in .env file")
        sys.exit(1)
    
    print("\nStarting workflow test agent...")
    print("This will test the complete pipeline!\n")
    
    test_agent.run()

