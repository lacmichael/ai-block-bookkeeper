# Reconciliation Agent

**Automated Financial Transaction Matcher and Reconciliation Engine**

## Overview

The Reconciliation Agent automatically matches invoices to payments and creates reconciliation records, providing intelligent financial reconciliation for business transactions. This agent ensures accurate financial records by identifying and linking related transactions.

## Key Capabilities

- **Automatic Matching**: Intelligently matches invoices to payments using multiple criteria
- **Confidence Scoring**: Provides match confidence levels for quality assessment
- **Partial Match Detection**: Identifies and flags transactions with discrepancies
- **Reconciliation Records**: Creates detailed reconciliation records for matched transactions
- **Multi-Criteria Matching**: Uses amount, reference numbers, dates, and metadata for matching

## Use Cases

### Invoice-to-Payment Matching
- Match received invoices with outgoing payments
- Identify payment references and invoice numbers
- Handle partial payments and payment splits
- Process recurring payment patterns

### Payment Reconciliation
- Reconcile bank statements with invoice records
- Match payment confirmations to invoices
- Handle payment timing discrepancies
- Process multi-currency transactions

### Financial Statement Reconciliation
- Match internal records with external statements
- Identify missing or duplicate transactions
- Process bulk reconciliation requests
- Handle complex payment scenarios

### Discrepancy Management
- Flag amount mismatches for review
- Identify timing discrepancies
- Process partial payment scenarios
- Handle currency conversion differences

## API Endpoints

### Reconciliation Request
Submit transactions for automatic matching:

```json
{
  "event_id": "invoice-12345",
  "business_event": {
    "event_id": "invoice-12345",
    "event_kind": "INVOICE_RECEIVED",
    "amount_minor": 100000,
    "currency": "USD",
    "metadata": {
      "invoice_number": "INV-001",
      "vendor": "Sample Vendor",
      "due_date": "2024-02-15"
    }
  }
}
```

### Reconciliation Response
Receive matching results and reconciliation status:

```json
{
  "event_id": "invoice-12345",
  "success": true,
  "reconciliation_status": "RECONCILED",
  "matched_event_id": "payment-67890",
  "discrepancy": null
}
```

### Partial Match Response
Handle transactions with discrepancies:

```json
{
  "event_id": "invoice-12345",
  "success": true,
  "reconciliation_status": "PARTIAL",
  "matched_event_id": "payment-67890",
  "discrepancy": {
    "type": "AMOUNT_MISMATCH",
    "invoice_amount": 100000,
    "payment_amount": 95000,
    "difference": 5000
  }
}
```

### Health Check
Monitor agent performance and statistics:

```json
{
  "status": "healthy",
  "agent_address": "agent1...",
  "timestamp": "2024-01-15T10:30:00Z",
  "reconciliation_stats": {
    "total_processed": 1250,
    "reconciled": 1100,
    "partial_matches": 100,
    "unreconciled": 50
  }
}
```

## Matching Algorithms

### Primary Matching Criteria
- **Exact Amount Match**: Perfect amount alignment
- **Reference Number Match**: Invoice/payment reference matching
- **Date Proximity**: Transactions within acceptable time windows
- **Currency Consistency**: Same currency validation

### Secondary Matching Criteria
- **Vendor/Customer Matching**: Party identification
- **Description Similarity**: Transaction description analysis
- **Pattern Recognition**: Recurring transaction patterns
- **Metadata Correlation**: Additional data point matching

### Confidence Scoring
- **High Confidence (0.9-1.0)**: Perfect matches with all criteria
- **Medium Confidence (0.7-0.9)**: Strong matches with minor discrepancies
- **Low Confidence (0.5-0.7)**: Partial matches requiring review
- **No Match (0.0-0.5)**: Insufficient matching criteria

## Reconciliation Status Types

### RECONCILED
- Perfect match found with high confidence
- All criteria align successfully
- No discrepancies detected
- Ready for final processing

### PARTIAL
- Match found with discrepancies
- Requires manual review
- Discrepancy details provided
- May need adjustment or approval

### UNRECONCILED
- No suitable match found
- Will retry with future transactions
- May require manual intervention
- Queued for periodic re-evaluation

## Integration Workflow

1. **Transaction Receipt**: Receive new transaction events
2. **Match Search**: Search for counterpart transactions
3. **Criteria Evaluation**: Apply matching algorithms
4. **Confidence Assessment**: Calculate match confidence
5. **Reconciliation Creation**: Generate reconciliation records
6. **Status Update**: Update transaction reconciliation status
7. **Response Delivery**: Return reconciliation results

## Performance Metrics

- **Processing Speed**: < 5 seconds per transaction
- **Match Accuracy**: > 95% for standard transactions
- **Reconciliation Rate**: > 85% automatic reconciliation
- **False Positive Rate**: < 2% for high-confidence matches

## Configuration Requirements

- Database connection for transaction storage
- Matching algorithm parameters
- Confidence threshold settings
- Retry and timeout configurations

## Error Handling

- Database connectivity issues
- Invalid transaction data
- Matching algorithm failures
- Partial processing recovery
- Timeout and retry mechanisms

## Security Features

- Transaction data validation
- Secure database operations
- Audit trail maintenance
- Data integrity verification
- Access control enforcement

## Limitations

- Requires counterpart transactions for matching
- Processing time increases with transaction volume
- Limited to configured matching criteria
- Manual review required for complex cases
- Depends on data quality and completeness

## Monitoring and Alerts

- Reconciliation success rate monitoring
- Processing queue status
- Match confidence distribution
- Error rate tracking
- Performance metric alerts

---

**Keywords**: reconciliation, transaction matching, invoice matching, payment reconciliation, financial matching, automated reconciliation, discrepancy detection, confidence scoring, financial automation

