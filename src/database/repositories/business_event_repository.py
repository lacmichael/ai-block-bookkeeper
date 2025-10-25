# Database repository for business events
# This file will contain all SQL functions and database operations
import asyncpg
import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from src.domain.models import BusinessEvent

#
# --- QUERY FUNCTIONS ---
#

async def get_business_event_by_id(
    db: asyncpg.Connection, event_id: UUID
) -> Optional[BusinessEvent]:
    """Fetches a single event by its ID."""
    row = await db.fetchrow(
        """
        SELECT * FROM business_events
        WHERE event_id = $1
        """,
        event_id
    )
    return BusinessEvent.model_validate(row) if row else None

async def find_payment_by_reference(
    db: asyncpg.Connection,
    payment_reference: str,
    processing_state: str,
    currency: str
) -> Optional[BusinessEvent]:
    """Finds a matching, unreconciled payment."""
    query = """
        SELECT * FROM business_events
        WHERE event_kind = 'PAYMENT_SENT'
          AND processing_state = $1
          AND currency = $2
          AND metadata->>'payment_reference' = $3
          AND metadata->>'reconciliation_match_id' IS NULL
        LIMIT 1
    """
    row = await db.fetchrow(query, processing_state, currency, payment_reference)
    return BusinessEvent.model_validate(row) if row else None

async def find_invoice_by_number(
    db: asyncpg.Connection,
    invoice_number: str,
    processing_state: str,
    currency: str
) -> Optional[BusinessEvent]:
    """Finds a matching, unreconciled invoice."""
    query = """
        SELECT * FROM business_events
        WHERE event_kind = 'INVOICE_RECEIVED'
          AND processing_state = $1
          AND currency = $2
          AND metadata->>'invoice_number' = $3
          AND metadata->>'reconciliation_match_id' IS NULL
        LIMIT 1
    """
    row = await db.fetchrow(query, processing_state, currency, invoice_number)
    return BusinessEvent.model_validate(row) if row else None

async def get_unreconciled_mapped_events(
    db: asyncpg.Connection, limit: int = 50
) -> List[BusinessEvent]:
    """
    Gets a batch of unreconciled events for polling.
    CRITICAL: Uses FOR UPDATE NOWAIT to prevent race conditions.
    """
    query = """
        SELECT * FROM business_events
        WHERE processing_state = 'MAPPED'
          AND event_kind IN ('INVOICE_RECEIVED', 'PAYMENT_SENT')
          AND metadata->>'reconciliation_match_id' IS NULL
        ORDER BY recorded_at ASC
        LIMIT $1
        FOR UPDATE NOWAIT
    """
    rows = await db.fetch(query, limit)
    return [BusinessEvent.model_validate(row) for row in rows]

#
# --- ATOMIC UPDATE FUNCTIONS ---
#

async def update_both_to_reconciled(
    db: asyncpg.Connection,
    event1_id: UUID,
    event2_id: UUID,
    match_info: Dict[str, Any]
) -> None:
    """Atomically updates two matched events to RECONCILED."""
    async with db.transaction():
        query = """
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
        await db.execute(query, event1_id, str(event2_id), json.dumps(match_info))
        await db.execute(query, event2_id, str(event1_id), json.dumps(match_info))

async def flag_both_for_review(
    db: asyncpg.Connection,
    event1_id: UUID,
    event2_id: UUID,
    discrepancy: Dict[str, Any]
) -> None:
    """Atomically updates two partially-matched events to FLAGGED_FOR_REVIEW."""
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
        await db.execute(query, event1_id, str(event2_id), json.dumps(discrepancy))
        await db.execute(query, event2_id, str(event1_id), json.dumps(discrepancy))

async def update_reconciliation_attempt(
    db: asyncpg.Connection, event_id: UUID, attempted_at: str
) -> None:
    """Updates the attempt timestamp for an event with no match."""
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

async def create_audit_log(
    db: asyncpg.Connection,
    action: str,
    entity_id: UUID,
    changes: List[Dict[str, Any]],
    metadata: Dict[str, Any]
) -> None:
    """Inserts a new record into the audit log."""
    query = """
        INSERT INTO audit_logs
            (action, entity_type, entity_id, actor_type, actor_id, changes, metadata)
        VALUES ($1, 'BUSINESS_EVENT', $2, 'AI_AGENT', 'reconciliation-agent', $3, $4)
    """
    await db.execute(
        query,
        action,
        entity_id,
        json.dumps(changes),
        json.dumps(metadata)
    )

async def set_event_status(
    db: asyncpg.Connection, event_id: UUID, status: str
) -> None:
    """Simple status update function needed by the FastAPI verification route."""
    await db.execute(
        "UPDATE business_events SET processing_state = $1 WHERE event_id = $2",
        status,
        event_id
    )
