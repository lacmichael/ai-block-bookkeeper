# /Users/brandonnguyen/Projects/ai-block-bookkeeper/backend/models/domain_models.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from decimal import Decimal

class PartyRef(BaseModel):
    party_id: str
    role: Literal["VENDOR", "CUSTOMER", "EMPLOYEE", "INTERNAL"]

class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    file_type: Literal["PDF", "CSV", "EXCEL", "IMAGE"]
    file_size: int
    storage_url: str
    sha256: str
    upload_date: datetime
    processed_by_agent: Optional[str] = None
    processing_timestamp: Optional[datetime] = None
    extraction_confidence: Optional[float] = None
    onchain_hash_recorded: Optional[bool] = None
    onchain_digest: Optional[str] = None

class ProcessingState(BaseModel):
    state: Literal["PENDING", "MAPPED", "POSTED_ONCHAIN", "INDEXED", "FAILED"]
    last_error: Optional[str] = None

class BusinessEvent(BaseModel):
    event_id: str
    source_system: Literal["PLAID", "MANUAL", "INVOICE_PORTAL", "SUI", "OTHER"]
    source_id: str
    occurred_at: datetime
    recorded_at: datetime
    event_kind: Literal["BANK_POSTED", "INVOICE_RECEIVED", "PAYMENT_SENT", "REFUND", "ADJUSTMENT"]
    amount_minor: int  # Using int instead of bigint for JSON serialization
    currency: str
    description: Optional[str] = None
    payer: Optional[PartyRef] = None
    payee: Optional[PartyRef] = None
    documents: List[DocumentMetadata] = []
    processing: ProcessingState
    dedupe_key: str
    metadata: Optional[Dict[str, Any]] = None

class Posting(BaseModel):
    line_no: int
    account_code: int
    side: Literal["DEBIT", "CREDIT"]
    amount_minor: int
    currency: str
    department: Optional[str] = None
    project_code: Optional[str] = None
    cost_center: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tax_amount_minor: Optional[int] = None
    tax_jurisdiction: Optional[str] = None

class SuiData(BaseModel):
    digest: Optional[str] = None
    object_id: Optional[str] = None
    checkpoint: Optional[int] = None
    recorded: bool = False
    immutable: bool = False

class JournalEntry(BaseModel):
    entry_id: str
    business_event_id: str
    entry_ts: datetime
    memo_hash: Optional[str] = None
    postings: List[Posting]
    sui: SuiData
    reconciliation_state: Literal["UNRECONCILED", "PARTIAL", "RECONCILED"]
    metadata: Optional[Dict[str, Any]] = None

class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class Party(BaseModel):
    party_id: str
    display_name: str
    type: Literal["VENDOR", "CUSTOMER", "EMPLOYEE", "INTERNAL"]
    legal_name: Optional[str] = None
    tax_id_hash: Optional[str] = None
    email: Optional[str] = None
    address: Optional[Address] = None
    sui_address: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AuditLog(BaseModel):
    log_id: str
    timestamp: datetime
    action: Literal["CREATE", "UPDATE", "POST_ONCHAIN", "RECONCILE", "VERIFY", "DISPUTE"]
    entity_type: Literal["BUSINESS_EVENT", "JOURNAL_ENTRY", "DOCUMENT", "PARTY"]
    entity_id: str
    actor_type: Literal["USER", "AI_AGENT", "SYSTEM"]
    actor_id: str
    request_id: Optional[str] = None
    changes: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None