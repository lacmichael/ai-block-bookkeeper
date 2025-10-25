# Document Processing Agent

## Overview

The Document Processing Agent serves as the entry point for financial document ingestion in the AI Block Bookkeeper system. It specializes in extracting structured financial data from PDF invoices and receipts, converting them into standardized `BusinessEvent` objects that can be processed by downstream agents.

## 1. Agent Architecture

### Core Responsibilities

- **PDF Text Extraction**: Extract text content from PDF invoices and receipts
- **Data Parsing**: Parse financial information using AI/ML models
- **Data Normalization**: Convert extracted data to standardized `BusinessEvent` format
- **Document Storage**: Store processed documents with metadata
- **Quality Validation**: Validate extracted data and flag uncertain items
- **Error Handling**: Manage processing failures and retry logic

### Input Sources

- **PDF Invoices**: Vendor invoices, service bills, subscription renewals
- **PDF Receipts**: Purchase receipts, expense reports, transaction confirmations
- **Manual Uploads**: User-uploaded documents via web interface
- **API Integrations**: Future integration with document management systems

### Output Format

The agent outputs standardized `BusinessEvent` objects that conform to the domain model defined in `domain-models.md`:

```typescript
interface BusinessEvent {
  event_id: string; // UUID
  source_system: "MANUAL" | "PDF_PROCESSOR" | "OTHER";
  source_id: string; // Document filename or external ID
  occurred_at: string; // Invoice/receipt date
  recorded_at: string; // Processing timestamp
  event_kind: "INVOICE_RECEIVED" | "PAYMENT_SENT" | "REFUND" | "ADJUSTMENT";

  // Financial data
  amount_minor: bigint; // Amount in minor units (cents)
  currency: string; // ISO 4217 currency code
  description?: string; // Extracted description

  // Party information
  payer?: PartyRef; // Who pays (for invoices)
  payee?: PartyRef; // Who receives payment (for receipts)

  // Document metadata
  documents: DocumentMetadata[];

  // Processing state
  processing: {
    state: "PENDING" | "MAPPED" | "POSTED_ONCHAIN" | "INDEXED" | "FAILED";
    last_error?: string;
  };

  // Deduplication
  dedupe_key: string; // `${source_system}:${source_id}`

  // Extracted metadata
  metadata?: Record<string, any>;
}
```

## 2. PDF Processing Pipeline

### Stage 1: Document Ingestion

**Input Validation**

- Verify PDF file format and integrity
- Check file size limits (max 10MB)
- Validate document type (invoice vs receipt)
- Generate unique document ID

**Document Storage**

- Store original PDF in secure storage
- Calculate SHA256 hash for integrity verification
- Create `DocumentMetadata` record

### Stage 2: Text Extraction

**PDF Text Extraction**

- Use PyPDF2 or pdfplumber for text extraction
- Handle scanned PDFs with OCR (Tesseract)
- Extract text from tables and structured layouts
- Preserve formatting and positioning information

**Content Preprocessing**

- Clean and normalize extracted text
- Remove headers, footers, and irrelevant content
- Identify key sections (header, line items, totals, footer)

### Stage 3: AI-Powered Data Extraction

**Invoice Information Extraction**

- **Vendor Information**: Company name, address, contact details
- **Invoice Details**: Invoice number, date, due date, PO number
- **Financial Data**: Line items, subtotals, taxes, total amount
- **Payment Terms**: Payment method, terms, bank details

**Receipt Information Extraction**

- **Merchant Information**: Store name, location, contact
- **Transaction Details**: Date, time, transaction ID
- **Financial Data**: Items purchased, quantities, prices, total
- **Payment Method**: Card type, last 4 digits, authorization code

**AI Model Integration**

- Use OpenAI GPT-4 or similar for intelligent extraction
- Implement confidence scoring for extracted fields
- Handle multiple languages and document formats
- Extract structured data from unstructured text

### Stage 4: Data Validation & Normalization

**Field Validation**

- Validate currency codes against ISO 4217
- Check date formats and ranges
- Verify amount calculations (line items sum to total)
- Validate email addresses and phone numbers

**Data Normalization**

- Convert amounts to minor units (cents)
- Standardize date formats (ISO 8601)
- Normalize company names and addresses
- Map currencies to standard codes

**Confidence Scoring**

- Assign confidence scores to each extracted field
- Flag low-confidence extractions for human review
- Implement quality thresholds for automatic processing

### Stage 5: BusinessEvent Creation

**Event Classification**

- Determine event type based on document content
- Classify as invoice, receipt, refund, or adjustment
- Identify payer and payee relationships

**Party Resolution**

- Match extracted company names to existing parties
- Create new party records for unknown entities
- Link parties to business events via `PartyRef`

**Metadata Enrichment**

- Store extraction confidence scores
- Preserve original document references
- Add processing timestamps and agent information

## 3. Data Extraction Specifications

### Invoice Data Fields

**Required Fields**

- `invoice_number`: Unique invoice identifier
- `invoice_date`: Date invoice was issued
- `due_date`: Payment due date
- `total_amount`: Total amount due
- `currency`: Currency code
- `vendor_name`: Company issuing invoice

**Optional Fields**

- `po_number`: Purchase order reference
- `payment_terms`: Payment terms (e.g., "Net 30")
- `tax_amount`: Tax amount
- `subtotal`: Amount before tax
- `line_items`: Individual items/services
- `vendor_address`: Vendor contact information
- `payment_method`: Preferred payment method

### Receipt Data Fields

**Required Fields**

- `transaction_date`: Date of transaction
- `total_amount`: Total amount paid
- `currency`: Currency code
- `merchant_name`: Store/merchant name

**Optional Fields**

- `transaction_id`: Unique transaction identifier
- `items`: List of purchased items
- `payment_method`: Payment method used
- `merchant_address`: Store location
- `tax_amount`: Tax amount
- `discount_amount`: Discount applied

### Line Item Extraction

**For Invoices**

```typescript
interface InvoiceLineItem {
  description: string;
  quantity: number;
  unit_price_minor: bigint;
  total_price_minor: bigint;
  tax_amount_minor?: bigint;
  category?: string;
}
```

**For Receipts**

```typescript
interface ReceiptLineItem {
  description: string;
  quantity: number;
  unit_price_minor: bigint;
  total_price_minor: bigint;
  category?: string;
}
```

## 4. Error Handling & Quality Assurance

### Processing Error Types

**Document Errors**

- Corrupted or unreadable PDF files
- Password-protected documents
- Scanned documents with poor quality
- Unsupported document formats

**Extraction Errors**

- Low confidence in extracted data
- Missing required fields
- Inconsistent data (e.g., amounts don't add up)
- Unrecognized document types

**Validation Errors**

- Invalid currency codes
- Future dates or invalid date ranges
- Negative amounts where not expected
- Invalid email or phone formats

### Error Handling Strategy

**Retry Logic**

- Automatic retry for transient errors (network, temporary failures)
- Exponential backoff for rate-limited operations
- Maximum 3 retry attempts before marking as failed

**Human Review Queue**

- Flag documents with low confidence scores
- Queue for manual review and correction
- Allow human override of extracted data

**Error Reporting**

- Detailed error logs with context
- User-friendly error messages
- Processing statistics and success rates

### Quality Metrics

**Extraction Accuracy**

- Field-level confidence scores
- Overall document processing success rate
- Human correction rate

**Processing Performance**

- Average processing time per document
- Throughput (documents per minute)
- Resource utilization (CPU, memory)

## 5. Integration Points

### With Database Service

**Document Storage**

- Store original PDF files with metadata
- Create `DocumentMetadata` records
- Link documents to extracted business events

**BusinessEvent Creation**

- Insert new business events with `PENDING` status
- Create audit log entries for processing actions
- Handle duplicate detection via `dedupe_key`

### With Reconciliation Agent

**Event Notification**

- Send HTTP notification when business event is created
- Include event ID and processing status
- Trigger downstream reconciliation processing

**Status Updates**

- Update processing status as events move through pipeline
- Provide reconciliation metadata (invoice numbers, payment references)

### With Audit & Verification Agent

**On-Chain Recording**

- Provide business events for blockchain recording
- Include document hashes for immutable audit trail
- Update processing status after on-chain confirmation

## 6. Configuration & Deployment

### Environment Configuration

**AI Model Settings**

```yaml
ai_models:
  openai:
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-4"
    max_tokens: 4000
    temperature: 0.1

  ocr:
    tesseract_path: "/usr/bin/tesseract"
    language: "eng"
    confidence_threshold: 0.7
```

**Processing Settings**

```yaml
processing:
  max_file_size_mb: 10
  supported_formats: ["pdf"]
  confidence_threshold: 0.8
  retry_attempts: 3
  retry_delay_seconds: 5
```

**Storage Settings**

```yaml
storage:
  type: "local" # or "s3", "gcs"
  base_path: "/app/documents"
  max_storage_gb: 100
```

### Agent Configuration

**uAgents Framework**

```python
from uagents import Agent, Context

agent = Agent(
    name="DocumentProcessingAgent",
    seed="document-processing-agent-seed",
    port=8001
)

@agent.on_message(DocumentProcessingRequest)
async def process_document(ctx: Context, sender: str, msg: DocumentProcessingRequest):
    # Process document and extract business event
    pass
```

## 7. Testing Strategy

### Unit Tests

**PDF Processing Tests**

- Test text extraction from various PDF formats
- Test OCR functionality with scanned documents
- Test error handling for corrupted files

**Data Extraction Tests**

- Test extraction accuracy with sample invoices
- Test confidence scoring algorithms
- Test data validation and normalization

**Integration Tests**

- Test end-to-end document processing pipeline
- Test database integration and event creation
- Test error handling and retry logic

### Test Data

**Sample Documents**

- Various invoice formats (different vendors, layouts)
- Receipt samples (retail, restaurant, online)
- Edge cases (poor quality scans, unusual formats)
- Multi-language documents

**Expected Outcomes**

- Accurate extraction of key financial data
- Proper business event creation
- Appropriate confidence scoring
- Error handling for problematic documents

## 8. Monitoring & Observability

### Key Metrics

**Processing Metrics**

- Documents processed per hour
- Average processing time per document
- Success rate by document type
- Error rate and error types

**Quality Metrics**

- Average confidence score
- Human review rate
- Data accuracy (validated against known good data)

**System Metrics**

- CPU and memory utilization
- Storage usage
- API response times

### Logging

**Structured Logging**

- Document processing events
- Extraction results and confidence scores
- Error details and stack traces
- Performance metrics

**Audit Trail**

- Document upload and processing history
- User actions and corrections
- System configuration changes

## 9. Future Enhancements

### Advanced Features

**Multi-Format Support**

- Excel/CSV file processing
- Image file processing (JPG, PNG)
- Email attachment processing

**Enhanced AI Models**

- Fine-tuned models for specific document types
- Multi-language support
- Industry-specific extraction rules

**Automated Workflows**

- Batch processing capabilities
- Scheduled processing jobs
- Integration with document management systems

### Scalability Improvements

**Distributed Processing**

- Horizontal scaling across multiple agents
- Load balancing for high-volume processing
- Queue-based processing for reliability

**Caching & Optimization**

- Cache extracted data for similar documents
- Optimize AI model calls
- Implement document deduplication

## 10. Implementation Files

**Core Agent**

- `src/agents/document_processing_agent.py` - Main agent implementation
- `src/agents/document_processing/extractor.py` - PDF text extraction
- `src/agents/document_processing/parser.py` - AI-powered data parsing
- `src/agents/document_processing/validator.py` - Data validation logic

**Models & Types**

- `src/models/document_processing_models.py` - Pydantic models
- `src/models/extraction_models.py` - Extraction result models

**Services**

- `src/services/pdf_service.py` - PDF processing utilities
- `src/services/ai_service.py` - AI model integration
- `src/services/storage_service.py` - Document storage management

**Tests**

- `tests/agents/test_document_processing_agent.py` - Unit tests
- `tests/integration/test_document_processing_flow.py` - Integration tests
- `tests/fixtures/sample_documents/` - Test document samples
