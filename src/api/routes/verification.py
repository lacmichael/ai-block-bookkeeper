# FastAPI route for verification
# This file will contain the API endpoint that triggers the agent
import httpx
import os
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
import asyncpg

# This is a placeholder for your actual Supabase/DB dependency
# In a real FastAPI app, you'd have a dependency injection system
# For now, this is a simplified example.
async def get_db_connection():
    # This is NOT production-ready, but good for a modular example.
    # In reality, you'd use a shared pool.
    try:
        conn = await asyncpg.connect(os.environ.get("SUPABASE_CONN_STRING"))
        yield conn
    finally:
        await conn.close()

from src.database.repositories import business_event_repository as db_repo

router = APIRouter()

# Get the agent's address from an env var or config
RECON_AGENT_ADDRESS = os.environ.get("RECON_AGENT_ADDRESS", "http://127.0.0.1:8000/submit")

@router.post("/verify/{event_id}", status_code=202)
async def verify_event(
    event_id: UUID,
    db: asyncpg.Connection = Depends(get_db_connection)
):
    """
    Verifies an event and triggers the ReconciliationAgent.
    """
    try:
        # 1. Set the event status to 'MAPPED'
        await db_repo.set_event_status(db, event_id, "MAPPED")

        # 2. Trigger the agent via HTTP POST
        message = {"event_id": str(event_id)}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(RECON_AGENT_ADDRESS, json=message)
        
        # 3. Check if agent was successfully notified
        if response.status_code != 200:
            # Log the error, but don't fail the user request
            # The polling fallback will catch this.
            print(f"Warning: ReconciliationAgent returned {response.status_code}")
            
        return {"message": "Event verified. Reconciliation triggered."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
