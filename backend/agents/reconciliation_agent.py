"""
Reconciliation Agent - Automatically matches invoices to payments
Uses Fetch.ai uAgents framework for agent-to-agent communication.

This agent:
1. Receives new transaction events from Document Processing Agent
2. Searches for matching counterpart transactions (invoice ↔ payment)
3. Uses matcher.py logic to evaluate match quality
4. Inserts reconciliation records and updates event statuses
5. Sends response back to requester
"""
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Load environment variables
load_dotenv()

# Add parent directory for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.shared_models import ReconciliationRequest, ReconciliationResponse
from agents.reconciliation.matcher import evaluate_match
from agents.reconciliation.database_helpers import (
    find_matching_payment,
    find_matching_invoice,
    insert_reconciliation,
    update_event_reconciliation_status,
    get_event_by_id
)
from config.database import supabase_config
from domain.models import BusinessEvent, MatchResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment configuration
DOCUMENT_AGENT_ADDRESS = os.getenv("DOCUMENT_AGENT_ADDRESS", "")

# Create the agent
agent = Agent(
    name="ReconciliationAgent",
    seed="reconciliation-agent-seed-phrase-12345",
    port=8004,
    endpoint=["http://127.0.0.1:8004/submit"],
)

# Fund the agent if needed
fund_agent_if_low(agent.wallet.address())


def reconstruct_business_event(event_dict: Dict[str, Any]) -> BusinessEvent:
    """
    Reconstruct a BusinessEvent from a dictionary.
    Handles both UUID and string event_id formats.
    """
    from uuid import UUID
    
    # Handle event_id - convert string to UUID if needed
    event_id = event_dict.get("event_id")
    if isinstance(event_id, str):
        try:
            event_id = UUID(event_id)
        except ValueError:
            # If not a valid UUID, keep as string (domain model will validate)
            pass
    
    # Parse datetime strings
    occurred_at = event_dict.get("occurred_at")
    if isinstance(occurred_at, str):
        occurred_at = datetime.fromisoformat(occurred_at.replace('Z', '+00:00'))
    
    recorded_at = event_dict.get("recorded_at")
    if isinstance(recorded_at, str):
        recorded_at = datetime.fromisoformat(recorded_at.replace('Z', '+00:00'))
    
    return BusinessEvent(
        event_id=event_id,
        source_system=event_dict.get("source_system", ""),
        source_id=event_dict.get("source_id", ""),
        occurred_at=occurred_at,
        recorded_at=recorded_at,
        event_kind=event_dict.get("event_kind"),
        amount_minor=event_dict.get("amount_minor"),
        currency=event_dict.get("currency", "USD"),
        processing={"state": "MAPPED"},  # Use MAPPED instead of POSTED_ONCHAIN
        dedupe_key=event_dict.get("dedupe_key", ""),
        metadata=event_dict.get("metadata", {})
    )


async def process_reconciliation(event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main reconciliation logic - finds matching transactions and creates reconciliation records.
    Returns reconciliation result dict.
    """
    try:
        # Get Supabase client
        client = supabase_config.get_client(use_service_role=True)
        
        # Parse event details
        event_kind = event_dict.get("event_kind")
        event_id = event_dict.get("event_id")
        currency = event_dict.get("currency", "USD")
        metadata = event_dict.get("metadata", {})
        
        logger.info(f"Processing reconciliation for {event_kind} event {event_id}")
        
        # Find matching counterpart based on event type
        counterpart_event = None
        
        if event_kind == "INVOICE_RECEIVED":
            # Find matching payment
            invoice_number = metadata.get("invoice_number")
            if not invoice_number:
                logger.warning(f"Invoice {event_id} has no invoice_number - cannot reconcile")
                return {
                    "success": True,
                    "reconciliation_status": "UNRECONCILED",
                    "error_message": "No invoice number found in metadata"
                }
            
            counterpart_event = await find_matching_payment(client, invoice_number, currency)
            
        elif event_kind == "INVOICE_SENT":
            # Find matching payment for sent invoice
            invoice_number = metadata.get("invoice_number")
            if not invoice_number:
                logger.warning(f"Invoice {event_id} has no invoice_number - cannot reconcile")
                return {
                    "success": True,
                    "reconciliation_status": "UNRECONCILED",
                    "error_message": "No invoice number found in metadata"
                }
            
            counterpart_event = await find_matching_payment(client, invoice_number, currency)
            
        elif event_kind == "PAYMENT_SENT":
            # Find matching invoice
            payment_reference = metadata.get("payment_reference")
            if not payment_reference:
                logger.warning(f"Payment {event_id} has no payment_reference - cannot reconcile")
                return {
                    "success": True,
                    "reconciliation_status": "UNRECONCILED",
                    "error_message": "No payment reference found in metadata"
                }
            
            counterpart_event = await find_matching_invoice(client, payment_reference, currency)
        
        else:
            logger.warning(f"Event {event_id} is type {event_kind} - not supported for reconciliation")
            return {
                "success": True,
                "reconciliation_status": "UNRECONCILED",
                "error_message": f"Event kind {event_kind} not supported for reconciliation"
            }
        
        # If no counterpart found, log and return
        if not counterpart_event:
            logger.info(f"No matching counterpart found for event {event_id} - will retry later")
            return {
                "success": True,
                "reconciliation_status": "UNRECONCILED",
                "matched_event_id": None
            }
        
        # Reconstruct domain models for matcher
        event = reconstruct_business_event(event_dict)
        counterpart = reconstruct_business_event(counterpart_event)
        
        # Evaluate match quality using matcher logic
        match_result: MatchResult = evaluate_match(event, counterpart)
        
        logger.info(f"Match result: {match_result.type} with confidence {match_result.confidence}")
        
        # Handle based on match type
        if match_result.type == "PRIMARY_MATCH":
            # Perfect match - create reconciliation record
            reconciliation_data = {
                "invoice_event_id": str(match_result.invoice_id),
                "payment_event_id": str(match_result.payment_id),
                "match_type": "PRIMARY_MATCH",
                "confidence": float(match_result.confidence),
                "amount_difference": 0,
                "reconciled_by": "reconciliation-agent",
                "metadata": {
                    "reconciliation_timestamp": datetime.utcnow().isoformat(),
                    "match_confidence": float(match_result.confidence)
                }
            }
            
            # Insert reconciliation record
            reconciliation_id = await insert_reconciliation(client, reconciliation_data)
            
            # Update both events to POSTED_ONCHAIN status (keep same state, just add reconciliation metadata)
            await update_event_reconciliation_status(
                client,
                str(match_result.invoice_id),
                "POSTED_ONCHAIN",
                str(match_result.payment_id),
                {"reconciliation_id": reconciliation_id, "match_type": "PRIMARY_MATCH"}
            )
            
            await update_event_reconciliation_status(
                client,
                str(match_result.payment_id),
                "POSTED_ONCHAIN",
                str(match_result.invoice_id),
                {"reconciliation_id": reconciliation_id, "match_type": "PRIMARY_MATCH"}
            )
            
            logger.info(f"✓ Successfully reconciled {event_id} with {counterpart_event['event_id']}")
            
            return {
                "success": True,
                "reconciliation_status": "RECONCILED",
                "matched_event_id": counterpart_event["event_id"],
                "reconciliation_id": reconciliation_id
            }
        
        elif match_result.type == "PARTIAL_MATCH":
            # Partial match - create reconciliation but flag for review
            discrepancy_data = None
            amount_diff = 0
            
            if match_result.discrepancy:
                discrepancy_data = {
                    "type": match_result.discrepancy.type,
                    "invoice_amount": match_result.discrepancy.invoice_amount,
                    "payment_amount": match_result.discrepancy.payment_amount,
                    "difference": match_result.discrepancy.difference
                }
                amount_diff = abs(match_result.discrepancy.difference)
            
            reconciliation_data = {
                "invoice_event_id": str(match_result.invoice_id),
                "payment_event_id": str(match_result.payment_id),
                "match_type": "PARTIAL_MATCH",
                "confidence": float(match_result.confidence),
                "amount_difference": amount_diff,
                "discrepancy": discrepancy_data,
                "reconciled_by": "reconciliation-agent",
                "metadata": {
                    "reconciliation_timestamp": datetime.utcnow().isoformat(),
                    "match_confidence": float(match_result.confidence),
                    "requires_review": True
                }
            }
            
            # Insert reconciliation record
            reconciliation_id = await insert_reconciliation(client, reconciliation_data)
            
            # Update both events to POSTED_ONCHAIN status (keep same state, just add reconciliation metadata)
            await update_event_reconciliation_status(
                client,
                str(match_result.invoice_id),
                "POSTED_ONCHAIN",
                str(match_result.payment_id),
                {
                    "reconciliation_id": reconciliation_id,
                    "match_type": "PARTIAL_MATCH",
                    "discrepancy": discrepancy_data
                }
            )
            
            await update_event_reconciliation_status(
                client,
                str(match_result.payment_id),
                "POSTED_ONCHAIN",
                str(match_result.invoice_id),
                {
                    "reconciliation_id": reconciliation_id,
                    "match_type": "PARTIAL_MATCH",
                    "discrepancy": discrepancy_data
                }
            )
            
            logger.info(f"⚠ Partial match for {event_id} - flagged for review")
            
            return {
                "success": True,
                "reconciliation_status": "PARTIAL",
                "matched_event_id": counterpart_event["event_id"],
                "discrepancy": discrepancy_data,
                "reconciliation_id": reconciliation_id
            }
        
        else:  # NO_MATCH
            logger.info(f"No valid match found for event {event_id}")
            return {
                "success": True,
                "reconciliation_status": "UNRECONCILED",
                "matched_event_id": None
            }
    
    except Exception as e:
        logger.error(f"Error during reconciliation: {str(e)}")
        return {
            "success": False,
            "reconciliation_status": "UNRECONCILED",
            "error_message": str(e)
        }


@agent.on_message(ReconciliationRequest)
async def handle_reconciliation_request(ctx: Context, sender: str, msg: ReconciliationRequest):
    """
    Main handler for reconciliation requests.
    Receives new transaction events and attempts to match them with counterparts.
    """
    logger.info(f"Received reconciliation request for event {msg.event_id} from {sender}")
    
    try:
        # Process reconciliation
        result = await process_reconciliation(msg.business_event)
        
        # Send response back to sender
        response = ReconciliationResponse(
            event_id=msg.event_id,
            success=result["success"],
            reconciliation_status=result["reconciliation_status"],
            matched_event_id=result.get("matched_event_id"),
            discrepancy=result.get("discrepancy"),
            error_message=result.get("error_message")
        )
        
        await ctx.send(sender, response)
        logger.info(f"Sent reconciliation response for {msg.event_id}: {result['reconciliation_status']}")
        
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


@agent.on_event("startup")
async def startup(ctx: Context):
    """Agent startup handler"""
    logger.info("Reconciliation Agent started")
    logger.info(f"Agent address: {agent.address}")
    logger.info("Ready to process reconciliation requests")


@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    """Agent shutdown handler"""
    logger.info("Reconciliation Agent shutting down")


if __name__ == "__main__":
    agent.run()

