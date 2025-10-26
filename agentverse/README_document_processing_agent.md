# Document Processing Agent

**AI-Powered Financial Document Analyzer and Business Event Generator**

## Overview

The Document Processing Agent uses advanced AI to extract structured financial data from documents and generate business events for the financial processing pipeline. This agent serves as the entry point for document-based financial transactions.

## Key Capabilities

- **AI Document Extraction**: Uses Claude AI to extract financial data from various document formats
- **Multi-Format Support**: Processes PDF, CSV, Excel, and image files
- **Business Event Generation**: Converts extracted data into structured business events
- **Pipeline Coordination**: Orchestrates audit verification and reconciliation processes
- **Real-time Processing**: Immediate document analysis with sub-minute response times

## Use Cases

### Invoice Processing
- Extract invoice data from PDF documents
- Generate INVOICE_RECEIVED business events
- Process vendor invoices automatically
- Handle complex multi-line invoices

### Receipt Analysis
- Analyze receipt images and PDFs
- Extract transaction details and amounts
- Generate expense business events
- Support mobile receipt capture

### Financial Statement Processing
- Process bank statements and CSV exports
- Extract transaction records
- Generate PAYMENT_SENT/RECEIVED events
- Handle bulk transaction imports

### Document Digitization
- Convert paper documents to digital records
- Extract structured data from unstructured sources
- Generate searchable business events
- Support OCR and AI-powered extraction

## API Endpoints

### Document Processing Request
Submit documents for AI analysis:

```json
{
  "document_id": "doc-12345",
  "file_path": "/path/to/document.pdf",
  "filename": "invoice_001.pdf",
  "file_size": 1024000,
  "file_type": "PDF",
  "upload_timestamp": "2024-01-15T10:30:00Z",
  "requester_id": "user-123",
  "metadata": {
    "category": "vendor_invoice",
    "priority": "high"
  }
}
```

### Processing Response
Receive extracted data and business events:

```json
{
  "document_id": "doc-12345",
  "success": true,
  "business_event": {
    "event_id": "doc-12345",
    "event_kind": "INVOICE_RECEIVED",
    "amount_minor": 100000,
    "currency": "USD",
    "metadata": {
      "invoice_number": "INV-001",
      "vendor": "Sample Vendor"
    }
  },
  "processing_time_seconds": 15.2,
  "extracted_data": {
    "invoice_number": "INV-001",
    "amount": 1000.00,
    "vendor": "Sample Vendor"
  },
  "sui_digest": "0xabc123...",
  "supabase_inserted": true
}
```

### Health Check
Monitor agent status and configuration:

```json
{
  "status": "healthy",
  "agent_address": "agent1...",
  "timestamp": "2024-01-15T10:30:00Z",
  "anthropic_configured": true,
  "audit_agent_configured": true,
  "reconciliation_agent_configured": true,
  "pending_requests": 0
}
```

## Supported Document Types

### PDF Documents
- Invoice PDFs with structured layouts
- Receipt scans and digital receipts
- Financial statements and reports
- Multi-page documents with tables

### CSV Files
- Bank statement exports
- Transaction logs
- Bulk payment files
- Accounting system exports

### Excel Files
- Financial spreadsheets
- Invoice templates
- Payment schedules
- Budget reports

### Image Files
- Receipt photos
- Invoice scans
- Document screenshots
- Mobile capture images

## Integration Workflow

1. **Document Upload**: Receive document processing requests
2. **AI Extraction**: Use Claude AI to extract structured data
3. **Event Generation**: Create business events from extracted data
4. **Audit Coordination**: Send events to audit verification agent
5. **Reconciliation Trigger**: Initiate reconciliation process
6. **Response Delivery**: Return processing results to requester

## Configuration Requirements

- Anthropic API key for Claude AI access
- Audit agent address for blockchain posting
- Reconciliation agent address for transaction matching
- File storage configuration for document handling

## Performance Metrics

- Average processing time: 10-30 seconds per document
- Success rate: > 95% for standard document formats
- Concurrent processing: Up to 50 documents/minute
- AI extraction accuracy: > 90% for structured documents

## Error Handling

- Invalid document format detection
- AI extraction failure recovery
- Network connectivity issues
- Agent communication failures
- Partial extraction handling

## Security Features

- Document hash verification
- Secure file handling
- API key protection
- Data privacy compliance
- Audit trail maintenance

## Limitations

- Requires Anthropic API access
- Processing time varies by document complexity
- Limited to supported document formats
- AI accuracy depends on document quality
- Requires proper agent network configuration

## Monitoring and Alerts

- Document processing queue monitoring
- AI extraction success rates
- Agent communication status
- Processing time alerts
- Error rate notifications

---

**Keywords**: document processing, AI extraction, financial documents, invoice processing, receipt analysis, business events, Claude AI, OCR, document digitization, financial automation

