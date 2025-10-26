from datetime import datetime, timezone
import hashlib
import json
import os
import shlex
import subprocess
import asyncio
from typing import Optional

# Optional .env loader (python-dotenv fallback-free parser)
def _load_dotenv(path: str = ".env") -> None:
    """Load simple KEY=VALUE lines from a .env file into os.environ if not already set.
    Ignores comments and blank lines. Does not overwrite existing environment variables.
    """
    try:
        with open(path, "r") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except FileNotFoundError:
        return

# uagents imports (optional runtime dependency)
try:
    from uagents import Agent, Context, Model
except Exception:  # pragma: no cover - allow tests to import without uagents
    Agent = None
    Context = None
    Model = object

# Import audit request/response models
try:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from document_processing.models import AuditVerificationRequest, AuditVerificationResponse
except ImportError:
    # Fallback if imports fail
    AuditVerificationRequest = None
    AuditVerificationResponse = None


# Placeholder Pydantic-style models (lightweight)
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
        # return the args in order expected by the Move function (as strings)
        return [self.tx_id, str(self.amount), str(self.timestamp), self.document_hash, self.category, str(self.status)]


def map_business_event_to_transaction_hash(event: BusinessEvent) -> TransactionHash:
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
    # Example: sui client call --package 0x... --module financial_audit --function record_transaction --args <args> --gas-budget 100000000
    args = tx.to_args()
    # Convert args to space-separated quoted values for shell
    quoted_args = " ".join(shlex.quote(a) for a in args)
    # Sui CLI command structure (sender is determined by active address in client config)
    cmd_parts = ["sui", "client", "call", "--package", package_id, "--module", module, "--function", function, "--args", quoted_args]
    if gas:
        cmd_parts.extend(["--gas-budget", gas])
    else:
        cmd_parts.extend(["--gas-budget", "100000000"])  # default gas budget
    return " ".join(cmd_parts)


def run_shell_command(command: str, timeout: int = 120) -> str:
    """Run shell command and return stdout. Raises subprocess.CalledProcessError on failure."""
    proc = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, text=True)
    return proc.stdout


async def process_and_post_event(event: BusinessEvent, config: dict):
    tx = map_business_event_to_transaction_hash(event)
    package_id = config.get("SUI_PACKAGE_ID")
    module = config.get("SUI_MODULE", "financial_audit")
    function = config.get("SUI_FUNCTION", "record_transaction_fields")
    audit_trail_obj_id = config.get("AUDIT_TRAIL_OBJ_ID")
    sender = config.get("SENDER_ADDRESS")
    gas = config.get("GAS_BUDGET")

    if not all([package_id, audit_trail_obj_id, sender]):
        raise RuntimeError("Missing Sui configuration (SUI_PACKAGE_ID, AUDIT_TRAIL_OBJ_ID, SENDER_ADDRESS)")

    cmd = build_sui_move_call(package_id=package_id, module=module, function=function, audit_trail_obj_id=audit_trail_obj_id, tx=tx, sender=sender, gas=gas)
    # Prepend the audit trail object id to the args list (Move fn may expect a mutable reference first)
    cmd = cmd.replace("--args", f"--args {shlex.quote(audit_trail_obj_id)}")

    # Determine whether to run the sui CLI locally or inside the docker compose 'sui-cli' service
    use_docker_cli = config.get("USE_SUI_DOCKER_CLI", True)
    compose_file = config.get("DOCKER_COMPOSE_FILE")
    # When running inside docker, use the docker service name; otherwise use localhost
    sui_rpc_url = config.get("SUI_RPC_URL") or ("http://sui-localnet:9000" if use_docker_cli else "http://127.0.0.1:9000")

    # If using docker, wrap the command with docker compose exec to run inside the sui-cli container
    if use_docker_cli:
        # default compose file: relative to this repo if not provided
        if not compose_file:
            compose_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sui_env", "docker-compose.yml"))
        # Setup sui client environment, request gas, and run the command
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
        # run locally; prefix the environment variable so sui client uses the correct RPC endpoint
        run_cmd = f"SUI_RPC_URL={shlex.quote(sui_rpc_url)} {cmd}"

    output = ""
    try:
        output = run_shell_command(run_cmd)
        # naive parse: look for "Transaction Digest" or "transaction" in output
        digest = None
        for line in output.splitlines():
            if "Transaction Digest" in line or "transaction" in line.lower():
                digest = line.strip()
                break
        event.processing_state = ProcessingState.POSTED_ONCHAIN
        event.sui = {"raw_output": output, "digest": digest}
        return {"success": True, "output": output, "digest": digest}
    except subprocess.CalledProcessError as e:
        event.processing_state = ProcessingState.FAILED_ONCHAIN_POSTING
        event.sui = {"raw_output": getattr(e, "output", ""), "error": str(e)}
        return {"success": False, "output": getattr(e, "output", ""), "error": str(e)}


# Agent scaffolding using uagents. If uagents isn't installed, provide a simple CLI fallback.
AGENT_NAME = os.environ.get("AUDIT_AGENT_NAME", "audit_verification_agent")


async def _run_agent_loop(config: dict):
    # placeholder BusinessEvent for testing
    doc_hash = hashlib.sha256(b"placeholder document").hexdigest()
    event = BusinessEvent(event_id="evt-placeholder-1", amount_minor=1000, occurred_at=datetime.now(timezone.utc), document_meta=DocumentMetadata(sha256=doc_hash), event_kind="placeholder")
    print(f"[agent] Processing placeholder event {event.event_id}")
    result = await process_and_post_event(event, config)
    print(f"[agent] Result: {json.dumps(result)}")


def load_config_from_env() -> dict:
    # attempt to load .env file from repo root if present (do not overwrite existing envs)
    _load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    return {
        "SUI_PACKAGE_ID": os.environ.get("SUI_PACKAGE_ID"),
        "SUI_MODULE": os.environ.get("SUI_MODULE", "financial_audit"),
        "SUI_FUNCTION": os.environ.get("SUI_FUNCTION", "record_transaction_fields"),
        "AUDIT_TRAIL_OBJ_ID": os.environ.get("AUDIT_TRAIL_OBJ_ID"),
        "SENDER_ADDRESS": os.environ.get("SENDER_ADDRESS"),
        "GAS_BUDGET": os.environ.get("GAS_BUDGET"),
        "USE_SUI_DOCKER_CLI": os.environ.get("USE_SUI_DOCKER_CLI", "true").lower() in ("true", "1", "yes"),
        "DOCKER_COMPOSE_FILE": os.environ.get("DOCKER_COMPOSE_FILE"),
        "SUI_RPC_URL": os.environ.get("SUI_RPC_URL"),  # No default here - will be set based on docker vs local
    }


async def handle_audit_request_logic(event_dict: dict, request_id: str, config: dict):
    """
    Handle audit request logic - can be called from agent handler or directly.
    Returns dict with success, digest, and error fields.
    """
    try:
        # Create lightweight BusinessEvent for Sui posting
        doc_meta = DocumentMetadata(sha256=event_dict["documents"][0]["sha256"])
        
        # Parse occurred_at - handle both string and datetime objects
        occurred_at = event_dict["occurred_at"]
        if isinstance(occurred_at, str):
            occurred_at = datetime.fromisoformat(occurred_at.replace('Z', '+00:00'))
        elif not isinstance(occurred_at, datetime):
            # If it's neither string nor datetime, use current time
            occurred_at = datetime.now(timezone.utc)
        
        event = BusinessEvent(
            event_id=event_dict["event_id"],
            amount_minor=event_dict["amount_minor"],
            occurred_at=occurred_at,
            document_meta=doc_meta,
            event_kind=event_dict["event_kind"]
        )
        
        # Post to Sui blockchain
        result = await process_and_post_event(event, config)
        
        return {
            "success": result["success"],
            "sui_digest": result.get("digest"),
            "error_message": result.get("error")
        }
        
    except Exception as e:
        return {
            "success": False,
            "sui_digest": None,
            "error_message": str(e)
        }


def main():
    config = load_config_from_env()
    # If uagents available, use on_interval handler; otherwise run simple loop once.
    if Agent is not None:
        agent = Agent(name=AGENT_NAME, seed=os.environ.get("AGENT_SEED", "dev_seed"), endpoint=os.environ.get("AGENT_ENDPOINT", "127.0.0.1"), port=int(os.environ.get("AGENT_PORT", "8001")))

        # Handler for audit verification requests from document agent
        if AuditVerificationRequest and AuditVerificationResponse:
            @agent.on_message(AuditVerificationRequest)
            async def handle_audit_request(ctx: Context, sender: str, msg: AuditVerificationRequest):
                """Receive BusinessEvent and post to Sui blockchain"""
                print(f"[audit agent] Received audit request {msg.request_id} from {sender}")
                
                result = await handle_audit_request_logic(msg.business_event, msg.request_id, config)
                
                # Send response back to document agent
                response = AuditVerificationResponse(
                    request_id=msg.request_id,
                    success=result["success"],
                    sui_digest=result.get("sui_digest"),
                    error_message=result.get("error_message")
                )
                
                await ctx.send(sender, response)
                print(f"[audit agent] Sent audit response for {msg.request_id}: success={result['success']}")

        @agent.on_interval(seconds=int(os.environ.get("AGENT_INTERVAL_SECONDS", "60")))
        async def periodic(_: Context):
            await _run_agent_loop(config)

        print(f"[audit agent] Starting agent at port {agent.port}")
        print(f"[audit agent] Agent address: {agent.address}")
        agent.run()
    else:
        # CLI fallback for environments without uagents installed
        asyncio.run(_run_agent_loop(config))


if __name__ == "__main__":
    main()
