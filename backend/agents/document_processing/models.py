# /Users/brandonnguyen/Projects/ai-block-bookkeeper/backend/agents/document_processing/models.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
from datetime import datetime

# Try to import uagents Model, fallback to BaseModel if not available
try:
    from uagents import Model
except ImportError:
    Model = BaseModel

class DocumentProcessingRequest(BaseModel):
    """Request message for document processing"""
    document_id: str
    file_path: str
    filename: str
    file_size: int
    file_type: Literal["PDF", "CSV", "EXCEL", "IMAGE"]
    upload_timestamp: datetime
    requester_id: str
    metadata: Optional[Dict[str, Any]] = None

class DocumentProcessingResponse(BaseModel):
    """Response message for document processing"""
    document_id: str
    success: bool
    business_event: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time_seconds: float
    extracted_data: Optional[Dict[str, Any]] = None
    sui_digest: Optional[str] = None  # Sui transaction digest
    supabase_inserted: bool = False   # Track if DB insert succeeded

class AuditVerificationRequest(Model):
    """Request to audit agent to post to Sui blockchain"""
    business_event: Dict[str, Any]  # Serialized BusinessEvent
    request_id: str

class AuditVerificationResponse(Model):
    """Response from audit agent after Sui posting"""
    request_id: str
    success: bool
    sui_digest: Optional[str] = None
    error_message: Optional[str] = None
