import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from datetime import datetime, timezone
import hashlib, asyncio, os
from backend.agents.audit_verification_agent import DocumentMetadata, BusinessEvent, process_and_post_event, load_config_from_env

# optional: set env here or export before running
# os.environ["USE_SUI_DOCKER_CLI"] = "true"

doc_hash = hashlib.sha256(b"mock document").hexdigest()
event = BusinessEvent(event_id="evt-test-2", amount_minor=5005, occurred_at=datetime.now(timezone.utc), document_meta=DocumentMetadata(sha256=doc_hash), event_kind="test")

config = load_config_from_env()
result = asyncio.run(process_and_post_event(event, config))
print("processing_state:", event.processing_state)
print("sui field:", event.sui)
print("result:", result)