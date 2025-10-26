"""
Database helper functions for reconciliation agent.
Handles querying for unreconciled events and inserting reconciliation records.
"""
import logging
from typing import Dict, Any, Optional, List
from supabase import Client
from datetime import datetime

logger = logging.getLogger(__name__)


async def find_unreconciled_invoices(client: Client, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Find unreconciled INVOICE_RECEIVED and INVOICE_SENT events that are ready for reconciliation.
    Returns events that have been posted on-chain but not yet reconciled.
    """
    try:
        result = client.table("business_events").select("*").in_(
            "event_kind", ["INVOICE_RECEIVED", "INVOICE_SENT"]
        ).eq(
            "processing_state", "POSTED_ONCHAIN"
        ).is_(
            "metadata->>reconciliation_match_id", "null"
        ).order(
            "recorded_at", desc=False
        ).limit(limit).execute()
        
        return result.data if result.data else []
    except Exception as e:
        logger.error(f"Error finding unreconciled invoices: {str(e)}")
        raise


async def find_matching_payment(
    client: Client, 
    invoice_number: str, 
    currency: str
) -> Optional[Dict[str, Any]]:
    """
    Find a matching PAYMENT_SENT event for an invoice.
    Matches on payment_reference == invoice_number and currency.
    Returns first unreconciled payment found.
    """
    try:
        # Query for PAYMENT_SENT with matching reference
        result = client.table("business_events").select("*").eq(
            "event_kind", "PAYMENT_SENT"
        ).eq(
            "processing_state", "POSTED_ONCHAIN"
        ).eq(
            "currency", currency
        ).is_(
            "metadata->>reconciliation_match_id", "null"
        ).limit(1).execute()
        
        # Filter by payment_reference in metadata
        if result.data:
            for event in result.data:
                metadata = event.get("metadata", {})
                if metadata.get("payment_reference") == invoice_number:
                    return event
        
        return None
    except Exception as e:
        logger.error(f"Error finding matching payment for invoice {invoice_number}: {str(e)}")
        raise


async def find_matching_invoice(
    client: Client,
    payment_reference: str,
    currency: str
) -> Optional[Dict[str, Any]]:
    """
    Find a matching INVOICE_RECEIVED or INVOICE_SENT event for a payment.
    Matches on invoice_number == payment_reference and currency.
    Returns first unreconciled invoice found.
    """
    try:
        # Query for INVOICE_RECEIVED and INVOICE_SENT with matching invoice number
        result = client.table("business_events").select("*").in_(
            "event_kind", ["INVOICE_RECEIVED", "INVOICE_SENT"]
        ).eq(
            "processing_state", "POSTED_ONCHAIN"
        ).eq(
            "currency", currency
        ).is_(
            "metadata->>reconciliation_match_id", "null"
        ).limit(1).execute()
        
        # Filter by invoice_number in metadata
        if result.data:
            for event in result.data:
                metadata = event.get("metadata", {})
                if metadata.get("invoice_number") == payment_reference:
                    return event
        
        return None
    except Exception as e:
        logger.error(f"Error finding matching invoice for payment {payment_reference}: {str(e)}")
        raise


async def insert_reconciliation(client: Client, reconciliation_data: Dict[str, Any]) -> str:
    """
    Insert a reconciliation record into the reconciliations table.
    Returns the reconciliation_id.
    """
    try:
        result = client.table("reconciliations").insert(reconciliation_data).execute()
        
        if not result.data:
            raise Exception("Failed to insert reconciliation - no data returned")
        
        reconciliation_id = result.data[0]["reconciliation_id"]
        logger.info(f"Successfully inserted reconciliation: {reconciliation_id}")
        return reconciliation_id
    except Exception as e:
        logger.error(f"Error inserting reconciliation: {str(e)}")
        raise


async def update_event_reconciliation_status(
    client: Client,
    event_id: str,
    status: str,
    matched_event_id: str,
    reconciliation_notes: Dict[str, Any]
) -> None:
    """
    Update a business_event's processing state and add reconciliation metadata.
    Marks the event as reconciled and links it to its matching counterpart.
    """
    try:
        # Get current metadata
        current_event = client.table("business_events").select("metadata").eq(
            "event_id", event_id
        ).single().execute()
        
        metadata = current_event.data.get("metadata", {}) if current_event.data else {}
        
        # Update metadata with reconciliation info
        metadata["reconciliation_match_id"] = matched_event_id
        metadata["reconciliation_notes"] = reconciliation_notes
        metadata["reconciled_at"] = datetime.utcnow().isoformat()
        
        # Update the event
        client.table("business_events").update({
            "processing_state": status,
            "metadata": metadata
        }).eq("event_id", event_id).execute()
        
        logger.info(f"Updated event {event_id} to status {status}")
    except Exception as e:
        logger.error(f"Error updating event reconciliation status for {event_id}: {str(e)}")
        raise


async def get_event_by_id(client: Client, event_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single business event by its ID.
    """
    try:
        result = client.table("business_events").select("*").eq(
            "event_id", event_id
        ).single().execute()
        
        return result.data if result.data else None
    except Exception as e:
        logger.error(f"Error getting event {event_id}: {str(e)}")
        return None

