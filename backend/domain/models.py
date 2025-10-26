# Domain models for the AI Block Bookkeeper
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class EventKind(str, Enum):
    INVOICE_RECEIVED = "INVOICE_RECEIVED"
    INVOICE_SENT = "INVOICE_SENT"
    PAYMENT_SENT = "PAYMENT_SENT"

class ProcessingState(str, Enum):
    PENDING = "PENDING"
    MAPPED = "MAPPED"
    RECONCILED = "RECONCILED"
    FLAGGED_FOR_REVIEW = "FLAGGED_FOR_REVIEW"

class Processing(BaseModel):
    state: ProcessingState

class BusinessEvent(BaseModel):
    event_id: UUID
    source_system: str
    source_id: str
    occurred_at: datetime
    recorded_at: datetime
    event_kind: EventKind
    amount_minor: int  # Amount in minor units (cents)
    currency: str
    processing: Processing
    dedupe_key: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DiscrepancyType(str, Enum):
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"

class Discrepancy(BaseModel):
    type: DiscrepancyType
    invoice_amount: int
    payment_amount: int
    difference: int

class MatchResultType(str, Enum):
    PRIMARY_MATCH = "PRIMARY_MATCH"
    PARTIAL_MATCH = "PARTIAL_MATCH"
    NO_MATCH = "NO_MATCH"

class MatchResult(BaseModel):
    type: MatchResultType
    confidence: Optional[float] = None
    invoice_id: Optional[UUID] = None
    payment_id: Optional[UUID] = None
    discrepancy: Optional[Discrepancy] = None
