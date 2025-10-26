"""
Shared message models for agent-to-agent communication.
These models define the structure of messages exchanged between agents.
"""

from typing import Optional, Dict, Any
from uagents import Model


class BusinessEventMessage(Model):
    """
    Message sent from Document Processing Agent to Audit Verification Agent.
    Contains the full business event data for blockchain posting.
    """
    event_id: str
    business_event: Dict[str, Any]  # Full BusinessEvent as dict
    confidence_score: float
    document_id: str


class AuditResponse(Model):
    """
    Response sent from Audit Verification Agent back to Document Processing Agent.
    Contains the result of blockchain posting attempt.
    """
    event_id: str
    document_id: str
    success: bool
    transaction_digest: Optional[str] = None
    error_message: Optional[str] = None
    blockchain_output: Optional[str] = None


class ReconciliationRequest(Model):
    """
    Message sent to Reconciliation Agent to trigger reconciliation for a new transaction.
    Sent from Document Processing Agent after successful blockchain posting.
    """
    event_id: str
    business_event: Dict[str, Any]  # Full BusinessEvent as dict


class ReconciliationResponse(Model):
    """
    Response sent from Reconciliation Agent back to requester.
    Contains the result of reconciliation attempt.
    """
    event_id: str
    success: bool
    reconciliation_status: str  # RECONCILED, PARTIAL, UNRECONCILED
    matched_event_id: Optional[str] = None
    discrepancy: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

