# Financial Analysis Agent
# This file contains the main financial analysis agent with 3-step workflow
import asyncpg
import yaml
import os
import httpx
from uagents import Agent, Context, Model
from pydantic import Field
from typing import Dict, Any, Optional

# --- Global DB Pool & Config ---
db_pool: Optional[asyncpg.Pool] = None
agent_config: Dict[str, Any] = {}

# --- Agent Definition ---
FINANCIAL_ANALYSIS_AGENT_SEED = os.environ.get("FINANCIAL_ANALYSIS_AGENT_SEED", "financial_analysis_agent_default_seed")
agent = Agent(name="FinancialAnalysisAgent", seed=FINANCIAL_ANALYSIS_AGENT_SEED)

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

class ChatMessage(Model):
    """Simple chat message model for user queries"""
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

# --- Agent Handlers ---

@agent.on_message(model=ChatMessage)
async def on_message(ctx: Context, sender: str, msg: ChatMessage):
    """
    Main message handler that orchestrates the 3-step workflow:
    1. Parse intent from user message using LLM
    2. Retrieve data from database based on intent
    3. Generate response using LLM with retrieved data
    """
    ctx.logger.info(f"Financial analysis request received: {msg.message}")
    
    try:
        # Step 1: Parse intent from user message
        intent = _parse_intent_from_llm(ctx, msg.message)
        ctx.logger.info(f"Parsed intent: {intent}")
        
        # Step 2: Retrieve data from database
        data = await _retrieve_data_from_db(ctx, intent)
        ctx.logger.info(f"Retrieved data: {len(data) if isinstance(data, list) else 'single record'}")
        
        # Step 3: Generate response using LLM
        response = _generate_response_from_llm(ctx, msg.message, data)
        ctx.logger.info("Generated response successfully")
        
        return response
        
    except Exception as e:
        ctx.logger.error(f"Error in financial analysis workflow: {e}")
        return f"Sorry, I encountered an error while processing your request: {str(e)}"

# --- Helper Functions ---

def _parse_intent_from_llm(ctx: Context, user_message: str) -> Dict[str, Any]:
    """
    Parse user intent using ASI:One API with 'Parse Intent' system prompt.
    This function will call the ASI:One API using ASI_API_KEY from environment variables.
    """
    # Stub implementation - will be replaced with ASI:One API call
    ctx.logger.info("Parsing intent from user message using ASI:One API")
    
    # For now, return a simple intent structure
    return {
        "intent_type": "financial_analysis",
        "query_type": "general",
        "parameters": {
            "message": user_message
        }
    }

async def _retrieve_data_from_db(ctx: Context, intent: Dict[str, Any]) -> Any:
    """
    Retrieve data from database based on parsed intent.
    This will import build_sql_query from agents.financial_analysis.query_builder,
    run the query, and return the data.
    """
    from agents.financial_analysis.query_builder import build_sql_query, execute_query
    
    ctx.logger.info("Retrieving data from database based on intent")
    
    db_pool = ctx.storage.get("db_pool")
    if not db_pool:
        raise RuntimeError("Database pool not available")
    
    # Build SQL query based on intent
    query, parameters = build_sql_query(intent)
    ctx.logger.info(f"Built SQL query: {query}")
    ctx.logger.info(f"Query parameters: {parameters}")
    
    # Execute query and return results
    async with db_pool.acquire() as db:
        data = await execute_query(db, query, parameters)
        return data

def _generate_response_from_llm(ctx: Context, user_message: str, data: Any) -> str:
    """
    Generate response using ASI:One API with 'Generate Response' prompt.
    This will call the ASI:One API a second time with the retrieved data.
    """
    # Stub implementation - will be replaced with ASI:One API call
    ctx.logger.info("Generating response using ASI:One API")
    
    # For now, return a simple response
    return f"Based on your query '{user_message}', I found {len(data) if isinstance(data, list) else 'some'} relevant data. This is a placeholder response."

if __name__ == "__main__":
    agent.run()
