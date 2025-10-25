# Reconciliation Agent Plan

## Overview

The Reconciliation Agent serves as the "logic bridge" between document ingestion and blockchain recording. It monitors the database for verified BusinessEvents and intelligently matches INVOICE_RECEIVED events with their corresponding PAYMENT_SENT events, updating their processing states accordingly.

## 1. Agent Architecture

### Recommended Trigger Mechanism: **Hybrid Approach (Event-Driven with Polling Fallback)**

**Primary: Event-Driven (Recommended)**

- FastAPI verification endpoint sends direct message to agent via message queue (RabbitMQ/Redis Pub/Sub)
- Agent receives `event_id` of newly verified BusinessEvent
- Immediate processing with minimal latency
- More efficient than polling (no wasted DB queries)
- Better for real-time reconciliation needs

**Fallback: Polling Safety Net**

- `@on_interval(60)` decorator runs every 60 seconds
- Catches any events missed by message system (network failures, agent downtime)
- Queries for BusinessEvents with `processing.state = 'MAPPED'` that haven't been processed yet
- Uses a `metadata.reconciliation_attempted_at` timestamp to track processing attempts

**Rationale**: Event-driven provides speed and efficiency for normal operations, while polling ensures no events fall through the cracks during system issues.

## 2. Data Model Extensions

### BusinessEvent.metadata Schema for Reconciliation

```python
# For INVOICE_RECEIVED events:
metadata = {
    "invoice_number": "INV-2024-001",
    "due_date": "2024-11-01",
    "vendor_name": "Microsoft",
    "reconciliation_attempted_at": "2024-10-25T10:30:00Z",
    "reconciliation_match_id": "event_id_of_payment",  # Set when matched
    "reconciliation_notes": []  # Array of match attempt notes
}

# For PAYMENT_SENT events:
metadata = {
    "payment_reference": "INV-2024-001",  # References invoice number
    "payment_method": "ACH",
    "bank_transaction_id": "TXN-123",
    "reconciliation_attempted_at": "2024-10-25T10:30:00Z",
    "reconciliation_match_id": "event_id_of_invoice",  # Set when matched
    "reconciliation_notes": []
}
```

### Processing State Flow

```
PENDING → MAPPED → RECONCILED → POSTED_ONCHAIN → INDEXED
              ↓
       FLAGGED_FOR_REVIEW (if mismatch detected)
```

- **MAPPED**: BusinessEvent has been verified by human/system and is ready for reconciliation
- **RECONCILED**: Successfully matched with counterpart event
- **FLAGGED_FOR_REVIEW**: Partial match or discrepancy detected, needs human review
- **POSTED_ONCHAIN**: Recorded to Sui blockchain (handled by Audit & Verification Agent)

## 3. Core Logic Implementation

### Main Handler: `handle_reconciliation_request(event_id: str)`

**Step 1: Fetch and Validate Event**

```python
business_event = await db.get_business_event_by_id(event_id)

# Validate eligibility
if business_event.processing.state != 'MAPPED':
    return  # Only process MAPPED events

if business_event.event_kind not in ['INVOICE_RECEIVED', 'PAYMENT_SENT']:
    return  # Only reconcile invoices and payments

if business_event.metadata.get('reconciliation_match_id'):
    return  # Already reconciled
```

**Step 2: Find Potential Counterpart**

```python
if business_event.event_kind == 'INVOICE_RECEIVED':
    invoice_number = business_event.metadata.get('invoice_number')
    counterpart = await db.find_payment_by_reference(
        payment_reference=invoice_number,
        processing_state='MAPPED',
        currency=business_event.currency
    )
else:  # PAYMENT_SENT
    payment_reference = business_event.metadata.get('payment_reference')
    counterpart = await db.find_invoice_by_number(
        invoice_number=payment_reference,
        processing_state='MAPPED',
        currency=business_event.currency
    )
```

**Step 3: Apply Matching Rules**

```python
match_result = evaluate_match(business_event, counterpart)

if match_result.type == 'PRIMARY_MATCH':
    # High-confidence: invoice_number matches AND amounts match
    await update_both_to_reconciled(business_event, counterpart, match_result)

elif match_result.type == 'PARTIAL_MATCH':
    # Discrepancy: invoice_number matches BUT amounts differ
    await flag_both_for_review(business_event, counterpart, match_result)

else:  # NO_MATCH
    # Update attempt timestamp, wait for counterpart to be uploaded
    await db.update_reconciliation_attempt(
        event_id=business_event.event_id,
        attempted_at=utcnow()
    )
```

**Step 4: Create Audit Trail**

```python
await db.create_audit_log(
    action='RECONCILE',
    entity_type='BUSINESS_EVENT',
    entity_id=business_event.event_id,
    actor_type='AI_AGENT',
    actor_id='reconciliation-agent',
    changes=[...],
    metadata={'match_type': match_result.type, ...}
)
```

### Matching Rule Logic: `evaluate_match(event, counterpart)`

```python
def evaluate_match(event: BusinessEvent, counterpart: BusinessEvent | None) -> MatchResult:
    if not counterpart:
        return MatchResult(type='NO_MATCH')

    # Extract matching fields
    if event.event_kind == 'INVOICE_RECEIVED':
        invoice_num = event.metadata.get('invoice_number')
        payment_ref = counterpart.metadata.get('payment_reference')
        invoice_amount = event.amount_minor
        payment_amount = counterpart.amount_minor
    else:
        invoice_num = counterpart.metadata.get('invoice_number')
        payment_ref = event.metadata.get('payment_reference')
        invoice_amount = counterpart.amount_minor
        payment_amount = event.amount_minor

    # Check reference match
    if invoice_num != payment_ref:
        return MatchResult(type='NO_MATCH')

    # Check amount match (allowing 1% tolerance for rounding)
    amount_diff = abs(invoice_amount - payment_amount)
    tolerance = invoice_amount * 0.01

    if amount_diff <= tolerance:
        return MatchResult(
            type='PRIMARY_MATCH',
            confidence=1.0,
            invoice_id=event.event_id if event.event_kind == 'INVOICE_RECEIVED' else counterpart.event_id,
            payment_id=counterpart.event_id if event.event_kind == 'INVOICE_RECEIVED' else event.event_id
        )
    else:
        return MatchResult(
            type='PARTIAL_MATCH',
            confidence=0.5,
            discrepancy={
                'type': 'AMOUNT_MISMATCH',
                'invoice_amount': invoice_amount,
                'payment_amount': payment_amount,
                'difference': amount_diff
            },
            invoice_id=...,
            payment_id=...
        )
```

## 4. Database Operations (SQL)

### SQL Database Schema

The agent works with a PostgreSQL database. Key tables:

**business_events table:**

```sql
CREATE TABLE business_events (
    event_id UUID PRIMARY KEY,
    source_system VARCHAR(50) NOT NULL,
    source_id VARCHAR(255) NOT NULL,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    event_kind VARCHAR(50) NOT NULL,
    amount_minor BIGINT NOT NULL,
    currency VARCHAR(3) NOT NULL,
    description TEXT,
    payer_id UUID REFERENCES parties(party_id),
    payee_id UUID REFERENCES parties(party_id),
    processing_state VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    processing_last_error TEXT,
    dedupe_key VARCHAR(500) UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_dedupe UNIQUE(dedupe_key)
);

-- Indexes for reconciliation queries
CREATE INDEX idx_business_events_processing_state ON business_events(processing_state);
CREATE INDEX idx_business_events_event_kind ON business_events(event_kind);
CREATE INDEX idx_business_events_currency ON business_events(currency);
CREATE INDEX idx_business_events_metadata_invoice_number ON business_events
    USING gin ((metadata->'invoice_number'));
CREATE INDEX idx_business_events_metadata_payment_reference ON business_events
    USING gin ((metadata->'payment_reference'));
CREATE INDEX idx_business_events_reconciliation_match ON business_events
    USING gin ((metadata->'reconciliation_match_id'));
```

**audit_logs table:**

```sql
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    actor_type VARCHAR(50) NOT NULL,
    actor_id VARCHAR(255) NOT NULL,
    request_id UUID,
    changes JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
```

### Required SQL Query Functions

**Query Functions:**

1. **Get Business Event by ID**

```python
async def get_business_event_by_id(event_id: str) -> BusinessEvent | None:
    query = """
        SELECT event_id, source_system, source_id, occurred_at, recorded_at,
               event_kind, amount_minor, currency, description, payer_id, payee_id,
               processing_state, processing_last_error, dedupe_key, metadata
        FROM business_events
        WHERE event_id = $1
    """
    row = await db.fetchrow(query, event_id)
    return BusinessEvent.from_db_row(row) if row else None
```

2. **Find Payment by Reference**

```python
async def find_payment_by_reference(
    payment_reference: str,
    processing_state: str,
    currency: str
) -> BusinessEvent | None:
    query = """
        SELECT event_id, source_system, source_id, occurred_at, recorded_at,
               event_kind, amount_minor, currency, description, payer_id, payee_id,
               processing_state, processing_last_error, dedupe_key, metadata
        FROM business_events
        WHERE event_kind = 'PAYMENT_SENT'
          AND processing_state = $1
          AND currency = $2
          AND metadata->>'payment_reference' = $3
          AND metadata->>'reconciliation_match_id' IS NULL
        LIMIT 1
    """
    row = await db.fetchrow(query, processing_state, currency, payment_reference)
    return BusinessEvent.from_db_row(row) if row else None
```

3. **Find Invoice by Number**

```python
async def find_invoice_by_number(
    invoice_number: str,
    processing_state: str,
    currency: str
) -> BusinessEvent | None:
    query = """
        SELECT event_id, source_system, source_id, occurred_at, recorded_at,
               event_kind, amount_minor, currency, description, payer_id, payee_id,
               processing_state, processing_last_error, dedupe_key, metadata
        FROM business_events
        WHERE event_kind = 'INVOICE_RECEIVED'
          AND processing_state = $1
          AND currency = $2
          AND metadata->>'invoice_number' = $3
          AND metadata->>'reconciliation_match_id' IS NULL
        LIMIT 1
    """
    row = await db.fetchrow(query, processing_state, currency, invoice_number)
    return BusinessEvent.from_db_row(row) if row else None
```

4. **Get Unreconciled Mapped Events (Polling Fallback)**

```python
async def get_unreconciled_mapped_events(limit: int = 50) -> List[BusinessEvent]:
    query = """
        SELECT event_id, source_system, source_id, occurred_at, recorded_at,
               event_kind, amount_minor, currency, description, payer_id, payee_id,
               processing_state, processing_last_error, dedupe_key, metadata
        FROM business_events
        WHERE processing_state = 'MAPPED'
          AND event_kind IN ('INVOICE_RECEIVED', 'PAYMENT_SENT')
          AND metadata->>'reconciliation_match_id' IS NULL
        ORDER BY recorded_at ASC
        LIMIT $1
    """
    rows = await db.fetch(query, limit)
    return [BusinessEvent.from_db_row(row) for row in rows]
```

### Atomic Update Functions (SQL Transactions)

**1. Update Both Events to RECONCILED**

```python
async def update_both_to_reconciled(
    event1_id: str,
    event2_id: str,
    match_info: dict
) -> None:
    async with db.transaction():
        # Update event 1
        query1 = """
            UPDATE business_events
            SET processing_state = 'RECONCILED',
                metadata = jsonb_set(
                    jsonb_set(
                        metadata,
                        '{reconciliation_match_id}',
                        to_jsonb($2::text)
                    ),
                    '{reconciliation_notes}',
                    COALESCE(metadata->'reconciliation_notes', '[]'::jsonb) ||
                        to_jsonb($3::jsonb)
                ),
                updated_at = NOW()
            WHERE event_id = $1
        """
        await db.execute(query1, event1_id, event2_id, match_info)

        # Update event 2 (symmetric)
        query2 = """
            UPDATE business_events
            SET processing_state = 'RECONCILED',
                metadata = jsonb_set(
                    jsonb_set(
                        metadata,
                        '{reconciliation_match_id}',
                        to_jsonb($2::text)
                    ),
                    '{reconciliation_notes}',
                    COALESCE(metadata->'reconciliation_notes', '[]'::jsonb) ||
                        to_jsonb($3::jsonb)
                ),
                updated_at = NOW()
            WHERE event_id = $1
        """
        await db.execute(query2, event2_id, event1_id, match_info)

        # Transaction commits automatically if no exceptions
        # Rolls back both updates if either fails
```

**2. Flag Both Events for Review**

```python
async def flag_both_for_review(
    event1_id: str,
    event2_id: str,
    discrepancy: dict
) -> None:
    async with db.transaction():
        query = """
            UPDATE business_events
            SET processing_state = 'FLAGGED_FOR_REVIEW',
                metadata = jsonb_set(
                    jsonb_set(
                        metadata,
                        '{reconciliation_match_id}',
                        to_jsonb($2::text)
                    ),
                    '{reconciliation_notes}',
                    COALESCE(metadata->'reconciliation_notes', '[]'::jsonb) ||
                        to_jsonb($3::jsonb)
                ),
                updated_at = NOW()
            WHERE event_id = $1
        """
        await db.execute(query, event1_id, event2_id, discrepancy)
        await db.execute(query, event2_id, event1_id, discrepancy)
```

**3. Update Reconciliation Attempt Timestamp**

```python
async def update_reconciliation_attempt(event_id: str, attempted_at: str) -> None:
    query = """
        UPDATE business_events
        SET metadata = jsonb_set(
                metadata,
                '{reconciliation_attempted_at}',
                to_jsonb($2::text)
            ),
            updated_at = NOW()
        WHERE event_id = $1
    """
    await db.execute(query, event_id, attempted_at)
```

**4. Create Audit Log**

```python
async def create_audit_log(
    action: str,
    entity_type: str,
    entity_id: str,
    actor_type: str,
    actor_id: str,
    changes: List[dict],
    metadata: dict
) -> None:
    query = """
        INSERT INTO audit_logs
            (action, entity_type, entity_id, actor_type, actor_id, changes, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    await db.execute(
        query,
        action,
        entity_type,
        entity_id,
        actor_type,
        actor_id,
        json.dumps(changes),
        json.dumps(metadata)
    )
```

### Database Connection Setup

**Using asyncpg (recommended for PostgreSQL):**

```python
# src/database/connection.py
import asyncpg
from contextlib import asynccontextmanager

class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20,
            command_timeout=60
        )

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    @asynccontextmanager
    async def transaction(self):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
```

### Database Transaction Safety Features

1. **Row-Level Locking (Prevent Duplicate Processing)**

```python
async def get_business_event_with_lock(event_id: str) -> BusinessEvent | None:
    query = """
        SELECT * FROM business_events
        WHERE event_id = $1
        FOR UPDATE NOWAIT
    """
    # NOWAIT ensures immediate failure if row is already locked
    # Prevents two agents from processing same event simultaneously
```

2. **Optimistic Locking with Version Field**

```sql
ALTER TABLE business_events ADD COLUMN version INTEGER DEFAULT 1;

-- Update query checks version hasn't changed
UPDATE business_events
SET processing_state = 'RECONCILED',
    version = version + 1,
    updated_at = NOW()
WHERE event_id = $1 AND version = $2;
-- If 0 rows updated, someone else modified it first
```

3. **Idempotency Check Before Update**

```python
async def safe_update_to_reconciled(event1_id: str, event2_id: str):
    async with db.transaction():
        # Verify neither is already reconciled
        check_query = """
            SELECT COUNT(*) FROM business_events
            WHERE event_id IN ($1, $2)
              AND processing_state = 'MAPPED'
              AND metadata->>'reconciliation_match_id' IS NULL
        """
        count = await db.fetchval(check_query, event1_id, event2_id)

        if count != 2:
            raise AlreadyReconciledError("One or both events already reconciled")

        # Proceed with update (both checks passed)
        await update_both_to_reconciled(event1_id, event2_id, match_info)
```

## 5. Error Handling & Resilience

### Transaction Failure Recovery

- **Problem**: Database update fails mid-transaction
- **Solution**: Use atomic database transactions (rollback on failure)
- **Retry Logic**: Exponential backoff (3 attempts: 0s, 2s, 4s)
- **Dead Letter Queue**: Move failed events to DLQ after 3 attempts for manual review

### Duplicate Processing Prevention

- Check `metadata.reconciliation_match_id` before processing
- Use database row-level locking during updates
- Idempotency: Re-running same event_id should be safe

### Missing Counterpart Handling

- Update `metadata.reconciliation_attempted_at` timestamp
- Wait for counterpart to arrive (polling will retry later)
- Log attempt count in metadata to detect perpetually unmatched events

### Agent Crash Recovery

- Polling fallback ensures events aren't lost
- Agent can restart safely (no in-memory state required)
- All state persisted in database

## 6. Testing Plan

### Test Case 1: High-Confidence Match (Primary Match)

**Setup:**

- Create INVOICE_RECEIVED event: `invoice_number="INV-001"`, `amount_minor=100000` (USD 1000.00), `state='MAPPED'`
- Create PAYMENT_SENT event: `payment_reference="INV-001"`, `amount_minor=100000`, `state='MAPPED'`

**Expected Result:**

- Both events updated to `state='RECONCILED'`
- `metadata.reconciliation_match_id` set on both (cross-reference)
- AuditLog entry created with action='RECONCILE'

### Test Case 2: Partial Payment Match (Amount Discrepancy)

**Setup:**

- Create INVOICE_RECEIVED: `invoice_number="INV-002"`, `amount_minor=100000`, `state='MAPPED'`
- Create PAYMENT_SENT: `payment_reference="INV-002"`, `amount_minor=95000` (short $50), `state='MAPPED'`

**Expected Result:**

- Both events updated to `state='FLAGGED_FOR_REVIEW'`
- `metadata.reconciliation_notes` contains discrepancy details: `{"type": "AMOUNT_MISMATCH", "difference": 5000}`
- Human review workflow triggered

### Test Case 3: No Match (Orphaned Invoice)

**Setup:**

- Create INVOICE_RECEIVED: `invoice_number="INV-003"`, `amount_minor=100000`, `state='MAPPED'`
- No corresponding payment exists

**Expected Result:**

- Invoice remains in `state='MAPPED'`
- `metadata.reconciliation_attempted_at` updated with current timestamp
- No changes to processing state
- Polling will retry later (when payment arrives)

### Test Case 4: Database Transaction Failure

**Setup:**

- Create matching invoice and payment
- Force database connection failure during update

**Expected Result:**

- Transaction rolls back (neither event updated)
- Agent retries after exponential backoff
- No partial state (both events remain in `MAPPED` or both move to `RECONCILED`)

### Test Case 5: Duplicate Processing Prevention

**Setup:**

- Create matching invoice and payment
- Trigger reconciliation twice simultaneously

**Expected Result:**

- First request processes successfully
- Second request detects `reconciliation_match_id` already set and exits early
- No duplicate audit logs or state corruption

### Test Case 6: Currency Mismatch Prevention

**Setup:**

- Create INVOICE_RECEIVED: `invoice_number="INV-004"`, `amount_minor=100000`, `currency='USD'`
- Create PAYMENT_SENT: `payment_reference="INV-004"`, `amount_minor=100000`, `currency='EUR'`

**Expected Result:**

- No match detected (currency filter in query)
- Both remain `MAPPED`, waiting for correct currency counterpart

### Test Case 7: Event-Driven Trigger

**Setup:**

- FastAPI verification endpoint updates invoice to `state='MAPPED'`
- Endpoint publishes message to agent queue

**Expected Result:**

- Agent receives message within 1 second
- Processes reconciliation immediately
- Faster than polling interval (60s)

### Test Case 8: Polling Fallback (Missed Event)

**Setup:**

- Message queue is down
- Invoice updated to `state='MAPPED'` but message not sent
- Agent's polling interval triggers

**Expected Result:**

- Polling query finds unprocessed `MAPPED` event
- Agent processes it via polling path
- Event reconciled within 60 seconds (polling interval)

## 7. Integration with Other Agents

### With Document Processing Agent

- Document agent creates BusinessEvents with `state='PENDING'`
- After human/system verification, updates to `state='MAPPED'`
- Sends event-driven notification to Reconciliation Agent

### With Audit & Verification Agent

- Reconciliation Agent sets `state='RECONCILED'`
- Audit Agent monitors for `RECONCILED` events
- Audit Agent records to Sui blockchain and updates to `state='POSTED_ONCHAIN'`

### With Financial Assistant Agent

- Query agent reads `processing.state` and `metadata.reconciliation_match_id`
- Can answer questions like "Show me all unreconciled invoices" (state='MAPPED', event_kind='INVOICE_RECEIVED')
- Can display linked invoice-payment pairs using reconciliation_match_id

## 8. Implementation Files

**Agent Implementation:**

- `src/agents/reconciliation_agent.py` - Main agent class using uAgents framework
- `src/agents/reconciliation/matcher.py` - Matching logic and rules
- `src/agents/reconciliation/models.py` - Pydantic models for MatchResult

**Database Layer:**

- `src/database/repositories/business_event_repository.py` - Query and update functions
- `src/database/repositories/audit_log_repository.py` - Audit trail functions

**API Integration:**

- `src/api/routes/verification.py` - FastAPI endpoint that triggers reconciliation
- `src/messaging/reconciliation_publisher.py` - Message queue publisher

**Tests:**

- `tests/agents/test_reconciliation_agent.py` - Unit tests for matching logic
- `tests/integration/test_reconciliation_flow.py` - End-to-end integration tests

## 9. Configuration

```yaml
# config/reconciliation_agent.yaml
reconciliation:
  polling_interval_seconds: 60
  amount_tolerance_percent: 1.0 # Allow 1% variance for rounding
  max_retry_attempts: 3
  retry_backoff_seconds: [0, 2, 4]
  message_queue:
    type: redis # or rabbitmq
    host: localhost
    port: 6379
    channel: reconciliation_events
```

## 10. Monitoring & Observability

**Key Metrics:**

- `reconciliation_attempts_total` (counter)
- `reconciliation_matches_by_type` (gauge: primary_match, partial_match, no_match)
- `reconciliation_processing_duration_seconds` (histogram)
- `reconciliation_errors_total` (counter)

**Alerts:**

- Alert if `no_match` rate exceeds 50% (possible data quality issue)
- Alert if processing duration exceeds 5 seconds (database performance)
- Alert if error rate exceeds 5% (system health issue)
