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

