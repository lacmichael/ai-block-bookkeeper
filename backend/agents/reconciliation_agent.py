# Main reconciliation agent file
# This file will contain startup logic and handlers
import asyncpg
import yaml
import os
import httpx
from uuid import UUID
from datetime import datetime, timezone
from uagents import Agent, Context, Model
from pydantic import Field
from typing import Dict, Any, Optional

from domain.models import BusinessEvent, MatchResult
from agents.reconciliation.matcher import evaluate_match
import database.repositories.business_event_repository as db_repo

# --- Global DB Pool & Config ---
db_pool: Optional[asyncpg.Pool] = None
agent_config: Dict[str, Any] = {}

# --- Agent Definition ---
RECON_AGENT_SEED = os.environ.get("RECON_AGENT_SEED", "reconciliation_agent_default_seed")
agent = Agent(name="ReconciliationAgent", seed=RECON_AGENT_SEED)

def load_config():
    """Loads agent config from YAML and environment variables."""
    global agent_config
    with open("config/agent_config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    db_pass = os.environ.get("SUPABASE_DB_PASSWORD")
    if not db_pass:
        raise ValueError("SUPABASE_DB_PASSWORD environment variable not set.")
    
    config['database']['password'] = db_pass
    agent_config = config

# --- Agent Lifecycle Handlers ---

@agent.on_event("startup")
async def startup(ctx: Context):
    """Initializes the Supabase DB pool when the agent starts."""
    global db_pool
    
    load_config()
    ctx.storage.set("config", agent_config)
    
    ctx.logger.info("Connecting to SupABASE (PostgreSQL)...")
    db_config = agent_config['database']
    
    SUPABASE_CONN_STRING = (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['name']}"
    )

    try:
        db_pool = await asyncpg.create_pool(
            SUPABASE_CONN_STRING, min_size=5, max_size=20
        )
        ctx.storage.set("db_pool", db_pool)
        ctx.logger.info("Database pool connected. Agent is online.")
    except Exception as e:
        ctx.logger.error(f"Failed to connect to Supabase DB: {e}")
        raise e

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    """Closes the DB pool when the agent stops."""
    global db_pool
    if db_pool:
        ctx.logger.info("Closing database pool...")
        await db_pool.close()
        ctx.logger.info("Database pool closed. Agent is offline.")

# --- Agent Message Models ---

class ReconciliationRequest(Model):
    event_id: UUID

# --- Agent Handlers ---

@agent.on_message(model=ReconciliationRequest)
async def on_reconciliation_request(ctx: Context, sender: str, msg: ReconciliationRequest):
    """
    Event-driven handler triggered by the FastAPI endpoint.
    """
    ctx.logger.info(f"Event-driven request received for event: {msg.event_id}")
    db_pool = ctx.storage.get("db_pool")
    
    async with db_pool.acquire() as db:
        try:
            # Use a transaction for the check + update
            async with db.transaction():
                # We use a lock to prevent the polling agent from grabbing this
                await db.execute("SELECT 1 FROM business_events WHERE event_id = $1 FOR UPDATE NOWAIT", msg.event_id)
                await handle_reconciliation_logic(ctx, db, msg.event_id)
        except asyncpg.exceptions.LockNotAvailableError:
            ctx.logger.warning(f"Event {msg.event_id} is already being processed (likely by polling). Skipping.")
        except Exception as e:
            ctx.logger.error(f"Error in on_message handler for {msg.event_id}: {e}")

@agent.on_interval(period=agent_config.get('reconciliation', {}).get('polling_interval_seconds', 60))
async def polling_safety_net(ctx: Context):
    """
    Polling fallback to catch any events missed by the HTTP trigger.
    """
    ctx.logger.info("Polling for missed events...")
    db_pool = ctx.storage.get("db_pool")
    
    events_processed = 0
    try:
        async with db_pool.acquire() as db:
            # Start ONE transaction for the entire batch
            async with db.transaction():
                # This query uses FOR UPDATE NOWAIT to lock the rows
                events_to_process = await db_repo.get_unreconciled_mapped_events(db, limit=50)
                
                if not events_to_process:
                    ctx.logger.info("Polling: No new events found.")
                    return

                for event in events_to_process:
                    await handle_reconciliation_logic(ctx, db, event.event_id)
                    events_processed += 1
                    
        if events_processed > 0:
            ctx.logger.info(f"Polling: Processed {events_processed} missed events.")
            
    except asyncpg.exceptions.LockNotAvailableError:
        ctx.logger.warning("Polling: Could not acquire lock (race condition with event-handler). Will retry next cycle.")
    except Exception as e:
        ctx.logger.error(f"Error in polling handler: {e}")

# --- Core Logic ---

async def handle_reconciliation_logic(
    ctx: Context, db: asyncpg.Connection, event_id: UUID
):
    """
    The main reconciliation logic, shared by both handlers.
    Assumes it is already inside a database transaction.
    """
    # 1. Fetch the event
    event = await db_repo.get_business_event_by_id(db, event_id)
    
    # 2. Validate eligibility
    if not event or event.processing.state != 'MAPPED' or event.metadata.get('reconciliation_match_id'):
        return # Already processed or not ready

    # 3. Find potential counterpart
    counterpart = None
    if event.event_kind == 'INVOICE_RECEIVED':
        counterpart = await db_repo.find_payment_by_reference(
            db,
            payment_reference=event.metadata.get('invoice_number', ''),
            processing_state='MAPPED',
            currency=event.currency
        )
    elif event.event_kind == 'PAYMENT_SENT':
        counterpart = await db_repo.find_invoice_by_number(
            db,
            invoice_number=event.metadata.get('payment_reference', ''),
            processing_state='MAPPED',
            currency=event.currency
        )

    # 4. Apply Matching Rules
    match_result = evaluate_match(event, counterpart)

    # 5. Act on MatchResult and create audit logs
    if match_result.type == 'PRIMARY_MATCH':
        ctx.logger.info(f"PRIMARY_MATCH found for event {event_id}")
        await db_repo.update_both_to_reconciled(
            db, event.event_id, counterpart.event_id, match_result.model_dump()
        )
        await db_repo.create_audit_log(
            db, "RECONCILE_SUCCESS", event.event_id, [], match_result.model_dump()
        )
    
    elif match_result.type == 'PARTIAL_MATCH':
        ctx.logger.warn(f"PARTIAL_MATCH found for event {event_id}. Flagging.")
        await db_repo.flag_both_for_review(
            db, event.event_id, counterpart.event_id, match_result.model_dump()
        )
        await db_repo.create_audit_log(
            db, "RECONCILE_FAIL_PARTIAL", event.event_id, [], match_result.model_dump()
        )
        
    else: # NO_MATCH
        ctx.logger.info(f"NO_MATCH found for event {event_id}. Updating timestamp.")
        await db_repo.update_reconciliation_attempt(
            db, event.event_id, datetime.now(timezone.utc).isoformat()
        )
        
if __name__ == "__main__":
    agent.run()
