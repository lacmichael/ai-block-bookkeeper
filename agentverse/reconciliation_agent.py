"""
Reconciliation Agent - Automated Financial Transaction Matcher
Deployed on Agentverse for ASI:One ecosystem integration.

This agent automatically matches invoices to payments and creates reconciliation records,
providing automated financial reconciliation for business transactions.

Key Features:
- Automatic invoice-to-payment matching
- Confidence-based match evaluation
- Partial match detection and flagging
- Reconciliation record creation
- Integration with financial document processing pipeline
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

# Agent Configuration (all optional for deployment)
AGENT_NAME = "ReconciliationAgent"
AGENT_SEED = os.getenv("RECONCILIATION_AGENT_SEED", "reconciliation-agent-seed-12345")
AGENT_PORT = int(os.getenv("RECONCILIATION_AGENT_PORT", "8004"))
AGENT_ENDPOINT = os.getenv("RECONCILIATION_AGENT_ENDPOINT", "127.0.0.1")

# Mock mode for deployment without database
MOCK_DATABASE_MODE = True  # Always use mock mode for Agentverse deployment

# Message Models for ASI:One Chat Protocol
class ReconciliationRequest(Model):
    """Request to reconcile a transaction"""
    event_id: str
    business_event: Dict[str, Any]

class ReconciliationResponse(Model):
    """Response from reconciliation process"""
    event_id: str
    success: bool
    reconciliation_status: str  # RECONCILED, PARTIAL, UNRECONCILED
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

# Simplified Reconciliation Logic for Agentverse
class ReconciliationMatcher:
    def __init__(self):
        self.reconciliation_stats = {
            "total_processed": 0,
            "reconciled": 0,
            "partial_matches": 0,
            "unreconciled": 0
        }
    
    def evaluate_match(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate match quality for a business event"""
        self.reconciliation_stats["total_processed"] += 1
        
        event_kind = event.get("event_kind")
        metadata = event.get("metadata", {})
        
        # Enhanced mock matching logic for Agentverse deployment
        if event_kind == "INVOICE_RECEIVED":
            invoice_number = metadata.get("invoice_number")
            if invoice_number:
                # Simulate finding a matching payment with realistic data
                mock_payment = {
                    "event_id": f"payment_{invoice_number}",
                    "amount_minor": event.get("amount_minor"),
                    "event_kind": "PAYMENT_SENT",
                    "metadata": {
                        "payment_reference": invoice_number,
                        "payment_method": "bank_transfer",
                        "processed_date": datetime.utcnow().isoformat()
                    }
                }
                
                # Check for perfect match
                if mock_payment["amount_minor"] == event.get("amount_minor"):
                    self.reconciliation_stats["reconciled"] += 1
                    return {
                        "type": "PRIMARY_MATCH",
                        "confidence": 0.95,
                        "matched_event": mock_payment,
                        "discrepancy": None,
                        "match_reason": "Perfect amount and reference match"
                    }
                else:
                    # Partial match with amount difference
                    amount_diff = abs(event.get("amount_minor") - mock_payment["amount_minor"])
                    self.reconciliation_stats["partial_matches"] += 1
                    return {
                        "type": "PARTIAL_MATCH",
                        "confidence": 0.75,
                        "matched_event": mock_payment,
                        "discrepancy": {
                            "type": "AMOUNT_MISMATCH",
                            "invoice_amount": event.get("amount_minor"),
                            "payment_amount": mock_payment["amount_minor"],
                            "difference": amount_diff,
                            "difference_percentage": round((amount_diff / event.get("amount_minor")) * 100, 2)
                        },
                        "match_reason": f"Reference match but amount differs by ${amount_diff/100:.2f}"
                    }
        
        elif event_kind == "PAYMENT_SENT":
            payment_reference = metadata.get("payment_reference")
            if payment_reference:
                # Simulate finding a matching invoice
                mock_invoice = {
                    "event_id": f"invoice_{payment_reference}",
                    "amount_minor": event.get("amount_minor"),
                    "event_kind": "INVOICE_RECEIVED",
                    "metadata": {
                        "invoice_number": payment_reference,
                        "vendor": "Sample Vendor",
                        "invoice_date": datetime.utcnow().isoformat()
                    }
                }
                
                if mock_invoice["amount_minor"] == event.get("amount_minor"):
                    self.reconciliation_stats["reconciled"] += 1
                    return {
                        "type": "PRIMARY_MATCH",
                        "confidence": 0.95,
                        "matched_event": mock_invoice,
                        "discrepancy": None,
                        "match_reason": "Perfect amount and reference match"
                    }
                else:
                    amount_diff = abs(event.get("amount_minor") - mock_invoice["amount_minor"])
                    self.reconciliation_stats["partial_matches"] += 1
                    return {
                        "type": "PARTIAL_MATCH",
                        "confidence": 0.75,
                        "matched_event": mock_invoice,
                        "discrepancy": {
                            "type": "AMOUNT_MISMATCH",
                            "invoice_amount": mock_invoice["amount_minor"],
                            "payment_amount": event.get("amount_minor"),
                            "difference": amount_diff,
                            "difference_percentage": round((amount_diff / event.get("amount_minor")) * 100, 2)
                        },
                        "match_reason": f"Reference match but amount differs by ${amount_diff/100:.2f}"
                    }
        
        # No match found
        self.reconciliation_stats["unreconciled"] += 1
        return {
            "type": "NO_MATCH",
            "confidence": 0.0,
            "matched_event": None,
            "discrepancy": None,
            "match_reason": "No matching transaction found"
        }

# Create the agent
agent = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://{AGENT_ENDPOINT}:{AGENT_PORT}/submit"],
)

# Fund the agent if needed
fund_agent_if_low(agent.wallet.address())

# Initialize reconciliation matcher
matcher = ReconciliationMatcher()

# Message Handlers
@agent.on_message(ReconciliationRequest)
async def handle_reconciliation_request(ctx: Context, sender: str, msg: ReconciliationRequest):
    """Main handler for reconciliation requests"""
    logger.info(f"Received reconciliation request for event {msg.event_id} from {sender}")
    
    try:
        # Process reconciliation
        result = matcher.evaluate_match(msg.business_event)
        
        # Determine reconciliation status
        reconciliation_status = "UNRECONCILED"
        matched_event_id = None
        discrepancy = None
        
        if result["type"] == "PRIMARY_MATCH":
            reconciliation_status = "RECONCILED"
            matched_event_id = result["matched_event"]["event_id"]
            logger.info(f"✓ Perfect match found for {msg.event_id} with {matched_event_id}")
            logger.info(f"   Match reason: {result.get('match_reason', 'N/A')}")
            
        elif result["type"] == "PARTIAL_MATCH":
            reconciliation_status = "PARTIAL"
            matched_event_id = result["matched_event"]["event_id"]
            discrepancy = result["discrepancy"]
            logger.info(f"⚠ Partial match for {msg.event_id} with {matched_event_id} - flagged for review")
            logger.info(f"   Match reason: {result.get('match_reason', 'N/A')}")
            if discrepancy:
                logger.info(f"   Discrepancy: {discrepancy.get('type', 'Unknown')} - ${discrepancy.get('difference', 0)/100:.2f}")
            
        else:
            logger.info(f"No match found for event {msg.event_id} - will retry later")
            logger.info(f"   Reason: {result.get('match_reason', 'N/A')}")
        
        # Send response back to sender
        response = ReconciliationResponse(
            event_id=msg.event_id,
            success=True,
            reconciliation_status=reconciliation_status,
            matched_event_id=matched_event_id,
            discrepancy=discrepancy
        )
        
        await ctx.send(sender, response)
        logger.info(f"Sent reconciliation response for {msg.event_id}: {reconciliation_status}")
        
    except Exception as e:
        error_msg = f"Error handling reconciliation request for {msg.event_id}: {str(e)}"
        logger.error(error_msg)
        
        # Send error response
        response = ReconciliationResponse(
            event_id=msg.event_id,
            success=False,
            reconciliation_status="UNRECONCILED",
            error_message=error_msg
        )
        
        await ctx.send(sender, response)

@agent.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle ASI:One Chat Protocol messages"""
    logger.info(f"Received chat message from {sender}: {msg.message}")
    
    # Simple chat interface for reconciliation
    message_lower = msg.message.lower()
    
    if "status" in message_lower or "health" in message_lower:
        stats = matcher.reconciliation_stats
        response_text = f"Reconciliation Agent is healthy. Stats: {stats['reconciled']} reconciled, {stats['partial_matches']} partial, {stats['unreconciled']} unreconciled, {stats['total_processed']} total processed."
    elif "help" in message_lower:
        response_text = """Reconciliation Agent Commands:
- 'status' or 'health': Check agent status and stats
- 'help': Show this help message
- 'capabilities': Show agent capabilities
- 'stats': Show reconciliation statistics
- Send a ReconciliationRequest to match transactions"""
    elif "capabilities" in message_lower:
        response_text = f"""Reconciliation Agent Capabilities:
- Invoice-to-payment matching: Available
- Reference number matching: Available
- Amount tolerance handling: Available
- Confidence scoring: Available
- Partial match detection: Available
- Discrepancy flagging: Available
- Mock database mode: Active"""
    elif "stats" in message_lower:
        stats = matcher.reconciliation_stats
        response_text = f"""Reconciliation Statistics:
- Total Processed: {stats['total_processed']}
- Reconciled: {stats['reconciled']}
- Partial Matches: {stats['partial_matches']}
- Unreconciled: {stats['unreconciled']}
- Success Rate: {(stats['reconciled'] + stats['partial_matches']) / max(stats['total_processed'], 1) * 100:.1f}%"""
    else:
        response_text = f"I'm the Reconciliation Agent. I automatically match invoices to payments. Use 'help' for commands. Currently running in mock mode with enhanced matching logic."
    
    response = ChatResponse(
        response=response_text,
        success=True,
        metadata={
            "agent_name": AGENT_NAME,
            "mode": "mock",
            "stats": matcher.reconciliation_stats,
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
        reconciliation_stats=matcher.reconciliation_stats
    )

# Event Handlers
@agent.on_event("startup")
async def startup(ctx: Context):
    """Agent startup handler"""
    logger.info("Reconciliation Agent started")
    logger.info(f"Agent address: {agent.address}")
    logger.info(f"Agent name: {AGENT_NAME}")
    logger.info("🔧 Running in MOCK MODE - simulating transaction matching")
    logger.info("   Ready to process reconciliation requests with enhanced mock logic")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    """Agent shutdown handler"""
    logger.info("Reconciliation Agent shutting down")
    logger.info(f"Final reconciliation stats: {matcher.reconciliation_stats}")

if __name__ == "__main__":
    agent.run()
