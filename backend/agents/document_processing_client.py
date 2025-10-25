import os
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import pdfplumber
import anthropic

from .document_processing.models import (
    DocumentProcessingRequest, 
    DocumentProcessingResponse
)
from .document_processing.prompts import INVOICE_EXTRACTION_PROMPT
from models.domain_models import BusinessEvent, ProcessingState, PartyRef

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessingClient:
    """Client for handling document processing operations"""
    
    def __init__(self, anthropic_api_key: str):
        """Initialize the document processing client"""
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        logger.info("Document Processing Client initialized")
    
    def extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber"""
        try:
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    async def extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """Extract structured invoice data using AI"""
        prompt = INVOICE_EXTRACTION_PROMPT.format(text=text)

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse JSON response
            response_text = response.content[0].text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error extracting invoice data: {str(e)}")
            return {"error": str(e)}
    
    def create_business_event(
        self, 
        request: DocumentProcessingRequest, 
        extracted_data: Dict[str, Any]
    ) -> BusinessEvent:
        """Create a BusinessEvent from the extracted data"""
        
        # Create party reference for vendor (if available)
        vendor_party_ref = None
        if extracted_data.get("vendor_name"):
            vendor_party_ref = PartyRef(
                party_id=f"vendor_{extracted_data['vendor_name'].lower().replace(' ', '_')}",
                role="VENDOR"
            )
        
        # Convert amount to minor units (cents)
        amount_minor = 0
        if extracted_data.get("total_amount"):
            amount_minor = int(extracted_data["total_amount"] * 100)
        
        # Create business event
        business_event = BusinessEvent(
            event_id=str(uuid.uuid4()),
            source_system="INVOICE_PORTAL",
            source_id=extracted_data.get("invoice_number") or request.document_id,
            occurred_at=extracted_data.get("invoice_date") or request.upload_timestamp,
            recorded_at=datetime.utcnow(),
            event_kind="INVOICE_RECEIVED",
            amount_minor=amount_minor,
            currency=extracted_data.get("currency") or "USD",
            description=f"Invoice from {extracted_data.get('vendor_name')}" if extracted_data.get("vendor_name") else "Invoice",
            payee=vendor_party_ref,
            documents=[],  # No document storage needed
            processing=ProcessingState(
                state="MAPPED",
                last_error=None
            ),
            dedupe_key=f"INVOICE_PORTAL:{extracted_data.get('invoice_number') or request.document_id}",
            metadata={
                "extracted_data": extracted_data,
                "processing_agent": "DocumentProcessingAgent"
            }
        )
        
        return business_event
    
    async def process_document(self, request: DocumentProcessingRequest) -> DocumentProcessingResponse:
        """Process a document and return the response"""
        start_time = datetime.utcnow()
        logger.info(f"Processing document {request.document_id}")
        
        try:
            # Extract text from PDF
            text = self.extract_pdf_text(request.file_path)
            
            # Extract structured data using AI
            extracted_data = await self.extract_invoice_data(text)
            
            # Create BusinessEvent
            business_event = self.create_business_event(request, extracted_data)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Return success response
            return DocumentProcessingResponse(
                document_id=request.document_id,
                success=True,
                business_event=business_event.dict(),
                processing_time_seconds=processing_time,
                extracted_data=extracted_data
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Error processing document {request.document_id}: {str(e)}"
            logger.error(error_msg)
            
            return DocumentProcessingResponse(
                document_id=request.document_id,
                success=False,
                error_message=error_msg,
                processing_time_seconds=processing_time
            )
