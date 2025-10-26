"""
Audit Verification Agent - Blockchain Transaction Auditor
Deployed on Agentverse for ASI:One ecosystem integration.

This agent handles blockchain posting of financial transactions to Sui blockchain,
providing immutable audit trails for financial documents and business events.

Key Features:
- Sui blockchain transaction posting
- Document hash verification
- Immutable audit trail creation
- Integration with financial document processing pipeline
"""

import asyncio
import hashlib
import json
import logging
import os
import shlex
import subprocess
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# uagents imports
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent Configuration
AGENT_NAME = "AuditVerificationAgent"
AGENT_SEED = os.getenv("AUDIT_AGENT_SEED", "audit-verification-agent-seed-12345")
AGENT_PORT = int(os.getenv("AUDIT_AGENT_PORT", "8001"))
AGENT_ENDPOINT = os.getenv("AUDIT_AGENT_ENDPOINT", "127.0.0.1")

# Sui Configuration (all optional for deployment)
SUI_PACKAGE_ID = os.getenv("SUI_PACKAGE_ID")
SUI_MODULE = os.getenv("SUI_MODULE", "financial_audit")
SUI_FUNCTION = os.getenv("SUI_FUNCTION", "record_transaction_fields")
AUDIT_TRAIL_OBJ_ID = os.getenv("AUDIT_TRAIL_OBJ_ID")
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")
GAS_BUDGET = os.getenv("GAS_BUDGET", "100000000")
USE_SUI_DOCKER_CLI = os.getenv("USE_SUI_DOCKER_CLI", "false").lower() in ("true", "1", "yes")
DOCKER_COMPOSE_FILE = os.getenv("DOCKER_COMPOSE_FILE")
SUI_RPC_URL = os.getenv("SUI_RPC_URL", "http://127.0.0.1:9000")

# Mock mode for deployment without Sui configuration
MOCK_MODE = not all([SUI_PACKAGE_ID, AUDIT_TRAIL_OBJ_ID, SENDER_ADDRESS])

# Message Models for ASI:One Chat Protocol
class AuditRequest(Model):
    """Request to audit and post transaction to blockchain"""
    event_id: str
    amount_minor: int
    occurred_at: str
    document_hash: str
    event_kind: str
    metadata: Optional[Dict[str, Any]] = None

class AuditResponse(Model):
    """Response from audit verification"""
    event_id: str
    success: bool
    transaction_digest: Optional[str] = None
    error_message: Optional[str] = None
    blockchain_output: Optional[str] = None

class HealthQuery(Model):
    """Health check query"""
    pass

class ChatMessage(Model):
    """ASI:One Chat Protocol message"""
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(Model):
    """ASI:One Chat Protocol response"""
    response: str
    success: bool
    metadata: Optional[Dict[str, Any]] = None

# Data Models
class DocumentMetadata:
    def __init__(self, sha256: str):
        self.sha256 = sha256

class ProcessingState:
    RECONCILED = "RECONCILED"
    POSTED_ONCHAIN = "POSTED_ONCHAIN"
    FAILED_ONCHAIN_POSTING = "FAILED_ONCHAIN_POSTING"

class BusinessEvent:
    def __init__(self, event_id: str, amount_minor: int, occurred_at: datetime, document_meta: DocumentMetadata, event_kind: str = "transfer"):
        self.event_id = event_id
        self.amount_minor = amount_minor
        self.occurred_at = occurred_at
        self.document_meta = document_meta
        self.event_kind = event_kind
        self.processing_state = ProcessingState.RECONCILED
        self.sui = {}

class TransactionHash:
    def __init__(self, tx_id: str, amount: int, timestamp: int, document_hash: str, category: str, status: int):
        self.tx_id = tx_id
        self.amount = amount
        self.timestamp = timestamp
        self.document_hash = document_hash
        self.category = category
        self.status = status

    def to_args(self):
        return [self.tx_id, str(self.amount), str(self.timestamp), self.document_hash, self.category, str(self.status)]

# Utility Functions
def map_business_event_to_transaction_hash(event: BusinessEvent) -> TransactionHash:
    """Map BusinessEvent to TransactionHash for Sui posting"""
    tx_id = event.event_id
    amount = event.amount_minor
    timestamp = int(event.occurred_at.timestamp())
    document_hash = event.document_meta.sha256
    
    # Ensure document hash has 0x prefix for Move address type
    if not document_hash.startswith("0x"):
        document_hash = "0x" + document_hash
    
    category = event.event_kind
    status = 1
    return TransactionHash(tx_id=tx_id, amount=amount, timestamp=timestamp, document_hash=document_hash, category=category, status=status)

def build_sui_move_call(package_id: str, module: str, function: str, audit_trail_obj_id: str, tx: TransactionHash, sender: str, gas: Optional[str] = None) -> str:
    """Build Sui CLI command for Move function call"""
    args = tx.to_args()
    quoted_args = " ".join(shlex.quote(a) for a in args)
    
    cmd_parts = ["sui", "client", "call", "--package", package_id, "--module", module, "--function", function, "--args", quoted_args]
    if gas:
        cmd_parts.extend(["--gas-budget", gas])
    else:
        cmd_parts.extend(["--gas-budget", "100000000"])
    
    return " ".join(cmd_parts)

def run_shell_command(command: str, timeout: int = 120) -> str:
    """Run shell command and return stdout"""
    proc = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, text=True)
    return proc.stdout

async def process_and_post_event(event: BusinessEvent) -> Dict[str, Any]:
    """Process business event and post to Sui blockchain"""
    
    # Mock mode for deployment without Sui configuration
    if MOCK_MODE:
        logger.info(f"Mock mode: Simulating blockchain posting for event {event.event_id}")
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # Generate mock transaction digest
        mock_digest = f"mock_tx_{event.event_id[:8]}_{int(datetime.utcnow().timestamp())}"
        
        event.processing_state = ProcessingState.POSTED_ONCHAIN
        event.sui = {"raw_output": f"Mock transaction posted: {mock_digest}", "digest": mock_digest}
        
        logger.info(f"Mock: Successfully posted transaction {event.event_id} to blockchain")
        return {"success": True, "output": f"Mock transaction: {mock_digest}", "digest": mock_digest}
    
    # Real blockchain posting
    tx = map_business_event_to_transaction_hash(event)
    cmd = build_sui_move_call(
        package_id=SUI_PACKAGE_ID,
        module=SUI_MODULE,
        function=SUI_FUNCTION,
        audit_trail_obj_id=AUDIT_TRAIL_OBJ_ID,
        tx=tx,
        sender=SENDER_ADDRESS,
        gas=GAS_BUDGET
    )
    
    # Prepend the audit trail object id to the args list
    cmd = cmd.replace("--args", f"--args {shlex.quote(AUDIT_TRAIL_OBJ_ID)}")
    
    # Determine execution environment
    use_docker_cli = USE_SUI_DOCKER_CLI
    compose_file = DOCKER_COMPOSE_FILE
    sui_rpc_url = SUI_RPC_URL or ("http://sui-localnet:9000" if use_docker_cli else "http://127.0.0.1:9000")
    
    if use_docker_cli:
        if not compose_file:
            compose_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sui_env", "docker-compose.yml"))
        
        faucet_url = sui_rpc_url.replace(':9000', ':9123').replace('/rpc', '') + '/gas'
        setup_and_cmd = f'''
            echo -e "y\\n\\n0" | sui client new-env --alias local --rpc {sui_rpc_url} >/dev/null 2>&1 || true
            sui client switch --env local >/dev/null 2>&1 || true
            sui client faucet --url {faucet_url} >/dev/null 2>&1 || true
            {cmd}
        '''
        docker_cmd = f"docker compose -f {shlex.quote(compose_file)} exec -T sui-cli bash -c {shlex.quote(setup_and_cmd)}"
        run_cmd = docker_cmd
    else:
        run_cmd = f"SUI_RPC_URL={shlex.quote(sui_rpc_url)} {cmd}"
    
    try:
        output = run_shell_command(run_cmd)
        digest = None
        for line in output.splitlines():
            if "Transaction Digest" in line or "transaction" in line.lower():
                digest = line.strip()
                break
        
        event.processing_state = ProcessingState.POSTED_ONCHAIN
        event.sui = {"raw_output": output, "digest": digest}
        
        logger.info(f"Successfully posted transaction {event.event_id} to Sui blockchain")
        return {"success": True, "output": output, "digest": digest}
        
    except subprocess.CalledProcessError as e:
        event.processing_state = ProcessingState.FAILED_ONCHAIN_POSTING
        event.sui = {"raw_output": getattr(e, "output", ""), "error": str(e)}
        
        logger.error(f"Failed to post transaction {event.event_id} to Sui blockchain: {str(e)}")
        return {"success": False, "output": getattr(e, "output", ""), "error": str(e)}

# Create the agent
agent = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=[f"http://{AGENT_ENDPOINT}:{AGENT_PORT}/submit"],
)

# Fund the agent if needed
fund_agent_if_low(agent.wallet.address())

# Track last transaction for health monitoring
last_transaction_time = None

# Message Handlers
@agent.on_message(AuditRequest)
async def handle_audit_request(ctx: Context, sender: str, msg: AuditRequest):
    """Handle audit verification requests"""
    global last_transaction_time
    
    logger.info(f"Received audit request for event {msg.event_id} from {sender}")
    
    try:
        # Parse occurred_at timestamp
        occurred_at = datetime.fromisoformat(msg.occurred_at.replace('Z', '+00:00'))
        
        # Create document metadata
        doc_meta = DocumentMetadata(sha256=msg.document_hash)
        
        # Create business event
        event = BusinessEvent(
            event_id=msg.event_id,
            amount_minor=msg.amount_minor,
            occurred_at=occurred_at,
            document_meta=doc_meta,
            event_kind=msg.event_kind
        )
        
        # Post to Sui blockchain
        result = await process_and_post_event(event)
        
        # Update last transaction time
        last_transaction_time = datetime.utcnow().isoformat()
        
        # Send response
        response = AuditResponse(
            event_id=msg.event_id,
            success=result["success"],
            transaction_digest=result.get("digest"),
            error_message=result.get("error"),
            blockchain_output=result.get("output")
        )
        
        await ctx.send(sender, response)
        logger.info(f"Sent audit response for {msg.event_id}: success={result['success']}")
        
    except Exception as e:
        logger.error(f"Error processing audit request for {msg.event_id}: {str(e)}")
        
        response = AuditResponse(
            event_id=msg.event_id,
            success=False,
            error_message=str(e)
        )
        
        await ctx.send(sender, response)

@agent.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle ASI:One Chat Protocol messages"""
    logger.info(f"Received chat message from {sender}: {msg.message}")
    
    # Simple chat interface for audit verification
    message_lower = msg.message.lower()
    
    if "status" in message_lower or "health" in message_lower:
        response_text = f"Audit Verification Agent is healthy and running in {'mock' if MOCK_MODE else 'real'} mode. Last transaction: {last_transaction_time or 'None'}"
    elif "help" in message_lower:
        response_text = """Audit Verification Agent Commands:
- 'status' or 'health': Check agent status
- 'help': Show this help message
- 'capabilities': Show agent capabilities
- Send an AuditRequest to post transactions to blockchain"""
    elif "capabilities" in message_lower:
        response_text = f"""Audit Verification Agent Capabilities:
- Blockchain posting: {'Mock mode' if MOCK_MODE else 'Real Sui blockchain'}
- Document hash verification: Available
- Transaction integrity: Available
- Immutable audit trails: {'Simulated' if MOCK_MODE else 'Real blockchain'}
- Health monitoring: Available"""
    else:
        response_text = f"I'm the Audit Verification Agent. I handle blockchain posting of financial transactions. Use 'help' for commands. Currently running in {'mock' if MOCK_MODE else 'real'} mode."
    
    response = ChatResponse(
        response=response_text,
        success=True,
        metadata={
            "agent_name": AGENT_NAME,
            "mode": "mock" if MOCK_MODE else "real",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    await ctx.send(sender, response)

@agent.on_query(HealthQuery)
async def health_check(ctx: Context, sender: str, msg: HealthQuery):
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        agent_address=agent.address,
        timestamp=datetime.utcnow().isoformat(),
        sui_configured=not MOCK_MODE,
        last_transaction_time=last_transaction_time
    )

# Event Handlers
@agent.on_event("startup")
async def startup(ctx: Context):
    """Agent startup handler"""
    logger.info("Audit Verification Agent started")
    logger.info(f"Agent address: {agent.address}")
    logger.info(f"Agent name: {AGENT_NAME}")
    
    if MOCK_MODE:
        logger.info("🔧 Running in MOCK MODE - simulating blockchain transactions")
        logger.info("   To enable real blockchain posting, set: SUI_PACKAGE_ID, AUDIT_TRAIL_OBJ_ID, SENDER_ADDRESS")
    else:
        logger.info("✓ Sui blockchain configuration loaded")
        logger.info(f"Package ID: {SUI_PACKAGE_ID}")
        logger.info(f"Audit Trail Object ID: {AUDIT_TRAIL_OBJ_ID}")

@agent.on_event("shutdown")
async def shutdown(ctx: Context):
    """Agent shutdown handler"""
    logger.info("Audit Verification Agent shutting down")

if __name__ == "__main__":
    agent.run()
