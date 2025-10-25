import os
import uuid
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import pdfplumber
import anthropic

from .document_processing.models import (
    DocumentProcessingRequest, 
    DocumentProcessingResponse
)
from .document_processing.prompts import INVOICE_EXTRACTION_PROMPT
from models.domain_models import (
    BusinessEvent, 
    ProcessingState, 
    PartyRef, 
    DocumentMetadata,
    Address
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessingClient:
    """Client for handling document processing operations"""
    
    def __init__(self, anthropic_api_key: str):
        """Initialize the document processing client"""
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        logger.info("Document Processing Client initialized")
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files efficiently
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {str(e)}")
            return ""
    
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
    
    def _calculate_extraction_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on completeness of extracted data"""
        required_fields = ["vendor_name", "invoice_number", "invoice_date", "total_amount", "currency"]
        optional_high_value_fields = [
            "due_date", "payment_terms", "vendor_email", "vendor_address",
            "line_items", "subtotal", "tax_amount", "payer_name"
        ]
        
        # Count present required fields
        required_present = sum(1 for field in required_fields if extracted_data.get(field))
        required_score = required_present / len(required_fields)
        
        # Count present optional high-value fields
        optional_present = sum(1 for field in optional_high_value_fields if extracted_data.get(field))
        optional_score = optional_present / len(optional_high_value_fields)
        
        # Weighted score: 70% required, 30% optional
        confidence = (required_score * 0.7) + (optional_score * 0.3)
        
        return round(confidence, 2)
    
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
            
            extracted_data = json.loads(response_text)
            
            # Log extraction summary
            logger.info(f"Extracted data summary - Vendor: {extracted_data.get('vendor_name')}, "
                       f"Amount: {extracted_data.get('currency', 'USD')} {extracted_data.get('total_amount')}, "
                       f"Date: {extracted_data.get('invoice_date')}")
            
            return extracted_data
        except Exception as e:
            logger.error(f"Error extracting invoice data: {str(e)}")
            return {"error": str(e)}
    
    def _create_party_ref(
        self,
        name: Optional[str],
        role: str,
        extracted_data: Dict[str, Any],
        prefix: str
    ) -> Optional[PartyRef]:
        """Helper to create a PartyRef with normalized party_id"""
        if not name:
            return None
        
        # Create normalized party_id
        party_id = f"{role.lower()}_{name.lower().replace(' ', '_').replace('.', '').replace(',', '')}"
        
        return PartyRef(
            party_id=party_id,
            role=role
        )
    
    def _create_address(self, address_data: Optional[Dict[str, Any]]) -> Optional[Address]:
        """Helper to create Address object from extracted data"""
        if not address_data or not isinstance(address_data, dict):
            return None
        
        # Only create address if at least one field is present
        if any(address_data.values()):
            return Address(
                street=address_data.get("street"),
                city=address_data.get("city"),
                state=address_data.get("state"),
                postal_code=address_data.get("postal_code"),
                country=address_data.get("country")
            )
        return None
    
    def _build_metadata(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive metadata from extracted data"""
        metadata = {
            "processing_agent": "DocumentProcessingAgent",
            "extraction_timestamp": datetime.utcnow().isoformat()
        }
        
        # Payment information
        payment_info = {}
        if extracted_data.get("due_date"):
            payment_info["due_date"] = extracted_data["due_date"]
        if extracted_data.get("payment_terms"):
            payment_info["payment_terms"] = extracted_data["payment_terms"]
        if extracted_data.get("po_number"):
            payment_info["po_number"] = extracted_data["po_number"]
        if payment_info:
            metadata["payment_info"] = payment_info
        
        # Vendor details
        vendor_details = {}
        if extracted_data.get("vendor_legal_name"):
            vendor_details["legal_name"] = extracted_data["vendor_legal_name"]
        if extracted_data.get("vendor_email"):
            vendor_details["email"] = extracted_data["vendor_email"]
        if extracted_data.get("vendor_address"):
            vendor_details["address"] = extracted_data["vendor_address"]
        if extracted_data.get("vendor_tax_id"):
            vendor_details["tax_id"] = extracted_data["vendor_tax_id"]
        if vendor_details:
            metadata["vendor_details"] = vendor_details
        
        # Payer details
        payer_details = {}
        if extracted_data.get("payer_name"):
            payer_details["name"] = extracted_data["payer_name"]
        if extracted_data.get("payer_legal_name"):
            payer_details["legal_name"] = extracted_data["payer_legal_name"]
        if extracted_data.get("payer_email"):
            payer_details["email"] = extracted_data["payer_email"]
        if extracted_data.get("payer_address"):
            payer_details["address"] = extracted_data["payer_address"]
        if extracted_data.get("payer_tax_id"):
            payer_details["tax_id"] = extracted_data["payer_tax_id"]
        if payer_details:
            metadata["payer_details"] = payer_details
        
        # Financial breakdown
        financial_details = {}
        if extracted_data.get("subtotal") is not None:
            financial_details["subtotal"] = extracted_data["subtotal"]
        if extracted_data.get("tax_amount") is not None:
            financial_details["tax_amount"] = extracted_data["tax_amount"]
        if extracted_data.get("tax_rate") is not None:
            financial_details["tax_rate"] = extracted_data["tax_rate"]
        if extracted_data.get("tax_jurisdiction"):
            financial_details["tax_jurisdiction"] = extracted_data["tax_jurisdiction"]
        if extracted_data.get("discount_amount") is not None:
            financial_details["discount_amount"] = extracted_data["discount_amount"]
        if extracted_data.get("shipping_amount") is not None:
            financial_details["shipping_amount"] = extracted_data["shipping_amount"]
        if financial_details:
            metadata["financial_details"] = financial_details
        
        # Line items
        if extracted_data.get("line_items") and isinstance(extracted_data["line_items"], list):
            metadata["line_items"] = extracted_data["line_items"]
        
        # Additional notes and references
        if extracted_data.get("notes"):
            metadata["notes"] = extracted_data["notes"]
        if extracted_data.get("reference_numbers"):
            metadata["reference_numbers"] = extracted_data["reference_numbers"]
        
        # Store raw invoice data for debugging/audit
        metadata["raw_extraction"] = {
            k: v for k, v in extracted_data.items() 
            if k not in [
                "vendor_name", "vendor_legal_name", "vendor_email", 
                "vendor_address", "vendor_tax_id", "payer_name", 
                "payer_legal_name", "payer_email", "payer_address", 
                "payer_tax_id", "line_items", "notes", "reference_numbers",
                "subtotal", "tax_amount", "tax_rate", "tax_jurisdiction",
                "discount_amount", "shipping_amount", "due_date", 
                "payment_terms", "po_number"
            ]
        }
        
        return metadata
    
    def create_business_event(
        self, 
        request: DocumentProcessingRequest, 
        extracted_data: Dict[str, Any]
    ) -> BusinessEvent:
        """Create a comprehensive BusinessEvent from the extracted data"""
        
        # Create party reference for vendor/payee (if available)
        payee_party_ref = self._create_party_ref(
            name=extracted_data.get("vendor_name"),
            role="VENDOR",
            extracted_data=extracted_data,
            prefix="vendor"
        )
        
        # Create party reference for payer (if available)
        payer_party_ref = self._create_party_ref(
            name=extracted_data.get("payer_name"),
            role="CUSTOMER",
            extracted_data=extracted_data,
            prefix="payer"
        )
        
        # Convert amount to minor units (cents)
        amount_minor = 0
        if extracted_data.get("total_amount"):
            try:
                amount_minor = int(float(extracted_data["total_amount"]) * 100)
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid amount value: {extracted_data.get('total_amount')}, defaulting to 0")
        
        # Build comprehensive description
        description = extracted_data.get("description")
        if not description:
            vendor_name = extracted_data.get("vendor_name", "Unknown Vendor")
            invoice_num = extracted_data.get("invoice_number", "")
            description = f"Invoice from {vendor_name}"
            if invoice_num:
                description += f" (#{invoice_num})"
        
        # Parse invoice date
        occurred_at = request.upload_timestamp
        if extracted_data.get("invoice_date"):
            try:
                # Handle both datetime and string formats
                if isinstance(extracted_data["invoice_date"], str):
                    occurred_at = datetime.fromisoformat(extracted_data["invoice_date"].replace('Z', '+00:00'))
                else:
                    occurred_at = extracted_data["invoice_date"]
            except Exception as e:
                logger.warning(f"Invalid invoice_date format: {extracted_data.get('invoice_date')}, using upload_timestamp")
        
        # Calculate file hash for integrity verification
        file_hash = self.calculate_file_hash(request.file_path)
        
        # Calculate extraction confidence score
        extraction_confidence = self._calculate_extraction_confidence(extracted_data)
        
        # Create document metadata
        document_metadata = DocumentMetadata(
            document_id=request.document_id,
            filename=request.filename,
            file_type=request.file_type,
            file_size=request.file_size,
            storage_url=request.file_path,
            sha256=file_hash,
            upload_date=request.upload_timestamp,
            processed_by_agent="DocumentProcessingAgent",
            processing_timestamp=datetime.utcnow(),
            extraction_confidence=extraction_confidence,
            onchain_hash_recorded=False,
            onchain_digest=None
        )
        
        # Log confidence score
        logger.info(f"Document {request.document_id} extraction confidence: {extraction_confidence:.2f}")
        
        # Build comprehensive metadata
        metadata = self._build_metadata(extracted_data)
        
        # Create business event
        business_event = BusinessEvent(
            event_id=str(uuid.uuid4()),
            source_system="INVOICE_PORTAL",
            source_id=extracted_data.get("invoice_number") or request.document_id,
            occurred_at=occurred_at,
            recorded_at=datetime.utcnow(),
            event_kind="INVOICE_RECEIVED",
            amount_minor=amount_minor,
            currency=extracted_data.get("currency") or "USD",
            description=description,
            payer=payer_party_ref,
            payee=payee_party_ref,
            documents=[document_metadata],
            processing=ProcessingState(
                state="MAPPED",
                last_error=None
            ),
            dedupe_key=f"INVOICE_PORTAL:{extracted_data.get('invoice_number') or request.document_id}",
            metadata=metadata
        )
        
        # Log comprehensive business event creation
        logger.info(f"Created BusinessEvent {business_event.event_id}:")
        logger.info(f"  - Vendor/Payee: {extracted_data.get('vendor_name', 'N/A')}")
        logger.info(f"  - Payer: {extracted_data.get('payer_name', 'N/A')}")
        logger.info(f"  - Amount: {business_event.currency} {amount_minor/100:.2f}")
        logger.info(f"  - Metadata sections: {list(metadata.keys())}")
        if metadata.get("line_items"):
            logger.info(f"  - Line items: {len(metadata['line_items'])} items")
        if metadata.get("financial_details"):
            logger.info(f"  - Financial details: {list(metadata['financial_details'].keys())}")
        
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
