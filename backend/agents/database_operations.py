"""
Database operations for inserting invoice data into Supabase.
Handles party upserts, business events, and document metadata.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from supabase import Client
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import supabase_config
from models.domain_models import BusinessEvent, PartyRef, DocumentMetadata

logger = logging.getLogger(__name__)


def extract_party_from_event(party_ref: PartyRef, party_type: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Extract party data from BusinessEvent for database insertion"""
    party_data = {
        "party_id": party_ref.party_id,
        "display_name": party_ref.party_id.replace("vendor_", "").replace("customer_", "").replace("_", " ").title(),
        "type": party_type,
    }
    
    # Extract additional party details from metadata
    if party_type == "VENDOR" and metadata.get("vendor_details"):
        vendor = metadata["vendor_details"]
        party_data["legal_name"] = vendor.get("legal_name")
        party_data["email"] = vendor.get("email")
        
        # Handle address
        if vendor.get("address") and isinstance(vendor["address"], dict):
            addr = vendor["address"]
            party_data["street"] = addr.get("street")
            party_data["city"] = addr.get("city")
            party_data["state"] = addr.get("state")
            party_data["postal_code"] = addr.get("postal_code")
            party_data["country"] = addr.get("country")
    
    elif party_type == "CUSTOMER" and metadata.get("payer_details"):
        payer = metadata["payer_details"]
        party_data["legal_name"] = payer.get("legal_name")
        party_data["email"] = payer.get("email")
        
        # Handle address
        if payer.get("address") and isinstance(payer["address"], dict):
            addr = payer["address"]
            party_data["street"] = addr.get("street")
            party_data["city"] = addr.get("city")
            party_data["state"] = addr.get("state")
            party_data["postal_code"] = addr.get("postal_code")
            party_data["country"] = addr.get("country")
    
    return party_data


async def upsert_party(client: Client, party_data: Dict[str, Any]) -> str:
    """
    Upsert party (vendor/payer) into the parties table.
    Returns the party_id.
    """
    try:
        party_id = party_data["party_id"]
        
        # Check if party exists
        result = client.table("parties").select("party_id").eq("party_id", party_id).execute()
        
        if result.data and len(result.data) > 0:
            # Update existing party
            logger.info(f"Updating existing party: {party_id}")
            client.table("parties").update(party_data).eq("party_id", party_id).execute()
        else:
            # Insert new party
            logger.info(f"Inserting new party: {party_id}")
            client.table("parties").insert(party_data).execute()
        
        return party_id
    
    except Exception as e:
        logger.error(f"Error upserting party {party_data.get('party_id')}: {str(e)}")
        raise


def transform_business_event_to_db(business_event: BusinessEvent, sui_digest: str) -> Dict[str, Any]:
    """Transform BusinessEvent model to database row format"""
    event_data = {
        "event_id": business_event.event_id,
        "source_system": business_event.source_system,
        "source_id": business_event.source_id,
        "occurred_at": business_event.occurred_at.isoformat(),
        "recorded_at": business_event.recorded_at.isoformat(),
        "event_kind": business_event.event_kind,
        "amount_minor": business_event.amount_minor,
        "currency": business_event.currency,
        "description": business_event.description,
        "processing_state": "POSTED_ONCHAIN",  # Set to posted on chain
        "dedupe_key": business_event.dedupe_key,
        "metadata": business_event.metadata or {},
    }
    
    # Add party references if present
    if business_event.payer:
        event_data["payer_party_id"] = business_event.payer.party_id
        event_data["payer_role"] = business_event.payer.role
    
    if business_event.payee:
        event_data["payee_party_id"] = business_event.payee.party_id
        event_data["payee_role"] = business_event.payee.role
    
    # Add Sui digest to metadata
    if "blockchain" not in event_data["metadata"]:
        event_data["metadata"]["blockchain"] = {}
    event_data["metadata"]["blockchain"]["sui_digest"] = sui_digest
    
    return event_data


async def insert_business_event(client: Client, event_data: Dict[str, Any]) -> str:
    """
    Insert business_events record into the database.
    Returns the event_id.
    """
    try:
        event_id = event_data["event_id"]
        logger.info(f"Inserting business event: {event_id}")
        
        result = client.table("business_events").insert(event_data).execute()
        
        if not result.data:
            raise Exception("Failed to insert business event - no data returned")
        
        logger.info(f"Successfully inserted business event: {event_id}")
        return event_id
    
    except Exception as e:
        logger.error(f"Error inserting business event {event_data.get('event_id')}: {str(e)}")
        raise


def transform_document_to_db(document: DocumentMetadata, business_event_id: str, sui_digest: str, file_path: str = None) -> Dict[str, Any]:
    """Transform DocumentMetadata model to database row format"""
    doc_data = {
        "document_id": document.document_id,
        "business_event_id": business_event_id,
        "filename": document.filename,
        "file_type": document.file_type,
        "file_size": document.file_size,
        "storage_url": document.storage_url,
        "sha256": document.sha256,
        "upload_date": document.upload_date.isoformat(),
        "processed_by_agent": document.processed_by_agent,
        "processing_timestamp": document.processing_timestamp.isoformat() if document.processing_timestamp else None,
        "extraction_confidence": float(document.extraction_confidence) if document.extraction_confidence else None,
        "onchain_hash_recorded": True,  # Mark as recorded on chain
        "onchain_digest": sui_digest,
    }
    
    return doc_data


async def insert_document_metadata(client: Client, doc_data: Dict[str, Any]) -> str:
    """
    Insert document_metadata record into the database.
    Returns the document_id.
    """
    try:
        document_id = doc_data["document_id"]
        logger.info(f"Inserting document metadata: {document_id}")
        
        result = client.table("document_metadata").insert(doc_data).execute()
        
        if not result.data:
            raise Exception("Failed to insert document metadata - no data returned")
        
        logger.info(f"Successfully inserted document metadata: {document_id}")
        return document_id
    
    except Exception as e:
        logger.error(f"Error inserting document metadata {doc_data.get('document_id')}: {str(e)}")
        raise


async def insert_invoice_to_supabase(business_event: BusinessEvent, sui_digest: str, file_path: str = None):
    """
    Orchestrate all database inserts for an invoice:
    1. Upsert parties (vendor and payer)
    2. Insert business_event with POSTED_ONCHAIN state
    3. Insert document_metadata with onchain_digest and file_path
    
    This function ensures all related data is inserted in the correct order.
    """
    try:
        logger.info(f"Starting Supabase insert for event {business_event.event_id} with Sui digest {sui_digest}")
        
        # Get Supabase client with service role (admin access)
        client = supabase_config.get_client(use_service_role=True)
        
        # Step 1: Upsert parties (vendor and payer if present)
        if business_event.payee:
            party_data = extract_party_from_event(
                business_event.payee, 
                "VENDOR", 
                business_event.metadata or {}
            )
            await upsert_party(client, party_data)
        
        if business_event.payer:
            party_data = extract_party_from_event(
                business_event.payer,
                "CUSTOMER",
                business_event.metadata or {}
            )
            await upsert_party(client, party_data)
        
        # Step 2: Insert business_event with processing_state="POSTED_ONCHAIN"
        event_data = transform_business_event_to_db(business_event, sui_digest)
        await insert_business_event(client, event_data)
        
        # Step 3: Insert document_metadata with onchain_digest and file_path
        if business_event.documents and len(business_event.documents) > 0:
            logger.info(f"Inserting document_metadata for {len(business_event.documents)} document(s)")
            doc_data = transform_document_to_db(
                business_event.documents[0],
                business_event.event_id,
                sui_digest,
                file_path
            )
            await insert_document_metadata(client, doc_data)
            logger.info(f"✓ Document metadata inserted successfully")
        else:
            logger.warning(f"No documents found in business_event - skipping document_metadata insert")
        
        logger.info(f"✓ Successfully completed all Supabase inserts for event {business_event.event_id}")
        
    except Exception as e:
        logger.error(f"Error in insert_invoice_to_supabase: {str(e)}")
        logger.error(f"Sui digest for recovery: {sui_digest}")
        raise Exception(f"Database insertion failed: {str(e)}")

