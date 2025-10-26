# Reconciliation Agent

## Overview

The Reconciliation Agent automatically matches invoice and payment transactions, creating reconciliation records and updating transaction statuses. It uses the Fetch.ai uAgents framework for agent-to-agent communication.

## Features

- **Automatic Matching**: Matches `INVOICE_RECEIVED` ↔ `PAYMENT_SENT` transactions based on reference numbers
- **Tolerance-Based Amount Matching**: Uses 1% or $5 tolerance (whichever is less) for amount matching
- **Discrepancy Detection**: Flags transactions with amount mismatches for human review
- **Database Integration**: Stores reconciliation records in dedicated `reconciliations` table
- **Agent Communication**: Receives requests from Document Processing Agent and sends responses

## Architecture

```
Document Processing Agent → Reconciliation Agent
    ↓ (ReconciliationRequest)
    
Reconciliation Agent:
1. Receives new transaction event
2. Queries database for matching counterpart
3. Evaluates match quality using matcher.py
4. Creates reconciliation record
5. Updates both transaction statuses
    ↓ (ReconciliationResponse)
    
Document Processing Agent ← Response
```

## Setup

### 1. Run Database Migration

Apply the reconciliations table migration:

```bash
# Apply to your Supabase database
psql <your-supabase-connection-string> < backend/supabase/migrations/create_reconciliations_table.sql
```

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# Reconciliation Agent Configuration
RECONCILIATION_AGENT_ADDRESS=<agent_address_from_first_run>
RECONCILIATION_AGENT_SEED=reconciliation-agent-seed-phrase-12345
RECONCILIATION_AGENT_PORT=8004
```

### 3. Start the Agent

First run (to get agent address):
```bash
cd backend/agents
python reconciliation_agent.py
```

Copy the agent address from logs and add to `.env` as `RECONCILIATION_AGENT_ADDRESS`.

Then restart all agents:
```bash
# Terminal 1: Audit Agent
python audit_verification_agent.py

# Terminal 2: Document Processing Agent
python document_processing_agent.py

# Terminal 3: Reconciliation Agent
python reconciliation_agent.py
```

## Database Schema

### reconciliations Table

| Column | Type | Description |
|--------|------|-------------|
| reconciliation_id | UUID | Primary key |
| invoice_event_id | UUID | Reference to invoice business_event |
| payment_event_id | UUID | Reference to payment business_event |
| match_type | VARCHAR(20) | PRIMARY_MATCH or PARTIAL_MATCH |
| confidence | FLOAT | Match confidence (0-1) |
| amount_difference | INT | Absolute amount difference in minor units |
| discrepancy | JSONB | Details of any discrepancies |
| reconciled_at | TIMESTAMPTZ | When reconciliation occurred |
| reconciled_by | VARCHAR(50) | Agent that performed reconciliation |
| metadata | JSONB | Additional metadata |

## Matching Logic

### PRIMARY_MATCH
- Reference numbers match exactly (invoice_number == payment_reference)
- Amounts match within tolerance (1% or $5, whichever is less)
- Both events updated to `RECONCILED` status

### PARTIAL_MATCH
- Reference numbers match exactly
- Amounts differ beyond tolerance
- Both events updated to `FLAGGED_FOR_REVIEW` status
- Discrepancy details stored in reconciliation record

### NO_MATCH
- No matching counterpart found yet
- Event remains in `POSTED_ONCHAIN` status
- Will be retried when new transactions arrive

## Message Models

### ReconciliationRequest
```python
{
    "event_id": "evt-12345",
    "business_event": {
        "event_id": "evt-12345",
        "event_kind": "INVOICE_RECEIVED",
        "amount_minor": 100000,
        "currency": "USD",
        "metadata": {
            "invoice_number": "INV-001"
        }
    }
}
```

### ReconciliationResponse
```python
{
    "event_id": "evt-12345",
    "success": True,
    "reconciliation_status": "RECONCILED",  # or PARTIAL, UNRECONCILED
    "matched_event_id": "evt-67890",
    "discrepancy": None,  # or discrepancy details
    "error_message": None
}
```

## Testing

Test the reconciliation flow:

1. Upload an invoice document (creates INVOICE_RECEIVED event)
2. Upload a payment document with matching reference (creates PAYMENT_SENT event)
3. Check logs for reconciliation activity
4. Verify reconciliation record in database:

```sql
SELECT * FROM reconciliations 
WHERE reconciled_at > NOW() - INTERVAL '1 hour'
ORDER BY reconciled_at DESC;
```

## Troubleshooting

### Agent Not Receiving Messages
- Verify `RECONCILIATION_AGENT_ADDRESS` is set correctly in `.env`
- Check agent is running on port 8004
- Verify Document Processing Agent has the correct address

### Reconciliation Not Happening
- Check that events have `processing_state = 'POSTED_ONCHAIN'`
- Verify invoice has `invoice_number` in metadata
- Verify payment has `payment_reference` in metadata
- Check that reference numbers match exactly

### Database Errors
- Ensure reconciliations table migration has been applied
- Verify Supabase credentials are correct
- Check service role key has write permissions

## Files

- `reconciliation_agent.py` - Main agent implementation
- `matcher.py` - Matching logic and algorithms
- `database_helpers.py` - Database query functions
- `README.md` - This file

